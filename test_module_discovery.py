#!/usr/bin/env python3
"""
Test module discovery to see what's happening
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.module_registry import registry

def test_module_discovery():
    """Test module discovery"""
    print("🔍 Testing Module Discovery...\n")
    
    # Try to discover modules
    print("1. Auto-discovering modules...")
    registry.auto_discover('modules')
    
    print("\n2. Listing registered modules:")
    registry.list_modules()
    
    print("\n3. Testing specific module loading...")
    
    # Try to get QwenEngine directly
    try:
        from modules.llm.qwen_engine import QwenEngine
        print(f"   ✅ QwenEngine class found: {QwenEngine}")
        
        # Try to register manually
        registry.register('QwenEngine', QwenEngine)
        print("   ✅ QwenEngine registered manually")
        
    except Exception as e:
        print(f"   ❌ QwenEngine import failed: {e}")
    
    # Try to get GptOssEngine directly
    try:
        from modules.llm.gpt_oss_engine import GptOssEngine
        print(f"   ✅ GptOssEngine class found: {GptOssEngine}")
        
        # Try to register manually
        registry.register('GptOssEngine', GptOssEngine)
        print("   ✅ GptOssEngine registered manually")
        
    except Exception as e:
        print(f"   ❌ GptOssEngine import failed: {e}")
    
    print("\n4. Final module list:")
    registry.list_modules()

if __name__ == "__main__":
    test_module_discovery()
