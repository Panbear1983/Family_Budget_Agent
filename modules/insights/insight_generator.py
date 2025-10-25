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
            df = self.data_loader.load_month(month)
            if df is None or len(df) == 0:
                return {
                    'month': month,
                    'category_breakdown': {},
                    'total_spending': 0,
                    'transaction_count': 0
                }
            
            # Calculate category breakdown
            category_totals = df.groupby('category')['amount'].sum().to_dict()
            
            return {
                'month': month,
                'category_breakdown': category_totals,
                'categories': category_totals,  # Alias for GUI compatibility
                'total_spending': df['amount'].sum(),
                'transaction_count': len(df)
            }
        except Exception as e:
            return {
                'month': month,
                'category_breakdown': {},
                'categories': {},  # Alias for GUI compatibility
                'total_spending': 0,
                'transaction_count': 0,
                'error': str(e)
            }
    
    def generate_yearly_summary(self, silent: bool = False) -> Dict:
        """Generate yearly summary with monthly trends"""
        try:
            if not silent:
                print("📊 Generating yearly summary...")
            
            available_months = self.data_loader.get_available_months()
            monthly_trend = {}
            category_totals = {}
            
            for month in available_months:
                df = self.data_loader.load_month(month)
                if df is not None and len(df) > 0:
                    monthly_total = df['amount'].sum()
                    monthly_trend[month] = monthly_total
                    
                    # Aggregate categories
                    month_categories = df.groupby('category')['amount'].sum()
                    for category, amount in month_categories.items():
                        if category not in category_totals:
                            category_totals[category] = 0
                        category_totals[category] += amount
            
            # Calculate additional statistics
            total_spending = sum(monthly_trend.values())
            avg_monthly_spending = total_spending / len(monthly_trend) if monthly_trend else 0
            months_with_data = len([m for m in monthly_trend.values() if m > 0])
            
            return {
                'monthly_trend': monthly_trend,
                'category_totals': category_totals,
                'total_spending': total_spending,
                'avg_monthly_spending': avg_monthly_spending,
                'months_with_data': months_with_data,
                'category_breakdown': category_totals,  # Alias for compatibility
                'available_months': available_months
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
                'error': str(e)
            }
    
    def generate_comparison(self, month1: str, month2: str) -> Dict:
        """Generate comparison data between two months"""
        try:
            df1 = self.data_loader.load_month(month1)
            df2 = self.data_loader.load_month(month2)
            
            if df1 is None or df2 is None:
                return {
                    'month1': month1,
                    'month2': month2,
                    'category_changes': {},
                    'total_change': 0,
                    'error': 'No data available for one or both months'
                }
            
            # Calculate category changes
            cat1 = df1.groupby('category')['amount'].sum()
            cat2 = df2.groupby('category')['amount'].sum()
            
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
            
            # Calculate totals
            total1 = df1['amount'].sum()
            total2 = df2['amount'].sum()
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
