import json
import hashlib
import datetime
from typing import List, Dict, Optional, Any
from openai import OpenAI
import nailfec


class HPC_ChatBot:
    """
    SK (Shame Kitten) HPC Services ChatBot
    Provides AI-powered assistance for GPU booking, querying, and management
    """
    
    def __init__(self):
        """Initialize the chatbot with API client and load data"""
        self.client = OpenAI(
            api_key=nailfec.api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Load GPU inventory and bookings data
        with open('gpu_inventory.json', 'r') as f:
            self.gpu_data = json.load(f)
        
        with open('bookings.json', 'r') as f:
            self.bookings = json.load(f)
        
        # Conversation history
        self.conversation_history = []
        
        # Current booking session data
        self.current_booking = {}
        
        # Define available functions for the AI
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_available_gpus",
                    "description": "Search for available GPU instances based on model, time range, and specifications",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "GPU model to search for (e.g., 'RTX-4090', 'H100', 'A100'). If not specified, search all models."
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Start time in ISO format (e.g., '2025-07-23T10:00:00Z')"
                            },
                            "end_time": {
                                "type": "string",
                                "description": "End time in ISO format (e.g., '2025-07-23T18:00:00Z')"
                            },
                            "min_memory": {
                                "type": "number",
                                "description": "Minimum GPU memory required in GB"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_gpu_recommendations",
                    "description": "Get GPU recommendations based on user's use case and requirements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "use_case": {
                                "type": "string",
                                "description": "Description of the intended use case (e.g., 'LLaMA 8B training', 'gaming', 'video rendering')"
                            },
                            "budget_per_hour": {
                                "type": "number",
                                "description": "Maximum budget per hour in USD"
                            },
                            "memory_requirement": {
                                "type": "number",
                                "description": "Required GPU memory in GB"
                            }
                        },
                        "required": ["use_case"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_booking",
                    "description": "Create a new GPU booking reservation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "gpu_model": {
                                "type": "string",
                                "description": "GPU model to book"
                            },
                            "gpu_id": {
                                "type": "string",
                                "description": "Specific GPU instance ID"
                            },
                            "user_name": {
                                "type": "string",
                                "description": "User's full name"
                            },
                            "user_email": {
                                "type": "string",
                                "description": "User's email address"
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Start time in ISO format"
                            },
                            "end_time": {
                                "type": "string",
                                "description": "End time in ISO format"
                            },
                            "storage_gb": {
                                "type": "number",
                                "description": "Required storage in GB (default: 128)"
                            },
                            "memory_gb": {
                                "type": "number",
                                "description": "Required system memory in GB (default: 32)"
                            },
                            "cpu_cores": {
                                "type": "number",
                                "description": "Required CPU cores (default: 8)"
                            }
                        },
                        "required": ["gpu_model", "gpu_id", "user_name", "user_email", "start_time", "end_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_booking_info",
                    "description": "Query booking information by booking hash, email, or booking ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "booking_hash": {
                                "type": "string",
                                "description": "Booking hash identifier"
                            },
                            "user_email": {
                                "type": "string",
                                "description": "User's email address"
                            },
                            "booking_id": {
                                "type": "string",
                                "description": "Booking ID"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_booking",
                    "description": "Cancel an existing booking",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "booking_hash": {
                                "type": "string",
                                "description": "Booking hash identifier"
                            },
                            "user_email": {
                                "type": "string",
                                "description": "User's email for verification"
                            }
                        },
                        "required": ["booking_hash", "user_email"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_billing",
                    "description": "Calculate billing information for bookings",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_email": {
                                "type": "string",
                                "description": "User's email address"
                            },
                            "booking_hash": {
                                "type": "string",
                                "description": "Specific booking hash (optional)"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date for billing period (ISO format)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date for billing period (ISO format)"
                            }
                        },
                        "required": ["user_email"]
                    }
                }
            }
        ]

    def search_available_gpus(self, model: str = None, start_time: str = None, 
                            end_time: str = None, min_memory: float = None) -> Dict:
        """Search for available GPU instances"""
        available_gpus = []
        
        for gpu_model, gpu_info in self.gpu_data["gpu_models"].items():
            if model and model.lower() not in gpu_model.lower():
                continue
                
            if min_memory and float(gpu_info["memory"].split("GB")[0]) < min_memory:
                continue
            
            # Check availability for each instance
            for instance in gpu_info["instances"]:
                is_available = True
                
                if start_time and end_time:
                    # Check for conflicts with existing bookings
                    for booking in self.bookings:
                        if (booking["gpu_id"] == instance["id"] and 
                            booking["status"] in ["active", "scheduled"]):
                            booking_start = datetime.datetime.fromisoformat(booking["start_time"].replace('Z', '+00:00'))
                            booking_end = datetime.datetime.fromisoformat(booking["end_time"].replace('Z', '+00:00'))
                            request_start = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            request_end = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                            
                            if (request_start < booking_end and request_end > booking_start):
                                is_available = False
                                break
                
                if is_available:
                    available_gpus.append({
                        "model": gpu_model,
                        "id": instance["id"],
                        "name": gpu_info["name"],
                        "memory": gpu_info["memory"],
                        "description": gpu_info["description"],
                        "price_per_30min": gpu_info["price_per_30min"],
                        "cuda_cores": gpu_info["cuda_cores"]
                    })
        
        return {"available_gpus": available_gpus}

    def get_gpu_recommendations(self, use_case: str, budget_per_hour: float = None, 
                              memory_requirement: float = None) -> Dict:
        """Get GPU recommendations based on use case"""
        recommendations = []
        use_case_lower = use_case.lower()
        
        # Define use case patterns and recommendations
        if "llama" in use_case_lower or "llm" in use_case_lower or "language model" in use_case_lower:
            if "8b" in use_case_lower or "7b" in use_case_lower:
                # 8B models need ~16GB VRAM
                recommended_models = ["RTX-4090", "RTX-3090", "A100", "H100"]
            elif "13b" in use_case_lower:
                # 13B models need ~26GB VRAM
                recommended_models = ["A100", "H100"]
            elif "70b" in use_case_lower or "65b" in use_case_lower:
                # Large models need 80GB VRAM
                recommended_models = ["H100"]
            else:
                recommended_models = ["RTX-4090", "A100", "H100"]
        elif "gaming" in use_case_lower:
            recommended_models = ["RTX-4090", "RTX-4080", "RTX-4070", "RTX-3080"]
        elif "rendering" in use_case_lower or "3d" in use_case_lower:
            recommended_models = ["RTX-4090", "RTX-4080", "RTX-3090"]
        elif "training" in use_case_lower or "ai" in use_case_lower:
            recommended_models = ["H100", "A100", "RTX-4090"]
        else:
            recommended_models = ["RTX-4070", "RTX-4080", "RTX-4090"]
        
        for model in recommended_models:
            if model in self.gpu_data["gpu_models"]:
                gpu_info = self.gpu_data["gpu_models"][model]
                price_per_hour = gpu_info["price_per_30min"] * 2
                
                # Apply filters
                if budget_per_hour and price_per_hour > budget_per_hour:
                    continue
                if memory_requirement and float(gpu_info["memory"].split("GB")[0]) < memory_requirement:
                    continue
                
                recommendations.append({
                    "model": model,
                    "name": gpu_info["name"],
                    "memory": gpu_info["memory"],
                    "description": gpu_info["description"],
                    "price_per_hour": price_per_hour,
                    "cuda_cores": gpu_info["cuda_cores"],
                    "available_instances": len(gpu_info["instances"])
                })
        
        return {"recommendations": recommendations}

    def create_booking(self, gpu_model: str, gpu_id: str, user_name: str, user_email: str,
                      start_time: str, end_time: str, storage_gb: int = 128, 
                      memory_gb: int = 32, cpu_cores: int = 8) -> Dict:
        """Create a new booking"""
        # Generate booking ID and hash
        booking_id = f"book_{len(self.bookings) + 1:03d}"
        booking_hash = hashlib.md5(f"{booking_id}{user_email}{start_time}".encode()).hexdigest()
        
        # Calculate cost
        gpu_info = self.gpu_data["gpu_models"][gpu_model]
        start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
        duration_slots = duration_hours * 2  # 30-minute slots
        total_cost = duration_slots * gpu_info["price_per_30min"]
        
        # Create booking
        new_booking = {
            "booking_id": booking_id,
            "booking_hash": booking_hash,
            "user_name": user_name,
            "user_email": user_email,
            "gpu_model": gpu_model,
            "gpu_id": gpu_id,
            "start_time": start_time,
            "end_time": end_time,
            "status": "scheduled",
            "storage_gb": storage_gb,
            "memory_gb": memory_gb,
            "cpu_cores": cpu_cores,
            "created_at": datetime.datetime.now().isoformat() + "Z",
            "total_cost": round(total_cost, 2),
            "overtime_minutes": 0,
            "overtime_cost": 0.00
        }
        
        self.bookings.append(new_booking)
        
        # Save to file
        with open('bookings.json', 'w') as f:
            json.dump(self.bookings, f, indent=2)
        
        return {"booking": new_booking, "success": True}

    def query_booking_info(self, booking_hash: str = None, user_email: str = None, 
                          booking_id: str = None) -> Dict:
        """Query booking information"""
        matching_bookings = []
        
        for booking in self.bookings:
            if booking_hash and booking["booking_hash"] == booking_hash:
                matching_bookings.append(booking)
            elif user_email and booking["user_email"] == user_email:
                matching_bookings.append(booking)
            elif booking_id and booking["booking_id"] == booking_id:
                matching_bookings.append(booking)
        
        return {"bookings": matching_bookings}

    def cancel_booking(self, booking_hash: str, user_email: str) -> Dict:
        """Cancel a booking"""
        for i, booking in enumerate(self.bookings):
            if (booking["booking_hash"] == booking_hash and 
                booking["user_email"] == user_email):
                if booking["status"] in ["scheduled", "active"]:
                    self.bookings[i]["status"] = "cancelled"
                    
                    # Save to file
                    with open('bookings.json', 'w') as f:
                        json.dump(self.bookings, f, indent=2)
                    
                    return {"success": True, "message": "Booking cancelled successfully"}
                else:
                    return {"success": False, "message": "Booking cannot be cancelled (already completed or cancelled)"}
        
        return {"success": False, "message": "Booking not found"}

    def calculate_billing(self, user_email: str, booking_hash: str = None, 
                         start_date: str = None, end_date: str = None) -> Dict:
        """Calculate billing information"""
        relevant_bookings = []
        total_cost = 0
        total_overtime_cost = 0
        
        for booking in self.bookings:
            if booking["user_email"] != user_email:
                continue
            
            if booking_hash and booking["booking_hash"] != booking_hash:
                continue
            
            booking_date = datetime.datetime.fromisoformat(booking["created_at"].replace('Z', '+00:00'))
            
            if start_date:
                start_dt = datetime.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if booking_date < start_dt:
                    continue
            
            if end_date:
                end_dt = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                if booking_date > end_dt:
                    continue
            
            relevant_bookings.append(booking)
            total_cost += booking["total_cost"]
            total_overtime_cost += booking["overtime_cost"]
        
        return {
            "bookings": relevant_bookings,
            "total_cost": round(total_cost, 2),
            "total_overtime_cost": round(total_overtime_cost, 2),
            "grand_total": round(total_cost + total_overtime_cost, 2),
            "booking_count": len(relevant_bookings)
        }

    def execute_function(self, function_name: str, parameters: Dict) -> Any:
        """Execute a function call and return the result"""
        function_map = {
            "search_available_gpus": self.search_available_gpus,
            "get_gpu_recommendations": self.get_gpu_recommendations,
            "create_booking": self.create_booking,
            "query_booking_info": self.query_booking_info,
            "cancel_booking": self.cancel_booking,
            "calculate_billing": self.calculate_billing
        }
        
        if function_name in function_map:
            try:
                return function_map[function_name](**parameters)
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": f"Unknown function: {function_name}"}

    def send_message_to_ai(self, user_message: str) -> str:
        """Send message to AI and get response"""
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Prepare system message
        system_message = {
            "role": "system",
            "content": """You are an AI assistant for SK (Shame Kitten) HPC Services, a company that provides high-performance computing GPU rental services. 

Your role is to help users with:
1. Booking GPU instances for various workloads
2. Querying existing bookings and billing information
3. Cancelling bookings
4. Providing GPU recommendations based on use cases
5. Answering questions about server status and services

Company information:
- SK (Shame Kitten) offers affordable, reliable, and stable HPC services
- We have various GPU models available: RTX-4090, RTX-4080, RTX-4070, RTX-3090, RTX-3080, H100, A100, V100
- Our services are cost-effective with excellent connectivity
- We support various use cases from gaming to AI training to scientific computing

Guidelines:
- Always be helpful, professional, and simple
- Ask questions one at a time, not all at once
- Use function calls to access real data when needed
- Never provide fixed responses - always process through AI
- Guide users through the booking process step by step
- IMPORTANT: Just reply 1~3 sentences is enough - do not give too much responses
- IMPORTANT: Do not ask too much questions at a time - just ask a simple question to ask at a time if you need to ask for respose"""
        }
        
        # Prepare messages for API call
        messages = [system_message] + self.conversation_history
        
        # Make API call with function calling
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Handle function calls
            if message.tool_calls:
                # Add assistant message with tool calls to history
                self.conversation_history.append(message)
                
                # Execute function calls and add results
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    parameters = json.loads(tool_call.function.arguments)
                    result = self.execute_function(function_name, parameters)
                    
                    # Add function result to conversation
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                
                # Get final response after function execution
                final_response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[system_message] + self.conversation_history,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                final_message = final_response.choices[0].message
                self.conversation_history.append(final_message)
                return final_message.content
            
            else:
                # No function calls, just add response to history
                self.conversation_history.append(message)
                return message.content
                
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"

    def chat(self):
        """Main chat loop"""
        print("=" * 60)
        print("  SK (Shame Kitten) HPC Services - AI Assistant")
        print("=" * 60)
        print("Hello! I'm the AI assistant for SK HPC Services.")
        print("I can help you with GPU bookings, queries, and recommendations.")
        print("Type 'quit' to exit the chat.\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nBot: Thank you for using SK HPC Services! Have a great day!")
                break
            
            if not user_input:
                continue
            
            print("Bot: ", end="")
            response = self.send_message_to_ai(user_input)
            print(response)
            print()


if __name__ == "__main__":
    chatbot = HPC_ChatBot()
    chatbot.chat()
