# SK (Shame Kitten) HPC Services Chatbot

A comprehensive AI-powered chatbot system for HPC (High-Performance Computing) GPU rental services. This system provides intelligent assistance for GPU booking, querying, billing, and recommendations through both command-line and web interfaces.

## 🚀 Features

### AI Chatbot Capabilities
- **Smart GPU Booking**: Intelligent booking assistance with step-by-step guidance and confirmation workflows
- **AI Recommendations**: GPU recommendations based on use cases (LLaMA training, gaming, rendering, etc.)
- **Session Management**: Multi-user support with Redis-based session persistence
- **Query Management**: Check booking status, billing history, and account information
- **Booking Management**: Cancel or modify existing reservations with security verification
- **Real-time Debugging**: Conversation history tracking and session monitoring

### Database & Inventory
- **Extensive GPU Catalog**: RTX-4090, RTX-4080, RTX-4070, RTX-3090, RTX-3080, H100, A100, V100
- **Detailed Specifications**: Memory, CUDA cores, pricing, performance metrics
- **Real-time Availability**: Dynamic availability checking with conflict detection
- **Booking History**: Comprehensive booking records with billing information

### Web Dashboard & API
- **Unified Web Interface**: Single application serving both chat and dashboard
- **Timeline Visualization**: Interactive GPU booking timeline by model and instance
- **RESTful API**: Complete REST API for all chatbot functions
- **Session & Direct APIs**: Both stateful and stateless API endpoints
- **Responsive Design**: Modern, mobile-friendly interface

## 🏗️ System Architecture

```
├── app.py                 # Main unified Flask application (recommended)
├── hpc_chatbot.py         # Core chatbot class with AI integration
├── gpu_inventory.json     # GPU models and instance database
├── bookings.json          # Booking records and history
├── chat_interface.html    # Web-based chat interface
├── timeline_dashboard.html # GPU booking timeline dashboard
├── tests/                 # Test files directory
│   ├── test_card.py       # Booking card tests
│   ├── test_markdown.py   # Markdown rendering tests
│   └── README.md          # Testing documentation
├── examples/              # API usage examples
│   ├── function_calling.py
│   ├── simple_dialog.py
│   └── structured_output.py
└── legacy/                # Backup files (optional)
    ├── web_server.py      # Original web server
    └── unified_app.py     # Alternative unified version
```

## 📦 Setup

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

### 2. Start Redis (Optional, for session persistence)
```bash
# Windows with Redis installed
redis-server

# Linux/Mac
sudo systemctl start redis

# Or run without Redis - the app will automatically use memory storage
```

### 3. Run the Application
```bash
# Start the unified application
python app.py
```

The server will:
- ✅ Automatically detect Redis availability 
- ✅ Switch between persistent (Redis) and memory storage
- ✅ Display startup information and available services
- ✅ Be accessible at http://localhost:5000

### 4. Access the Services
Once running, open your browser to:
- **💬 Chat Interface**: http://localhost:5000
- **📊 Data Dashboard**: http://localhost:5000/dashboard  
- **📖 API Documentation**: http://localhost:5000/api/
- **🔧 Debug Tools**: http://localhost:5000/debug/history

## 🎯 Usage Examples

### Web Interface
1. Open http://localhost:5000 in your browser
2. Start chatting with the AI assistant
3. Use natural language for GPU booking requests
4. Access debug information at /debug/history

### Command Line Chat (Direct)
```bash
python hpc_chatbot.py
```
```
You: Hello, what services do you offer?
Bot: Hello! I'm the AI assistant for SK (Shame Kitten) HPC Services. We provide affordable, reliable, and high-performance GPU rental services...

You: I want to book a GPU for LLaMA 8B training
Bot: For LLaMA 8B model training, I recommend the RTX-4090 with 24GB VRAM at $2.50 per 30 minutes...
```

### API Usage

#### Session-based API (Recommended)
```python
import requests

# Chat with session management
response = requests.post('http://localhost:5000/api/chat', 
    json={'message': 'I want to book a RTX-4090'},
    cookies=session_cookies)

# Check conversation history
response = requests.get('http://localhost:5000/debug/history',
    cookies=session_cookies)
```

#### Direct API (Stateless)
```python
# Search available GPUs
response = requests.get('http://localhost:5000/api/search_gpus', params={
    'model': 'RTX-4090',
    'start_time': '2025-07-23T10:00:00Z',
    'end_time': '2025-07-23T18:00:00Z'
})

# Get recommendations  
response = requests.get('http://localhost:5000/api/recommendations', params={
    'use_case': 'LLaMA 8B training',
    'budget_per_hour': 10.0
})
```

## 🖥️ GPU Models Available

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

## 🧪 Testing

Run tests using:
```bash
# Run all tests
python -m pytest tests/

# Run specific tests
python tests/test_card.py
python tests/test_markdown.py
```

See `tests/README.md` for detailed testing information.

## 🔧 Development

### Adding New GPU Models
Edit `gpu_inventory.json` to add new GPU models with specifications and instances.

### Extending AI Functions
Add new functions to the `HPC_ChatBot` class and register them in the `tools` array.

### Customizing the Web Interface
Modify `chat_interface.html` and `timeline_dashboard.html` for UI customizations.

### Debugging
- Use `/debug/history` to view conversation history
- Use `/debug/sessions` to monitor active sessions
- Check Redis for persistent session data

## 📂 Project Structure

```text
nyu_chatbot/
├── 📱 Core Application
│   ├── app.py                 # Main unified Flask application
│   ├── hpc_chatbot.py         # Core chatbot logic & AI integration
│   └── nailfec.py             # API keys (not in repo)
├── 📊 Data & Config
│   ├── gpu_inventory.json     # GPU catalog & specifications
│   ├── bookings.json          # Booking records
│   └── requirements.txt       # Python dependencies
├── 🌐 Web Interface
│   ├── chat_interface.html    # Main chat UI
│   ├── timeline_dashboard.html # Data visualization
│   └── favicon.ico            # Site icon
├── 🧪 Testing
│   ├── tests/
│   │   ├── test_card.py       # Booking card tests
│   │   ├── test_markdown.py   # Markdown tests
│   │   └── README.md          # Test documentation
├── 📚 Examples & Docs
│   ├── examples/
│   │   ├── function_calling.py
│   │   ├── simple_dialog.py
│   │   └── structured_output.py
│   ├── README.md              # This file
│   └── PROJECT_SUMMARY.md     # Project overview
├── 🗂️ Legacy (Backup Files)
│   ├── web_server.py          # Original separate web server
│   ├── launcher.py            # Old launcher script
│   ├── main.py                # Old main entry point
│   ├── app_backup.py          # Previous app.py version
│   └── unified_app.py         # Development version
└── 🔧 Utilities
    └── rule.nailfec.txt       # Project rules/guidelines
```
