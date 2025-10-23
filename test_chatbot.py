#!/usr/bin/env python3
"""
Test script for the chatbot functionality
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.simple_orchestrator import SimpleLLMOrchestrator
from core.module_registry import registry
from modules.data import SimpleCategorizer, MonthlyMerger, AnnualManager
import config
from modules.insights.simple_ai_chat import SimpleAIChat
from modules.insights.multi_year_data_loader import MultiYearDataLoader

def test_chatbot():
    """Test the chatbot with debug logging"""
    print("🧪 Testing Chatbot Functionality\n")
    
    # Initialize system components
    print("🔧 Initializing system...")
    
    # Discover modules first
    print("📦 Loading modules...")
    registry.auto_discover('modules')
    
    # Initialize orchestrator
    orchestrator = SimpleLLMOrchestrator()
    if not orchestrator.initialize():
        print("❌ LLM initialization failed")
        return
    
    # Initialize data modules
    categorizer = registry.get_module('SimpleCategorizer', config={'mapping_file': 'category_mapping.json'})
    categorizer.set_llm_fallback(orchestrator.qwen)
    
    merger = registry.get_module('MonthlyMerger')
    merger.set_categorizer(categorizer)
    merger.set_orchestrator(orchestrator)
    
    annual_mgr = registry.get_module('AnnualManager', config={
        'onedrive_path': config.ONEDRIVE_PATH,
        'template_file': '20XX年開銷表（NT）.xlsx',
        'auto_create': True
    })
    
    # Get budget files
    budget_file = annual_mgr.get_active_budget_file()
    budget_files = annual_mgr.get_multi_year_files(num_years=2)
    
    print(f"📁 Budget files: {budget_files}")
    
    # Initialize multi-year data loader
    multi_data_loader = MultiYearDataLoader(budget_files)
    
    # Initialize AI Chat
    ai_chat = SimpleAIChat(
        data_loader=multi_data_loader,
        orchestrator=orchestrator,
        context_manager=None
    )
    
    print("\n" + "="*80)
    print("🤖 CHATBOT TEST - Ask questions to test the system")
    print("="*80 + "\n")
    
    # Test questions
    test_questions = [
        "七月花了多少？",
        "顯示七月的支出",
        "七月的伙食費是多少？",
        "比較七月和八月",
        "顯示圖表"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"🧪 TEST {i}: {question}")
        print('='*60)
        
        try:
            answer = ai_chat.answer_question(question)
            print(f"\n💡 助手回應:")
            print(answer)
        except Exception as e:
            print(f"\n❌ 錯誤: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    test_chatbot()
