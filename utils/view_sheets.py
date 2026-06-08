#!/usr/bin/env python3
"""
View Budget Sheets - Monthly and Annual Views
Displays budget data with rich formatting
"""

import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from rich.console import Console
from rich.table import Table
import config

EXCEL_FILE_PATH = config.BUDGET_PATH

CATEGORY_COL_INDICES = list(range(3, 9))  # D-I in 0-based pandas columns


def _sum_categories(row):
    """Sum expense categories D-I for a daily row."""
    return sum(
        float(row.iloc[i])
        for i in CATEGORY_COL_INDICES
        if i < len(row) and pd.notna(row.iloc[i]) and row.iloc[i] != 0
    )


def _format_expense_cells(row, thousands=False):
    """Format category columns D-I for display."""
    cells = []
    for col_idx in CATEGORY_COL_INDICES:
        if col_idx < len(row) and pd.notna(row.iloc[col_idx]) and row.iloc[col_idx] != 0:
            val = int(row.iloc[col_idx])
            cells.append(f'{val:,}' if thousands else str(val))
        else:
            cells.append('')
    return cells


def _format_expense_cells_from_totals(totals, thousands=True):
    """Format pre-summed category totals for weekly/monthly rows."""
    cells = []
    for total in totals:
        if total > 0:
            cells.append(f'{int(total):,}' if thousands else str(int(total)))
        else:
            cells.append('')
    return cells


def _format_total(val, thousands=True):
    if val is None or (isinstance(val, float) and pd.isna(val)) or val == 0:
        return ''
    try:
        return f'{int(val):,}' if thousands else str(int(val))
    except (ValueError, TypeError):
        return str(val)


def _is_daily_date(date_cell):
    return bool(re.search(r'\d{4}-\d{2}-\d{2}', date_cell))


def _sum_month_from_daily_rows(df):
    """Sum each category and grand total from daily rows (source of truth)."""
    totals = [0, 0, 0, 0, 0, 0]
    for _, row in df.iterrows():
        date_cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
        if not _is_daily_date(date_cell):
            continue
        for col_offset, col_idx in enumerate(CATEGORY_COL_INDICES):
            if col_idx < len(row) and pd.notna(row.iloc[col_idx]) and row.iloc[col_idx] != 0:
                totals[col_offset] += float(row.iloc[col_idx])
    return totals, int(sum(totals))


def display_monthly_sheet_from_file(file_path, sheet_name):
    """Display a monthly sheet from specific file with rich formatting"""
    console = Console()
    
    # Read the sheet with error handling
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    except TimeoutError:
        console.print(f"[red]Error: Timeout reading file '{file_path}'[/red]")
        console.print("[yellow]Possible causes:[/yellow]")
        console.print("  • OneDrive is syncing - wait a moment and try again")
        console.print("  • Excel has the file open - close it first")
        console.print("  • File is very large - may take longer to load")
        return
    except FileNotFoundError:
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        return
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        return
    
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
        
        # Check for summary rows
        is_weekly = '周總額' in date_cell or '周总额' in date_cell
        is_monthly = '單項總額' in date_cell or '单项总额' in date_cell
        is_summary = is_weekly or is_monthly
        
        # Skip rows without a date (except summary rows)
        if not date_cell or date_cell == 'nan':
            if not is_summary:
                continue
        
        if is_weekly:
            date_cell = date_cell.replace('：', '').replace(':', '')
            week_start_idx = header_row_idx + 1
            for prev_idx in range(idx - 1, header_row_idx, -1):
                if '周總額' in str(df.iloc[prev_idx, 0]):
                    week_start_idx = prev_idx + 1
                    break

            week_totals = [0, 0, 0, 0, 0, 0]
            for week_idx in range(week_start_idx, idx):
                week_row = df.iloc[week_idx]
                if _is_daily_date(str(week_row.iloc[0])):
                    for col_offset, col_idx in enumerate(CATEGORY_COL_INDICES):
                        val = week_row.iloc[col_idx] if col_idx < len(week_row) else 0
                        if pd.notna(val) and val != 0:
                            week_totals[col_offset] += val

            week_grand_total = sum(week_totals)
            if week_grand_total > 0:
                rows_to_add.append({
                    'cells': [date_cell, day_cell, *_format_expense_cells_from_totals(week_totals), _format_total(week_grand_total)],
                    'type': 'weekly_total'
                })
        elif is_monthly:
            month_totals = [0, 0, 0, 0, 0, 0]
            for scan_idx in range(header_row_idx + 1, idx):
                scan_row = df.iloc[scan_idx]
                scan_date = str(scan_row.iloc[0]) if pd.notna(scan_row.iloc[0]) else ''
                if _is_daily_date(scan_date):
                    for col_offset, col_idx in enumerate(CATEGORY_COL_INDICES):
                        val = scan_row.iloc[col_idx] if col_idx < len(scan_row) else 0
                        if pd.notna(val) and val != 0:
                            month_totals[col_offset] += val

            month_grand_total = sum(month_totals)
            monthly_grand_total = _format_total(month_grand_total)
            rows_to_add.append({
                'cells': [date_cell, day_cell, *_format_expense_cells_from_totals(month_totals), monthly_grand_total],
                'type': 'monthly_total'
            })
        else:
            expense_cols = _format_expense_cells(row, thousands=False)
            daily_total = _format_total(_sum_categories(row))
            rows_to_add.append({
                'cells': [date_cell[:10] if len(date_cell) > 10 else date_cell, day_cell, *expense_cols, daily_total],
                'type': 'regular'
            })
    
    # Add rows to table with section breaks
    for i, row_data in enumerate(rows_to_add):
        # Check if next row is monthly total (to add line before it)
        next_is_monthly = i + 1 < len(rows_to_add) and rows_to_add[i + 1]['type'] == 'monthly_total'
        
        # Determine styling and end_section
        if row_data['type'] == 'monthly_total':
            # Monthly total: red text
            table.add_row(
                f"[red]{row_data['cells'][0]}[/red]",
                row_data['cells'][1],
                f"[red]{row_data['cells'][2]}[/red]",
                f"[red]{row_data['cells'][3]}[/red]",
                f"[red]{row_data['cells'][4]}[/red]",
                f"[red]{row_data['cells'][5]}[/red]",
                f"[red]{row_data['cells'][6]}[/red]",
                f"[red]{row_data['cells'][7]}[/red]",
                f"[bold red]{row_data['cells'][8]}[/bold red]"
            )
        elif row_data['type'] == 'weekly_total':
            # Weekly total: yellow text, add separator if followed by monthly total
            table.add_row(
                f"[yellow]{row_data['cells'][0]}[/yellow]",
                row_data['cells'][1],
                f"[yellow]{row_data['cells'][2]}[/yellow]",
                f"[yellow]{row_data['cells'][3]}[/yellow]",
                f"[yellow]{row_data['cells'][4]}[/yellow]",
                f"[yellow]{row_data['cells'][5]}[/yellow]",
                f"[yellow]{row_data['cells'][6]}[/yellow]",
                f"[yellow]{row_data['cells'][7]}[/yellow]",
                f"[bold yellow]{row_data['cells'][8]}[/bold yellow]",
                end_section=next_is_monthly
            )
        else:
            # Regular data row: add separator before monthly total
            table.add_row(*row_data['cells'], end_section=next_is_monthly)
    
    # Display table
    console.print(table)
    
    # Show monthly total if found
    if monthly_grand_total:
        console.print(f"\n[bold green]月總額 (Monthly Total): NT$ {monthly_grand_total}[/bold green]")

def display_monthly_sheet(sheet_name):
    """Display a monthly sheet with rich formatting (uses current year file)"""
    console = Console()
    
    # Read the sheet with error handling
    try:
        df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet_name, header=None)
    except TimeoutError:
        console.print(f"[red]Error: Timeout reading file '{EXCEL_FILE_PATH}'[/red]")
        console.print("[yellow]Possible causes:[/yellow]")
        console.print("  • OneDrive is syncing - wait a moment and try again")
        console.print("  • Excel has the file open - close it first")
        console.print("  • File is very large - may take longer to load")
        return
    except FileNotFoundError:
        console.print(f"[red]Error: File not found: {EXCEL_FILE_PATH}[/red]")
        return
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        return
    
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
        # For daily rows, date_cell usually looks like "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS"
        has_date = bool(re.search(r'\d{4}-\d{2}-\d{2}', date_cell))
        if not has_date and '周總額' not in date_cell and '單項總額' not in date_cell:
            continue
        
        # Skip '月剩余額:' label row (value captured separately)
        if '月剩余額' in date_cell:
            continue
        
        # Clean up date format - take only the date part, not time
        if re.search(r'\d{4}-', date_cell) and '00:00:00' in date_cell:
            date_cell = date_cell.split()[0]
        
        expense_cols = _format_expense_cells(row, thousands=False)
        total_cell = _format_total(_sum_categories(row))
        
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
            
            week_totals = [0, 0, 0, 0, 0, 0]
            for week_idx in range(week_start_idx, idx):
                week_row = df.iloc[week_idx]
                if _is_daily_date(str(week_row.iloc[0])):
                    for col_offset, col_idx in enumerate(CATEGORY_COL_INDICES):
                        val = week_row.iloc[col_idx] if col_idx < len(week_row) else 0
                        if pd.notna(val) and val != 0:
                            week_totals[col_offset] += val

            week_grand_total = sum(week_totals)
            if week_grand_total > 0:
                rows_to_add.append({
                    'cells': [date_cell, day_cell, *_format_expense_cells_from_totals(week_totals), _format_total(week_grand_total)],
                    'style': 'bold blue',
                    'type': 'weekly_total'
                })
            
        elif '單項總額' in date_cell:
            month_totals = [0, 0, 0, 0, 0, 0]
            for scan_idx in range(header_row_idx + 1, idx):
                scan_row = df.iloc[scan_idx]
                scan_date = str(scan_row.iloc[0]) if pd.notna(scan_row.iloc[0]) else ''
                if _is_daily_date(scan_date):
                    for col_offset, col_idx in enumerate(CATEGORY_COL_INDICES):
                        val = scan_row.iloc[col_idx] if col_idx < len(scan_row) else 0
                        if pd.notna(val) and val != 0:
                            month_totals[col_offset] += val

            month_grand_total = sum(month_totals)
            monthly_grand_total = month_grand_total if month_grand_total > 0 else None
            rows_to_add.append({
                'cells': [date_cell, day_cell, *_format_expense_cells_from_totals(month_totals), _format_total(month_grand_total)],
                'style': 'bold red',
                'type': 'monthly_total'
            })
            
        else:
            # Regular data row
            rows_to_add.append({
                'cells': [date_cell, day_cell, *expense_cols, total_cell],
                'style': None,
                'type': 'regular'
            })
    
    # Add rows to table with section breaks around weekly totals and before monthly total
    for i, row_data in enumerate(rows_to_add):
        # Check if next row is a weekly total (to add line before it)
        next_is_weekly = i + 1 < len(rows_to_add) and rows_to_add[i + 1]['type'] == 'weekly_total'
        # Check if current row is a weekly total (to add line after it)
        is_weekly = row_data['type'] == 'weekly_total'
        # Check if next row is monthly total (to add line before it)
        next_is_monthly = i + 1 < len(rows_to_add) and rows_to_add[i + 1]['type'] == 'monthly_total'
        
        # Add end_section if this is the row before weekly total, or if this IS the weekly total, or if next row is monthly total
        end_section = next_is_weekly or is_weekly or next_is_monthly
        
        if row_data['style']:
            table.add_row(*row_data['cells'], style=row_data['style'], end_section=end_section)
        else:
            table.add_row(*row_data['cells'], end_section=end_section)
    
    console.print(table)
    
    # Display monthly grand total if available (from 單項總額 row)
    if monthly_grand_total is not None:
        grand_total_str = f'{monthly_grand_total:,}'
        console.print(f"\n💰 [bold yellow]月總金額 / Monthly Grand Total: NT$ {grand_total_str}[/bold yellow]\n")

def display_annual_summary(file_path=None):
    """Display annual summary of all months with averages at the bottom"""
    console = Console()
    
    # Use provided file path or default to EXCEL_FILE_PATH
    excel_path = file_path if file_path else EXCEL_FILE_PATH
    
    # Read all sheets with error handling
    try:
        excel_file = pd.ExcelFile(excel_path)
    except TimeoutError:
        console.print(f"[red]Error: Timeout reading file '{excel_path}'[/red]")
        console.print("[yellow]Possible causes:[/yellow]")
        console.print("  • OneDrive is syncing - wait a moment and try again")
        console.print("  • Excel has the file open - close it first")
        console.print("  • File is very large - may take longer to load")
        return
    except FileNotFoundError:
        console.print(f"[red]Error: File not found: {excel_path}[/red]")
        return
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        return
    
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
    
    # Track totals for calculating averages
    category_totals = {
        'transport': 0,
        'food': 0,
        'leisure': 0,
        'household': 0,
        'abang': 0,
        'other': 0,
        'monthly': 0
    }
    months_with_data = 0
    
    # Display each month - NO CALCULATIONS, just show what's in Excel
    month_count = 0
    total_months = len([m for m in months if m in excel_file.sheet_names])
    
    for month in months:
        if month not in excel_file.sheet_names:
            continue
        
        month_count += 1
        is_last_month = (month_count == total_months)
        
        try:
            df = pd.read_excel(excel_path, sheet_name=month, header=None)
        except (TimeoutError, FileNotFoundError, Exception) as e:
            console.print(f"[yellow]Warning: Could not read sheet '{month}': {e}[/yellow]")
            continue
        
        category_sums, month_total = _sum_month_from_daily_rows(df)
        if month_total > 0:
            transport, food, leisure, household, abang, other = category_sums
            category_totals['transport'] += transport
            category_totals['food'] += food
            category_totals['leisure'] += leisure
            category_totals['household'] += household
            category_totals['abang'] += abang
            category_totals['other'] += other
            category_totals['monthly'] += month_total
            months_with_data += 1

            summary_table.add_row(
                month,
                f'{int(transport):,}' if transport > 0 else '-',
                f'{int(food):,}' if food > 0 else '-',
                f'{int(leisure):,}' if leisure > 0 else '-',
                f'{int(household):,}' if household > 0 else '-',
                f'{int(abang):,}' if abang > 0 else '-',
                f'{int(other):,}' if other > 0 else '-',
                f'{month_total:,}',
                end_section=is_last_month
            )
    
    # Add row 64 data (D64:K64) if it exists
    if len(months) > 0:
        # Use first available month sheet to get row 64 label
        for month in months:
            if month in excel_file.sheet_names:
                try:
                    df = pd.read_excel(excel_path, sheet_name=month, header=None)
                except (TimeoutError, FileNotFoundError, Exception) as e:
                    console.print(f"[yellow]Warning: Could not read sheet '{month}' for row 64: {e}[/yellow]")
                    continue
                if len(df) > 63:  # Row 64 is index 63
                    row_64 = df.iloc[63]
                    
                    # Extract values from D64 to K64 (columns 3-10)
                    transport_64 = row_64.iloc[3] if len(row_64) > 3 and pd.notna(row_64.iloc[3]) and row_64.iloc[3] != 0 else 0
                    food_64 = row_64.iloc[4] if len(row_64) > 4 and pd.notna(row_64.iloc[4]) and row_64.iloc[4] != 0 else 0
                    leisure_64 = row_64.iloc[5] if len(row_64) > 5 and pd.notna(row_64.iloc[5]) and row_64.iloc[5] != 0 else 0
                    household_64 = row_64.iloc[6] if len(row_64) > 6 and pd.notna(row_64.iloc[6]) and row_64.iloc[6] != 0 else 0
                    abang_64 = row_64.iloc[7] if len(row_64) > 7 and pd.notna(row_64.iloc[7]) and row_64.iloc[7] != 0 else 0
                    other_64 = row_64.iloc[8] if len(row_64) > 8 and pd.notna(row_64.iloc[8]) and row_64.iloc[8] != 0 else 0
                    
                    row_64_categories = [
                        transport_64, food_64, leisure_64, household_64, abang_64, other_64
                    ]
                    total_64 = int(sum(row_64_categories))
                    total_64_str = f'{total_64:,}' if total_64 > 0 else '-'
                    
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
    
    # Calculate and add averages row (in yellow)
    if months_with_data > 0:
        avg_transport = int(category_totals['transport'] / months_with_data)
        avg_food = int(category_totals['food'] / months_with_data)
        avg_leisure = int(category_totals['leisure'] / months_with_data)
        avg_household = int(category_totals['household'] / months_with_data)
        avg_abang = int(category_totals['abang'] / months_with_data)
        avg_other = int(category_totals['other'] / months_with_data)
        avg_monthly = int(category_totals['monthly'] / months_with_data)
        
        summary_table.add_row(
            "平均值",
            f'{avg_transport:,}' if avg_transport > 0 else '-',
            f'{avg_food:,}' if avg_food > 0 else '-',
            f'{avg_leisure:,}' if avg_leisure > 0 else '-',
            f'{avg_household:,}' if avg_household > 0 else '-',
            f'{avg_abang:,}' if avg_abang > 0 else '-',
            f'{avg_other:,}' if avg_other > 0 else '-',
            f'{avg_monthly:,}',
            style="bold yellow"
        )
    
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

