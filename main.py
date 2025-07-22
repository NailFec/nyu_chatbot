#!/usr/bin/env python3
"""
SK (Shame Kitten) HPC Services - Main Entry Point
==================================================

This is the main entry point for the SK HPC Services chatbot system.
You can run this file directly or use the launcher.py for more options.
"""

import sys
import os
from pathlib import Path

def main():
    """Main function to start the chatbot"""
    print("=" * 60)
    print("  SK (Shame Kitten) HPC Services")
    print("=" * 60)
    print()
    
    # Check if required files exist
    required_files = ['nailfec.py', 'gpu_inventory.json', 'bookings.json', 'hpc_chatbot.py']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all files are in the current directory.")
        return 1
    
    # Import and run the chatbot
    try:
        print("🚀 Starting SK HPC Services AI Assistant...")
        print()
        
        from hpc_chatbot import HPC_ChatBot
        chatbot = HPC_ChatBot()
        chatbot.chat()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("  pip install openai")
        return 1
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using SK HPC Services!")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

