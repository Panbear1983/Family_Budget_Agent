"""
Insight Generator - Generates structured insights from data
"""

import pandas as pd
from typing import Dict, List

class InsightGenerator:
    """Generates insights from budget data"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
    
    def generate_monthly_insights(self, month: str) -> Dict:
        """Generate insights for a specific month"""
        df = self.data_loader.load_month(month)
        
        if df is None or df.empty:
            return {'error': f'No data for {month}'}
        
        insights = {
            'month': month,
            'total_spending': df['amount'].sum() if 'amount' in df.columns else 0,
            'transaction_count': len(df),
            'avg_transaction': df['amount'].mean() if 'amount' in df.columns else 0,
            'categories': {},
            'top_expenses': [],
            'warnings': []
        }
        
        # Category breakdown
        if 'category' in df.columns and 'amount' in df.columns:
            insights['categories'] = df.groupby('category')['amount'].sum().to_dict()
        
        # Top 5 expenses
        if 'amount' in df.columns:
            top_5 = df.nlargest(5, 'amount')[['description', 'amount', 'category']]
            insights['top_expenses'] = top_5.to_dict('records')
        
        # Warnings for unusual spending
        if 'amount' in df.columns:
            avg = df['amount'].mean()
            outliers = df[df['amount'] > avg * 3]
            if not outliers.empty:
                insights['warnings'].append(f'Found {len(outliers)} unusually large transactions')
        
        return insights
    
    def generate_comparison(self, month1: str, month2: str) -> Dict:
        """Compare two months"""
        df1 = self.data_loader.load_month(month1)
        df2 = self.data_loader.load_month(month2)
        
        if df1 is None or df2 is None:
            return {'error': 'Missing data for comparison'}
        
        total1 = df1['amount'].sum() if 'amount' in df1.columns else 0
        total2 = df2['amount'].sum() if 'amount' in df2.columns else 0
        
        change = total2 - total1
        change_pct = (change / total1 * 100) if total1 > 0 else 0
        
        comparison = {
            'month1': month1,
            'month2': month2,
            'total1': total1,
            'total2': total2,
            'change': change,
            'change_percent': change_pct,
            'category_changes': {}
        }
        
        # Category comparison
        if 'category' in df1.columns and 'category' in df2.columns:
            cat1 = df1.groupby('category')['amount'].sum()
            cat2 = df2.groupby('category')['amount'].sum()
            
            all_cats = set(cat1.index) | set(cat2.index)
            for cat in all_cats:
                val1 = cat1.get(cat, 0)
                val2 = cat2.get(cat, 0)
                comparison['category_changes'][cat] = {
                    'month1': val1,
                    'month2': val2,
                    'change': val2 - val1
                }
        
        return comparison
    
    def generate_yearly_summary(self) -> Dict:
        """Generate summary for entire year"""
        stats = self.data_loader.get_summary_stats()
        
        # Calculate averages
        if stats['total_months'] > 0:
            avg_monthly = stats['total_spending'] / stats['total_months']
        else:
            avg_monthly = 0
        
        # Find highest/lowest months
        if stats['by_month']:
            highest_month = max(stats['by_month'].items(), key=lambda x: x[1])
            lowest_month = min(stats['by_month'].items(), key=lambda x: x[1])
        else:
            highest_month = lowest_month = (None, 0)
        
        summary = {
            'total_spending': stats['total_spending'],
            'total_transactions': stats['total_transactions'],
            'months_with_data': stats['total_months'],
            'avg_monthly_spending': avg_monthly,
            'highest_month': {'month': highest_month[0], 'amount': highest_month[1]},
            'lowest_month': {'month': lowest_month[0], 'amount': lowest_month[1]},
            'category_breakdown': stats['by_category'],
            'monthly_trend': stats['by_month']
        }
        
        return summary

