#!/usr/bin/env python3
"""
Test LLM engines to ensure they're working
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.module_registry import registry
import config

def test_llm_engines():
    """Test both LLM engines"""
    print("🧪 Testing LLM Engines...\n")
    
    # Auto-discover modules first
    print("0. Auto-discovering modules...")
    registry.auto_discover('modules')
    
    # Test Qwen Engine
    print("1. Testing Qwen Engine...")
    try:
        qwen_config = config.LLM_CONFIG.get('structured', {})
        qwen = registry.get_module('QwenEngine', config=qwen_config)
        
        if qwen:
            # Test simple categorization
            test_transaction = {
                'description': '麥當勞午餐',
                'amount': 150,
                'category': ''
            }
            
            category, confidence = qwen.categorize(test_transaction)
            print(f"   ✅ Qwen categorization: {category} (confidence: {confidence:.2f})")
        else:
            print("   ❌ Failed to load Qwen engine")
            
    except Exception as e:
        print(f"   ❌ Qwen test failed: {e}")
    
    # Test GPT-OSS Engine
    print("\n2. Testing GPT-OSS Engine...")
    try:
        gpt_config = config.LLM_CONFIG.get('reasoning', {})
        gpt_oss = registry.get_module('GptOssEngine', config=gpt_config)
        
        if gpt_oss:
            # Test simple categorization
            test_transaction = {
                'description': 'Uber ride to airport',
                'amount': 300,
                'category': ''
            }
            
            category, confidence = gpt_oss.categorize(test_transaction)
            print(f"   ✅ GPT-OSS categorization: {category} (confidence: {confidence:.2f})")
        else:
            print("   ❌ Failed to load GPT-OSS engine")
            
    except Exception as e:
        print(f"   ❌ GPT-OSS test failed: {e}")
    
    print("\n🎉 LLM Engine tests completed!")

if __name__ == "__main__":
    test_llm_engines()
