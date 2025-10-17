"""
Trend Analyzer - Analyzes spending trends over time
"""

import pandas as pd
from typing import Dict, List, Tuple

class TrendAnalyzer:
    """Analyzes budget trends"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
    
    def analyze_category_trend(self, category: str, months: int = 6) -> Dict:
        """Analyze trend for a specific category"""
        all_data = self.data_loader.load_all_data()
        
        month_order = ['一月', '二月', '三月', '四月', '五月', '六月',
                      '七月', '八月', '九月', '十月', '十一月', '十二月']
        
        trend_data = []
        for month in month_order:
            if month in all_data:
                df = all_data[month]
                if 'category' in df.columns and 'amount' in df.columns:
                    cat_total = df[df['category'] == category]['amount'].sum()
                    trend_data.append({'month': month, 'amount': cat_total})
        
        # Calculate trend direction
        if len(trend_data) >= 2:
            recent_avg = sum(d['amount'] for d in trend_data[-3:]) / min(3, len(trend_data[-3:]))
            earlier_avg = sum(d['amount'] for d in trend_data[:3]) / min(3, len(trend_data[:3]))
            
            if recent_avg > earlier_avg * 1.1:
                direction = 'increasing'
            elif recent_avg < earlier_avg * 0.9:
                direction = 'decreasing'
            else:
                direction = 'stable'
        else:
            direction = 'insufficient_data'
        
        return {
            'category': category,
            'trend_data': trend_data,
            'direction': direction,
            'average': sum(d['amount'] for d in trend_data) / len(trend_data) if trend_data else 0
        }
    
    def detect_anomalies(self, threshold: float = 2.0) -> List[Dict]:
        """Detect unusual spending patterns"""
        all_data = self.data_loader.load_all_data()
        anomalies = []
        
        for month, df in all_data.items():
            if 'amount' in df.columns:
                mean = df['amount'].mean()
                std = df['amount'].std()
                
                if std > 0:  # Avoid division by zero
                    outliers = df[df['amount'] > mean + (threshold * std)]
                    
                    for _, row in outliers.iterrows():
                        anomalies.append({
                            'month': month,
                            'date': row.get('date'),
                            'amount': row.get('amount'),
                            'description': row.get('description'),
                            'category': row.get('category'),
                            'severity': 'high' if row.get('amount') > mean + (3 * std) else 'moderate'
                        })
        
        return anomalies
    
    def forecast_next_month(self, category: str = None) -> Dict:
        """Simple forecast for next month"""
        all_data = self.data_loader.load_all_data()
        
        if category:
            # Forecast for specific category
            amounts = []
            for df in all_data.values():
                if 'category' in df.columns and 'amount' in df.columns:
                    cat_total = df[df['category'] == category]['amount'].sum()
                    amounts.append(cat_total)
        else:
            # Forecast total spending
            amounts = [df['amount'].sum() for df in all_data.values() if 'amount' in df.columns]
        
        if len(amounts) < 2:
            return {'error': 'Insufficient data for forecast'}
        
        # Simple moving average
        forecast = sum(amounts[-3:]) / len(amounts[-3:])
        
        # Calculate confidence based on volatility
        if len(amounts) >= 3:
            volatility = pd.Series(amounts).std() / pd.Series(amounts).mean()
            confidence = 'high' if volatility < 0.2 else 'moderate' if volatility < 0.4 else 'low'
        else:
            confidence = 'low'
        
        return {
            'forecast_amount': forecast,
            'confidence': confidence,
            'based_on_months': len(amounts[-3:]),
            'category': category or 'total'
        }

