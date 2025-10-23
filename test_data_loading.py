#!/usr/bin/env python3
"""
Simple test for data loading functionality
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.module_registry import registry
import config
from modules.insights.multi_year_data_loader import MultiYearDataLoader

def test_data_loading():
    """Test just the data loading part"""
    print("🧪 Testing Data Loading\n")
    
    # Discover modules
    print("📦 Loading modules...")
    registry.auto_discover('modules')
    
    # Initialize annual manager
    annual_mgr = registry.get_module('AnnualManager', config={
        'onedrive_path': config.ONEDRIVE_PATH,
        'template_file': '20XX年開銷表（NT）.xlsx',
        'auto_create': True
    })
    
    # Get budget files
    budget_file = annual_mgr.get_active_budget_file()
    budget_files = annual_mgr.get_multi_year_files(num_years=2)
    
    print(f"📁 Budget file: {budget_file}")
    print(f"📁 Budget files: {budget_files}")
    
    # Test data loading
    if budget_files:
        print(f"\n🔍 Testing data loading with {len(budget_files)} files...")
        multi_data_loader = MultiYearDataLoader(budget_files)
        all_data = multi_data_loader.load_all_data()
        
        print(f"\n📊 Data loading results:")
        print(f"  Total months loaded: {len(all_data)}")
        
        for month_key, df in all_data.items():
            print(f"  📅 {month_key}: {len(df)} transactions")
            if len(df) > 0:
                print(f"    Sample data: {df.head(2).to_dict('records')}")
    else:
        print("❌ No budget files found!")

if __name__ == "__main__":
    test_data_loading()
