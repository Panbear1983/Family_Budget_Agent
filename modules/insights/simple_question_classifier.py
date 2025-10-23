"""
Simple Question Classifier - Qwen 8B focused intent routing
Simplified version for function-based chatbot architecture
"""

import re
from typing import Dict, List, Optional

class SimpleQuestionClassifier:
    """Simplified classifier for Qwen 8B intent routing to functions"""
    
    # Simplified patterns focused on function routing
    INTENT_PATTERNS = {
        'data_query': {
            'keywords': ['show', 'list', 'display', 'get', '查', '看', '顯示', '給我看', '列出'],
            'functions': ['show_monthly_table', 'show_category_breakdown', 'display_monthly_sheet']
        },
        'budget_analysis': {
            'keywords': ['budget', '預算', 'analysis', '分析', 'breakdown', '明細', 'summary', '總結'],
            'functions': ['show_category_breakdown', 'show_yearly_summary', 'display_annual_summary']
        },
        'visualization': {
            'keywords': ['chart', 'graph', 'plot', '圖表', '圖', '視覺', 'visual', 'pie', 'bar', 'line'],
            'functions': ['plot_pie_chart', 'plot_category_horizontal_bar', 'plot_monthly_bar']
        },
        'comparison': {
            'keywords': ['compare', 'vs', 'versus', '比較', '對比', 'difference', '差異'],
            'functions': ['show_comparison_table', 'plot_comparison_bars']
        },
        'trend': {
            'keywords': ['trend', 'pattern', '趨勢', '模式', 'change', '變化', 'over time', '最近'],
            'functions': ['plot_trend_line', 'show_trend_table', 'plot_stacked_trend']
        },
        'instant_answer': {
            'keywords': ['how much', '多少', 'total', '總', '總共', 'spent', '花了'],
            'functions': ['show_monthly_table', 'show_category_breakdown']
        }
    }
    
    # Entity extraction patterns (same as original)
    MONTHS_ZH = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    MONTHS_ZH_NUM = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    MONTHS_EN = ['january', 'february', 'march', 'april', 'may', 'june', 
                 'july', 'august', 'september', 'october', 'november', 'december']
    MONTHS_EN_SHORT = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    
    CATEGORIES_ZH = ['交通費', '伙食費', '休閒/娛樂', '家務', '其它', '阿幫']
    CATEGORIES_ZH_SIMPLIFIED = ['交通费', '伙食费', '休闲/娱乐', '家务', '其它', '阿幫']
    
    CATEGORIES_EN = {
        'transport': '交通費', 'transportation': '交通費', 'travel': '交通費',
        'food': '伙食費', 'meal': '伙食費', 'meals': '伙食費', 'dining': '伙食費',
        'entertainment': '休閒/娛樂', 'leisure': '休閒/娛樂', 'recreation': '休閒/娛樂',
        'household': '家務', 'housework': '家務', 'chores': '家務',
        'other': '其它', 'others': '其它', 'misc': '其它'
    }
    
    def __init__(self):
        self.classification_history: List[Dict] = []
    
    def classify(self, question: str) -> Dict:
        """
        Classify question and extract entities for function routing
        
        Returns:
            {
                'intent': str,           # Primary intent
                'confidence': float,     # Classification confidence
                'entities': dict,        # Extracted entities
                'suggested_functions': list  # Recommended functions
            }
        """
        q_lower = question.lower()
        
        # Extract entities first
        entities = self._extract_entities(question, q_lower)
        
        # Determine intent based on keywords
        intent_scores = {}
        for intent, info in self.INTENT_PATTERNS.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in q_lower:
                    score += 1
            
            if score > 0:
                intent_scores[intent] = score
        
        # Get primary intent
        if intent_scores:
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            confidence = min(intent_scores[primary_intent] / 3, 0.95)
        else:
            primary_intent = 'data_query'  # Default fallback
            confidence = 0.5
        
        # Get suggested functions for this intent
        suggested_functions = self.INTENT_PATTERNS[primary_intent]['functions']
        
        # Refine based on entities
        if entities.get('months') and len(entities['months']) >= 2:
            primary_intent = 'comparison'
            suggested_functions = ['show_comparison_table', 'plot_comparison_bars']
        elif entities.get('category') and any(word in q_lower for word in ['trend', '趨勢', 'change', '變化']):
            primary_intent = 'trend'
            suggested_functions = ['plot_trend_line', 'show_trend_table']
        
        result = {
            'intent': primary_intent,
            'confidence': confidence,
            'entities': entities,
            'suggested_functions': suggested_functions
        }
        
        # Store in history
        self.classification_history.append(result)
        if len(self.classification_history) > 20:
            self.classification_history = self.classification_history[-20:]
        
        return result
    
    def _extract_entities(self, question: str, q_lower: str) -> Dict:
        """Extract entities from question"""
        entities = {
            'month': None,
            'months': [],
            'category': None,
            'amount': None,
            'timeframe': None
        }
        
        # Extract months (Chinese - text format)
        for month in self.MONTHS_ZH:
            if month in question:
                if not entities['month']:
                    entities['month'] = month
                entities['months'].append(month)
        
        # Extract months (Chinese - numeric format)
        for i, month_num in enumerate(self.MONTHS_ZH_NUM):
            if month_num in question:
                month_zh = self.MONTHS_ZH[i]
                if not entities['month']:
                    entities['month'] = month_zh
                if month_zh not in entities['months']:
                    entities['months'].append(month_zh)
        
        # Extract months (English)
        for i, month in enumerate(self.MONTHS_EN + self.MONTHS_EN_SHORT):
            if month in q_lower:
                month_zh = self.MONTHS_ZH[i % 12]
                if not entities['month']:
                    entities['month'] = month_zh
                if month_zh not in entities['months']:
                    entities['months'].append(month_zh)
        
        # Extract categories (Traditional Chinese)
        for category in self.CATEGORIES_ZH:
            if category in question:
                entities['category'] = category
                break
        
        # Extract categories (Simplified Chinese)
        if not entities['category']:
            for category in self.CATEGORIES_ZH_SIMPLIFIED:
                if category in question:
                    entities['category'] = category
                    break
        
        # Extract categories (English)
        if not entities['category']:
            for en_cat, zh_cat in self.CATEGORIES_EN.items():
                if en_cat in q_lower:
                    entities['category'] = zh_cat
                    break
        
        # Extract amounts
        amount_pattern = r'NT?\$?[\s]*([\d,]+)'
        matches = re.findall(amount_pattern, question)
        if matches:
            try:
                entities['amount'] = float(matches[0].replace(',', ''))
            except:
                pass
        
        # Extract timeframe
        timeframes = {
            'this month': '本月', 'last month': '上月', 'next month': '下月',
            'this year': '今年', 'last year': '去年',
            '本月': '本月', '上月': '上月', '下月': '下月',
            '今年': '今年', '去年': '去年'
        }
        for en_time, zh_time in timeframes.items():
            if en_time in q_lower or zh_time in question:
                entities['timeframe'] = zh_time
                break
        
        return entities
    
    def get_stats(self) -> Dict:
        """Get classification statistics"""
        if not self.classification_history:
            return {'total': 0}
        
        intent_counts = {}
        total_confidence = 0
        
        for item in self.classification_history:
            intent = item['intent']
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            total_confidence += item['confidence']
        
        return {
            'total': len(self.classification_history),
            'intent_distribution': intent_counts,
            'avg_confidence': round(total_confidence / len(self.classification_history), 2),
            'most_common': max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else None
        }
