#!/usr/bin/env python3
"""
Test the AI chat system and function routing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.module_registry import registry
from core.qwen_orchestrator import QwenOrchestrator
import config

def test_chat_system():
    """Test the AI chat system"""
    print("🧪 Testing Chat System...\n")
    
    # Auto-discover modules first
    print("0. Auto-discovering modules...")
    registry.auto_discover('modules')
    
    # Test QwenOrchestrator
    print("1. Testing QwenOrchestrator...")
    try:
        qwen_orchestrator = QwenOrchestrator()
        if qwen_orchestrator.initialize():
            print("   ✅ QwenOrchestrator initialized successfully")
            
            # Test intent classification
            test_question = "顯示七月的支出數據"
            classification = qwen_orchestrator.classify_intent(test_question)
            print(f"   ✅ Intent classification: {classification}")
            
            # Test function routing
            function_name = qwen_orchestrator.route_to_function(classification)
            print(f"   ✅ Function routing: {function_name}")
            
        else:
            print("   ❌ Failed to initialize QwenOrchestrator")
            
    except Exception as e:
        print(f"   ❌ QwenOrchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test QwenChat if available
    print("\n2. Testing QwenChat...")
    try:
        from modules.insights.qwen_chat import QwenChat
        from modules.insights.multi_year_data_loader import MultiYearDataLoader
        
        # Create mock data loader
        budget_files = [config.BUDGET_PATH]  # Use the configured budget file
        multi_data_loader = MultiYearDataLoader(budget_files)
        
        # Initialize Qwen Chat
        qwen_chat = QwenChat(
            data_loader=multi_data_loader,
            orchestrator=qwen_orchestrator
        )
        
        print("   ✅ QwenChat initialized successfully")
        
        # Test question answering
        test_question = "顯示七月的支出數據"
        answer = qwen_chat.answer_question(test_question)
        print(f"   ✅ Question answering: {answer[:100]}...")
        
    except Exception as e:
        print(f"   ❌ QwenChat test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Chat system tests completed!")

if __name__ == "__main__":
    test_chat_system()
