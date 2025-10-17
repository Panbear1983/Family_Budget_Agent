#!/usr/bin/env python3
"""
View Budget Sheets - Monthly and Annual Views
Displays budget data with rich formatting
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from rich.console import Console
from rich.table import Table
import config

EXCEL_FILE_PATH = config.BUDGET_PATH

def display_monthly_sheet(sheet_name):
    """Display a monthly sheet with rich formatting"""
    console = Console()
    
    # Read the sheet
    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet_name, header=None)
    
    # Find header row (contains "日期：", "星期:")
    header_row_idx = None
    for idx, row in df.iterrows():
        if '日期' in str(row.iloc[0]) and '星期' in str(row.iloc[1]):
            header_row_idx = idx
            break
    
    if header_row_idx is None:
        console.print(f"[red]Error: Could not find header row in sheet '{sheet_name}'[/red]")
        return
    
    # Create rich table with vertical dividers and border
    from rich import box as rich_box
    
    table = Table(show_header=True, header_style="bold blue", show_lines=False, box=rich_box.SQUARE, padding=(0, 1))
    
    # Add columns with compact widths and alignment
    table.add_column("日期", width=12, justify="left")
    table.add_column("星期", width=6, justify="center")
    table.add_column("交通費", width=8, justify="right")
    table.add_column("伙食費", width=8, justify="right")
    table.add_column("休閒/娛樂", width=10, justify="right")
    table.add_column("家務", width=6, justify="right")
    table.add_column("阿幫", width=6, justify="right")
    table.add_column("其它", width=6, justify="right")
    table.add_column("總計", width=10, justify="right", style="green")
    
    # Track monthly grand total from 單項總額 row
    monthly_grand_total = None
    
    # Collect all rows first to determine section breaks
    rows_to_add = []
    
    # Process rows starting from header row + 1
    for idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[idx]
        
        # Stop at '年度明細表' section
        if '年度明細表' in str(row.iloc[0]):
            break
        
        # Skip completely empty rows
        is_empty = True
        for i in range(len(row)):
            if pd.notna(row.iloc[i]) and str(row.iloc[i]).strip() != '':
                is_empty = False
                break
        if is_empty:
            continue
        
        # Format row data
        date_cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
        day_cell = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ''
        
        # Skip rows without a date (except summary rows like 周總額, 單項總額)
        if not date_cell or date_cell == 'nan':
            continue
        if '2025-' not in date_cell and '周總額' not in date_cell and '單項總額' not in date_cell:
            continue
        
        # Skip '月剩余額:' label row (value captured separately)
        if '月剩余額' in date_cell:
            continue
        
        # Clean up date format - take only the date part, not time
        if '2025-' in date_cell and '00:00:00' in date_cell:
            date_cell = date_cell.split()[0]
        
        # Format expense columns (no thousand separators for daily entries)
        expense_cols = []
        for col_idx in range(3, 9):  # Columns 3-8 are expense categories
            if col_idx < len(row) and pd.notna(row.iloc[col_idx]) and row.iloc[col_idx] != 0:
                expense_cols.append(str(int(row.iloc[col_idx])))
            else:
                expense_cols.append('')
        
        # Format total column (with thousand separators) - show exactly what's in Excel
        total_cell = ''
        if len(row) > 9 and pd.notna(row.iloc[9]) and row.iloc[9] != 0:
            try:
                total_cell = f'{int(row.iloc[9]):,}'
            except (ValueError, TypeError):
                total_cell = str(row.iloc[9])
        else:
            total_cell = ''
        
        # Check if this is a summary row
        if '周總額' in date_cell:
            # Remove colon from 周總額
            date_cell = date_cell.replace('：', '').replace(':', '')
            
            # Calculate weekly totals by summing the week's data
            # Find the start of the week (previous 周總額 or header)
            week_start_idx = header_row_idx + 1
            for prev_idx in range(idx - 1, header_row_idx, -1):
                prev_row_val = str(df.iloc[prev_idx, 0])
                if '周總額' in prev_row_val:
                    week_start_idx = prev_idx + 1
                    break
            
            # Sum up the week's spending for each category
            week_totals = [0, 0, 0, 0, 0, 0]  # 6 expense categories
            for week_idx in range(week_start_idx, idx):
                week_row = df.iloc[week_idx]
                week_date = str(week_row.iloc[0])
                # Only sum rows with actual dates (2025-XX-XX)
                if '2025-' in week_date:
                    for col_idx in range(3, 9):
                        val = week_row.iloc[col_idx] if col_idx < len(week_row) else 0
                        if pd.notna(val) and val != 0:
                            week_totals[col_idx - 3] += val
            
            # Format weekly totals with thousand separators
            formatted_expenses = []
            for total in week_totals:
                if total > 0:
                    formatted_expenses.append(f'{int(total):,}')
                else:
                    formatted_expenses.append('')
            
            # Calculate grand total for the week
            week_grand_total = sum(week_totals)
            if week_grand_total > 0:
                total_cell = f'{int(week_grand_total):,}'
            else:
                total_cell = ''
            
            # Only show 周總額 row if there are actual numbers
            if week_grand_total > 0:
                rows_to_add.append({
                    'cells': [date_cell, day_cell, *formatted_expenses, total_cell],
                    'style': 'bold blue',
                    'type': 'weekly_total'
                })
            
        elif '單項總額' in date_cell:
            # Capture the grand total value for display after the table
            if len(row) > 10 and pd.notna(row.iloc[10]) and row.iloc[10] != 0:
                try:
                    monthly_grand_total = int(row.iloc[10])
                except (ValueError, TypeError):
                    monthly_grand_total = None
            
            # Show exactly what's in the Excel file (NO calculations)
            formatted_expenses = []
            for col_idx in range(3, 9):
                if col_idx < len(row) and pd.notna(row.iloc[col_idx]) and row.iloc[col_idx] != 0:
                    try:
                        formatted_expenses.append(f'{int(row.iloc[col_idx]):,}')
                    except (ValueError, TypeError):
                        formatted_expenses.append(str(row.iloc[col_idx]))
                else:
                    formatted_expenses.append('')
            
            # Show total from Excel (NO calculation)
            if len(row) > 10 and pd.notna(row.iloc[10]) and row.iloc[10] != 0:
                try:
                    total_cell = f'{int(row.iloc[10]):,}'
                except (ValueError, TypeError):
                    total_cell = str(row.iloc[10])
            else:
                total_cell = ''
            
            rows_to_add.append({
                'cells': [date_cell, day_cell, *formatted_expenses, total_cell],
                'style': 'bold yellow',
                'type': 'monthly_total'
            })
            
        else:
            # Regular data row
            rows_to_add.append({
                'cells': [date_cell, day_cell, *expense_cols, total_cell],
                'style': None,
                'type': 'regular'
            })
    
    # Add rows to table with section breaks around weekly totals
    for i, row_data in enumerate(rows_to_add):
        # Check if next row is a weekly total (to add line before it)
        next_is_weekly = i + 1 < len(rows_to_add) and rows_to_add[i + 1]['type'] == 'weekly_total'
        # Check if current row is a weekly total (to add line after it)
        is_weekly = row_data['type'] == 'weekly_total'
        
        # Add end_section if this is the row before weekly total, or if this IS the weekly total
        end_section = next_is_weekly or is_weekly
        
        if row_data['style']:
            table.add_row(*row_data['cells'], style=row_data['style'], end_section=end_section)
        else:
            table.add_row(*row_data['cells'], end_section=end_section)
    
    console.print(table)
    
    # Display monthly grand total if available (from 單項總額 row)
    if monthly_grand_total is not None:
        grand_total_str = f'{monthly_grand_total:,}'
        console.print(f"\n💰 [bold yellow]月總金額 / Monthly Grand Total: NT$ {grand_total_str}[/bold yellow]\n")

def display_annual_summary():
    """Display annual summary of all months"""
    console = Console()
    
    # Read all sheets
    excel_file = pd.ExcelFile(EXCEL_FILE_PATH)
    
    # Month names
    months = ['一月', '二月', '三月', '四月', '五月', '六月',
              '七月', '八月', '九月', '十月', '十一月', '十二月']
    
    # Create summary table with vertical dividers and border
    from rich import box as rich_box
    
    summary_table = Table(show_header=True, header_style="bold blue", show_lines=False, box=rich_box.SQUARE, padding=(0, 1))
    
    # Add columns with wider widths to flush with top border
    summary_table.add_column("月份", width=8, justify="center")
    summary_table.add_column("交通費", width=10, justify="right")
    summary_table.add_column("伙食費", width=10, justify="right")
    summary_table.add_column("休閒/娛樂", width=12, justify="right")
    summary_table.add_column("家務", width=8, justify="right")
    summary_table.add_column("阿幫", width=8, justify="right")
    summary_table.add_column("其它", width=8, justify="right")
    summary_table.add_column("月總計", width=12, justify="right", style="green")
    
    # Display each month - NO CALCULATIONS, just show what's in Excel
    month_count = 0
    total_months = len([m for m in months if m in excel_file.sheet_names])
    
    for month in months:
        if month not in excel_file.sheet_names:
            continue
        
        month_count += 1
        is_last_month = (month_count == total_months)
            
        df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=month, header=None)
        
        # Find 單項總額 row and show exactly what's in Excel
        for idx, row in df.iterrows():
            if '單項總額' in str(row.iloc[0]):
                # Extract values from Excel (NO calculation)
                transport = row.iloc[3] if pd.notna(row.iloc[3]) and row.iloc[3] != 0 else 0
                food = row.iloc[4] if pd.notna(row.iloc[4]) and row.iloc[4] != 0 else 0
                leisure = row.iloc[5] if pd.notna(row.iloc[5]) and row.iloc[5] != 0 else 0
                household = row.iloc[6] if pd.notna(row.iloc[6]) and row.iloc[6] != 0 else 0
                abang = row.iloc[7] if pd.notna(row.iloc[7]) and row.iloc[7] != 0 else 0
                other = row.iloc[8] if pd.notna(row.iloc[8]) and row.iloc[8] != 0 else 0
                
                # Get total from Excel (column K, index 10)
                if len(row) > 10 and pd.notna(row.iloc[10]) and row.iloc[10] != 0:
                    try:
                        month_total = int(row.iloc[10])
                        month_total_str = f'{month_total:,}'
                    except (ValueError, TypeError):
                        month_total_str = '-'
                else:
                    month_total_str = '-'
                
                # Format and add row (just formatting, no calculation)
                # Add end_section to last month to create divider before row 64
                summary_table.add_row(
                    month,
                    f'{int(transport):,}' if transport > 0 else '-',
                    f'{int(food):,}' if food > 0 else '-',
                    f'{int(leisure):,}' if leisure > 0 else '-',
                    f'{int(household):,}' if household > 0 else '-',
                    f'{int(abang):,}' if abang > 0 else '-',
                    f'{int(other):,}' if other > 0 else '-',
                    month_total_str,
                    end_section=is_last_month
                )
                break
    
    # Add row 64 data (D64:K64) if it exists
    if len(months) > 0:
        # Use first available month sheet to get row 64 label
        for month in months:
            if month in excel_file.sheet_names:
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=month, header=None)
                if len(df) > 63:  # Row 64 is index 63
                    row_64 = df.iloc[63]
                    
                    # Extract values from D64 to K64 (columns 3-10)
                    transport_64 = row_64.iloc[3] if len(row_64) > 3 and pd.notna(row_64.iloc[3]) and row_64.iloc[3] != 0 else 0
                    food_64 = row_64.iloc[4] if len(row_64) > 4 and pd.notna(row_64.iloc[4]) and row_64.iloc[4] != 0 else 0
                    leisure_64 = row_64.iloc[5] if len(row_64) > 5 and pd.notna(row_64.iloc[5]) and row_64.iloc[5] != 0 else 0
                    household_64 = row_64.iloc[6] if len(row_64) > 6 and pd.notna(row_64.iloc[6]) and row_64.iloc[6] != 0 else 0
                    abang_64 = row_64.iloc[7] if len(row_64) > 7 and pd.notna(row_64.iloc[7]) and row_64.iloc[7] != 0 else 0
                    other_64 = row_64.iloc[8] if len(row_64) > 8 and pd.notna(row_64.iloc[8]) and row_64.iloc[8] != 0 else 0
                    
                    # Get total from K64 (column 10)
                    if len(row_64) > 10 and pd.notna(row_64.iloc[10]) and row_64.iloc[10] != 0:
                        try:
                            total_64 = int(row_64.iloc[10])
                            total_64_str = f'{total_64:,}'
                        except (ValueError, TypeError):
                            total_64_str = '-'
                    else:
                        total_64_str = '-'
                    
                    # Get label from column A (index 0) or use default
                    label_64 = str(row_64.iloc[0]) if pd.notna(row_64.iloc[0]) else '總計'
                    
                    # Add row 64 as a summary row with end_section
                    summary_table.add_row(
                        label_64,
                        f'{int(transport_64):,}' if transport_64 > 0 else '-',
                        f'{int(food_64):,}' if food_64 > 0 else '-',
                        f'{int(leisure_64):,}' if leisure_64 > 0 else '-',
                        f'{int(household_64):,}' if household_64 > 0 else '-',
                        f'{int(abang_64):,}' if abang_64 > 0 else '-',
                        f'{int(other_64):,}' if other_64 > 0 else '-',
                        total_64_str,
                        style="bold red",
                        end_section=True
                    )
                break
    
    console.print(summary_table)

def main():
    """Main entry point"""
    console = Console()
    
    # Check if we're viewing a specific month or annual summary
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == 'annual' or arg == '13':
            # Display annual summary
            console.print("\n" + "="*100)
            console.print("  📊 年度總覽 (ANNUAL SUMMARY)".center(100))
            console.print("="*100)
            
            display_annual_summary()
            
            console.print("\n" + "="*100 + "\n")
        else:
            # Display specific month
            try:
                month_num = int(arg)
                if 1 <= month_num <= 12:
                    months = ['一月', '二月', '三月', '四月', '五月', '六月',
                             '七月', '八月', '九月', '十月', '十一月', '十二月']
                    sheet_name = months[month_num - 1]
                    
                    console.print("\n" + "="*100)
                    console.print(f"  📄 {sheet_name} (MONTH {month_num})".center(100))
                    console.print("="*100 + "\n")
                    
                    display_monthly_sheet(sheet_name)
                    
                    console.print("\n" + "="*100 + "\n")
                else:
                    console.print(f"[red]Error: Month number must be 1-12[/red]")
            except ValueError:
                console.print(f"[red]Error: Invalid argument '{arg}'[/red]")
    else:
        # Show menu
        console.print("\n[red]Usage:[/red]")
        console.print("  python utils/view_sheets.py [1-12]  - View specific month")
        console.print("  python utils/view_sheets.py annual  - View annual summary\n")

if __name__ == "__main__":
    main()

