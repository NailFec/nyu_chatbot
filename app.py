from flask import Flask, request, jsonify, session, send_from_directory, send_file
from hpc_chatbot import HPC_ChatBot
import secrets
import redis
import pickle
from threading import Lock
import json
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Redis connection (optional, use memory if Redis unavailable)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    USE_REDIS = True
    print("Redis connected successfully - Session persistence enabled")
except:
    USE_REDIS = False
    print("Redis not connected - Using memory storage (sessions lost on restart)")

lock = Lock()
memory_sessions = {}

def get_or_create_chatbot(session_id):
    """Get or create new chatbot instance"""
    if USE_REDIS:
        try:
            chatbot_pickle = redis_client.get(f'chatbot:{session_id}')
            if chatbot_pickle:
                return pickle.loads(chatbot_pickle)
        except Exception as e:
            print(f"Failed to deserialize chatbot from Redis: {e}")
    else:
        if session_id in memory_sessions:
            return memory_sessions[session_id]
    
    chatbot = HPC_ChatBot(session_id)
    save_chatbot(session_id, chatbot)
    return chatbot

def save_chatbot(session_id, chatbot):
    """Save chatbot state"""
    if USE_REDIS:
        redis_client.setex(f'chatbot:{session_id}', 3600, pickle.dumps(chatbot))
    else:
        memory_sessions[session_id] = chatbot

@app.route('/')
def home():
    """Main page - Chat interface"""
    return send_file('chat_interface.html')

@app.route('/dashboard')
def dashboard():
    """Data dashboard"""
    return send_file('timeline_dashboard.html')

@app.route('/test')
def test_chat():
    """Simple chat test page"""
    return send_file('test_chat.html')

@app.route('/favicon.ico')
def favicon():
    """Website icon"""
    return send_file('favicon.ico')

@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat_with_session():
    """Chat API with session management"""
    try:
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)
        
        session_id = session['session_id']
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        chatbot = get_or_create_chatbot(session_id)
        response = chatbot.send_message_to_ai(data['message'])
        save_chatbot(session_id, chatbot)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Flask API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/direct/chat', methods=['POST'])
def direct_chat():
    """Direct chat API without session"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        chatbot = HPC_ChatBot()
        response = chatbot.send_message_to_ai(data['message'])
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_gpus')
def search_gpus():
    """Search available GPUs"""
    try:
        chatbot = HPC_ChatBot()
        result = chatbot.search_available_gpus(
            model=request.args.get('model'),
            start_time=request.args.get('start_time'),
            end_time=request.args.get('end_time'),
            min_memory=request.args.get('min_memory', type=float)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations')
def get_recommendations():
    """Get GPU recommendations"""
    use_case = request.args.get('use_case', '')
    if not use_case:
        return jsonify({'error': 'Use case is required'}), 400
    
    try:
        chatbot = HPC_ChatBot()
        result = chatbot.get_gpu_recommendations(
            use_case=use_case,
            budget_per_hour=request.args.get('budget_per_hour', type=float),
            memory_requirement=request.args.get('memory_requirement', type=float)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gpu_inventory')
def get_gpu_inventory():
    """Get GPU inventory"""
    try:
        with open('gpu_inventory.json', 'r') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings')
def get_bookings():
    """Get booking data"""
    try:
        with open('bookings.json', 'r') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/current_datetime')
def get_current_datetime():
    """Get current time"""
    try:
        chatbot = HPC_ChatBot()
        return jsonify(chatbot.get_current_datetime())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    """Clear current session"""
    if 'session_id' in session:
        session_id = session['session_id']
        if USE_REDIS:
            redis_client.delete(f'chatbot:{session_id}')
        else:
            memory_sessions.pop(session_id, None)
        session.clear()
    return jsonify({'message': 'Session cleared'})

@app.route('/debug/history')
def debug_history():
    """View conversation history"""
    if 'session_id' not in session:
        return jsonify({'error': 'No active session found'})
    
    try:
        chatbot = get_or_create_chatbot(session['session_id'])
        if hasattr(chatbot, 'conversation_history'):
            return jsonify({
                'session_id': session['session_id'],
                'length': len(chatbot.conversation_history),
                'recent_history': chatbot.conversation_history[-10:],
                'full_history': chatbot.conversation_history
            })
        return jsonify({'error': 'No conversation history found'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/debug/sessions')
def debug_sessions():
    """View all active sessions"""
    if USE_REDIS:
        try:
            keys = redis_client.keys('chatbot:*')
            sessions = [key.decode().split(':')[1] for key in keys]
            return jsonify({'active_sessions': sessions, 'count': len(sessions)})
        except:
            return jsonify({'error': 'Redis connection failed'})
    else:
        return jsonify({
            'active_sessions': list(memory_sessions.keys()),
            'count': len(memory_sessions)
        })

@app.route('/api/')
def api_docs():
    """API documentation"""
    return jsonify({
        "version": "2.4",
        "session_apis": {
            "/api/chat": "POST - Chat with session",
            "/api/session/clear": "POST - Clear session"
        },
        "direct_apis": {
            "/api/direct/chat": "POST - Chat without session",
            "/api/search_gpus": "GET - Search GPUs",
            "/api/recommendations": "GET - GPU recommendations",
            "/api/gpu_inventory": "GET - GPU inventory",
            "/api/bookings": "GET - Booking data",
            "/api/current_datetime": "GET - Current time"
        },
        "debug_apis": {
            "/debug/history": "GET - View conversation history",
            "/debug/sessions": "GET - View active sessions"
        },
        "pages": {
            "/": "Chat interface",
            "/dashboard": "Data dashboard"
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  SK HPC Services - Unified Server")
    print("=" * 60)
    print(f"Storage mode: {'Redis (persistent)' if USE_REDIS else 'Memory (temporary)'}")
    print("Service URLs:")
    print("   - Chat interface: http://localhost:5000")
    print("   - Data dashboard: http://localhost:5000/dashboard")
    print("   - API docs: http://localhost:5000/api/")
    print("   - Debug interface: http://localhost:5000/debug/history")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
