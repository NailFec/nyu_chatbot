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

# 初始化 Redis 连接 (可选，如果没有Redis则使用内存)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()  # 测试连接
    USE_REDIS = True
    print("✅ Redis连接成功 - 启用会话持久化")
except:
    USE_REDIS = False
    print("⚠️  Redis未连接 - 使用内存存储 (重启后会话丢失)")

lock = Lock()
memory_sessions = {}  # 内存存储备用

def get_or_create_chatbot(session_id):
    """获取或创建新的 chatbot 实例"""
    # 检查是否已有实例
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
    
    # 创建新实例
    chatbot = HPC_ChatBot(session_id)
    save_chatbot(session_id, chatbot)
    return chatbot

def save_chatbot(session_id, chatbot):
    """保存 chatbot 状态"""
    if USE_REDIS:
        redis_client.setex(f'chatbot:{session_id}', 3600, pickle.dumps(chatbot))
    else:
        memory_sessions[session_id] = chatbot

# ===============================
# 前端页面路由
# ===============================
@app.route('/')
def home():
    """主页 - 聊天界面"""
    return send_file('chat_interface.html')

@app.route('/dashboard')
def dashboard():
    """数据仪表板"""
    return send_file('timeline_dashboard.html')

@app.route('/test')
def test_chat():
    """简单聊天测试页面"""
    return send_file('test_chat.html')

@app.route('/favicon.ico')
def favicon():
    """网站图标"""
    return send_file('favicon.ico')

# ===============================
# 聊天API (支持会话管理)
# ===============================
@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat_with_session():
    """带会话管理的聊天API"""
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

# ===============================
# RESTful API (无会话，直接调用)
# ===============================
@app.route('/api/direct/chat', methods=['POST'])
def direct_chat():
    """无会话的直接聊天API"""
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
    """搜索可用GPU"""
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
    """获取GPU推荐"""
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

# ===============================
# 数据API
# ===============================
@app.route('/api/gpu_inventory')
def get_gpu_inventory():
    """获取GPU库存"""
    try:
        with open('gpu_inventory.json', 'r') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings')
def get_bookings():
    """获取预订数据"""
    try:
        with open('bookings.json', 'r') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/current_datetime')
def get_current_datetime():
    """获取当前时间"""
    try:
        chatbot = HPC_ChatBot()
        return jsonify(chatbot.get_current_datetime())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===============================
# 会话管理
# ===============================
@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    """清除当前会话"""
    if 'session_id' in session:
        session_id = session['session_id']
        if USE_REDIS:
            redis_client.delete(f'chatbot:{session_id}')
        else:
            memory_sessions.pop(session_id, None)
        session.clear()
    return jsonify({'message': 'Session cleared'})

# ===============================
# 调试和监控
# ===============================
@app.route('/debug/history')
def debug_history():
    """查看对话历史"""
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
    """查看所有活跃会话"""
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
    """API文档"""
    return jsonify({
        "version": "2.1",
        "session_apis": {
            "/api/chat": "POST - 带会话的聊天",
            "/api/session/clear": "POST - 清除会话"
        },
        "direct_apis": {
            "/api/direct/chat": "POST - 无会话聊天",
            "/api/search_gpus": "GET - 搜索GPU",
            "/api/recommendations": "GET - GPU推荐",
            "/api/gpu_inventory": "GET - GPU库存",
            "/api/bookings": "GET - 预订数据",
            "/api/current_datetime": "GET - 当前时间"
        },
        "debug_apis": {
            "/debug/history": "GET - 查看对话历史",
            "/debug/sessions": "GET - 查看活跃会话"
        },
        "pages": {
            "/": "聊天界面",
            "/dashboard": "数据仪表板"
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  🚀 SK HPC Services - 统一服务器")
    print("=" * 60)
    print(f"💾 存储模式: {'Redis (持久化)' if USE_REDIS else '内存 (临时)'}")
    print("🌐 服务地址:")
    print("   - 聊天界面: http://localhost:5000")
    print("   - 数据仪表板: http://localhost:5000/dashboard")
    print("   - API文档: http://localhost:5000/api/")
    print("   - 调试接口: http://localhost:5000/debug/history")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
