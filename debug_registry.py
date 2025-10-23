#!/usr/bin/env python3
"""
Debug the registry to see what's happening
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.module_registry import registry
import config

def debug_registry():
    """Debug the registry"""
    print("🔍 Debugging Registry...\n")
    
    # Auto-discover modules
    print("1. Auto-discovering modules...")
    registry.auto_discover('modules')
    
    print(f"\n2. Registry state:")
    print(f"   Modules dict: {list(registry.modules.keys())}")
    print(f"   Instances dict: {list(registry.instances.keys())}")
    
    print(f"\n3. Looking for QwenEngine...")
    if 'QwenEngine' in registry.modules:
        print(f"   ✅ QwenEngine found in modules: {registry.modules['QwenEngine']}")
    else:
        print(f"   ❌ QwenEngine not in modules")
    
    print(f"\n4. Trying to get QwenEngine...")
    try:
        qwen_config = config.LLM_CONFIG.get('structured', {})
        print(f"   Config: {qwen_config}")
        
        qwen = registry.get_module('QwenEngine', config=qwen_config)
        print(f"   Result: {qwen}")
        
        if qwen:
            print(f"   ✅ Successfully got QwenEngine instance")
        else:
            print(f"   ❌ Failed to get QwenEngine instance")
            
    except Exception as e:
        print(f"   ❌ Exception getting QwenEngine: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_registry()
