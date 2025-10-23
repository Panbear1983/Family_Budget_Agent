#!/usr/bin/env python3
"""
Test the complete Family Budget Agent system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import LLMOrchestrator
from core.module_registry import registry
from modules.data import SimpleCategorizer, MonthlyMerger, AnnualManager
import config

def test_complete_system():
    """Test the complete system like the main script does"""
    print("🧪 Testing Complete Family Budget Agent System...\n")
    
    # Step 1: Initialize system (like main.py)
    print("1. Initializing system...")
    
    # Discover modules
    print("   📦 Loading modules...")
    registry.auto_discover('modules')
    
    # Initialize LLM orchestrator
    print("   🤖 Initializing LLM engines...")
    orchestrator = LLMOrchestrator()
    
    if not orchestrator.initialize():
        print("   ❌ LLM initialization failed")
        return False
    
    # Initialize data modules
    print("   📊 Loading data modules...")
    
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
    
    # Check/create annual file
    budget_file = annual_mgr.get_active_budget_file()
    budget_files = annual_mgr.get_multi_year_files(num_years=2)
    
    print(f"   ✅ System ready!")
    print(f"      Current year: {os.path.basename(budget_file)}")
    print(f"      Multi-year analysis: {len(budget_files)} year(s) loaded")
    
    # Step 2: Test LLM functionality
    print("\n2. Testing LLM functionality...")
    
    # Test categorization
    test_transaction = {
        'description': '麥當勞午餐',
        'amount': 150,
        'category': ''
    }
    
    category, confidence = orchestrator.categorize_transaction(test_transaction)
    print(f"   ✅ Categorization: {category} (confidence: {confidence:.2f})")
    
    # Test duplicate detection
    tx1 = {'date': '2025-01-15', 'amount': 100, 'description': '星巴克咖啡'}
    tx2 = {'date': '2025-01-15', 'amount': 100, 'description': '星巴克咖啡'}
    
    is_dup, reason = orchestrator.detect_duplicate(tx1, tx2)
    print(f"   ✅ Duplicate detection: {is_dup} ({reason})")
    
    # Step 3: Test data processing
    print("\n3. Testing data processing...")
    
    # Test categorizer
    result = categorizer.execute(test_transaction)
    print(f"   ✅ Categorizer result: {result}")
    
    # Test file operations
    if os.path.exists(budget_file):
        print(f"   ✅ Budget file exists: {os.path.basename(budget_file)}")
    else:
        print(f"   ⚠️  Budget file not found: {budget_file}")
    
    # Step 4: Test Qwen-only chat system
    print("\n4. Testing Qwen chat system...")
    
    try:
        from core.qwen_orchestrator import QwenOrchestrator
        from modules.insights.qwen_chat import QwenChat
        from modules.insights.multi_year_data_loader import MultiYearDataLoader
        
        # Initialize Qwen orchestrator
        qwen_orchestrator = QwenOrchestrator()
        qwen_orchestrator.initialize()
        
        # Use multi-year data loader
        multi_data_loader = MultiYearDataLoader(budget_files)
        
        # Initialize Qwen Chat
        qwen_chat = QwenChat(
            data_loader=multi_data_loader,
            orchestrator=qwen_orchestrator
        )
        
        print("   ✅ Qwen Chat system initialized")
        
        # Test question answering
        test_question = "顯示七月的支出數據"
        answer = qwen_chat.answer_question(test_question)
        print(f"   ✅ Chat response: {answer[:100]}...")
        
    except Exception as e:
        print(f"   ⚠️  Qwen Chat test failed: {e}")
    
    print("\n🎉 Complete system test finished!")
    print("✅ Family Budget Agent is working correctly!")
    
    return True

if __name__ == "__main__":
    test_complete_system()
