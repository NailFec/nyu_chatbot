#!/usr/bin/env python3
"""
SK (Shame Kitten) HPC Services Chatbot Launcher
==============================================

This script provides an easy way to launch different components of the SK HPC chatbot system.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

# Set the Python interpreter to use NYU conda environment
PYTHON_EXE = os.path.expanduser("~\\miniconda3\\envs\\nyu\\python.exe")

def print_banner():
    """Print the SK HPC Services banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                SK (Shame Kitten) HPC Services                ║
║                    AI Chatbot System                         ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import openai
        import flask
        print("✓ Dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_files():
    """Check if required files exist"""
    required_files = [
        'nailfec.py',
        'gpu_inventory.json',
        'bookings.json',
        'hpc_chatbot.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"✗ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✓ All required files are present")
        return True

def launch_cli_chatbot():
    """Launch the command-line chatbot"""
    print("\n🤖 Launching CLI Chatbot...")
    print("Type 'quit' to exit the chatbot")
    print("-" * 50)
    
    try:
        subprocess.run([PYTHON_EXE, "hpc_chatbot.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching CLI chatbot: {e}")
    except KeyboardInterrupt:
        print("\nChatbot terminated by user")

def launch_web_server():
    """Launch the web server with dashboard and API"""
    print("\n🌐 Launching Web Server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the web server
        process = subprocess.Popen([PYTHON_EXE, "web_server.py"])
        
        # Wait a moment and then open browser
        time.sleep(2)
        print("Opening dashboard in browser...")
        webbrowser.open("http://localhost:5000/timeline_dashboard.html")
        
        # Wait for the process to complete
        process.wait()
        
    except subprocess.CalledProcessError as e:
        print(f"Error launching web server: {e}")
    except KeyboardInterrupt:
        print("\nWeb server terminated by user")
        if 'process' in locals():
            process.terminate()

def launch_chat_interface():
    """Launch just the chat interface"""
    print("\n💬 Launching Chat Interface...")
    
    # Check if web server is running, if not start it
    try:
        import requests
        response = requests.get("http://localhost:5000/api/server_status", timeout=2)
        if response.status_code == 200:
            print("Web server is already running")
        else:
            raise Exception("Server not responding")
    except:
        print("Starting web server...")
        process = subprocess.Popen([PYTHON_EXE, "web_server.py"])
        time.sleep(3)
    
    print("Opening chat interface in browser...")
    webbrowser.open("http://localhost:5000/chat_interface.html")

def show_system_info():
    """Show system information and statistics"""
    print("\n📊 System Information")
    print("=" * 50)
    
    try:
        import json
        
        # Load GPU inventory
        with open('gpu_inventory.json', 'r') as f:
            gpu_data = json.load(f)
        
        # Load bookings
        with open('bookings.json', 'r') as f:
            bookings = json.load(f)
        
        # Calculate statistics
        total_gpus = sum(len(model['instances']) for model in gpu_data['gpu_models'].values())
        active_bookings = len([b for b in bookings if b['status'] == 'active'])
        total_bookings = len(bookings)
        total_revenue = sum(b['total_cost'] + b.get('overtime_cost', 0) for b in bookings)
        
        # GPU model breakdown
        print(f"Total GPU Instances: {total_gpus}")
        print(f"Active Bookings: {active_bookings}")
        print(f"Total Bookings: {total_bookings}")
        print(f"Total Revenue: ${total_revenue:.2f}")
        print(f"Utilization Rate: {(active_bookings/total_gpus)*100:.1f}%")
        
        print("\nGPU Models Available:")
        for model_key, model_info in gpu_data['gpu_models'].items():
            instances = len(model_info['instances'])
            price = model_info['price_per_30min']
            memory = model_info['memory']
            print(f"  • {model_key}: {instances} instances, {memory}, ${price}/30min")
        
        print("\nRecent Bookings:")
        recent_bookings = sorted(bookings, key=lambda x: x['created_at'], reverse=True)[:5]
        for booking in recent_bookings:
            user = booking['user_name']
            gpu = booking['gpu_model']
            status = booking['status']
            print(f"  • {user} - {gpu} - {status}")
            
    except Exception as e:
        print(f"Error loading system information: {e}")

def main():
    """Main launcher function"""
    print_banner()
    
    # Check prerequisites
    if not check_dependencies() or not check_files():
        print("\nPlease fix the above issues before continuing.")
        return
    
    while True:
        print("\n🚀 Launch Options:")
        print("1. Command-line Chatbot")
        print("2. Web Server + Dashboard")
        print("3. Chat Interface Only")
        print("4. System Information")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            launch_cli_chatbot()
        elif choice == "2":
            launch_web_server()
        elif choice == "3":
            launch_chat_interface()
        elif choice == "4":
            show_system_info()
        elif choice == "5":
            print("Goodbye! Thank you for using SK HPC Services.")
            break
        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()
