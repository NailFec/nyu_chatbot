# SK (Shame Kitten) HPC Services

## 🎯 Project Overview
A comprehensive AI-powered chatbot system for HPC (High-Performance Computing) GPU rental services built for SK (Shame Kitten) company. The system provides intelligent assistance for GPU booking, querying, billing, and recommendations through a unified web application with session management capabilities.

## 📁 Updated Project Structure (Post-Cleanup)
```
d:\nfile\Pro\python\nyu_chatbot\
├── 📱 Core Application
│   ├── app.py                 # Main unified Flask application ⭐
│   ├── hpc_chatbot.py         # Core chatbot logic with AI integration
│   └── nailfec.py             # API keys (provided separately)
├── 📊 Data & Configuration
│   ├── gpu_inventory.json     # GPU models and specifications database
│   ├── bookings.json          # Booking records and history  
│   └── requirements.txt       # Python dependencies
├── 🌐 Web Interface
│   ├── chat_interface.html    # Main chat UI with markdown support
│   ├── timeline_dashboard.html # GPU booking timeline visualization
│   └── favicon.ico            # Website icon
├── 🧪 Testing (Organized)
│   ├── tests/
│   │   ├── test_card.py       # Booking card functionality tests
│   │   ├── test_markdown.py   # Markdown rendering tests
│   │   └── README.md          # Testing documentation
├── 📚 Examples & Documentation
│   ├── examples/              # API usage examples
│   │   ├── function_calling.py
│   │   ├── simple_dialog.py
│   │   └── structured_output.py
│   ├── README.md              # Comprehensive user documentation
│   └── PROJECT_SUMMARY.md     # This development summary
├── 🗂️ Legacy Files (For Reference)
│   ├── web_server.py          # Original separate web server
│   ├── launcher.py            # Old launcher script (removed)
│   ├── main.py                # Old main entry point (removed)
│   ├── app_backup.py          # Previous app.py version
│   └── unified_app.py         # Development unified version
└── 🔧 Utilities
    ├── run_chatbot.bat        # Windows launcher (update needed)
    ├── start_server.bat       # Windows server launcher (update needed)
    └── rule.nailfec.txt       # Project development guidelines
```

## 🚀 Key Improvements Made

### 1. **Application Unification**
- ✅ Merged `app.py` and `web_server.py` functionality
- ✅ Single application serves all needs
- ✅ Automatic Redis/memory storage switching
- ✅ Both session-based and direct API endpoints

### 2. **Session Management Enhancement**
- ✅ Redis-based persistent sessions
- ✅ Memory fallback when Redis unavailable
- ✅ Multi-user support with session isolation
- ✅ Debug endpoints for conversation tracking

### 3. **Code Organization**
- ✅ Moved test files to dedicated `tests/` directory
- ✅ Created testing documentation
- ✅ Organized legacy files for reference
- ✅ Updated project documentation

### 4. **API Structure Improvement**
```
Session APIs (Stateful):
  /api/chat              - Chat with session persistence
  /api/session/clear     - Clear current session

Direct APIs (Stateless):
  /api/direct/chat       - One-off chat requests
  /api/search_gpus       - GPU availability search
  /api/recommendations   - GPU recommendations
  /api/gpu_inventory     - GPU catalog data
  /api/bookings          - Booking records

Debug APIs:
  /debug/history         - View conversation history
  /debug/sessions        - Monitor active sessions
```

## 🔧 Updated Setup Instructions

### 1. Environment Setup
Using NYU conda environment:
```bash
# The system uses the NYU Python environment:
~\miniconda3\envs\nyu\python.exe
```

### 2. Install Dependencies
```bash
~\miniconda3\envs\nyu\python.exe -m pip install -r requirements.txt
```

### 3. Optional: Start Redis (for session persistence)
```bash
# Windows with Redis installed:
redis-server

# Or run without Redis (automatic fallback to memory storage)
```

### 4. Run the Unified Application
```bash
# Main application
~\miniconda3\envs\nyu\python.exe app.py

# Or with standard Python
python app.py
```

### 5. Access the Services
- **Main Chat Interface**: http://localhost:5000
- **Data Dashboard**: http://localhost:5000/dashboard
- **API Documentation**: http://localhost:5000/api/
- **Debug Console**: http://localhost:5000/debug/history

## 🧪 Testing

### Run All Tests
```bash
~\miniconda3\envs\nyu\python.exe -m pytest tests/
```

### Run Individual Tests
```bash
~\miniconda3\envs\nyu\python.exe tests/test_card.py
~\miniconda3\envs\nyu\python.exe tests/test_markdown.py
```

## 🔄 Migration Guide (For Existing Users)

### Before (Multiple Files)
```bash
python web_server.py          # For web interface
python hpc_chatbot.py         # For CLI chat
```

### After (Unified Application)
```bash
python app.py                 # One application for everything
```

### Key Changes
- ✅ Single application replaces multiple servers  
- ✅ Session management added for multi-user support
- ✅ Debug endpoints for development
- ✅ Automatic Redis detection and fallback
- ✅ Tests organized in dedicated directory
- ✅ Removed launcher scripts (use app.py directly)
## 🤖 AI Features & Technology

### Core AI Capabilities
- **Natural Language Processing**: Understands complex booking requests in English
- **Function Calling**: Automatically executes database operations
- **Context Awareness**: Maintains conversation context for multi-step interactions
- **Dynamic Responses**: All responses generated by AI (no fixed templates)
- **Intelligent Recommendations**: GPU selection based on use cases
- **Session-Aware Conversations**: Remembers context across multiple interactions

### Supported Functions
1. `search_available_gpus` - Find available GPU instances
2. `get_gpu_recommendations` - AI-powered GPU recommendations  
3. `prepare_booking_confirmation` - Generate booking confirmations
4. `confirm_operation` - Execute confirmed bookings/cancellations
5. `query_booking_info` - Check booking status
6. `cancel_booking` - Cancel existing bookings
7. `calculate_billing` - Generate billing reports
8. `get_current_datetime` - Time information for scheduling

## 💾 Database System

### GPU Inventory (gpu_inventory.json)
- **8 GPU Models**: RTX-4090, RTX-4080, RTX-4070, RTX-3090, RTX-3080, H100, A100, V100
- **Multiple Instances**: Each model has 4-8 individual instances
- **Detailed Specs**: Memory, CUDA cores, performance metrics, pricing
- **Real-time Tracking**: Availability status and booking conflicts

### Booking System (bookings.json)
- **Complete Records**: User info, GPU details, timing, billing
- **Status Tracking**: Scheduled, active, completed, cancelled
- **Security**: Booking hash verification for cancellations
- **Billing**: Automatic cost calculation with overtime handling

## 🛠️ Development Notes

### Current Status (v2.0)
- ✅ **Unified Application**: Single Flask app handles all functionality
- ✅ **Session Management**: Multi-user support with Redis persistence
- ✅ **Debug Tools**: Conversation tracking and session monitoring
- ✅ **Organized Testing**: Dedicated tests directory with documentation
- ✅ **Updated Documentation**: Comprehensive README and project summary
- ✅ **Simplified Deployment**: Direct Python execution, no batch files needed

### Known Limitations
- ⚠️ Requires manual API key setup in `nailfec.py`
- ⚠️ Redis is optional but recommended for production
- ⚠️ Legacy files kept for reference but may be outdated

### Future Improvements
- 🔄 Add automated testing in CI/CD
- 🔄 Implement user authentication system
- 🔄 Add email notifications for bookings
- 🔄 Create admin dashboard for system management
- 🔄 Docker containerization for easy deployment

## 📞 Support & Contact

For technical support or questions:
- **Email**: nailfec17@gmail.com
- **Project Repository**: nyu_chatbot
- **Developed for**: NYU Shanghai CS course project
- **API Provider**: Kenny (NYU Shanghai) - Educational use

---

*This project demonstrates advanced AI integration, web development, and system architecture for educational purposes at NYU Shanghai.*
- **52 Total Instances**: Distributed across models
- **Detailed Specs**: Memory, CUDA cores, pricing, descriptions
- **Real-time Status**: Available/busy tracking

### Booking System (bookings.json)
- **20+ Sample Bookings**: Realistic user scenarios
- **Comprehensive Data**: User info, GPU assignments, timing, costs
- **Status Tracking**: Active, scheduled, completed, cancelled
- **Billing Integration**: Cost calculation with overtime handling

## 🌐 Web Components

### Timeline Dashboard (timeline_dashboard.html)
- **Interactive Timeline**: Visual booking schedule by GPU model
- **Real-time Stats**: Utilization rates, revenue, active bookings
- **Advanced Filtering**: Date range, status, model filters
- **Responsive Design**: Modern, mobile-friendly interface

### Chat Interface (chat_interface.html)
- **AI-Powered Chat**: Full conversation interface
- **Quick Actions**: Pre-defined common queries
- **Real-time Responses**: Simulated typing indicators
- **Modern UI**: Clean, professional design

### Web Server (web_server.py)
- **REST API**: Complete API for all chatbot functions
- **Static File Serving**: Dashboard and data files
- **CORS Support**: Cross-origin requests
- **Error Handling**: Comprehensive error responses

## 📊 Sample Data Highlights

### GPU Models & Pricing
| Model | Memory | Price/30min | Instances | Best For |
|-------|--------|-------------|-----------|----------|
| H100 | 80GB HBM3 | $8.00 | 3 | Large AI models |
| A100 | 40GB HBM2e | $5.00 | 4 | Professional AI |
| RTX-4090 | 24GB GDDR6X | $2.50 | 5 | Gaming/Content |
| RTX-4080 | 16GB GDDR6X | $2.00 | 7 | High performance |
| RTX-4070 | 12GB GDDR6X | $1.50 | 10 | Value option |

### Realistic Booking Scenarios
- **Active Bookings**: Alice (H100), Bob (A100), Carol (RTX-4090), etc.
- **Diverse Users**: Research institutions, gaming companies, AI startups
- **Varied Durations**: From 12-hour sessions to week-long reservations
- **Real Timestamps**: Current date-relative scheduling

## 🎯 Usage Examples

### Conversation Flow Example
```
User: Hello, what services do you offer?
Bot: Hello! I'm the AI assistant for SK (Shame Kitten) HPC Services. We provide affordable, reliable, and high-performance GPU rental services...

User: I want to book a GPU for LLaMA 8B training
Bot: For LLaMA 8B model training, I recommend the RTX-4090 with 24GB VRAM at $2.50 per 30 minutes...

User: What's available tomorrow at 10 AM?
Bot: [Checks database] I found several RTX-4090 instances available tomorrow at 10 AM...
```

### API Usage
```python
# Get recommendations
GET /api/recommendations?use_case=LLaMA 8B training&budget_per_hour=10

# Create booking
POST /api/create_booking
{
  "gpu_model": "RTX-4090",
  "gpu_id": "RTX4090-001",
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "start_time": "2025-07-23T10:00:00Z",
  "end_time": "2025-07-23T18:00:00Z"
}
```

## 🚀 Key Achievements

1. **Complete AI Integration**: All responses go through AI API (no fixed responses)
2. **Realistic Database**: 52 GPU instances, 20+ bookings with real scenarios
3. **Function Calling**: Advanced AI function calling for database operations
4. **Web Visualization**: Interactive timeline dashboard for booking management
5. **Multi-Interface**: CLI, web chat, and REST API access
6. **Professional Quality**: Production-ready code with error handling
7. **Comprehensive Documentation**: Full README and inline comments
8. **Easy Deployment**: Multiple launch options including batch files

## 🎨 Technical Highlights

- **AI Model**: DeepSeek Chat with function calling
- **Backend**: Python with OpenAI API integration
- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **Database**: JSON-based for simplicity and portability
- **Server**: Flask with RESTful API design
- **Environment**: Conda-based Python environment management

This system demonstrates a complete, production-ready chatbot solution for HPC services with intelligent AI integration, comprehensive database management, and modern web interfaces.
