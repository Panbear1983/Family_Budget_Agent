"""
Trend Analyzer - Analyzes trends in budget data
"""

from typing import Dict, List, Any
import pandas as pd

class TrendAnalyzer:
    """Analyzes trends in budget data"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
    
    def analyze_category_trend(self, category: str) -> Dict:
        """Analyze trend for a specific category across months"""
        try:
            available_months = self.data_loader.get_available_months()
            trend_data = []
            
            for month in available_months:
                df = self.data_loader.load_month(month)
                if df is not None and len(df) > 0:
                    category_df = df[df['category'] == category]
                    amount = category_df['amount'].sum()
                    # Handle NaN values
                    if pd.isna(amount):
                        amount = 0
                    trend_data.append({
                        'month': month,
                        'amount': float(amount)
                    })
            
            # Calculate trend statistics
            amounts = [item['amount'] for item in trend_data]
            if len(amounts) > 1:
                trend_direction = "increasing" if amounts[-1] > amounts[0] else "decreasing"
                avg_amount = sum(amounts) / len(amounts)
                max_amount = max(amounts)
                min_amount = min(amounts)
            else:
                trend_direction = "stable"
                avg_amount = amounts[0] if amounts else 0
                max_amount = amounts[0] if amounts else 0
                min_amount = amounts[0] if amounts else 0
            
            return {
                'category': category,
                'trend_data': trend_data,
                'trend_direction': trend_direction,
                'average_amount': avg_amount,
                'max_amount': max_amount,
                'min_amount': min_amount,
                'total_months': len(trend_data)
            }
        except Exception as e:
            return {
                'category': category,
                'trend_data': [],
                'trend_direction': 'unknown',
                'average_amount': 0,
                'max_amount': 0,
                'min_amount': 0,
                'total_months': 0,
                'error': str(e)
            }
