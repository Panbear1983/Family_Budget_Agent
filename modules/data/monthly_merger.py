"""
Monthly Merger - Merge your + wife's exports into main budget
"""

import pandas as pd
import os
from datetime import datetime
from openpyxl import load_workbook
from core.base_module import BaseModule
from typing import Tuple

class MonthlyMerger(BaseModule):
    """Handle monthly budget merges"""
    
    def _setup(self):
        """Initialize merger"""
        self.categorizer = None  # Will be set by orchestrator
        self.orchestrator = None
        print("  📥 Monthly Merger initialized")
    
    def set_categorizer(self, categorizer):
        """Set categorizer module"""
        self.categorizer = categorizer
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator for LLM access"""
        self.orchestrator = orchestrator
    
    def execute_from_dataframes(self, peter_df: pd.DataFrame, dolly_df: pd.DataFrame, 
                                target_month: str, main_budget_path: str, merge_mode: bool = False):
        """
        Execute merge from pre-parsed DataFrames (from FileParser)
        Returns: (success, merged_count, merged_dataframe)
        """
        try:
            print(f"\n🔍 Categorizing transactions...")
            
            # Categorize Peter's transactions
            if len(peter_df) > 0:
                peter_categorized = self.categorizer.batch_categorize(
                    peter_df.to_dict('records'),
                    person='peter'
                )
            else:
                peter_categorized = []
            
            # Categorize Dolly's transactions
            if len(dolly_df) > 0:
                dolly_categorized = self.categorizer.batch_categorize(
                    dolly_df.to_dict('records'),
                    person='wife'
                )
            else:
                dolly_categorized = []
            
            # Combine
            all_transactions = peter_categorized + dolly_categorized
            combined_df = pd.DataFrame(all_transactions)
            print(f"  ✅ Combined: {len(combined_df)} total transactions")
            
            # Deduplicate
            print(f"\n🔍 Detecting duplicates...")
            deduped = self.deduplicate(combined_df)
            print(f"  ✅ After dedup: {len(deduped)} unique transactions")
            
            # Preview
            self.show_preview(deduped, target_month)
            
            return True, len(deduped), deduped
            
        except Exception as e:
            return False, 0, f"Error: {str(e)}"
    
    def execute(self, your_file: str, wife_file: str, target_month: str, main_budget_path: str):
        """
        Main merge workflow
        Returns: (success, merged_count, message)
        """
        try:
            # Step 1: Load exports
            print(f"\n📂 Loading exports...")
            your_df = pd.read_excel(your_file)
            wife_df = pd.read_excel(wife_file)
            print(f"  ✅ Your data: {len(your_df)} transactions")
            print(f"  ✅ Wife's data: {len(wife_df)} transactions")
            
            # Step 2: Categorize
            print(f"\n🔍 Categorizing transactions...")
            your_categorized = self.categorizer.batch_categorize(
                your_df.to_dict('records'),
                person='peter'
            )
            
            wife_categorized = self.categorizer.batch_categorize(
                wife_df.to_dict('records'),
                person='wife'
            )
            
            # Step 3: Combine
            all_transactions = your_categorized + wife_categorized
            combined_df = pd.DataFrame(all_transactions)
            print(f"  ✅ Combined: {len(combined_df)} total transactions")
            
            # Step 4: Deduplicate
            print(f"\n🔍 Detecting duplicates...")
            deduped = self.deduplicate(combined_df)
            print(f"  ✅ After dedup: {len(deduped)} unique transactions")
            
            # Step 5: Preview
            self.show_preview(deduped, target_month)
            
            # Step 6: Append to main budget (will be confirmed by user in UI)
            return True, len(deduped), deduped
            
        except Exception as e:
            return False, 0, f"Error: {str(e)}"
    
    def deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicates: exact matches + LLM-assisted fuzzy matches
        """
        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Stage 1: Remove exact duplicates (fast)
        before_count = len(df)
        df_deduped = df.drop_duplicates(subset=['date', 'amount', 'description'], keep='first')
        exact_dups = before_count - len(df_deduped)
        
        if exact_dups > 0:
            print(f"  ✅ Removed {exact_dups} exact duplicates")
        
        # Stage 2: Fuzzy duplicate detection (LLM-assisted)
        # Check for same date + similar amount + different description
        potential_dups = []
        df_deduped = df_deduped.sort_values('date').reset_index(drop=True)
        
        for i in range(len(df_deduped) - 1):
            for j in range(i + 1, min(i + 5, len(df_deduped))):  # Check next 4 rows
                row1 = df_deduped.iloc[i]
                row2 = df_deduped.iloc[j]
                
                # Same date and similar amount?
                if (row1['date'] == row2['date'] and 
                    abs(row1['amount'] - row2['amount']) <= 1):
                    
                    # Different description but might be same transaction
                    if row1['description'] != row2['description']:
                        potential_dups.append((i, j))
        
        # Use LLM for fuzzy matches if orchestrator available
        if potential_dups and self.orchestrator:
            print(f"  🤖 Checking {len(potential_dups)} potential duplicates with LLM...")
            to_remove = set()
            
            for i, j in potential_dups[:10]:  # Limit to 10 for speed
                tx1 = df_deduped.iloc[i].to_dict()
                tx2 = df_deduped.iloc[j].to_dict()
                
                is_dup, reason = self.orchestrator.detect_duplicate(tx1, tx2)
                if is_dup:
                    to_remove.add(j)
                    print(f"    ✅ Duplicate found: {df_deduped.iloc[j]['description'][:30]}")
            
            if to_remove:
                df_deduped = df_deduped.drop(list(to_remove)).reset_index(drop=True)
                print(f"  ✅ Removed {len(to_remove)} fuzzy duplicates")
        
        return df_deduped
    
    def show_preview(self, df: pd.DataFrame, month: str):
        """Show detailed preview in annual sheet format"""
        print("\n" + "="*100)
        print(f"  📋 PREVIEW: {month} Sheet (As it will appear)".center(100))
        print("="*100 + "\n")
        
        # Summary stats
        print("📊 SUMMARY:")
        print(f"   Total Transactions: {len(df)}")
        print(f"   Total Amount: NT${df['amount'].sum():,.0f}")
        print(f"   Date Range: {df['date'].min().date()} to {df['date'].max().date()}")
        
        # By category
        print("\n📁 BY CATEGORY:")
        by_cat = df.groupby('main_category')['amount'].agg(['count', 'sum'])
        for cat, row in by_cat.iterrows():
            print(f"   {cat:15s}: {int(row['count']):3d} items = NT${int(row['sum']):,}")
        
        # Group by date for daily entries
        daily = df.groupby(df['date'].dt.date).apply(
            lambda x: x.groupby('main_category')['amount'].sum().to_dict()
        ).to_dict()
        
        # Table header (matches annual sheet format)
        print("\n" + "="*100)
        print(f"{'日期':12s} │ {'星期':6s} │ {'交通費':>8s} │ {'伙食費':>8s} │ {'休閒/娛樂':>10s} │ {'家務':>6s} │ {'阿幫':>6s} │ {'其它':>6s} │ {'每日總額':>10s}")
        print("─" * 100)
        
        # Weekly totals tracking
        weekly_totals = {
            '交通費': 0, '伙食費': 0, '休閒/娛樂': 0,
            '家務': 0, '阿幫': 0, '其它': 0
        }
        weekly_total = 0
        last_week = None
        
        # Data rows
        for date, cats in sorted(daily.items()):
            dow = pd.Timestamp(date).strftime('%A')
            dow_chinese = {
                'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三',
                'Thursday': '星期四', 'Friday': '星期五', 
                'Saturday': '星期六', 'Sunday': '星期天'
            }.get(dow, dow)
            
            # Check if we need to print weekly total
            current_week = pd.Timestamp(date).isocalendar()[1]
            if last_week is not None and current_week != last_week and weekly_total > 0:
                # Print weekly total row
                print("─" * 100)
                wt_trans = weekly_totals['交通費']
                wt_food = weekly_totals['伙食費']
                wt_fun = weekly_totals['休閒/娛樂']
                wt_home = weekly_totals['家務']
                wt_helper = weekly_totals['阿幫']
                wt_other = weekly_totals['其它']
                print(f"{'周總額':12s} │ {'      ':6s} │ {wt_trans:8.0f} │ {wt_food:8.0f} │ {wt_fun:10.0f} │ {wt_home:6.0f} │ {wt_helper:6.0f} │ {wt_other:6.0f} │ {weekly_total:10.0f}")
                print("─" * 100)
                
                # Reset weekly totals
                weekly_totals = {k: 0 for k in weekly_totals}
                weekly_total = 0
            
            last_week = current_week
            
            # Print daily row
            trans = cats.get('交通費', 0)
            food = cats.get('伙食費', 0)
            fun = cats.get('休閒/娛樂', 0)
            home = cats.get('家務', 0)
            helper = cats.get('阿幫', 0)
            other = cats.get('其它', 0)
            total = trans + food + fun + home + helper + other
            
            print(f"{date} │ {dow_chinese:6s} │ {trans:8.0f} │ {food:8.0f} │ {fun:10.0f} │ {home:6.0f} │ {helper:6.0f} │ {other:6.0f} │ {total:10.0f}")
            
            # Accumulate weekly totals
            weekly_totals['交通費'] += trans
            weekly_totals['伙食費'] += food
            weekly_totals['休閒/娛樂'] += fun
            weekly_totals['家務'] += home
            weekly_totals['阿幫'] += helper
            weekly_totals['其它'] += other
            weekly_total += total
        
        # Print final weekly total if any data remains
        if weekly_total > 0:
            print("─" * 100)
            wt_trans = weekly_totals['交通費']
            wt_food = weekly_totals['伙食費']
            wt_fun = weekly_totals['休閒/娛樂']
            wt_home = weekly_totals['家務']
            wt_helper = weekly_totals['阿幫']
            wt_other = weekly_totals['其它']
            print(f"{'周總額':12s} │ {'      ':6s} │ {wt_trans:8.0f} │ {wt_food:8.0f} │ {wt_fun:10.0f} │ {wt_home:6.0f} │ {wt_helper:6.0f} │ {wt_other:6.0f} │ {weekly_total:10.0f}")
        
        print("\n" + "="*100)
    
    def append_to_month_tab(self, df: pd.DataFrame, month_name: str, budget_file: str, merge_mode: bool = False):
        """
        Write transactions to monthly tab with calendar-aligned row placement
        Only writes to restricted areas: rows 3-9, 11-17, 19-25, 27-33, 35-41, 43-49
        Only writes amounts to columns D-I (4-9)
        Assumes columns A & B (date & weekday) are pre-filled by auto-fill function
        
        Args:
            df: DataFrame with transactions
            month_name: Name of the month sheet
            budget_file: Path to budget Excel file
            merge_mode: If True, add to existing values; if False, overwrite existing values
        """
        from openpyxl import load_workbook
        # #region agent log
        import json
        import time
        def _debug_log(message, data, hypothesis_id):
            try:
                with open("/Users/peter/Desktop/Old_Projects/GitHub/Family_Budget_Agent/.cursor/debug.log", "a") as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "pre-fix",
                        "hypothesisId": hypothesis_id,
                        "location": "modules/data/monthly_merger.py:append_to_month_tab",
                        "message": message,
                        "data": data,
                        "timestamp": int(time.time() * 1000)
                    }) + "\n")
            except Exception:
                pass
        # #endregion
        
        # Load workbook
        wb = load_workbook(budget_file)
        
        # #region agent log
        _debug_log(
            "append_to_month_tab entry",
            {
                "budget_file": budget_file,
                "month_name": month_name,
                "merge_mode": merge_mode,
                "df_rows": int(len(df)),
                "df_date_min": str(df["date"].min()) if "date" in df else None,
                "df_date_max": str(df["date"].max()) if "date" in df else None
            },
            "A"
        )
        # #endregion
        
        if month_name not in wb.sheetnames:
            print(f"  ❌ Sheet '{month_name}' not found in budget file")
            # #region agent log
            _debug_log(
                "month sheet missing",
                {"sheetnames": wb.sheetnames},
                "D"
            )
            # #endregion
            return False
        
        ws = wb[month_name]
        
        # Define weekly blocks (Mon-Sun rows for each week)
        weekly_blocks = [
            (3, 9),    # Week 1: Mon(3), Tue(4), Wed(5), Thu(6), Fri(7), Sat(8), Sun(9)
            (11, 17),  # Week 2: Mon(11) through Sun(17)
            (19, 25),  # Week 3
            (27, 33),  # Week 4
            (35, 41),  # Week 5
            (43, 49),  # Week 6
        ]
        
        # Column mapping (only write to columns D-I for amounts)
        col_map = {
            '交通費': 4,      # Column D
            '伙食費': 5,      # Column E
            '休閒/娛樂': 6,   # Column F
            '家務': 7,        # Column G
            '阿幫': 8,        # Column H
            '其它': 9         # Column I
        }
        
        # Group by date for daily entries
        daily_totals = df.groupby(df['date'].dt.date).apply(
            lambda x: x.groupby('main_category')['amount'].sum().to_dict()
        ).to_dict()
        
        # #region agent log
        _debug_log(
            "daily_totals prepared",
            {
                "daily_count": int(len(daily_totals)),
                "daily_sample_dates": [str(d) for d in sorted(list(daily_totals.keys()))[:5]]
            },
            "E"
        )
        # #endregion
        
        mode_text = "merge mode (adding to existing)" if merge_mode else "overwrite mode (replacing existing)"
        print(f"\n  📅 Writing {len(daily_totals)} days to {month_name} (calendar-aligned, {mode_text})")
        
        # Build date-to-row mapping by reading pre-written dates from column A
        print("  🔍 Reading dates from Excel to find correct row positions...")
        date_to_row = {}  # Maps date -> row number (1-based)
        
        # Scan rows 3-49 (the weekly blocks) to find dates in column A
        non_empty_cells = 0
        formula_cells = 0
        sample_cells = []
        for row_num in range(3, 50):  # rows 3-49 (1-based)
            date_cell = ws.cell(row_num, 1).value  # Column A (1-based)
            cell_obj = ws.cell(row_num, 1)
            if date_cell is not None:
                non_empty_cells += 1
                if cell_obj.data_type == 'f':
                    formula_cells += 1
            if len(sample_cells) < 6:
                sample_cells.append({
                    "row": row_num,
                    "value": str(date_cell) if date_cell is not None else None,
                    "type": type(date_cell).__name__ if date_cell is not None else None,
                    "data_type": cell_obj.data_type
                })
            
            if date_cell:
                # Handle datetime objects and date strings
                date_key = None
                if isinstance(date_cell, datetime):
                    date_key = date_cell.date()
                elif isinstance(date_cell, str):
                    try:
                        # Try parsing date string (e.g., "2025-10-13")
                        date_key = pd.to_datetime(date_cell).date()
                    except:
                        continue
                else:
                    # Try to convert other types
                    try:
                        date_key = pd.to_datetime(date_cell).date()
                    except:
                        continue
                
                if date_key:
                    date_to_row[date_key] = row_num
        
        # #region agent log
        _debug_log(
            "date scan results",
            {
                "non_empty_cells": non_empty_cells,
                "formula_cells": formula_cells,
                "sample_cells": sample_cells,
                "date_to_row_count": int(len(date_to_row)),
                "date_to_row_sample": [str(d) for d in sorted(list(date_to_row.keys()))[:5]]
            },
            "A"
        )
        # #endregion
        
        print(f"  ✅ Found {len(date_to_row)} dates in Excel sheet")
        
        # Fallback: if no dates found, derive row mapping from calendar
        if len(date_to_row) == 0:
            import calendar
            print("  ⚠️  No dates found in column A; using calendar fallback mapping")
            calendar_cache = {}
            for date_key in sorted(daily_totals.keys()):
                year = date_key.year
                month = date_key.month
                cache_key = (year, month)
                if cache_key not in calendar_cache:
                    first_weekday, days_in_month = calendar.monthrange(year, month)
                    calendar_cache[cache_key] = (first_weekday, days_in_month)
                first_weekday, days_in_month = calendar_cache[cache_key]
                
                if date_key.day > days_in_month:
                    continue
                
                offset = first_weekday + (date_key.day - 1)
                week_index = offset // 7
                weekday_index = offset % 7
                
                if week_index >= len(weekly_blocks):
                    continue
                
                row_num = weekly_blocks[week_index][0] + weekday_index
                date_to_row[date_key] = row_num
            
            # #region agent log
            _debug_log(
                "calendar fallback mapping",
                {
                    "fallback_count": int(len(date_to_row)),
                    "fallback_sample_dates": [str(d) for d in sorted(list(date_to_row.keys()))[:5]]
                },
                "B"
            )
            # #endregion
            
            print(f"  ✅ Generated {len(date_to_row)} dates from calendar fallback")
        
        # Process each date
        written_count = 0
        skipped_count = 0
        
        for date, categories in sorted(daily_totals.items()):
            # Look up row number from Excel date mapping
            row_num = date_to_row.get(date)
            
            if row_num is None:
                print(f"  ⚠️  Date {date} not found in Excel sheet (skipping)")
                skipped_count += 1
                continue
            
            # Validate row is within the weekly blocks (safety check)
            in_valid_block = False
            for week_start, week_end in weekly_blocks:
                if week_start <= row_num <= week_end:
                    in_valid_block = True
                    break
            
            if not in_valid_block:
                print(f"  ⚠️  Date {date} at row {row_num} outside valid weekly blocks (skipping)")
                skipped_count += 1
                continue
            
            # ✅ Write amounts to columns D-I (4-9)
            # NOTE: We do NOT write to columns A & B (date/weekday) - assumed pre-filled
            for cat, col in col_map.items():
                amount = categories.get(cat, 0)
                if amount > 0:
                    if merge_mode:
                        # Merge mode: add to existing value
                        existing_value = ws.cell(row_num, col).value or 0
                        new_total = existing_value + amount
                        ws.cell(row_num, col, new_total)
                    else:
                        # Overwrite mode: replace existing value
                        ws.cell(row_num, col, amount)
            
            written_count += 1
        
        # Save
        wb.save(budget_file)
        
        # Force recalculation of formulas
        print("  🔄 Forcing Excel formula recalculation...")
        for sheet in wb.worksheets:
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.data_type == 'f':  # Formula cell
                        cell.value = cell.value  # Force recalculation
        
        # Save again after recalculation
        wb.save(budget_file)
        
        if skipped_count > 0:
            print(f"  ⚠️  Skipped {skipped_count} date(s) outside 6-week range")
        
        print(f"  ✅ Updated {month_name} tab with {written_count} daily entries")
        print(f"  🔄 Formulas recalculated automatically")
        print(f"  ☁️  OneDrive will auto-sync changes")
        
        return True

