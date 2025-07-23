#!/usr/bin/env python3
"""
Test script for booking card functionality
"""

from hpc_chatbot import HPC_ChatBot
import json

def test_booking_card():
    """Test the booking card generation and display"""
    
    # Create chatbot instance
    chatbot = HPC_ChatBot()
    
    # Create a sample booking for testing
    sample_booking = {
        "booking_id": "book_999",
        "booking_hash": "test123abc456def789",
        "user_name": "John Doe",
        "user_email": "john.doe@example.com",
        "gpu_model": "RTX-4090",
        "gpu_id": "RTX-4090-01",
        "start_time": "2025-07-25T10:00:00Z",
        "end_time": "2025-07-25T18:00:00Z",
        "status": "scheduled",
        "storage_gb": 256,
        "memory_gb": 64,
        "cpu_cores": 16,
        "created_at": "2025-07-23T12:00:00Z",
        "total_cost": 45.50,
        "overtime_minutes": 0,
        "overtime_cost": 0.00
    }
    
    print("Testing booking confirmation card...")
    # Test confirmation card
    success = chatbot.display_booking_card(sample_booking, is_cancelled=False)
    if success:
        print("✅ Confirmation card generated successfully!")
    else:
        print("❌ Failed to generate confirmation card")
    
    print("\nTesting booking cancellation card...")
    # Test cancellation card
    sample_booking["status"] = "cancelled"
    success = chatbot.display_booking_card(sample_booking, is_cancelled=True)
    if success:
        print("✅ Cancellation card generated successfully!")
    else:
        print("❌ Failed to generate cancellation card")
    
    print("\nBoth cards should have opened in your default browser!")

if __name__ == "__main__":
    test_booking_card()
