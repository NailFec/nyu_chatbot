from flask import Flask, request, jsonify, session, send_from_directory, send_file
from hpc_chatbot import HPC_ChatBot
import secrets
import redis
import pickle
from threading import Lock
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 初始化 Redis 连接
redis_client = redis.Redis(host='localhost', port=6379, db=0)
lock = Lock()

def get_or_create_chatbot(session_id):
    """获取或创建新的 chatbot 实例，使用 Redis 存储"""
    # 使用锁来确保线程安全
    with lock:
        # 尝试从 Redis 获取现有的 chatbot
        chatbot_pickle = redis_client.get(f'chatbot:{session_id}')
        
        if chatbot_pickle:
            try:
                return pickle.loads(chatbot_pickle)
            except:
                # 如果反序列化失败，创建新实例
                chatbot = HPC_ChatBot(session_id)
        else:
            # 如果不存在，创建新实例
            chatbot = HPC_ChatBot(session_id)
        
        # 将新实例存储到 Redis
        redis_client.setex(
            f'chatbot:{session_id}',
            3600,  # 1小时过期
            pickle.dumps(chatbot)
        )
        return chatbot

def save_chatbot(session_id, chatbot):
    """将更新后的 chatbot 保存到 Redis"""
    with lock:
        redis_client.setex(
            f'chatbot:{session_id}',
            3600,  # 1小时过期
            pickle.dumps(chatbot)
        )

@app.route('/')
def home():
    """主页路由，提供聊天界面"""
    return send_file('chat_interface.html')

@app.route('/favicon.ico')
def favicon():
    """提供favicon文件"""
    return send_file('favicon.ico')

@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    # 生成或获取会话 ID
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
    
    session_id = session['session_id']
    
    # 验证请求数据
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        # 获取或创建 chatbot 实例
        chatbot = get_or_create_chatbot(session_id)
        
        # 处理用户消息
        user_message = data['message']
        response = chatbot.send_message_to_ai(user_message)
        
        # 保存更新后的 chatbot 状态
        save_chatbot(session_id, chatbot)
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_session():
    """清除用户会话"""
    if 'session_id' in session:
        redis_client.delete(f'chatbot:{session["session_id"]}')
        session.clear()
    return jsonify({'message': 'Session cleared'})

@app.route('/debug/history')
def debug_history():
    """查看对话历史的调试接口"""
    if 'session_id' not in session:
        return jsonify({'error': 'No active session found'})
    
    session_id = session['session_id']
    
    try:
        # 获取当前会话的 chatbot 实例
        chatbot = get_or_create_chatbot(session_id)
        
        if hasattr(chatbot, 'conversation_history'):
            return jsonify({
                'session_id': session_id,
                'length': len(chatbot.conversation_history),
                'history': chatbot.conversation_history[-10:],  # 最后10条
                'full_history': chatbot.conversation_history  # 完整历史记录
            })
        else:
            return jsonify({'error': 'No conversation history found in chatbot instance'})
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve history: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
