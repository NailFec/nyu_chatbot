# SK (Shame Kitten) HPC Services Chatbot

A comprehensive AI-powered chatbot system for HPC (High-Performance Computing) GPU rental services. This system provides intelligent assistance for GPU booking, querying, billing, and recommendations through both command-line and web interfaces.

## Features

### AI Chatbot Capabilities
- **GPU Booking**: Intelligent booking assistance with step-by-step guidance
- **Recommendations**: AI-powered GPU recommendations based on use cases (LLaMA training, gaming, rendering, etc.)
- **Query Management**: Check booking status, billing history, and account information
- **Booking Management**: Cancel or modify existing reservations
- **Server Status**: Real-time server and datacenter status information

### Database & Inventory
- **Extensive GPU Catalog**: RTX-4090, RTX-4080, RTX-4070, RTX-3090, RTX-3080, H100, A100, V100
- **Detailed Specifications**: Memory, CUDA cores, pricing, performance metrics
- **Real-time Availability**: Dynamic availability checking with conflict detection
- **Booking History**: Comprehensive booking records with billing information

### Web Dashboard
- **Timeline Visualization**: Interactive GPU booking timeline by model and instance
- **Real-time Stats**: Utilization rates, active bookings, revenue tracking
- **Filtering**: Date range, status, and model-based filtering
- **Responsive Design**: Modern, mobile-friendly interface

### API Integration
- **Function Calling**: Advanced AI function calling for database operations
- **RESTful API**: Complete REST API for all chatbot functions
- **Web Interface**: User-friendly chat interface with quick actions

## System Architecture

```
├── hpc_chatbot.py          # Main chatbot class with AI integration
├── gpu_inventory.json      # GPU models and instance database
├── bookings.json          # Booking records and history
├── web_server.py          # Flask web server with API endpoints
├── chat_interface.html    # Web-based chat interface
├── timeline_dashboard.html # GPU booking timeline dashboard
└── examples/              # API usage examples
    ├── function_calling.py
    ├── simple_dialog.py
    └── structured_output.py
```

## Setup

### Prerequisites
You should include a `nailfec.py` file under the home folder, which contains your API keys:

```python
api_key = "sk-your-api-key-here"
api_key_2 = "sk-your-backup-api-key-here"
```

The API keys are provided by Kenny from NYU Shanghai for educational purposes.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Chatbot (Command Line)
```bash
python hpc_chatbot.py
```

### 3. Run the Web Server
```bash
python web_server.py
```

Then open:
- Chat Interface: http://localhost:5000/chat_interface.html
- Timeline Dashboard: http://localhost:5000/timeline_dashboard.html
- API Documentation: http://localhost:5000/api/

## Usage Examples

### Command Line Chat
```
You: Hello, what services do you offer?
Bot: Hello! I'm the AI assistant for SK (Shame Kitten) HPC Services. We provide affordable, reliable, and high-performance GPU rental services...

You: I want to book a GPU for LLaMA 8B training
Bot: For LLaMA 8B model training, I recommend the RTX-4090 with 24GB VRAM at $2.50 per 30 minutes...

You: What's the price?
Bot: The RTX-4090 costs $2.50 per 30-minute period. For a full day (48 periods), that would be $120...
```

### API Usage
```python
# Search available GPUs
response = requests.get('/api/search_gpus', params={
    'model': 'RTX-4090',
    'start_time': '2025-07-23T10:00:00Z',
    'end_time': '2025-07-23T18:00:00Z'
})

# Get recommendations
response = requests.get('/api/recommendations', params={
    'use_case': 'LLaMA 8B training',
    'budget_per_hour': 10.0
})

# Create booking
response = requests.post('/api/create_booking', json={
    'gpu_model': 'RTX-4090',
    'gpu_id': 'RTX4090-001',
    'user_name': 'John Doe',
    'user_email': 'john@example.com',
    'start_time': '2025-07-23T10:00:00Z',
    'end_time': '2025-07-23T18:00:00Z'
})
```

## GPU Models Available

| Model | Memory | Price/30min | Best For |
|-------|--------|-------------|----------|
| H100 | 80GB HBM3 | $8.00 | Large AI models, enterprise |
| A100 | 40GB HBM2e | $5.00 | Professional AI training |
| RTX-4090 | 24GB GDDR6X | $2.50 | Gaming, content creation, medium AI |
| RTX-4080 | 16GB GDDR6X | $2.00 | High-performance mainstream |
| RTX-4070 | 12GB GDDR6X | $1.50 | Value gaming, light AI |
| RTX-3090 | 24GB GDDR6X | $1.80 | Previous gen, large memory |
| RTX-3080 | 10GB GDDR6X | $1.30 | Popular gaming choice |
| V100 | 32GB HBM2 | $3.00 | Scientific computing |

## AI Integration

The chatbot uses advanced AI with function calling capabilities:

1. **Natural Language Processing**: Understands complex booking requests
2. **Context Awareness**: Maintains conversation context for multi-step bookings
3. **Function Calling**: Automatically executes database operations
4. **Recommendations**: AI-powered GPU selection based on use cases
5. **Dynamic Responses**: All responses generated by AI, no fixed templates

## Company Information

**SK (Shame Kitten) HPC Services** provides:
- Affordable GPU rental rates
- Reliable, stable connections
- Multiple datacenter locations
- 24/7 technical support
- Flexible booking options
- Professional-grade hardware

## Development

### Adding New GPU Models
Edit `gpu_inventory.json` to add new GPU models with specifications and instances.

### Extending AI Functions
Add new functions to the `HPC_ChatBot` class and register them in the `tools` array.

### Customizing the Web Interface
Modify `chat_interface.html` and `timeline_dashboard.html` for UI customizations.

## File Structure

```text
TODO: add file structure
```
