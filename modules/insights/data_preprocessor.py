"""
Data Preprocessor - Compute stats before sending to LLM
Reduces token usage and improves LLM accuracy by providing condensed, relevant data
"""

from typing import Dict, List, Optional

class DataPreprocessor:
    """Prepare and condense data for LLM consumption"""
    
    def __init__(self, data_loader, insight_generator, trend_analyzer):
        """
        Initialize preprocessor
        
        Args:
            data_loader: DataLoader instance
            insight_generator: InsightGenerator instance
            trend_analyzer: TrendAnalyzer instance
        """
        self.data_loader = data_loader
        self.insight_generator = insight_generator
        self.trend_analyzer = trend_analyzer
    
    def prepare_for_llm(self, question: str, entities: Dict) -> Dict:
        """
        Prepare condensed, relevant data for LLM
        
        Args:
            question: User's question
            entities: Extracted entities from classifier
        
        Returns:
            Condensed data dict ready for LLM
        """
        prepared = {
            'question_context': {},
            'relevant_stats': {},
            'trends': {},
            'warnings': []
        }
        
        # ═══════════════════════════════════════════════════════════
        # Extract question-specific data (not all data!)
        # ═══════════════════════════════════════════════════════════
        
        # If question mentions specific month(s)
        if entities.get('month'):
            prepared['question_context']['month'] = entities['month']
            prepared['relevant_stats']['monthly'] = self._get_month_stats(entities['month'])
        
        # If question mentions multiple months (comparison)
        if entities.get('months') and len(entities['months']) >= 2:
            prepared['question_context']['months'] = entities['months']
            prepared['relevant_stats']['comparison'] = self._get_comparison_stats(
                entities['months'][0], 
                entities['months'][1]
            )
        
        # If question mentions category
        if entities.get('category'):
            prepared['question_context']['category'] = entities['category']
            prepared['trends']['category'] = self._get_category_trend(entities['category'])
        
        # If question is about overall spending
        if not entities.get('month') and not entities.get('category'):
            prepared['relevant_stats']['overall'] = self._get_overall_stats()
        
        # Always include context about available data
        prepared['metadata'] = {
            'available_months': list(self.data_loader.load_all_data().keys()),
            'available_categories': self._get_categories()
        }
        
        return prepared
    
    def _get_month_stats(self, month: str) -> Dict:
        """Get condensed stats for a specific month"""
        try:
            insights = self.insight_generator.generate_monthly_insights(month)
            
            if 'error' in insights:
                return {'error': insights['error']}
            
            # Condense to essential info only
            return {
                'total': insights.get('total_spending', 0),
                'transaction_count': insights.get('transaction_count', 0),
                'avg_transaction': insights.get('avg_transaction', 0),
                'top_category': max(insights.get('categories', {}).items(), 
                                  key=lambda x: x[1])[0] if insights.get('categories') else None,
                'all_categories': dict(sorted(insights.get('categories', {}).items(), 
                                               key=lambda x: x[1], reverse=True)),  # No truncation
                'has_warnings': len(insights.get('warnings', [])) > 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_comparison_stats(self, month1: str, month2: str) -> Dict:
        """Get condensed comparison between two months"""
        try:
            comparison = self.insight_generator.generate_comparison(month1, month2)
            
            if 'error' in comparison:
                return {'error': comparison['error']}
            
            # Condense to key differences only
            return {
                'month1': month1,
                'month2': month2,
                'total1': comparison.get('total1', 0),
                'total2': comparison.get('total2', 0),
                'change': comparison.get('change', 0),
                'change_percent': comparison.get('change_percent', 0),
                'biggest_changes': dict(sorted(
                    comparison.get('category_changes', {}).items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                ))  # No truncation - show all changes
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_category_trend(self, category: str) -> Dict:
        """Get condensed trend for a category"""
        try:
            trend = self.trend_analyzer.analyze_category_trend(category)
            
            # Condense to trend direction and key stats
            return {
                'category': category,
                'direction': trend.get('direction', 'unknown'),
                'average': trend.get('average', 0),
                'recent_values': trend.get('trend_data', [])[-3:] if trend.get('trend_data') else [],
                'data_points': len(trend.get('trend_data', []))
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_overall_stats(self) -> Dict:
        """Get condensed overall statistics"""
        try:
            stats = self.data_loader.get_summary_stats()
            
            if not stats:
                return {'error': 'No data available'}
            
            # Condense to key overview stats
            return {
                'total_spending': stats.get('total_spending', 0),
                'months_count': stats.get('months_with_data', 0),
                'avg_monthly': stats.get('total_spending', 0) / max(stats.get('months_with_data', 1), 1),
                'top_category': max(stats.get('by_category', {}).items(), 
                                  key=lambda x: x[1])[0] if stats.get('by_category') else None,
                'category_breakdown': stats.get('by_category', {})
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_categories(self) -> List[str]:
        """Get list of available categories"""
        try:
            all_data = self.data_loader.load_all_data()
            categories = set()
            
            for df in all_data.values():
                if 'category' in df.columns:
                    categories.update(df['category'].unique())
            
            return sorted(list(categories))
        except:
            return []
    
    def prepare_for_forecast(self, category: Optional[str] = None) -> Dict:
        """Prepare data specifically for forecasting"""
        try:
            forecast_data = self.trend_analyzer.forecast_next_month(category)
            
            # Add historical context
            if category:
                trend = self.trend_analyzer.analyze_category_trend(category)
                forecast_data['trend_context'] = {
                    'direction': trend.get('direction'),
                    'recent_avg': trend.get('average')
                }
            
            return forecast_data
        except Exception as e:
            return {'error': str(e)}
    
    def prepare_for_optimization(self) -> Dict:
        """Prepare data for finding savings opportunities"""
        try:
            # Get anomalies (unusual spending)
            anomalies = self.trend_analyzer.detect_anomalies(threshold=2.0)
            
            # Get category breakdown
            stats = self.data_loader.get_summary_stats()
            categories = stats.get('by_category', {})
            
            # Calculate category percentages
            total = stats.get('total_spending', 1)
            category_pcts = {
                cat: (amt / total * 100) for cat, amt in categories.items()
            }
            
            # Find high-percentage categories (potential optimization targets)
            high_pct_cats = {
                cat: pct for cat, pct in category_pcts.items() 
                if pct > 20  # More than 20% of total
            }
            
            return {
                'anomalies': anomalies,  # No truncation - show all anomalies
                'high_percentage_categories': high_pct_cats,
                'category_breakdown': categories,
                'total_spending': total,
                'optimization_potential': len(anomalies) + len(high_pct_cats)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_context_summary(self, question: str, entities: Dict) -> str:
        """
        Get a text summary of context for LLM
        (Alternative to structured data)
        """
        parts = []
        
        if entities.get('month'):
            parts.append(f"Question is about {entities['month']}")
        
        if entities.get('category'):
            parts.append(f"Focuses on {entities['category']}")
        
        if entities.get('months') and len(entities['months']) >= 2:
            parts.append(f"Comparing {' and '.join(entities['months'])}")
        
        if not parts:
            parts.append("General budget question")
        
        return "; ".join(parts)

