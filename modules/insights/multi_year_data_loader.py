"""
Multi-Year Data Loader - Load and merge data from multiple years
Extends DataLoader to support continuous timeline analysis across years
"""

import pandas as pd
from openpyxl import load_workbook
from typing import Dict, List
from datetime import datetime
from .data_loader import DataLoader


class MultiYearDataLoader(DataLoader):
    """Loads and merges data from multiple budget files"""
    
    def __init__(self, budget_files: List[str]):
        """
        Initialize multi-year data loader
        
        Args:
            budget_files: List of file paths [2025年開銷表.xlsx, 2026年開銷表.xlsx]
        """
        self.budget_files = budget_files
        self.cache = {}
        self.last_loaded = None
        self.ttl = 300  # Cache for 5 minutes
        
        # Extract years from filenames
        self.years = []
        for file in budget_files:
            # Extract year from filename like "2025年開銷表（NT）.xlsx"
            import os
            filename = os.path.basename(file)
            year = filename[:4]
            if year.isdigit():
                self.years.append(int(year))
        
        self.years.sort()
        print(f"  📅 Multi-Year Loader: {len(self.years)} years ({', '.join(map(str, self.years))})")
    
    def load_all_data(self, force_reload: bool = False) -> Dict[str, pd.DataFrame]:
        """Load all months from all budget files and merge"""
        
        # Check cache
        if not force_reload and self._is_cache_valid():
            return self.cache
        
        print(f"📊 Loading multi-year budget data ({', '.join(map(str, self.years))})...")
        
        all_data = {}
        total_transactions = 0
        
        for budget_file, year in zip(self.budget_files, self.years):
            try:
                wb = load_workbook(budget_file, read_only=True, data_only=True)
                months = ['一月', '二月', '三月', '四月', '五月', '六月',
                         '七月', '八月', '九月', '十月', '十一月', '十二月']
                
                year_month_count = 0
                year_transaction_count = 0
                
                for month in months:
                    if month in wb.sheetnames:
                        ws = wb[month]
                        
                        rows = []
                        categories = ['交通費', '伙食費', '休閒/娛樂', '家務', '阿幫', '其它']
                        category_cols = [3, 4, 5, 6, 7, 8]
                        
                        for row in ws.iter_rows(min_row=3, values_only=True):
                            if row[0]:
                                date = row[0]
                                
                                # Only process datetime objects
                                if not isinstance(date, datetime):
                                    continue
                                
                                # Skip summary rows
                                date_str = str(date)
                                if any(keyword in date_str for keyword in 
                                    ['周總額', '單項總額', '月總額', '總計', '年度明細', '周总额', '单项总额']):
                                    continue
                                
                                # Extract each category amount
                                for cat, col_idx in zip(categories, category_cols):
                                    amount = row[col_idx] if col_idx < len(row) else None
                                    
                                    if amount and isinstance(amount, (int, float)) and amount > 0:
                                        rows.append({
                                            'date': date,
                                            'category': cat,
                                            'description': '',
                                            'amount': float(amount),
                                            'person': '',
                                            'year': year  # Track source year
                                        })
                        
                        if rows:
                            df = pd.DataFrame(rows)
                            # Key format: "2025-一月" or "2026-二月"
                            key = f"{year}-{month}"
                            all_data[key] = df
                            year_month_count += 1
                            year_transaction_count += len(rows)
                
                wb.close()
                
                if year_month_count > 0:
                    print(f"  ✅ {year}: Loaded {year_month_count} months with {year_transaction_count} transactions")
                    total_transactions += year_transaction_count
                
            except FileNotFoundError:
                print(f"  ⚠️  {year}: File not found (skipping)")
                continue
            except Exception as e:
                print(f"  ⚠️  {year}: Could not load ({e})")
                continue
        
        # Update cache
        self.cache = all_data
        self.last_loaded = datetime.now()
        
        print(f"✅ Total: {len(all_data)} months with {total_transactions} transactions")
        
        return all_data
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics across all years"""
        data = self.load_all_data()
        
        stats = {
            'total_months': len(data),
            'total_transactions': sum(len(df) for df in data.values()),
            'total_spending': 0,
            'by_category': {},
            'by_month': {},
            'by_year': {}  # Year breakdown
        }
        
        for month_key, df in data.items():
            if 'amount' in df.columns:
                month_total = df['amount'].sum()
                stats['total_spending'] += month_total
                stats['by_month'][month_key] = month_total
                
                # Year tracking
                year = df['year'].iloc[0] if 'year' in df.columns and len(df) > 0 else None
                if year:
                    stats['by_year'][year] = stats['by_year'].get(year, 0) + month_total
                
                # Category breakdown
                if 'category' in df.columns:
                    for cat, amount in df.groupby('category')['amount'].sum().items():
                        stats['by_category'][cat] = stats['by_category'].get(cat, 0) + amount
        
        return stats
    
    def get_year_range(self) -> tuple:
        """
        Return (min_year, max_year)
        
        Returns:
            Tuple of (earliest_year, latest_year) or (None, None) if no data
        """
        if self.years:
            return (min(self.years), max(self.years))
        return (None, None)
    
    def get_available_months(self) -> List[str]:
        """
        Get list of available months in format 'YYYY-月份'
        
        Returns:
            Sorted list of month keys
        """
        data = self.load_all_data()
        return sorted(data.keys())

