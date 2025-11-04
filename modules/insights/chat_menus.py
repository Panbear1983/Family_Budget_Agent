"""
Chat Menus - Helper functions for budget chat workflow
"""

from rich.console import Console
from typing import List

console = Console()

def select_month(available_months: List[str]) -> str:
    """Helper to select a month"""
    if not available_months:
        raise ValueError("沒有可用的月份數據 (No month data available)")
    
    print("\n可用月份 (Available months):")
    for i, month in enumerate(available_months, 1):
        print(f"   {i}. {month}")
    print(f"   x. 返回主選單 (Back to Main Menu)")
    
    choice = input(f"\n選擇月份 (1-{len(available_months)}, x) 或輸入月份名稱: ").strip().lower()
    
    if choice == 'x':
        raise ValueError("返回主選單")
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(available_months):
            return available_months[idx]
        else:
            print(f"⚠️  Invalid number (1-{len(available_months)} only), using {available_months[0]}")
            return available_months[0]
    elif choice in available_months:
        return choice
    else:
        print(f"⚠️  '{choice}' not found, using {available_months[0]}")
        return available_months[0]

def select_two_months(available_months: List[str]) -> tuple:
    """Helper to select two months"""
    if not available_months:
        raise ValueError("沒有可用的月份數據 (No month data available)")
    
    if len(available_months) < 2:
        raise ValueError("需要至少兩個月的數據才能對比 (Need at least 2 months for comparison)")
    
    print("\n可用月份 (Available months):")
    for i, month in enumerate(available_months, 1):
        print(f"   {i}. {month}")
    
    month1_input = input("\n第一個月 (First month): ").strip()
    month2_input = input("第二個月 (Second month): ").strip()
    
    # Parse month1 with validation
    if month1_input.isdigit():
        idx1 = int(month1_input) - 1
        if 0 <= idx1 < len(available_months):
            month1 = available_months[idx1]
        else:
            print(f"⚠️  Invalid number, using {available_months[0]}")
            month1 = available_months[0]
    else:
        month1 = month1_input if month1_input in available_months else available_months[0]
    
    # Parse month2 with validation
    if month2_input.isdigit():
        idx2 = int(month2_input) - 1
        if 0 <= idx2 < len(available_months):
            month2 = available_months[idx2]
        else:
            print(f"⚠️  Invalid number, using {available_months[1]}")
            month2 = available_months[1]
    else:
        month2 = month2_input if month2_input in available_months else available_months[1]
    
    return month1, month2

def select_category(categories: List[str]) -> str:
    """Helper to select a category"""
    if not categories:
        raise ValueError("沒有可用的分類數據 (No category data available)")
    
    print("\n可用分類 (Available categories):")
    for i, cat in enumerate(categories, 1):
        print(f"   {i}. {cat}")
    
    choice = input(f"\n選擇分類 (1-{len(categories)}): ").strip()
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(categories):
            return categories[idx]
        else:
            print(f"⚠️  Invalid number (1-{len(categories)} only), using {categories[0]}")
            return categories[0]
    elif choice in categories:
        return choice
    else:
        print(f"⚠️  '{choice}' not found, using {categories[0]}")
        return categories[0]

def visual_analysis_menu(chat_module, available_months: List[str], categories: List[str]) -> None:
    """Visual analysis submenu"""
    # Check if we have data
    if not available_months:
        print("\n❌ 錯誤: 沒有找到預算數據")
        print("請確認 Excel 檔案存在並包含月份工作表 (一月, 二月, 等等)")
        input("\n按 Enter 返回...")
        return
    
    while True:
        print("\n📊 視覺化分析 (VISUAL ANALYSIS)")
        print("─" * 100)
        print(f"📅 可用月份: {', '.join(available_months)}")
        print("─" * 100)
        
        console.print("   [[green]1[/green]] 📅 單月分析 (Monthly Analysis) - Tables + Charts")
        console.print("   [[green]2[/green]] ⚖️  雙月對比 (Compare Months) - Tables + Charts")
        console.print("   [[green]3[/green]] 📊 年度總覽 (Yearly Summary) - Tables + Charts")
        console.print("   [[green]4[/green]] 📈 趨勢分析 (Trend Analysis) - Tables + Charts")
        console.print("   [[green]5[/green]] 📋 完整月報表 (Full Monthly View) - Excel Sheet View")
        console.print("   [[green]x[/green]] 返回 (Back)")
        
        print("─" * 100)
        choice = input("\n選擇 (Choose): ").strip()
        
        if choice == 'x':
            break
        
        elif choice == '1':
            # Monthly analysis
            try:
                month = select_month(available_months)
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\n按 Enter 繼續...")
                continue
            
            print(f"\n📊 {month} 分析...")
            
            # Show category table
            chat_module.execute('show_category_table', month)
            
            # Show transaction details automatically (no y/n question)
            print()
            chat_module.execute('show_monthly_table', month)
            print("\n✅ 交易明細已顯示")
            
            # Go directly back to month selection menu (no Enter continue)
            continue
        
        elif choice == '5':
            # Full monthly view (Excel sheet view)
            try:
                month = select_month(available_months)
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\n按 Enter 繼續...")
                continue
            
            print(f"\n📋 {month} 完整月報表...")
            
            # Show full Excel sheet view
            try:
                chat_module.execute('show_full_monthly_view', month)
                print("\n✅ 完整月報表已顯示")
            except Exception as e:
                print(f"❌ 顯示完整月報表失敗: {e}")
                import traceback
                traceback.print_exc()
            
            input("\n按 Enter 繼續...")
            continue
        
        elif choice == '2':
            # Month comparison
            try:
                month1, month2 = select_two_months(available_months)
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\n按 Enter 繼續...")
                continue
            
            print(f"\n⚖️  對比 {month1} vs {month2}...")
            
            # Show comparison table
            try:
                result = chat_module.execute('show_comparison_table', month1, month2)
                print(result if result else "✅ 對比表格已顯示")
            except Exception as e:
                print(f"❌ 對比表格顯示失敗: {e}")
            
            # Go directly back to visual analysis menu - no useless chart options
            continue
        
        elif choice == '3':
            # Yearly summary
            print("\n📊 生成年度總覽...")
            
            # Show tables
            try:
                result = chat_module.execute('show_yearly_table')
                print(result if result else "✅ 年度總覽表格已顯示")
            except Exception as e:
                print(f"❌ 年度總覽表格顯示失敗: {e}")
            
            # Ask for graphs - single selection
            print("\n圖表選項:")
            print("  1. 月度趨勢圖 (Monthly Trend)")
            print("  2. 分類圓餅圖 (Category Pie)")
            print("  3. 堆疊面積圖 (Stacked Area)")
            print("  4. 全部顯示 (Show All)")
            print("  5. 跳過 (Skip)")
            print("  x. 返回主選單 (Back to Main Menu)")
            
            graph_choice = input("選擇 (1-5, x): ").strip().lower()
            
            if graph_choice == 'x':
                return  # Go back to main menu
            
            if graph_choice == '5':
                pass  # Skip graphs, continue to main visual menu
            
            # Show selected graphs
            if graph_choice in ['1', '4']:
                print("\n1=Terminal, 2=GUI: ", end='')
                mode = input().strip()
                if mode == '1':
                    chat_module.execute('plot_terminal', 'monthly_bar')
                else:
                    chat_module.execute('plot_gui', 'monthly_bar')
            
            if graph_choice in ['2', '4']:
                chat_module.execute('plot_gui', 'donut')
            
            if graph_choice in ['3', '4']:
                chat_module.execute('plot_gui', 'stacked_area')
            
            # Return to main visual menu after showing graphs
        
        elif choice == '4':
            # Trend analysis
            try:
                category = select_category(categories)
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\n按 Enter 繼續...")
                continue
            
            print(f"\n📈 分析 {category} 趨勢...")
            
            # Show trend table
            chat_module.execute('show_trend_table', category)
            
            # Ask for graph
            show_graph = input("\n顯示趨勢圖? (1=Terminal, 2=GUI, n=No): ").strip()
            
            if show_graph == '1':
                chat_module.execute('plot_terminal', 'trend_line', category)
            elif show_graph == '2':
                chat_module.execute('plot_gui', 'trend_line', category)
            
            input("\n按 Enter 繼續...")

def chart_options_menu(chat_module, available_months: List[str], categories: List[str]) -> None:
    """Chart options submenu - standalone chart selection"""
    # Check if we have data
    if not available_months:
        print("\n❌ 錯誤: 沒有找到預算數據")
        print("請確認 Excel 檔案存在並包含月份工作表 (一月, 二月, 等等)")
        input("\n按 Enter 返回...")
        return
    
    while True:
        print("\n📊 圖表選項 (CHART OPTIONS)")
        print("─" * 100)
        print(f"📅 可用月份: {', '.join(available_months)}")
        print("─" * 100)
        
        console.print("   [[green]1[/green]] 📈 月度趨勢圖 (Monthly Trend Chart)")
        console.print("   [[green]2[/green]] 🥧 分類圓餅圖 (Category Pie Chart)")
        console.print("   [[green]3[/green]] 📊 堆疊面積圖 (Stacked Area Chart)")
        console.print("   [[green]4[/green]] 📉 趨勢線圖 (Trend Line Chart)")
        console.print("   [[green]5[/green]] 📊 比較柱狀圖 (Comparison Bar Chart)")
        console.print("   [[green]6[/green]] 🍩 甜甜圈圖 (Donut Chart)")
        console.print("   [[green]7[/green]] 📊 水平柱狀圖 (Horizontal Bar Chart)")
        console.print("   [[green]8[/green]] 📈 堆疊趨勢圖 (Stacked Trend Chart)")
        console.print("   [[green]9[/green]] 🎯 全部顯示 (Show All Charts)")
        console.print("   [[green]x[/green]] 返回 (Back)")
        
        print("─" * 100)
        choice = input("\n選擇圖表類型 (Choose chart type): ").strip()
        
        if choice == 'x':
            break
        
        elif choice == '1':
            # Monthly trend chart
            print("\n📈 月度趨勢圖選項:")
            print("  1. 終端模式 (Terminal Mode)")
            print("  2. 圖形模式 (GUI Mode)")
            mode = input("選擇模式 (1-2): ").strip()
            
            if mode == '1':
                chat_module.execute('plot_terminal', 'monthly_bar')
            else:
                chat_module.execute('plot_gui', 'monthly_bar')
        
        elif choice == '2':
            # Category pie chart
            try:
                month = select_month(available_months)
                chat_module.execute('plot_gui', 'pie', month)
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\n按 Enter 繼續...")
                continue
        
        elif choice == '3':
            # Stacked area chart
            chat_module.execute('plot_gui', 'stacked_area')
        
        elif choice == '4':
            # Trend line chart
            try:
                category = select_category(categories)
                print("\n📈 趨勢線圖選項:")
                print("  1. 終端模式 (Terminal Mode)")
                print("  2. 圖形模式 (GUI Mode)")
                mode = input("選擇模式 (1-2): ").strip()
                
                if mode == '1':
                    chat_module.execute('plot_terminal', 'trend_line', category)
                else:
                    chat_module.execute('plot_gui', 'trend_line', category)
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\n按 Enter 繼續...")
                continue
        
        elif choice == '5':
            # Comparison bar chart
            try:
                month1, month2 = select_two_months(available_months)
                print("\n📊 比較柱狀圖選項:")
                print("  1. 終端模式 (Terminal Mode)")
                print("  2. 圖形模式 (GUI Mode)")
                mode = input("選擇模式 (1-2): ").strip()
                
                if mode == '1':
                    chat_module.execute('plot_terminal', 'comparison', month1, month2)
                else:
                    chat_module.execute('plot_gui', 'comparison', month1, month2)
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\n按 Enter 繼續...")
                continue
        
        elif choice == '6':
            # Donut chart
            chat_module.execute('plot_gui', 'donut')
        
        elif choice == '7':
            # Horizontal bar chart
            try:
                month = select_month(available_months)
                chat_module.execute('plot_terminal', 'category_bar', month)
            except ValueError as e:
                print(f"\n❌ {e}")
                input("\n按 Enter 繼續...")
                continue
        
        elif choice == '8':
            # Stacked trend chart
            chat_module.execute('plot_terminal', 'stacked_trend')
        
        elif choice == '9':
            # Show all charts
            print("\n🎯 顯示所有圖表...")
            print("這將顯示多個圖表，請稍候...")
            
            # Monthly trend
            chat_module.execute('plot_gui', 'monthly_bar')
            input("\n按 Enter 繼續下一個圖表...")
            
            # Category pie
            month = available_months[0]  # Use first available month
            chat_module.execute('plot_gui', 'pie', month)
            input("\n按 Enter 繼續下一個圖表...")
            
            # Donut chart
            chat_module.execute('plot_gui', 'donut')
            input("\n按 Enter 繼續下一個圖表...")
            
            # Stacked area
            chat_module.execute('plot_gui', 'stacked_area')
            input("\n按 Enter 繼續下一個圖表...")
            
            # Trend line
            category = categories[0] if categories else '伙食费'
            chat_module.execute('plot_gui', 'trend_line', category)
        
        input("\n按 Enter 繼續...")

