#!/usr/bin/env python3
"""
Test data processing modules
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.module_registry import registry
import config

def test_data_modules():
    """Test data processing modules"""
    print("🧪 Testing Data Modules...\n")
    
    # Auto-discover modules first
    print("0. Auto-discovering modules...")
    registry.auto_discover('modules')
    
    # Test SimpleCategorizer
    print("1. Testing SimpleCategorizer...")
    try:
        categorizer = registry.get_module('SimpleCategorizer', config={'mapping_file': 'category_mapping.json'})
        if categorizer:
            print("   ✅ SimpleCategorizer loaded successfully")
            
            # Test categorization
            test_transaction = {
                'description': '星巴克咖啡',
                'amount': 120,
                'category': ''
            }
            
            result = categorizer.execute(test_transaction)
            print(f"   ✅ Categorization result: {result}")
        else:
            print("   ❌ Failed to load SimpleCategorizer")
            
    except Exception as e:
        print(f"   ❌ SimpleCategorizer test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test FileParser
    print("\n2. Testing FileParser...")
    try:
        parser = registry.get_module('FileParser')
        if parser:
            print("   ✅ FileParser loaded successfully")
        else:
            print("   ❌ Failed to load FileParser")
            
    except Exception as e:
        print(f"   ❌ FileParser test failed: {e}")
    
    # Test MonthlyMerger
    print("\n3. Testing MonthlyMerger...")
    try:
        merger = registry.get_module('MonthlyMerger')
        if merger:
            print("   ✅ MonthlyMerger loaded successfully")
        else:
            print("   ❌ Failed to load MonthlyMerger")
            
    except Exception as e:
        print(f"   ❌ MonthlyMerger test failed: {e}")
    
    # Test AnnualManager
    print("\n4. Testing AnnualManager...")
    try:
        annual_mgr = registry.get_module('AnnualManager', config={
            'onedrive_path': config.ONEDRIVE_PATH,
            'template_file': '20XX年開銷表（NT）.xlsx',
            'auto_create': True
        })
        if annual_mgr:
            print("   ✅ AnnualManager loaded successfully")
            
            # Test getting budget file
            budget_file = annual_mgr.get_active_budget_file()
            print(f"   ✅ Active budget file: {os.path.basename(budget_file)}")
        else:
            print("   ❌ Failed to load AnnualManager")
            
    except Exception as e:
        print(f"   ❌ AnnualManager test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Data module tests completed!")

if __name__ == "__main__":
    test_data_modules()
