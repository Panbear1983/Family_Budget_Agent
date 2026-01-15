"""
Insight Generator - Generates insights and summaries from budget data
"""

from typing import Dict, List, Any
import pandas as pd

class InsightGenerator:
    """Generates insights from budget data"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
    
    def generate_monthly_insights(self, month: str) -> Dict:
        """Generate insights for a specific month"""
        try:
            # Handle MultiYearDataLoader format (e.g., "2025-九月")
            df = None
            if hasattr(self.data_loader, 'load_all_data'):
                all_data = self.data_loader.load_all_data()
                # Try full key first
                if month in all_data:
                    df = all_data[month]
                # Try extracting month name if format is "2025-九月"
                elif '-' in month:
                    month_name = month.split('-')[1]
                    if month_name in all_data:
                        df = all_data[month_name]
            # Fallback to load_month if available
            if df is None:
                month_name = month.split('-')[1] if '-' in month else month
                df = self.data_loader.load_month(month_name)
            
            # Handle empty DataFrames (months with no transactions)
            if df is None or len(df) == 0:
                return {
                    'month': month,
                    'category_breakdown': {},
                    'categories': {},  # Add categories key for compatibility
                    'total_spending': 0,
                    'transaction_count': 0,
                    'has_data': False
                }
            
            # Calculate category breakdown (handles empty DataFrames gracefully)
            if len(df) > 0 and 'category' in df.columns and 'amount' in df.columns:
                category_totals = df.groupby('category')['amount'].sum().to_dict()
                total_spending = df['amount'].sum()
                transaction_count = len(df)
            else:
                category_totals = {}
                total_spending = 0
                transaction_count = 0
            
            return {
                'month': month,
                'category_breakdown': category_totals,
                'categories': category_totals,  # Alias for GUI compatibility
                'total_spending': total_spending,
                'transaction_count': transaction_count,
                'has_data': transaction_count > 0
            }
        except Exception as e:
            return {
                'month': month,
                'category_breakdown': {},
                'categories': {},  # Alias for GUI compatibility
                'total_spending': 0,
                'transaction_count': 0,
                'has_data': False,
                'error': str(e)
            }
    
    def generate_daily_category_summary(self, month: str) -> Dict[str, Dict]:
        """Return per-category daily spending stats for the requested month."""
        try:
            df = None
            if hasattr(self.data_loader, 'load_all_data'):
                all_data = self.data_loader.load_all_data()
                if month in all_data:
                    df = all_data[month]
                elif '-' in month:
                    month_name = month.split('-', 1)[1]
                    df = all_data.get(month_name)
            if df is None:
                month_name = month.split('-', 1)[1] if '-' in month else month
                df = self.data_loader.load_month(month_name)

            if df is None or len(df) == 0 or 'date' not in df.columns or 'category' not in df.columns:
                return {}

            df = df.copy()
            df['date'] = pd.to_datetime(df['date']).dt.date
            if 'amount' not in df.columns:
                return {}

            daily_totals = df.groupby(['category', 'date'])['amount'].sum()
            results: Dict[str, Dict] = {}

            for category in daily_totals.index.get_level_values('category').unique():
                cat_series = daily_totals.loc[category]
                if not isinstance(cat_series, pd.Series):
                    cat_series = pd.Series({cat_series.index: cat_series})
                top_day = cat_series.idxmax()
                results[category] = {
                    'top_day': str(top_day),
                    'top_amount': float(cat_series.loc[top_day]),
                    'daily_totals': {str(day): float(value) for day, value in cat_series.items()}
                }

            return results
        except Exception:
            return {}
    
    def generate_yearly_summary(self, silent: bool = False) -> Dict:
        """Generate yearly summary with monthly trends"""
        try:
            if not silent:
                print("📊 Generating yearly summary...")
            
            # Force reload to get latest data with rolling 12-month window
            available_months = self.data_loader.get_available_months()
            # Also force reload when loading data (with rolling window)
            if hasattr(self.data_loader, 'load_all_data'):
                self.data_loader.load_all_data(force_reload=True, use_rolling_window=True)
            monthly_trend = {}
            category_totals = {}
            months_with_data_keys: List[str] = []
            months_without_data_keys: List[str] = []
            
            for month in available_months:
                # Handle MultiYearDataLoader format (e.g., "2025-九月")
                df = None
                if hasattr(self.data_loader, 'load_all_data'):
                    all_data = self.data_loader.load_all_data()
                    # Try full key first
                    if month in all_data:
                        df = all_data[month]
                    # Try extracting month name if format is "2025-九月"
                    elif '-' in month:
                        month_name = month.split('-')[1]
                        if month_name in all_data:
                            df = all_data[month_name]
                # Fallback to load_month if available
                if df is None:
                    month_name = month.split('-')[1] if '-' in month else month
                    df = self.data_loader.load_month(month_name)
                if df is not None and len(df) > 0:
                    monthly_total = df['amount'].sum()
                    monthly_trend[month] = monthly_total
                    
                    # Aggregate categories
                    month_categories = df.groupby('category')['amount'].sum()
                    for category, amount in month_categories.items():
                        if category not in category_totals:
                            category_totals[category] = 0
                        category_totals[category] += amount
                    months_with_data_keys.append(month)
                else:
                    months_without_data_keys.append(month)
            
            # Calculate additional statistics
            total_spending = sum(monthly_trend.values())
            avg_monthly_spending = total_spending / len(monthly_trend) if monthly_trend else 0
            months_with_data = len(months_with_data_keys)
            
            return {
                'monthly_trend': monthly_trend,
                'category_totals': category_totals,
                'total_spending': total_spending,
                'avg_monthly_spending': avg_monthly_spending,
                'months_with_data': months_with_data,
                'category_breakdown': category_totals,  # Alias for compatibility
                'available_months': available_months,
                'months_with_data_keys': months_with_data_keys,
                'months_without_data_keys': months_without_data_keys
            }
        except Exception as e:
            return {
                'monthly_trend': {},
                'category_totals': {},
                'total_spending': 0,
                'avg_monthly_spending': 0,
                'months_with_data': 0,
                'category_breakdown': {},
                'available_months': [],
                'months_with_data_keys': [],
                'months_without_data_keys': [],
                'error': str(e)
            }
    
    def generate_comparison(self, month1: str, month2: str) -> Dict:
        """Generate comparison data between two months"""
        try:
            # Handle MultiYearDataLoader format (e.g., "2025-九月")
            df1 = None
            df2 = None
            
            if hasattr(self.data_loader, 'load_all_data'):
                all_data = self.data_loader.load_all_data()
                # Try full key first
                if month1 in all_data:
                    df1 = all_data[month1]
                elif '-' in month1:
                    month1_name = month1.split('-')[1]
                    if month1_name in all_data:
                        df1 = all_data[month1_name]
                if month2 in all_data:
                    df2 = all_data[month2]
                elif '-' in month2:
                    month2_name = month2.split('-')[1]
                    if month2_name in all_data:
                        df2 = all_data[month2_name]
            
            # Fallback to load_month if available
            if df1 is None:
                month1_name = month1.split('-')[1] if '-' in month1 else month1
                df1 = self.data_loader.load_month(month1_name)
            if df2 is None:
                month2_name = month2.split('-')[1] if '-' in month2 else month2
                df2 = self.data_loader.load_month(month2_name)
            
            # Handle empty DataFrames (months with no transactions)
            if df1 is None:
                df1 = pd.DataFrame(columns=['date', 'category', 'description', 'amount', 'person', 'year'])
            if df2 is None:
                df2 = pd.DataFrame(columns=['date', 'category', 'description', 'amount', 'person', 'year'])
            
            # Ensure 'amount' column exists for empty DataFrames
            if 'amount' not in df1.columns:
                df1['amount'] = 0
            if 'amount' not in df2.columns:
                df2['amount'] = 0
            
            # Calculate category changes (handles empty DataFrames gracefully)
            if len(df1) > 0:
                cat1 = df1.groupby('category')['amount'].sum()
            else:
                cat1 = pd.Series(dtype=float)
            if len(df2) > 0:
                cat2 = df2.groupby('category')['amount'].sum()
            else:
                cat2 = pd.Series(dtype=float)
            
            # Get all categories from both months
            all_categories = set(cat1.index) | set(cat2.index)
            category_changes = {}
            
            for cat in all_categories:
                val1 = cat1.get(cat, 0)
                val2 = cat2.get(cat, 0)
                change = val2 - val1
                category_changes[cat] = {
                    'month1': val1,
                    'month2': val2,
                    'change': change
                }
            
            # Calculate totals (handles empty DataFrames)
            total1 = df1['amount'].sum() if len(df1) > 0 else 0
            total2 = df2['amount'].sum() if len(df2) > 0 else 0
            total_change = total2 - total1
            
            return {
                'month1': month1,
                'month2': month2,
                'category_changes': category_changes,
                'total1': total1,
                'total2': total2,
                'total_change': total_change
            }
        except Exception as e:
            return {
                'month1': month1,
                'month2': month2,
                'category_changes': {},
                'total_change': 0,
                'error': str(e)
            }
