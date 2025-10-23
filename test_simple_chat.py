#!/usr/bin/env python3
"""
Simple chatbot test with one question
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.simple_orchestrator import SimpleLLMOrchestrator
from core.module_registry import registry
import config
from modules.insights.simple_ai_chat import SimpleAIChat
from modules.insights.multi_year_data_loader import MultiYearDataLoader

def test_simple_chat():
    """Test chatbot with one simple question"""
    print("🧪 Testing Simple Chatbot\n")
    
    # Discover modules
    print("📦 Loading modules...")
    registry.auto_discover('modules')
    
    # Initialize orchestrator
    orchestrator = SimpleLLMOrchestrator()
    if not orchestrator.initialize():
        print("❌ LLM initialization failed")
        return
    
    # Initialize annual manager
    annual_mgr = registry.get_module('AnnualManager', config={
        'onedrive_path': config.ONEDRIVE_PATH,
        'template_file': '20XX年開銷表（NT）.xlsx',
        'auto_create': True
    })
    
    # Get budget files
    budget_files = annual_mgr.get_multi_year_files(num_years=2)
    print(f"📁 Budget files: {budget_files}")
    
    # Initialize data loader
    multi_data_loader = MultiYearDataLoader(budget_files)
    
    # Initialize AI Chat
    ai_chat = SimpleAIChat(
        data_loader=multi_data_loader,
        orchestrator=orchestrator,
        context_manager=None
    )
    
    # Test one question
    question = "七月花了多少？"
    print(f"\n🤖 Testing question: {question}")
    print("="*60)
    
    try:
        answer = ai_chat.answer_question(question)
        print(f"\n💡 助手回應:")
        print(answer)
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_chat()
