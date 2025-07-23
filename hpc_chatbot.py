import json
import hashlib
import datetime
import webbrowser
import tempfile
import os
import markdown
import re
from typing import List, Dict, Optional, Any
from openai import OpenAI
import nailfec


class HPC_ChatBot:
    """
    SK (Shame Kitten) HPC Services ChatBot
    Provides AI-powered assistance for GPU booking, querying, and management
    """
    
    def __init__(self, session_id=None):
        """Initialize the chatbot with API client and load data"""
        self.client = OpenAI(
            api_key=nailfec.api_key,
            base_url="https://api.deepseek.com",
            timeout=30.0  # 添加30秒超时
        )
        
        # Load GPU inventory and bookings data
        with open('gpu_inventory.json', 'r') as f:
            self.gpu_data = json.load(f)
        
        with open('bookings.json', 'r') as f:
            self.bookings = json.load(f)
        
        # Session-specific conversation history
        self.session_id = session_id or hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()
        self.conversation_history = []
        
        # Current booking session data
        self.current_booking = {}
        
        # Pending operations awaiting confirmation
        self.pending_operation = None
        self.pending_data = {}
        
        # Define available functions for the AI
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_available_gpus",
                    "description": "REQUIRED: Search for available GPU instances. Must be called whenever users ask about GPU availability, quantities, or 'how many' GPUs are available. Also required when checking availability for specific dates/times for booking.",
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
                                "description": "Specific GPU instance ID (optional - will auto-select if not provided)"
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
                        "required": ["gpu_model", "user_name", "user_email", "start_time", "end_time"]
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
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_datetime",
                    "description": "Get the current date and time. Use this when users mention 'today', 'now', 'right now', 'current time', or need to book something immediately.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "prepare_booking_confirmation",
                    "description": "Prepare booking details for user confirmation before creating the actual booking. Call this when all booking information is collected.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "gpu_model": {"type": "string", "description": "GPU model to book"},
                            "gpu_id": {"type": "string", "description": "Specific GPU instance ID (optional)"},
                            "user_name": {"type": "string", "description": "User's full name"},
                            "user_email": {"type": "string", "description": "User's email address"},
                            "start_time": {"type": "string", "description": "Start time in ISO format"},
                            "end_time": {"type": "string", "description": "End time in ISO format"},
                            "storage_gb": {"type": "number", "description": "Required storage in GB (default: 128)"},
                            "memory_gb": {"type": "number", "description": "Required system memory in GB (default: 32)"},
                            "cpu_cores": {"type": "number", "description": "Required CPU cores (default: 8)"}
                        },
                        "required": ["gpu_model", "user_name", "user_email", "start_time", "end_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "prepare_cancellation_confirmation",
                    "description": "Prepare cancellation details for user confirmation before cancelling the booking. Call this when booking hash and email are collected.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "booking_hash": {"type": "string", "description": "Booking hash identifier"},
                            "user_email": {"type": "string", "description": "User's email for verification"}
                        },
                        "required": ["booking_hash", "user_email"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "confirm_operation",
                    "description": "Confirm and execute the pending operation (booking or cancellation) after user confirmation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "confirmed": {"type": "boolean", "description": "Whether the user confirmed the operation"}
                        },
                        "required": ["confirmed"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "clear_conversation_history",
                    "description": "Clear the conversation history to start fresh after completing an operation.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
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

    def get_available_gpu_id(self, gpu_model: str, start_time: str, end_time: str) -> str:
        """Get the first available GPU ID for a given model and time period"""
        if gpu_model not in self.gpu_data["gpu_models"]:
            return None
        
        gpu_info = self.gpu_data["gpu_models"][gpu_model]
        
        for instance in gpu_info["instances"]:
            is_available = True
            
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
                return instance["id"]
        
        return None

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

    def create_booking(self, gpu_model: str, gpu_id: str = None, user_name: str = None, user_email: str = None,
                      start_time: str = None, end_time: str = None, storage_gb: int = 128, 
                      memory_gb: int = 32, cpu_cores: int = 8) -> Dict:
        """Create a new booking - requires all essential information"""
        
        # Validate all required parameters
        if not gpu_model or not user_name or not user_email or not start_time or not end_time:
            return {"success": False, "message": "All booking information is required: GPU model, user name, email, start time, and end time"}
        
        # Validate email format
        if "@" not in user_email or "." not in user_email:
            return {"success": False, "message": "Invalid email format"}
        
        # Validate user name (should not be empty or just spaces)
        if not user_name.strip():
            return {"success": False, "message": "User name cannot be empty"}
        
        # Validate GPU model exists
        if gpu_model not in self.gpu_data["gpu_models"]:
            return {"success": False, "message": f"GPU model '{gpu_model}' not found in inventory"}
        
        # Auto-select GPU ID if not provided
        if not gpu_id:
            gpu_id = self.get_available_gpu_id(gpu_model, start_time, end_time)
            if not gpu_id:
                return {"success": False, "message": f"No available {gpu_model} GPUs found for the requested time period"}
        else:
            # Validate provided GPU ID exists for this model
            gpu_info = self.gpu_data["gpu_models"][gpu_model]
            valid_gpu_ids = [instance["id"] for instance in gpu_info["instances"]]
            if gpu_id not in valid_gpu_ids:
                return {"success": False, "message": f"GPU ID '{gpu_id}' not found for model '{gpu_model}'"}
        
        # Validate time format and logic
        try:
            start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if start_dt >= end_dt:
                return {"success": False, "message": "End time must be after start time"}
            
            if start_dt < datetime.datetime.now(datetime.timezone.utc):
                return {"success": False, "message": "Start time cannot be in the past"}
                
        except ValueError:
            return {"success": False, "message": "Invalid time format. Please use ISO format (e.g., '2025-07-23T10:00:00Z')"}
        
        # Check if GPU is available during the requested time
        for booking in self.bookings:
            if (booking["gpu_id"] == gpu_id and 
                booking["status"] in ["active", "scheduled"]):
                booking_start = datetime.datetime.fromisoformat(booking["start_time"].replace('Z', '+00:00'))
                booking_end = datetime.datetime.fromisoformat(booking["end_time"].replace('Z', '+00:00'))
                
                if (start_dt < booking_end and end_dt > booking_start):
                    return {"success": False, "message": f"GPU {gpu_id} is not available during the requested time period"}
        
        # Generate booking ID and hash
        booking_id = f"book_{len(self.bookings) + 1:03d}"
        booking_hash = hashlib.md5(f"{booking_id}{user_email}{start_time}".encode()).hexdigest()
        
        # Calculate cost
        gpu_info = self.gpu_data["gpu_models"][gpu_model]
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
        duration_slots = duration_hours * 2  # 30-minute slots
        total_cost = duration_slots * gpu_info["price_per_30min"]
        
        # Create booking
        new_booking = {
            "booking_id": booking_id,
            "booking_hash": booking_hash,
            "user_name": user_name.strip(),
            "user_email": user_email.lower().strip(),
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
        
        # Display booking card
        self.display_booking_card(new_booking, is_cancelled=False)
        
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

    def generate_booking_card_data(self, booking: Dict, is_cancelled: bool = False) -> Dict:
        """Generate structured booking card data using AI"""
        
        status_text = "CANCELLED" if is_cancelled else "CONFIRMED"
        
        system_prompt = f"""
        You are a booking card data generator. Generate a structured JSON object for displaying a booking information card.
        The card should be well-designed and contain all relevant booking information.
        
        REQUIRED JSON FORMAT:
        {{
            "card_type": "booking_confirmation" or "booking_cancellation",
            "status": "{status_text}",
            "booking_hash": "booking hash",
            "user_info": {{
                "name": "user name",
                "email": "user email"
            }},
            "gpu_info": {{
                "model": "GPU model",
                "id": "GPU instance ID",
                "memory": "GPU memory",
                "cores": "CPU cores allocated"
            }},
            "time_info": {{
                "start_time": "formatted start time",
                "end_time": "formatted end time",
                "duration": "duration in hours"
            }},
            "resources": {{
                "storage": "storage in GB",
                "memory": "system memory in GB",
                "cpu_cores": "CPU cores"
            }},
            "billing": {{
                "total_cost": "total cost in USD",
                "overtime_cost": "overtime cost in USD"
            }},
            "card_style": {{
                "background_color": "#4CAF50" for confirmed or "#f44336" for cancelled,
                "border_color": "#45a049" for confirmed or "#d32f2f" for cancelled,
                "status_color": "#ffffff"
            }}
        }}
        """
        
        user_prompt = f"Generate booking card data for: {json.dumps(booking)}"
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={'type': 'json_object'}
            )
            
            card_data = json.loads(response.choices[0].message.content)
            return card_data
            
        except Exception as e:
            # Fallback to manual card data generation
            return self._manual_card_data(booking, is_cancelled)

    def _manual_card_data(self, booking: Dict, is_cancelled: bool = False) -> Dict:
        """Fallback manual card data generation"""
        start_time = datetime.datetime.fromisoformat(booking["start_time"].replace('Z', '+00:00'))
        end_time = datetime.datetime.fromisoformat(booking["end_time"].replace('Z', '+00:00'))
        duration = (end_time - start_time).total_seconds() / 3600
        
        return {
            "card_type": "booking_cancellation" if is_cancelled else "booking_confirmation",
            "status": "CANCELLED" if is_cancelled else "CONFIRMED",
            "booking_hash": booking["booking_hash"],
            "user_info": {
                "name": booking["user_name"],
                "email": booking["user_email"]
            },
            "gpu_info": {
                "model": booking["gpu_model"],
                "id": booking["gpu_id"],
                "memory": self.gpu_data["gpu_models"].get(booking["gpu_model"], {}).get("memory", "N/A"),
                "cores": str(booking.get("cpu_cores", 8))
            },
            "time_info": {
                "start_time": start_time.strftime("%Y-%m-%d %H:%M"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M"),
                "duration": f"{duration:.1f} hours"
            },
            "resources": {
                "storage": f"{booking.get('storage_gb', 128)} GB",
                "memory": f"{booking.get('memory_gb', 32)} GB",
                "cpu_cores": str(booking.get('cpu_cores', 8))
            },
            "billing": {
                "total_cost": f"${booking['total_cost']:.2f}",
                "overtime_cost": f"${booking.get('overtime_cost', 0):.2f}"
            },
            "card_style": {
                "background_color": "#f44336" if is_cancelled else "#4CAF50",
                "border_color": "#d32f2f" if is_cancelled else "#45a049",
                "status_color": "#ffffff"
            }
        }

    def generate_booking_card_html(self, card_data: Dict) -> str:
        """Generate HTML for booking card"""
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SK HPC Services - Booking {card_data['status']}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .booking-card {{
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    max-width: 500px;
                    width: 100%;
                    overflow: hidden;
                    animation: slideIn 0.6s ease-out;
                }}
                
                @keyframes slideIn {{
                    from {{
                        opacity: 0;
                        transform: translateY(30px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                
                .card-header {{
                    background: {card_data['card_style']['background_color']};
                    color: {card_data['card_style']['status_color']};
                    padding: 24px;
                    text-align: center;
                    position: relative;
                }}
                
                .status-badge {{
                    font-size: 18px;
                    font-weight: bold;
                    letter-spacing: 2px;
                    margin-bottom: 8px;
                }}
                
                .company-logo {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-top: 8px;
                }}
                
                .card-body {{
                    padding: 24px;
                }}
                
                .section {{
                    margin-bottom: 20px;
                    padding-bottom: 16px;
                    border-bottom: 1px solid #f0f0f0;
                }}
                
                .section:last-child {{
                    border-bottom: none;
                    margin-bottom: 0;
                }}
                
                .section-title {{
                    font-size: 14px;
                    font-weight: 600;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 12px;
                }}
                
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                }}
                
                .info-label {{
                    color: #888;
                    font-size: 14px;
                }}
                
                .info-value {{
                    font-weight: 600;
                    color: #333;
                    font-size: 14px;
                }}
                
                .booking-hash {{
                    background: #f8f9fa;
                    padding: 12px;
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    color: #495057;
                    word-break: break-all;
                    text-align: center;
                }}
                
                .gpu-badge {{
                    display: inline-block;
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    padding: 6px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-top: 4px;
                }}
                
                .cost-highlight {{
                    font-size: 18px;
                    font-weight: bold;
                    color: {card_data['card_style']['background_color']};
                }}
                
                .footer {{
                    background: #f8f9fa;
                    padding: 16px 24px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="booking-card">
                <div class="card-header">
                    <div class="status-badge">{card_data['status']}</div>
                    <div>Booking Hash: {card_data['booking_hash'][:8]}...</div>
                    <div class="company-logo">SK (Shame Kitten) HPC Services</div>
                </div>
                
                <div class="card-body">
                    <div class="section">
                        <div class="section-title">User Information</div>
                        <div class="info-row">
                            <span class="info-label">Name:</span>
                            <span class="info-value">{card_data['user_info']['name']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Email:</span>
                            <span class="info-value">{card_data['user_info']['email']}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">GPU & Resources</div>
                        <div class="info-row">
                            <span class="info-label">GPU Model:</span>
                            <span class="info-value">
                                {card_data['gpu_info']['model']}
                                <span class="gpu-badge">{card_data['gpu_info']['memory']}</span>
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">GPU ID:</span>
                            <span class="info-value">{card_data['gpu_info']['id']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Storage:</span>
                            <span class="info-value">{card_data['resources']['storage']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">System Memory:</span>
                            <span class="info-value">{card_data['resources']['memory']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">CPU Cores:</span>
                            <span class="info-value">{card_data['resources']['cpu_cores']}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">Schedule</div>
                        <div class="info-row">
                            <span class="info-label">Start Time:</span>
                            <span class="info-value">{card_data['time_info']['start_time']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">End Time:</span>
                            <span class="info-value">{card_data['time_info']['end_time']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Duration:</span>
                            <span class="info-value">{card_data['time_info']['duration']}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">Billing</div>
                        <div class="info-row">
                            <span class="info-label">Base Cost:</span>
                            <span class="info-value cost-highlight">{card_data['billing']['total_cost']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Overtime Cost:</span>
                            <span class="info-value">{card_data['billing']['overtime_cost']}</span>
                        </div>
                    </div>
                    
                    <div class="booking-hash">
                        Full Booking Hash: {card_data['booking_hash']}
                    </div>
                </div>
                
                <div class="footer">
                    For support, contact: nailfec17@gmail.com<br>
                    Thank you for choosing SK HPC Services!
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template

    def display_booking_card(self, booking: Dict, is_cancelled: bool = False):
        """Generate and display booking card in browser"""
        try:
            # Generate card data using AI
            card_data = self.generate_booking_card_data(booking, is_cancelled)
            
            # Generate HTML
            html_content = self.generate_booking_card_html(card_data)
            
            # Save to temporary file and open in browser
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
            
            # Open in default browser
            webbrowser.open(f'file://{temp_file}')
            
            # Clean up after a delay (optional)
            # Note: In a real application, you might want to manage this differently
            
            return True
            
        except Exception as e:
            print(f"Error displaying booking card: {str(e)}")
            return False

    def cancel_booking(self, booking_hash: str, user_email: str) -> Dict:
        """Cancel a booking - requires both correct booking hash and user email"""
        # Validate required parameters
        if not booking_hash or not user_email:
            return {"success": False, "message": "Both booking hash and user email are required to cancel a booking"}
        
        # Validate email format
        if "@" not in user_email or "." not in user_email:
            return {"success": False, "message": "Invalid email format"}
        
        for i, booking in enumerate(self.bookings):
            if (booking["booking_hash"] == booking_hash and 
                booking["user_email"].lower().strip() == user_email.lower().strip()):
                if booking["status"] in ["scheduled", "active"]:
                    self.bookings[i]["status"] = "cancelled"
                    
                    # Save to file
                    with open('bookings.json', 'w') as f:
                        json.dump(self.bookings, f, indent=2)
                    
                    # Display cancellation card
                    self.display_booking_card(self.bookings[i], is_cancelled=True)
                    
                    return {"success": True, "message": "Booking cancelled successfully"}
                else:
                    return {"success": False, "message": "Booking cannot be cancelled (already completed or cancelled)"}
        
        return {"success": False, "message": "Booking not found or email/hash combination is incorrect"}

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

    def get_current_datetime(self) -> Dict:
        """Get the current date and time information"""
        now = datetime.datetime.now()
        
        return {
            "current_datetime": now.isoformat(),
            "current_date": now.strftime("%Y-%m-%d"),
            "current_time": now.strftime("%H:%M:%S"),
            "formatted_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timezone": "Local time",
            "iso_format": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second
        }

    def prepare_booking_confirmation(self, gpu_model: str, gpu_id: str = None, user_name: str = None, 
                                   user_email: str = None, start_time: str = None, end_time: str = None, 
                                   storage_gb: int = 128, memory_gb: int = 32, cpu_cores: int = 8) -> Dict:
        """Prepare booking details for user confirmation"""
        
        # Validate all required parameters
        if not gpu_model or not user_name or not user_email or not start_time or not end_time:
            return {"success": False, "message": "All booking information is required: GPU model, user name, email, start time, and end time"}
        
        # Validate email format
        if "@" not in user_email or "." not in user_email:
            return {"success": False, "message": "Invalid email format"}
        
        # Validate user name
        if not user_name.strip():
            return {"success": False, "message": "User name cannot be empty"}
        
        # Validate GPU model exists
        if gpu_model not in self.gpu_data["gpu_models"]:
            return {"success": False, "message": f"GPU model '{gpu_model}' not found in inventory"}
        
        # Auto-select GPU ID if not provided
        if not gpu_id:
            gpu_id = self.get_available_gpu_id(gpu_model, start_time, end_time)
            if not gpu_id:
                return {"success": False, "message": f"No available {gpu_model} GPUs found for the requested time period"}
        
        # Validate time format and logic
        try:
            start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if start_dt >= end_dt:
                return {"success": False, "message": "End time must be after start time"}
            
            if start_dt < datetime.datetime.now(datetime.timezone.utc):
                return {"success": False, "message": "Start time cannot be in the past"}
                
        except ValueError:
            return {"success": False, "message": "Invalid time format. Please use ISO format (e.g., '2025-07-23T10:00:00Z')"}
        
        # Calculate cost
        gpu_info = self.gpu_data["gpu_models"][gpu_model]
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
        duration_slots = duration_hours * 2  # 30-minute slots
        total_cost = duration_slots * gpu_info["price_per_30min"]
        
        # Store pending operation data
        self.pending_operation = "booking"
        self.pending_data = {
            "gpu_model": gpu_model,
            "gpu_id": gpu_id,
            "user_name": user_name.strip(),
            "user_email": user_email.lower().strip(),
            "start_time": start_time,
            "end_time": end_time,
            "storage_gb": storage_gb,
            "memory_gb": memory_gb,
            "cpu_cores": cpu_cores,
            "total_cost": round(total_cost, 2),
            "duration_hours": duration_hours
        }
        
        # Generate confirmation markdown
        confirmation_markdown = f"""
## 📋 **Booking Confirmation Required**

Please review the following booking details carefully:

### 👤 **User Information**
- **Name:** {user_name}
- **Email:** {user_email}

### 🖥️ **GPU & Resources**
- **GPU Model:** **{gpu_model}** 
- **GPU ID:** `{gpu_id}`
- **GPU Memory:** {gpu_info['memory']}
- **System Memory:** {memory_gb} GB
- **Storage:** {storage_gb} GB  
- **CPU Cores:** {cpu_cores}

### ⏰ **Schedule**
- **Start Time:** {start_dt.strftime('%Y-%m-%d %H:%M:%S')}
- **End Time:** {end_dt.strftime('%Y-%m-%d %H:%M:%S')}
- **Duration:** {duration_hours:.1f} hours

### 💰 **Billing**
- **Rate:** ${gpu_info['price_per_30min']:.2f} per 30 minutes
- **Total Cost:** **${total_cost:.2f}**

---

**Please type 'yes' or 'confirm' to proceed with this booking, or 'no' to cancel.**
"""
        
        return {
            "success": True,
            "confirmation_needed": True,
            "markdown_summary": confirmation_markdown
        }

    def prepare_cancellation_confirmation(self, booking_hash: str, user_email: str) -> Dict:
        """Prepare cancellation details for user confirmation"""
        
        # Validate required parameters
        if not booking_hash or not user_email:
            return {"success": False, "message": "Both booking hash and user email are required"}
        
        # Validate email format
        if "@" not in user_email or "." not in user_email:
            return {"success": False, "message": "Invalid email format"}
        
        # Find the booking
        booking_found = None
        for booking in self.bookings:
            if (booking["booking_hash"] == booking_hash and 
                booking["user_email"].lower().strip() == user_email.lower().strip()):
                booking_found = booking
                break
        
        if not booking_found:
            return {"success": False, "message": "Booking not found or email/hash combination is incorrect"}
        
        if booking_found["status"] not in ["scheduled", "active"]:
            return {"success": False, "message": "Booking cannot be cancelled (already completed or cancelled)"}
        
        # Store pending operation data
        self.pending_operation = "cancellation"
        self.pending_data = {
            "booking_hash": booking_hash,
            "user_email": user_email.lower().strip(),
            "booking": booking_found
        }
        
        # Generate confirmation markdown
        start_time = datetime.datetime.fromisoformat(booking_found["start_time"].replace('Z', '+00:00'))
        end_time = datetime.datetime.fromisoformat(booking_found["end_time"].replace('Z', '+00:00'))
        
        confirmation_markdown = f"""
## ❌ **Cancellation Confirmation Required**

Please review the booking you want to cancel:

### 📄 **Booking Details**
- **Booking ID:** {booking_found['booking_id']}
- **Booking Hash:** `{booking_hash}`

### 👤 **User Information**
- **Name:** {booking_found['user_name']}
- **Email:** {booking_found['user_email']}

### 🖥️ **GPU Information**
- **GPU Model:** **{booking_found['gpu_model']}**
- **GPU ID:** `{booking_found['gpu_id']}`

### ⏰ **Schedule**
- **Start Time:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **End Time:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Status:** {booking_found['status'].upper()}

### 💰 **Billing**
- **Total Cost:** ${booking_found['total_cost']:.2f}

---

**⚠️ Warning: This action cannot be undone.**

**Please type 'yes' or 'confirm' to proceed with cancellation, or 'no' to keep the booking.**
"""
        
        return {
            "success": True,
            "confirmation_needed": True,
            "markdown_summary": confirmation_markdown
        }

    def confirm_operation(self, confirmed: bool) -> Dict:
        """Confirm and execute the pending operation"""
        
        if not self.pending_operation:
            return {"success": False, "message": "No pending operation to confirm"}
        
        if not confirmed:
            # User declined, clear pending operation
            operation_type = self.pending_operation
            self.pending_operation = None
            self.pending_data = {}
            return {
                "success": True, 
                "message": f"{operation_type.capitalize()} cancelled by user request.",
                "cancelled": True
            }
        
        # User confirmed, execute the operation
        if self.pending_operation == "booking":
            result = self._execute_confirmed_booking()
        elif self.pending_operation == "cancellation":
            result = self._execute_confirmed_cancellation()
        else:
            return {"success": False, "message": f"Unknown operation type: {self.pending_operation}"}
        
        # Clear pending operation
        self.pending_operation = None
        self.pending_data = {}
        
        return result

    def _execute_confirmed_booking(self) -> Dict:
        """Execute the confirmed booking operation"""
        data = self.pending_data
        
        # Generate booking ID and hash
        booking_id = f"book_{len(self.bookings) + 1:03d}"
        booking_hash = hashlib.md5(f"{booking_id}{data['user_email']}{data['start_time']}".encode()).hexdigest()
        
        # Create booking
        new_booking = {
            "booking_id": booking_id,
            "booking_hash": booking_hash,
            "user_name": data["user_name"],
            "user_email": data["user_email"],
            "gpu_model": data["gpu_model"],
            "gpu_id": data["gpu_id"],
            "start_time": data["start_time"],
            "end_time": data["end_time"],
            "status": "scheduled",
            "storage_gb": data["storage_gb"],
            "memory_gb": data["memory_gb"],
            "cpu_cores": data["cpu_cores"],
            "created_at": datetime.datetime.now().isoformat() + "Z",
            "total_cost": data["total_cost"],
            "overtime_minutes": 0,
            "overtime_cost": 0.00
        }
        
        self.bookings.append(new_booking)
        
        # Save to file
        with open('bookings.json', 'w') as f:
            json.dump(self.bookings, f, indent=2)
        
        # Display booking card
        self.display_booking_card(new_booking, is_cancelled=False)
        
        return {
            "success": True,
            "booking": new_booking,
            "message": "Booking created successfully! A booking card has been generated and opened in your browser.",
            "clear_history": True
        }

    def _execute_confirmed_cancellation(self) -> Dict:
        """Execute the confirmed cancellation operation"""
        data = self.pending_data
        booking_hash = data["booking_hash"]
        user_email = data["user_email"]
        
        # Find and cancel the booking
        for i, booking in enumerate(self.bookings):
            if (booking["booking_hash"] == booking_hash and 
                booking["user_email"] == user_email):
                self.bookings[i]["status"] = "cancelled"
                
                # Save to file
                with open('bookings.json', 'w') as f:
                    json.dump(self.bookings, f, indent=2)
                
                # Display cancellation card
                self.display_booking_card(self.bookings[i], is_cancelled=True)
                
                return {
                    "success": True,
                    "message": "Booking cancelled successfully! A cancellation card has been generated and opened in your browser.",
                    "clear_history": True
                }
        
        return {"success": False, "message": "Booking not found during cancellation"}

    def clear_conversation_history(self) -> Dict:
        """Clear the conversation history to start fresh"""
        self.conversation_history = []
        self.pending_operation = None
        self.pending_data = {}
        self.current_booking = {}
        
        return {
            "success": True,
            "message": "Conversation history cleared. Starting fresh!"
        }

    def markdown_to_html(self, text: str) -> str:
        """Convert markdown text to HTML with custom styling"""
        # Configure markdown with extensions
        md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc'
        ])
        
        # Convert markdown to HTML
        html = md.convert(text)
        
        # Add custom CSS classes for better styling
        html = self._add_custom_css_classes(html)
        
        return html
    
    def _add_custom_css_classes(self, html: str) -> str:
        """Add custom CSS classes to HTML elements for better styling"""
        # Add classes to common elements
        replacements = [
            (r'<table>', r'<table class="markdown-table">'),
            (r'<blockquote>', r'<blockquote class="markdown-blockquote">'),
            (r'<code>', r'<code class="markdown-inline-code">'),
            (r'<pre>', r'<pre class="markdown-code-block">'),
            (r'<h1>', r'<h1 class="markdown-h1">'),
            (r'<h2>', r'<h2 class="markdown-h2">'),
            (r'<h3>', r'<h3 class="markdown-h3">'),
            (r'<h4>', r'<h4 class="markdown-h4">'),
            (r'<ul>', r'<ul class="markdown-ul">'),
            (r'<ol>', r'<ol class="markdown-ol">'),
            (r'<li>', r'<li class="markdown-li">'),
        ]
        
        for pattern, replacement in replacements:
            html = re.sub(pattern, replacement, html)
        
        return html

    def execute_function(self, function_name: str, parameters: Dict) -> Any:
        """Execute a function call and return the result"""
        function_map = {
            "search_available_gpus": self.search_available_gpus,
            "get_gpu_recommendations": self.get_gpu_recommendations,
            "create_booking": self.create_booking,
            "query_booking_info": self.query_booking_info,
            "cancel_booking": self.cancel_booking,
            "calculate_billing": self.calculate_billing,
            "get_current_datetime": self.get_current_datetime,
            "prepare_booking_confirmation": self.prepare_booking_confirmation,
            "prepare_cancellation_confirmation": self.prepare_cancellation_confirmation,
            "confirm_operation": self.confirm_operation,
            "clear_conversation_history": self.clear_conversation_history
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
- Our company name comes from a cute student called Shane, and he is as cute as a kitten and always shame
- We have various GPU models available: RTX-4090, RTX-4080, RTX-4070, RTX-3090, RTX-3080, H100, A100, V100
- Our services are cost-effective with excellent connectivity
- We support various use cases from gaming to AI training to scientific computing
- If the user want to turn to human response, show the E-mail nailfec17@gmail.com for user to connect with

MARKDOWN FORMATTING:
- You can use Markdown formatting in your responses for better readability
- Use **bold** for important information like prices, GPU models, and booking details
- Use `code blocks` for GPU IDs, booking hashes, and technical terms
- Use tables for comparing GPU specifications or pricing
- Use > blockquotes for important warnings or notes
- Use bullet points and numbered lists for step-by-step instructions
- Use headings (##, ###) to organize longer responses
- Example: **RTX-4090** with `24GB VRAM` costs **$15.00 per 30 minutes**

Guidelines:
- Always be helpful, professional, and simple
- Ask questions one at a time, not all at once
- Use function calls to access real data when needed
- Never provide fixed responses - always process through AI
- Guide users through the booking process step by step
- Do not say anything that is not related to your assistant role about GPU and our company
- You do not need to check if the date is in the future or not, and the year is 2025 if the user does not specify
- The user can only book one GPU at a time
- When asking user for time information, do not suggest user using the specific time format rule
- IMPORTANT: Just reply 1~3 sentences is enough - do not give too much responses
- IMPORTANT: Do not ask too much questions at a time - just ask a simple question to ask at a time if you need to ask for respose

BOOKING SECURITY REQUIREMENTS:
- NEVER create a booking without collecting ALL required information: user name, email, GPU model, specific GPU ID, start time, and end time
- GPU ID can be automatically selected from available instances after checking availability
- Always validate that the user has provided a valid email address
- Always check GPU availability before attempting to book
- If any required information is missing, ask for it before proceeding

CANCELLATION SECURITY REQUIREMENTS:
- NEVER cancel a booking without BOTH the correct booking hash AND the user's email address
- Both booking hash and email must match exactly with the original booking
- If either piece of information is missing or incorrect, deny the cancellation request
- Always verify the booking exists and belongs to the requesting user

CONFIRMATION WORKFLOW (CRITICAL):
- NEVER call create_booking or cancel_booking directly
- Instead, when all information is collected:
  * For bookings: Call prepare_booking_confirmation to show a Markdown summary for user confirmation
  * For cancellations: Call prepare_cancellation_confirmation to show a Markdown summary for user confirmation
- After showing the confirmation, ask the user to confirm with 'yes'/'confirm' or decline with 'no'
- When user responds with confirmation intent, call confirm_operation with confirmed=true
- When user declines, call confirm_operation with confirmed=false
- After successful operations (booking/cancellation), the conversation history will be cleared automatically
- If user wants to modify details after seeing confirmation, collect new details and show confirmation again

USER CONFIRMATION PATTERNS:
- Confirmation: "yes", "confirm", "proceed", "do it", "go ahead", "that's correct", "looks good", "confirm"
- Decline: "no", "cancel", "stop", "wait", "not correct", "change", "modify", "wait", "i want ... to be ..."

CRITICAL FUNCTION CALLING RULES:
- ALWAYS call search_available_gpus when users ask about availability, quantities, or "how many" GPUs are available
- ALWAYS include the specific GPU model (e.g., "RTX-3080") when searching
- When users mention specific dates/times for booking, ALWAYS include start_time and end_time in the search to check real availability
- Never give availability information without calling the search function first
- Examples requiring search_available_gpus:
  * "how many 3080 available"
  * "are RTX-4090s available"
  * "check availability for July 22-25"
  * "what GPUs are free this week" """
        }
        
        # Prepare messages for API call
        messages = [system_message] + self.conversation_history
        
        # Make API call with function calling
        try:
            print("Making API call to DeepSeek...")  # 调试日志
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                timeout=30  # 30秒超时
            )
            print("API call successful!")  # 调试日志
            
            message = response.choices[0].message
            
            # Handle function calls
            if message.tool_calls:
                # Add assistant message with tool calls to history
                assistant_message = {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        } for tool_call in message.tool_calls
                    ]
                }
                self.conversation_history.append(assistant_message)
                
                # Execute function calls and add results
                should_clear_history = False
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    parameters = json.loads(tool_call.function.arguments)
                    result = self.execute_function(function_name, parameters)
                    
                    # Check if we should clear history after this operation
                    if isinstance(result, dict) and result.get("clear_history"):
                        should_clear_history = True
                    
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
                
                # Add final response to history
                final_assistant_message = {
                    "role": "assistant",
                    "content": final_message.content
                }
                self.conversation_history.append(final_assistant_message)
                
                # Clear history if requested (after successful booking/cancellation)
                if should_clear_history:
                    self.clear_conversation_history()
                
                return final_message.content
            
            else:
                # No function calls, just add response to history
                assistant_message = {
                    "role": "assistant",
                    "content": message.content
                }
                self.conversation_history.append(assistant_message)
                return message.content
                
        except Exception as e:
            print(f"AI API Error: {str(e)}")  # 添加调试日志
            import traceback
            traceback.print_exc()  # 打印完整错误堆栈
            
            # 提供备用响应
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                return "⚠️ AI服务暂时响应较慢，请稍后重试。您也可以发送邮件到 nailfec17@gmail.com 寻求人工帮助。"
            elif "api" in str(e).lower() or "key" in str(e).lower():
                return "⚠️ AI服务配置问题，请联系管理员。邮箱：nailfec17@gmail.com"
            else:
                return f"⚠️ 抱歉，我遇到了技术问题：{str(e)}。请稍后重试或联系支持团队：nailfec17@gmail.com"

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
