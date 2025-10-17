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
from utils.view_sheets import display_monthly_sheet, display_annual_summary
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
        'template_file': 'TEMPLATE_年開銷表.xlsx',
        'auto_create': True
    })
    
    # Check/create annual file
    budget_file = annual_mgr.get_active_budget_file()
    
    print(f"\n✅ 系統準備完成! Active budget: {os.path.basename(budget_file)}\n")
    
    return orchestrator, merger, annual_mgr

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

def view_budget_workflow():
    """View 2025年開銷表（NT） with month navigation"""
    console = Console()
    while True:
        print("\n📊 查看 2025 年預算表 (VIEW 2025 BUDGET)\n")
        print("="*100 + "\n")
        
        months = ['一月', '二月', '三月', '四月', '五月', '六月', 
                 '七月', '八月', '九月', '十月', '十一月', '十二月']
        
        print("月份選擇 (Select Month):\n")
        for i, month in enumerate(months, 1):
            console.print(f"   [[green]{i:2d}[/green]] {month}")
        
        console.print(f"\n   [[green]13[/green]] 📊 年度總覽 (Year Summary)")
        console.print(f"   [[green] x[/green]] 返回 (Back)")
        
        print("\n" + "="*100)
        choice = input("\n選擇 (Choose): ").strip()
        
        if choice == 'x':
            return
        elif choice in [str(i) for i in range(1, 13)]:
            month_num = int(choice)
            months = ['一月', '二月', '三月', '四月', '五月', '六月', 
                     '七月', '八月', '九月', '十月', '十一月', '十二月']
            sheet_name = months[month_num - 1]
            
            print("\n" + "="*100)
            print(f"  📄 {sheet_name} (MONTH {month_num})".center(100))
            print("="*100 + "\n")
            
            display_monthly_sheet(sheet_name)
            
            print("\n" + "="*100 + "\n")
        elif choice == '13':
            print("\n" + "="*100)
            print("  📊 年度總覽 (ANNUAL SUMMARY)".center(100))
            print("="*100)
            
            display_annual_summary()
            
            print("\n" + "="*100 + "\n")
        
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

def budget_chat_workflow(orchestrator, annual_mgr):
    """Enhanced budget chat with visual capabilities"""
    print_header()
    print("💬 預算分析對話 (BUDGET CHAT & INSIGHTS)\n")
    print("="*100 + "\n")
    
    # Attempt to load enhanced insights module
    enhanced_mode = False
    chat_module = None
    ai_chat = None
    
    try:
        from core.module_registry import registry
        from modules.insights.ai_chat import AIChat
        
        chat_module = registry.get_module('BudgetChat', config={
            'budget_file': annual_mgr.get_active_budget_file()
        })
        chat_module.set_orchestrator(orchestrator)
        
        # Initialize AI Chat controller (text-only mode)
        ai_chat = AIChat(
            data_loader=chat_module.data_loader,
            orchestrator=orchestrator,
            context_manager=chat_module.context_manager,
            insight_generator=chat_module.insight_generator,
            trend_analyzer=chat_module.trend_analyzer
        )
        
        enhanced_mode = True
        print("✅ Enhanced insights mode activated (with AI Chat!)\n")
    except Exception as e:
        print("⚠️  Enhanced insights module not available")
        print(f"   Using basic chat mode (Reason: {e})\n")
        enhanced_mode = False
    
    # Get available data
    if enhanced_mode:
        available_months = list(chat_module.data_loader.load_all_data().keys())
        stats = chat_module.data_loader.get_summary_stats()
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
            console.print("   [green]1. 支出查詢 (Spending Queries):[/green]")
            print("      • 「七月花了多少？」/ \"How much in July?\"")
            print("      • 「七月的伙食費是多少？」/ \"How much food in July?\"")
            print("      • 「總支出是多少？」/ \"What's the total spending?\"")
            print("      • 「平均每月花費多少？」/ \"What's the average monthly spending?\"")
            print("")
            console.print("   [green]2. 比較分析 (Comparisons):[/green]")
            print("      • 「比較七月和八月」/ \"Compare July and August\"")
            print("      • 「七月跟八月差多少？」/ \"What's the difference between July and August?\"")
            print("")
            console.print("   [green]3. 趨勢分析 (Trend Analysis):[/green]")
            print("      • 「伙食費的趨勢如何？」/ \"What's the food spending trend?\"")
            print("      • 「交通費有什麼變化？」/ \"How is transportation cost changing?\"")
            print("")
            console.print("   [green]4. 預測 (Forecasts):[/green]")
            print("      • 「預測下個月支出」/ \"Forecast next month\"")
            print("      • 「預測下個月的伙食費」/ \"Predict next month's food spending\"")
            print("")
            console.print("   [green]5. 深入洞察 (Insights & Reasoning):[/green]")
            print("      • 「為什麼七月支出增加？」/ \"Why did spending increase in July?\"")
            print("      • 「解釋伙食費的變化」/ \"Explain the food cost changes\"")
            print("")
            console.print("   [green]6. 建議與優化 (Advice & Optimization):[/green]")
            print("      • 「我應該如何減少支出？」/ \"How should I reduce spending?\"")
            print("      • 「哪裡可以節省？」/ \"Where can I save money?\"")
            print("      • 「建議如何優化預算」/ \"Recommend budget optimizations\"")
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
                    if enhanced_mode and ai_chat:
                        # Use new AI Chat system with all smart features
                        answer = ai_chat.answer_question(question)
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
                print("\n⚠️  視覺化分析需要 enhanced insights 模組")
                input("按 Enter 繼續...")
                continue
            
            from modules.insights.chat_menus import visual_analysis_menu
            visual_analysis_menu(chat_module, available_months, categories)
    
    # Return directly to main menu (no extra Enter needed)

def system_tools():
    """System tools and settings"""
    console = Console()
    print_header()
    print("⚙️  系統工具 (SYSTEM TOOLS)\n")
    print("="*100 + "\n")
    
    console.print("   [[green]1[/green]] 查看模組狀態 (View Module Status)")
    console.print("   [[green]2[/green]] 查看 LLM 設定 (View LLM Config)")
    console.print("   [[green]3[/green]] 測試 OneDrive 連接 (Test OneDrive)")
    console.print("   [[green]4[/green]] 重新載入模組 (Reload Module)")
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
    
    elif choice == 'x':
        return  # Return directly without extra Enter
    
    # Only wait for Enter if user performed an action
    if choice != 'x':
        input("\n按 Enter 返回...")

def main():
    """Main program loop"""
    # Initialize
    orchestrator, merger, annual_mgr = initialize_system()
    
    if not orchestrator:
        print("\n❌ System initialization failed")
        return
    
    # Show header once at startup
    print_header()
    
    # Main menu loop
    while True:
        choice = main_menu()
        
        if choice == '1':
            view_budget_workflow()
        elif choice == '2':
            update_monthly_workflow(merger, annual_mgr)
        elif choice == '3':
            budget_chat_workflow(orchestrator, annual_mgr)
        elif choice == '4':
            system_tools()
        elif choice == 'x':
            print("\n👋 再見! Goodbye!\n")
            sys.exit(0)
        else:
            input("\n❌ 無效選擇 (Invalid choice). Press Enter...")

if __name__ == "__main__":
    main()

