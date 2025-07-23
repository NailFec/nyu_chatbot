from flask import Flask, request, jsonify, session
from hpc_chatbot import HPC_ChatBot
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 存储用户会话对应的 chatbot 实例
chatbot_instances = {}

@app.route('/chat', methods=['POST'])
def chat():
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
    
    session_id = session['session_id']
    
    # 获取或创建用户专属的 chatbot 实例
    if session_id not in chatbot_instances:
        chatbot_instances[session_id] = HPC_ChatBot(session_id)
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    # 获取用户消息并发送到对应的 chatbot 实例
    user_message = data['message']
    chatbot = chatbot_instances[session_id]
    response = chatbot.send_message_to_ai(user_message)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
