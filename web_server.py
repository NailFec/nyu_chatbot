from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
from hpc_chatbot import HPC_ChatBot

app = Flask(__name__)

# Initialize chatbot instance
chatbot = HPC_ChatBot()

@app.route('/')
def dashboard():
    """Serve the timeline dashboard"""
    return send_from_directory('.', 'timeline_dashboard.html')

@app.route('/api/gpu_inventory')
def get_gpu_inventory():
    """API endpoint to get GPU inventory data"""
    try:
        with open('gpu_inventory.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings')
def get_bookings():
    """API endpoint to get bookings data"""
    try:
        with open('bookings.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chatbot interaction"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        response = chatbot.send_message_to_ai(message)
        return jsonify({"response": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search_gpus')
def search_gpus():
    """API endpoint to search available GPUs"""
    try:
        model = request.args.get('model')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        min_memory = request.args.get('min_memory', type=float)
        
        result = chatbot.search_available_gpus(model, start_time, end_time, min_memory)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommendations')
def get_recommendations():
    """API endpoint to get GPU recommendations"""
    try:
        use_case = request.args.get('use_case', '')
        budget_per_hour = request.args.get('budget_per_hour', type=float)
        memory_requirement = request.args.get('memory_requirement', type=float)
        
        if not use_case:
            return jsonify({"error": "Use case is required"}), 400
        
        result = chatbot.get_gpu_recommendations(use_case, budget_per_hour, memory_requirement)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create_booking', methods=['POST'])
def create_booking_api():
    """API endpoint to create a new booking"""
    try:
        data = request.get_json()
        
        required_fields = ['gpu_model', 'gpu_id', 'user_name', 'user_email', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        result = chatbot.create_booking(**data)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/query_booking')
def query_booking_api():
    """API endpoint to query booking information"""
    try:
        booking_hash = request.args.get('booking_hash')
        user_email = request.args.get('user_email')
        booking_id = request.args.get('booking_id')
        
        result = chatbot.query_booking_info(booking_hash, user_email, booking_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cancel_booking', methods=['POST'])
def cancel_booking_api():
    """API endpoint to cancel a booking"""
    try:
        data = request.get_json()
        
        if 'booking_hash' not in data or 'user_email' not in data:
            return jsonify({"error": "Booking hash and user email are required"}), 400
        
        result = chatbot.cancel_booking(data['booking_hash'], data['user_email'])
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/billing')
def calculate_billing_api():
    """API endpoint to calculate billing information"""
    try:
        user_email = request.args.get('user_email')
        booking_hash = request.args.get('booking_hash')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not user_email:
            return jsonify({"error": "User email is required"}), 400
        
        result = chatbot.calculate_billing(user_email, booking_hash, start_date, end_date)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/server_status')
def server_status():
    """API endpoint to get simulated server status"""
    # This returns simulated server status information
    status_data = {
        "timestamp": "2025-07-22T12:00:00Z",
        "overall_status": "healthy",
        "datacenter_locations": [
            {
                "location": "US-West (Oregon)",
                "status": "online",
                "temperature": "22°C",
                "humidity": "45%",
                "power_usage": "85%",
                "network_latency": "2ms"
            },
            {
                "location": "US-East (Virginia)",
                "status": "online",
                "temperature": "24°C",
                "humidity": "42%",
                "power_usage": "78%",
                "network_latency": "1ms"
            },
            {
                "location": "EU-West (Ireland)",
                "status": "maintenance",
                "temperature": "21°C",
                "humidity": "48%",
                "power_usage": "20%",
                "network_latency": "5ms"
            }
        ],
        "system_metrics": {
            "total_gpus": 52,
            "active_gpus": 28,
            "utilization_rate": "54%",
            "average_temperature": "67°C",
            "network_throughput": "9.2 Gbps",
            "storage_usage": "73%"
        },
        "recent_alerts": [
            {
                "level": "info",
                "message": "Scheduled maintenance for EU-West datacenter completed",
                "timestamp": "2025-07-22T08:30:00Z"
            },
            {
                "level": "warning",
                "message": "High utilization detected on H100 cluster",
                "timestamp": "2025-07-22T11:45:00Z"
            }
        ]
    }
    
    return jsonify(status_data)

# Serve static files (JSON data files)
@app.route('/gpu_inventory.json')
def serve_gpu_inventory():
    return send_from_directory('.', 'gpu_inventory.json')

@app.route('/bookings.json')
def serve_bookings():
    return send_from_directory('.', 'bookings.json')

if __name__ == '__main__':
    print("=" * 60)
    print("  SK (Shame Kitten) HPC Services - Web Dashboard")
    print("=" * 60)
    print("Starting web server...")
    print("Dashboard available at: http://localhost:5000")
    print("API endpoints available at: http://localhost:5000/api/")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
