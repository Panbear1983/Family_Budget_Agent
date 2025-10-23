#!/usr/bin/env python3
"""
Family Budget Agent v2.0 - Main Control Center
Simplified, dictionary-driven, dual-LLM collaboration
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import LLMOrchestrator
from core.module_registry import registry
from modules.data import SimpleCategorizer, MonthlyMerger, AnnualManager
import config
from rich.console import Console

# Import utility functions
from utils.view_sheets import display_monthly_sheet, display_monthly_sheet_from_file, display_annual_summary
from utils.edit_cells import main as edit_cells_main

def print_header():
    print("\n" + "="*100)
    print("  💰 家庭預算管理系統 - FAMILY BUDGET AGENT v2.0".center(100))
    print("="*100 + "\n")

def initialize_system():
    """Initialize the modular system"""
    print("🔧 系統初始化中 (Initializing system)...\n")
    
    # Discover modules
    print("📦 載入模組 (Loading modules)...")
    registry.auto_discover('modules')
    
    # Initialize LLM orchestrator
    print("🤖 初始化 LLM 引擎 (Initializing LLM engines)...")
    orchestrator = LLMOrchestrator()
    
    if not orchestrator.initialize():
        print("❌ LLM initialization failed")
        return None, None, None
    
    # Initialize data modules
    print("📊 載入資料模組 (Loading data modules)...")
    
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
    
    # Get multi-year files for read-only features (current + previous year)
    budget_files = annual_mgr.get_multi_year_files(num_years=2)
    
    print(f"\n✅ 系統準備完成!")
    print(f"   Current year: {os.path.basename(budget_file)}")
    print(f"   Multi-year analysis: {len(budget_files)} year(s) loaded\n")
    
    return orchestrator, merger, annual_mgr, budget_files

def main_menu():
    """Display main menu"""
    console = Console()
    print("="*100)
    print("\n📋 主選單 MAIN MENU:\n")
    console.print("   [[green]1[/green]] 📊 查看 2025 年預算表 (View 2025 Budget)")
    console.print("   [[green]2[/green]] 📥 更新每月預算 (Update Monthly Budget - Me + Wife)")
    console.print("   [[green]3[/green]] 💬 預算分析對話 (Budget Chat & Insights)")
    console.print("   [[green]4[/green]] ⚙️  系統工具 (System Tools)")
    console.print("   [[green]x[/green]] 退出 (Exit)")
    print("\n" + "="*100)
    
    choice = input("\n👉 請選擇 (Choose): ").strip()
    return choice

def view_budget_workflow(budget_files):
    """View budget with multi-year support (2025+)"""
    console = Console()
    
    # Detect available years from files (2025 onwards only)
    available_years = []
    for file in budget_files:
        year = os.path.basename(file)[:4]
        if year.isdigit():
            year_int = int(year)
            if year_int >= 2025:  # Filter: Only 2025 and later
                available_years.append(year_int)
    available_years.sort()
    
    # If no years available after filtering, show message
    if not available_years:
        print("\n⚠️  沒有可用的預算年份 (No budget years available for 2025+)")
        input("\n按 Enter 返回...")
        return
    
    while True:
        print("\n📊 查看預算表 (VIEW BUDGET)\n")
        print("="*100 + "\n")
        
        months = ['一月', '二月', '三月', '四月', '五月', '六月', 
                 '七月', '八月', '九月', '十月', '十一月', '十二月']
        
        option_num = 1
        month_map = {}  # Map option number to (year, month, file_path)
        
        # Show months grouped by year
        for year in available_years:
            console.print(f"\n   [yellow]─── {year} 年 ───[/yellow]")
            
            # Find file for this year
            year_file = next((f for f in budget_files if f"{year}年" in f), None)
            
            for month in months:
                console.print(f"   [[green]{option_num:2d}[/green]] {year}-{month}")
                month_map[str(option_num)] = (year, month, year_file)
                option_num += 1
        
        console.print(f"\n   [[green]{option_num}[/green]] 📊 多年度總覽 (Multi-Year Summary)")
        summary_option = str(option_num)
        console.print(f"   [[green] x[/green]] 返回 (Back)")
        
        print("\n" + "="*100)
        choice = input("\n選擇 (Choose): ").strip()
        
        if choice == 'x':
            return
        elif choice in month_map:
            year, month, file_path = month_map[choice]
            
            if file_path and os.path.exists(file_path):
                print("\n" + "="*100)
                print(f"  📄 {year}-{month}".center(100))
                print("="*100 + "\n")
                
                display_monthly_sheet_from_file(file_path, month)
                
                print("\n" + "="*100 + "\n")
            else:
                print(f"\n❌ 文件不存在: {year}年開銷表")
                input("\n按 Enter 繼續...")
        
        elif choice == summary_option:
            print("\n" + "="*100)
            print("  📊 多年度總覽 (MULTI-YEAR SUMMARY)".center(100))
            print("="*100 + "\n")
            
            # Show summary for each available year (2025+ only)
            for year_file in budget_files:
                year = os.path.basename(year_file)[:4]
                if year.isdigit() and int(year) >= 2025:  # Only 2025+
                    console.print(f"\n[bold blue]{year} 年度總覽:[/bold blue]")
                    display_annual_summary(year_file)  # Pass file path
                    print()
            
            print("="*100 + "\n")
        
        # No input() needed - loop continues automatically

def merge_budget_workflow(merger, annual_mgr):
    """Merge monthly budget sheets from Peter and Dolly"""
    import os
    import shutil
    import pandas as pd
    from datetime import datetime
    from core.module_registry import registry
    
    print("\n📊 合并家庭预算表 (MERGE FAMILY BUDGET SHEETS)\n")
    print("="*100 + "\n")
    
    # Step 1: Get file paths
    print("請輸入文件路徑 (Enter file paths):\n")
    peter_file = input("Peter's file: ").strip()
    dolly_file = input("Dolly's file: ").strip()
    
    # Validate files exist
    if not os.path.exists(peter_file):
        print(f"\n❌ 文件不存在: {peter_file}")
        input("\n按 Enter 返回...")
        return
    
    if not os.path.exists(dolly_file):
        print(f"\n❌ 文件不存在: {dolly_file}")
        input("\n按 Enter 返回...")
        return
    
    # Step 2: Select target month
    print("\n" + "="*100)
    print("\n選擇目標月份 (Select target month):\n")
    
    months = ['一月', '二月', '三月', '四月', '五月', '六月', 
             '七月', '八月', '九月', '十月', '十一月', '十二月']
    
    for i, month in enumerate(months, 1):
        print(f"   {i:2d}. {month}")
    
    print("\n" + "="*100)
    month_choice = input("\n選擇月份 (Choose month 1-12): ").strip()
    
    try:
        month_num = int(month_choice)
        if not 1 <= month_num <= 12:
            raise ValueError
        target_month = months[month_num - 1]
    except:
        print("\n❌ 無效月份 (Invalid month)")
        input("\n按 Enter 返回...")
        return
    
    # Step 3: Parse files using FileParser
    print(f"\n🔄 處理中... (Processing)...")
    
    try:
        parser = registry.get_module('FileParser')
        
        # Parse Peter's file
        peter_data = parser.execute(peter_file, person='peter')
        
        # Parse Dolly's file
        dolly_data = parser.execute(dolly_file, person='wife')
        
        # Step 4: Merge data (categorize, combine, deduplicate, show preview)
        budget_file = annual_mgr.get_active_budget_file()
        
        success, count, merged_df = merger.execute_from_dataframes(
            peter_data, dolly_data, target_month, budget_file
        )
        
        if not success:
            print(f"\n❌ 合并失败: {merged_df}")
            input("\n按 Enter 返回...")
            return
        
        # Step 5: Confirm before applying
        print("\n" + "="*100)
        confirm = input(f"\n✅ Write {count} transactions to {target_month}? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("\n❌ Cancelled. No changes made.")
            input("\n按 Enter 返回...")
            return
        
        # Step 6: Create backup and write
        print(f"\n🔄 Writing to {target_month}...")
        
        backup_file = budget_file.replace('.xlsx', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        shutil.copy2(budget_file, backup_file)
        print(f"  💾 Backup: {os.path.basename(backup_file)}")
        
        # Apply to budget file
        write_success = merger.append_to_month_tab(merged_df, target_month, budget_file)
        
        if write_success:
            print(f"\n✅ Success! {count} transactions written to {target_month}")
            print(f"☁️  OneDrive will auto-sync changes")
            print(f"\n💡 Backup saved: {backup_file}")
        else:
            print("\n❌ Write failed, restoring backup...")
            shutil.copy2(backup_file, budget_file)
            print("✅ Restored from backup")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    input("\n按 Enter 返回...")

def update_monthly_workflow(merger, annual_mgr):
    """Update monthly budget - submenu for different update modes"""
    console = Console()
    while True:
        print("\n📥 更新每月預算 (UPDATE MONTHLY BUDGET)\n")
        print("="*100 + "\n")
        
        console.print("   [[green]1[/green]] ✏️  逐格编辑 (Edit Cell-by-Cell)")
        console.print("   [[green]2[/green]] 📊 合并家庭预算表 (Merge Family Budget Sheets)")
        console.print("   [[green]x[/green]] 返回 (Back)")
        
        print("\n" + "="*100)
        choice = input("\n選擇 (Choose): ").strip()
        
        if choice == '1':
            # Cell-by-cell editing
            edit_cells_main()
        elif choice == '2':
            # Merge family budget sheets
            merge_budget_workflow(merger, annual_mgr)
        elif choice == 'x':
            return
        else:
            input("\n❌ 無效選擇 (Invalid choice). Press Enter...")

def budget_chat_workflow(orchestrator, annual_mgr, budget_files):
    """Simplified budget chat using Qwen for function routing"""
    print_header()
    print("💬 預算分析對話 (BUDGET CHAT & INSIGHTS)\n")
    print("="*100 + "\n")
    
    # Load simplified Qwen-based chat system
    enhanced_mode = False
    qwen_chat = None
    
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
        
        enhanced_mode = True
        
        # Show year range
        min_year, max_year = multi_data_loader.get_year_range()
        if min_year and max_year:
            print(f"✅ Qwen Chat mode (Multi-Year: {min_year}-{max_year})\n")
        else:
            print("✅ Qwen Chat mode activated - Natural language routing to existing functions\n")
            
    except Exception as e:
        print("⚠️  Qwen Chat module not available")
        print(f"   Using basic chat mode (Reason: {e})\n")
        import traceback
        traceback.print_exc()
        enhanced_mode = False
    
    # Get available data (filter to 2025+ only)
    if enhanced_mode:
        all_months = list(multi_data_loader.load_all_data().keys())
        # Filter: Only show months from 2025 onwards
        available_months = [m for m in all_months if not m.startswith('2024')]
        stats = multi_data_loader.get_summary_stats()
        categories = list(stats['by_category'].keys()) if stats else ['伙食费', '交通费', '休闲/娱乐']
    else:
        available_months = ['一月', '二月', '三月', '四月', '五月', '六月', '七月']
        categories = []
    
    console = Console()
    
    while True:
        print("\n選擇模式 (Choose mode):")
        print("─" * 100)
        
        console.print("   [[green]1[/green]] 🤖 智能問答 (AI Chat) - Natural language Q&A")
        console.print("   [[green]2[/green]] 📊 視覺化分析 (Visual Analysis) - Tables & Charts")
        console.print("   [[green]x[/green]] 返回 (Back)")
        
        print("─" * 100)
        mode = input("\n選擇 (Choose): ").strip()
        
        if mode == 'x':
            break
        
        elif mode == '1':
            # AI Chat mode
            print("\n🤖 智能問答模式 (AI Chat Mode)")
            print("─" * 100)
            print("\n✅ 我能回答的問題類型 (What I Can Answer):\n")
            console.print("   [green]1. 📊 數據查詢 (Data Queries):[/green]")
            print("      • 「顯示七月數據」/ \"Show July data\"")
            print("      • 「七月分類統計」/ \"July category breakdown\"")
            print("      • 「年度總覽」/ \"Show yearly summary\"")
            print("")
            console.print("   [green]2. 📈 視覺化分析 (Visualization):[/green]")
            print("      • 「七月圓餅圖」/ \"July pie chart\"")
            print("      • 「月度趨勢圖」/ \"Monthly trend chart\"")
            print("      • 「分類柱狀圖」/ \"Category bar chart\"")
            print("")
            console.print("   [green]3. ⚖️  比較分析 (Comparisons):[/green]")
            print("      • 「比較七月和八月」/ \"Compare July and August\"")
            print("      • 「顯示對比圖表」/ \"Show comparison chart\"")
            print("")
            console.print("   [green]4. 📈 趨勢分析 (Trend Analysis):[/green]")
            print("      • 「伙食費趨勢」/ \"Food spending trend\"")
            print("      • 「顯示趨勢圖表」/ \"Show trend chart\"")
            print("")
            print("💡 提示: 使用自然語言描述您想要的分析，例如:")
            print("   • \"顯示七月的支出數據\"")
            print("   • \"比較七月和八月的花費\"")
            print("   • \"伙食費的趨勢如何\"")
            print("   • \"顯示年度總覽表格\"")
            print("")
            console.print("   [yellow]📊 需要圖表？ (Need Charts?):[/yellow]")
            print("      返回主選單選擇 [2] 視覺化分析")
            print("      Return to main menu and select [2] Visual Analysis")
            print("")
            print("💡 請用簡單、具體的問題 (Keep questions simple & specific)")
            print("\n輸入 'x' 或 'exit' 返回選單")
            print("─" * 100)
            
            while True:
                question = input("\n您有屁快放(Spit it Dummie): ").strip()
                
                if question.lower() in ['exit', 'x', '返回']:
                    break
                
                if not question:
                    continue
                
                print("🤔 AI 思考中...", end='', flush=True)
                
                try:
                    if enhanced_mode and qwen_chat:
                        # Use simplified Qwen Chat system for function routing
                        answer = qwen_chat.answer_question(question)
                    else:
                        # Fallback to basic mode
                        budget_data = {
                            'file': annual_mgr.get_active_budget_file(),
                            'year': 2025,
                            'months_with_data': available_months
                        }
                        answer = orchestrator.answer_question(question, budget_data)
                    
                    print(f"\r💡 助手: {answer}\n")
                except Exception as e:
                    print(f"\r❌ 錯誤: {e}\n")
                    import traceback
                    traceback.print_exc()
        
        elif mode == '2':
            # Visual analysis mode
            if not enhanced_mode:
                print("\n⚠️  視覺化分析需要 Qwen Chat 模組")
                input("按 Enter 繼續...")
                continue
            
            from modules.insights.chat_menus import visual_analysis_menu
            # Create a mock chat_module for compatibility
            class MockChatModule:
                def execute(self, function_name, *args):
                    # Route to function registry
                    if enhanced_mode and qwen_chat:
                        return qwen_chat.function_registry.execute_function(function_name, *args)
                    return f"Function {function_name} not available"
            
            mock_chat_module = MockChatModule()
            visual_analysis_menu(mock_chat_module, available_months, categories)
    
    # Return directly to main menu (no extra Enter needed)

def system_tools(annual_mgr):
    """System tools and settings"""
    console = Console()
    print_header()
    print("⚙️  系統工具 (SYSTEM TOOLS)\n")
    print("="*100 + "\n")
    
    console.print("   [[green]1[/green]] 查看模組狀態 (View Module Status)")
    console.print("   [[green]2[/green]] 查看 LLM 設定 (View LLM Config)")
    console.print("   [[green]3[/green]] 測試 OneDrive 連接 (Test OneDrive)")
    console.print("   [[green]4[/green]] 重新載入模組 (Reload Module)")
    console.print("   [[green]5[/green]] 🆕 創建下一年預算表 (Create Next Year Budget)")
    console.print("   [[green]x[/green]] 返回 (Back)")
    
    choice = input("\n選擇 (Choose): ").strip()
    
    if choice == '1':
        print("\n📦 模組狀態:")
        registry.list_modules()
    
    elif choice == '2':
        print(f"\n🤖 LLM 設定:")
        print(f"   Structured Tasks: {config.STRUCTURED_LLM}")
        print(f"   Reasoning Tasks: {config.REASONING_LLM}")
        print(f"\n💡 To change: Edit config.py")
    
    elif choice == '3':
        print("\n💡 OneDrive 連接測試 (OneDrive Connection Test)")
        print(f"📂 OneDrive 路徑: {config.ONEDRIVE_PATH}")
        if os.path.exists(config.ONEDRIVE_PATH):
            print("✅ OneDrive 路徑存在 (OneDrive path exists)")
        else:
            print("❌ OneDrive 路徑不存在 (OneDrive path not found)")
    
    elif choice == '4':
        module_name = input("Module name: ").strip()
        if module_name:
            registry.reload_module(module_name)
            print(f"✅ Reloaded {module_name}")
    
    elif choice == '5':
        create_next_year_budget(annual_mgr)
    
    elif choice == 'x':
        return  # Return directly without extra Enter
    
    # Only wait for Enter if user performed an action
    if choice != 'x':
        input("\n按 Enter 返回...")

def create_next_year_budget(annual_mgr):
    """Create next year's budget file from template"""
    from datetime import datetime
    
    current_year = datetime.now().year
    next_year = current_year + 1
    
    print(f"\n🆕 創建 {next_year} 年預算表 (Create {next_year} Budget File)")
    print("="*100 + "\n")
    
    # Check if next year file already exists
    next_year_file = annual_mgr.get_budget_file_path(next_year)
    
    if os.path.exists(next_year_file):
        print(f"⚠️  {next_year} 年預算表已存在!")
        print(f"   檔案: {os.path.basename(next_year_file)}")
        
        overwrite = input(f"\n是否重新創建? (覆蓋現有檔案) [y/N]: ").strip().lower()
        if overwrite != 'y':
            print("\n❌ 取消操作")
            return
        
        # Create backup before overwriting
        import shutil
        backup_file = next_year_file.replace('.xlsx', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        shutil.copy2(next_year_file, backup_file)
        print(f"  💾 已備份至: {os.path.basename(backup_file)}")
    
    # Check if template exists
    template_path = os.path.join(config.ONEDRIVE_PATH, annual_mgr.template_file)
    
    if not os.path.exists(template_path):
        print(f"❌ 模板檔案不存在: {annual_mgr.template_file}")
        print(f"   預期位置: {template_path}")
        print("\n💡 請確保模板檔案存在於 OneDrive 目錄中")
        return
    
    try:
        print(f"\n🔄 從模板創建 {next_year} 年預算表...")
        print(f"   模板: {annual_mgr.template_file}")
        
        # Create the new year file
        created_file = annual_mgr.create_annual_budget(next_year)
        
        print(f"\n✅ 成功! {next_year} 年預算表已創建")
        print(f"   檔案: {os.path.basename(created_file)}")
        print(f"   路徑: {created_file}")
        print(f"\n☁️  OneDrive 將自動同步此檔案")
        
    except Exception as e:
        print(f"\n❌ 創建失敗: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main program loop"""
    # Initialize
    orchestrator, merger, annual_mgr, budget_files = initialize_system()
    
    if not orchestrator:
        print("\n❌ System initialization failed")
        return
    
    # Show header once at startup
    print_header()
    
    # Main menu loop
    while True:
        choice = main_menu()
        
        if choice == '1':
            view_budget_workflow(budget_files)
        elif choice == '2':
            update_monthly_workflow(merger, annual_mgr)
        elif choice == '3':
            budget_chat_workflow(orchestrator, annual_mgr, budget_files)
        elif choice == '4':
            system_tools(annual_mgr)
        elif choice == 'x':
            print("\n👋 再見魯蛇🐍! GoodbyeeeeEEEeeee111111...!\n")
            sys.exit(0)
        else:
            input("\n❌ 無效選擇 (Invalid choice). Press Enter...")

if __name__ == "__main__":
    main()

