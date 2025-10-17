"""
Question Classifier - Route questions to appropriate handlers
Intelligently determines question type and extracts entities
"""

import re
from typing import Dict, List, Optional

class QuestionClassifier:
    """Classify questions and route to optimal handlers"""
    
    # Question type patterns (bilingual)
    PATTERNS = {
        'instant_answer': {
            'keywords': ['how much', '多少', 'total', '總', '總共', 'sum', '加總'],
            'handler': 'instant',
            'priority': 1  # Highest priority (fastest)
        },
        'data_query': {
            'keywords': ['show', 'list', '顯示', '給我看', '列出', 'get', '查', '看'],
            'handler': 'data',
            'priority': 2
        },
        'visualization': {
            'keywords': ['chart', 'graph', 'plot', '圖表', '圖', '視覺', 'visual'],
            'handler': 'redirect_visual',  # Redirect to Mode 2
            'priority': 2
        },
        'comparison': {
            'keywords': ['compare', 'vs', 'versus', '比較', '對比', 'difference', '差異'],
            'handler': 'compare',
            'priority': 3
        },
        'forecast': {
            'keywords': ['forecast', 'predict', '預測', '預計', 'estimate', '估計', '下個月', 'next month'],
            'handler': 'forecast',
            'priority': 3
        },
        'trend': {
            'keywords': ['trend', 'pattern', '趨勢', '模式', 
                        'change', 'changing', 'changed', '變化', '改變',
                        'increase', 'increasing', 'increased', 'decrease', 'decreasing', 'decreased',
                        'growth', 'growing', 'decline', 'declining', 'risen', 'falling',
                        'rising', 'going up', 'going down', 'progression',
                        '增加', '減少', '上升', '下降', '成長', '衰退',
                        'over time', 'recently', 'lately', '最近'],
            'handler': 'trend',
            'priority': 4  # Increased from 3 to match insight priority
        },
        'insight': {
            'keywords': ['why', 'reason', 'because', '為什麼', '原因', 'explain', '解釋'],
            'handler': 'insight',
            'priority': 4  # Needs LLM reasoning
        },
        'advice': {
            'keywords': ['should', 'recommend', 'suggest', '應該', '建議', 'advice', 'tip', 'how to', '怎麼'],
            'handler': 'advice',
            'priority': 4
        },
        'optimization': {
            'keywords': ['save', 'reduce', 'cut', 'optimize', '節省', '省錢', '減少', '降低', '優化'],
            'handler': 'optimize',
            'priority': 4
        }
    }
    
    # Complex question indicators (too complex to answer)
    COMPLEX_INDICATORS = [
        # Multi-part questions
        'and', '和', '還有', 'also', '以及',
        # Conditional questions
        'if', '如果', '假如', 'when', '當',
        # Multiple entities
        'all', 'every', '所有', '每個', 'each',
        # Vague questions
        'best', 'worst', '最好', '最差', 'optimal',
        # Opinion questions
        'think', 'believe', '認為', '覺得',
        # Future speculation
        'will', 'would', '會', '將會'
    ]
    
    # Entity extraction patterns
    MONTHS_ZH = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    MONTHS_ZH_NUM = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']  # Numeric months
    MONTHS_EN = ['january', 'february', 'march', 'april', 'may', 'june', 
                 'july', 'august', 'september', 'october', 'november', 'december']
    MONTHS_EN_SHORT = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    
    # Traditional Chinese (to match Excel data)
    CATEGORIES_ZH = ['交通費', '伙食費', '休閒/娛樂', '家務', '其它', '阿幫']
    
    # Also support simplified Chinese for input
    CATEGORIES_ZH_SIMPLIFIED = ['交通费', '伙食费', '休闲/娱乐', '家务', '其它', '阿幫']
    
    # English to Traditional Chinese mapping
    CATEGORIES_EN = {
        'transport': '交通費',
        'transportation': '交通費',
        'travel': '交通費',
        'commute': '交通費',
        'food': '伙食費',
        'meal': '伙食費',
        'meals': '伙食費',
        'dining': '伙食費',
        'eating': '伙食費',
        'entertainment': '休閒/娛樂',
        'leisure': '休閒/娛樂',
        'recreation': '休閒/娛樂',
        'fun': '休閒/娛樂',
        'household': '家務',
        'housework': '家務',
        'chores': '家務',
        'home': '家務',
        'other': '其它',
        'others': '其它',
        'misc': '其它',
        'miscellaneous': '其它'
    }
    
    def __init__(self):
        """Initialize classifier"""
        self.classification_history: List[Dict] = []
    
    def _normalize_category(self, category: str) -> str:
        """
        Normalize category names to match Excel data (Traditional Chinese)
        Handles both Traditional and Simplified Chinese input
        
        Args:
            category: Category name in any format
        
        Returns:
            Normalized category name in Traditional Chinese
        """
        # Mapping: Any format → Traditional Chinese (Excel format)
        normalization_map = {
            # Simplified → Traditional
            '交通费': '交通費',
            '伙食费': '伙食費',
            '休闲/娱乐': '休閒/娛樂',
            '家务': '家務',
            # Traditional (already correct)
            '交通費': '交通費',
            '伙食費': '伙食費',
            '休閒/娛樂': '休閒/娛樂',
            '家務': '家務',
            # Other categories (unchanged)
            '其它': '其它',
            '阿幫': '阿幫'
        }
        
        return normalization_map.get(category, category)
    
    def classify(self, question: str) -> Dict:
        """
        Classify question and extract entities
        
        Args:
            question: User's question
        
        Returns:
            {
                'type': str,           # Question type
                'handler': str,        # Which handler to use
                'confidence': float,   # Classification confidence
                'entities': {          # Extracted entities
                    'month': str or None,
                    'months': list,
                    'category': str or None,
                    'amount': float or None,
                    'timeframe': str or None
                }
            }
        """
        q_lower = question.lower()
        
        # ═══════════════════════════════════════════════════════════
        # Step 0: Check if question is too complex
        # ═══════════════════════════════════════════════════════════
        complexity_score = sum(1 for indicator in self.COMPLEX_INDICATORS 
                              if indicator in q_lower)
        
        # If too many complex indicators, mark as complex
        if complexity_score >= 2 or len(question.split()) > 15:
            return {
                'type': 'too_complex',
                'handler': 'no_answer',
                'confidence': 0.9,
                'entities': {},
                'all_matches': []
            }
        
        # ═══════════════════════════════════════════════════════════
        # Step 1: Determine question type(s)
        # ═══════════════════════════════════════════════════════════
        type_scores = {}
        
        for q_type, info in self.PATTERNS.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in q_lower:
                    score += 1
            
            if score > 0:
                type_scores[q_type] = score
        
        # Get primary type (highest score, or highest priority if tied)
        if type_scores:
            primary_type = max(type_scores.items(), 
                             key=lambda x: (x[1], -self.PATTERNS[x[0]]['priority']))[0]
            confidence = min(type_scores[primary_type] / 3, 0.95)  # Normalize confidence
        else:
            # Default to insight for unknown questions
            primary_type = 'insight'
            confidence = 0.5
        
        # ═══════════════════════════════════════════════════════════
        # Step 2: Extract entities
        # ═══════════════════════════════════════════════════════════
        entities = self._extract_entities(question, q_lower)
        
        # ═══════════════════════════════════════════════════════════
        # Step 3: Refine type based on entities
        # ═══════════════════════════════════════════════════════════
        primary_type = self._refine_type(primary_type, entities, q_lower)
        
        # ═══════════════════════════════════════════════════════════
        # Build classification result
        # ═══════════════════════════════════════════════════════════
        result = {
            'type': primary_type,
            'handler': self.PATTERNS[primary_type]['handler'],
            'confidence': confidence,
            'entities': entities,
            'all_matches': list(type_scores.keys())  # For debugging
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
        
        # ─────────────────────────────────────────────────────────
        # Extract months (Chinese - text format like 七月)
        # ─────────────────────────────────────────────────────────
        for month in self.MONTHS_ZH:
            if month in question:
                if not entities['month']:
                    entities['month'] = month
                entities['months'].append(month)
        
        # ─────────────────────────────────────────────────────────
        # Extract months (Chinese - numeric format like 7月)
        # ─────────────────────────────────────────────────────────
        for i, month_num in enumerate(self.MONTHS_ZH_NUM):
            if month_num in question:
                month_zh = self.MONTHS_ZH[i]  # Convert to standard format
                if not entities['month']:
                    entities['month'] = month_zh
                if month_zh not in entities['months']:
                    entities['months'].append(month_zh)
        
        # ─────────────────────────────────────────────────────────
        # Extract months (English)
        # ─────────────────────────────────────────────────────────
        for i, month in enumerate(self.MONTHS_EN + self.MONTHS_EN_SHORT):
            if month in q_lower:
                month_zh = self.MONTHS_ZH[i % 12]
                if not entities['month']:
                    entities['month'] = month_zh
                if month_zh not in entities['months']:
                    entities['months'].append(month_zh)
        
        # ─────────────────────────────────────────────────────────
        # Extract categories (Traditional Chinese)
        # ─────────────────────────────────────────────────────────
        for category in self.CATEGORIES_ZH:
            if category in question:
                entities['category'] = self._normalize_category(category)
                break
        
        # ─────────────────────────────────────────────────────────
        # Extract categories (Simplified Chinese - normalize to Traditional)
        # ─────────────────────────────────────────────────────────
        if not entities['category']:
            for category in self.CATEGORIES_ZH_SIMPLIFIED:
                if category in question:
                    entities['category'] = self._normalize_category(category)
                    break
        
        # ─────────────────────────────────────────────────────────
        # Extract categories (English - map to Traditional Chinese)
        # ─────────────────────────────────────────────────────────
        if not entities['category']:
            for en_cat, zh_cat in self.CATEGORIES_EN.items():
                if en_cat in q_lower:
                    entities['category'] = zh_cat  # Already in Traditional Chinese
                    break
        
        # ─────────────────────────────────────────────────────────
        # Extract amounts (NT$ or numbers)
        # ─────────────────────────────────────────────────────────
        amount_pattern = r'NT?\$?[\s]*([\d,]+)'
        matches = re.findall(amount_pattern, question)
        if matches:
            try:
                entities['amount'] = float(matches[0].replace(',', ''))
            except:
                pass
        
        # ─────────────────────────────────────────────────────────
        # Extract timeframe
        # ─────────────────────────────────────────────────────────
        timeframes = {
            'this month': '本月',
            'last month': '上月',
            'next month': '下月',
            'this year': '今年',
            'last year': '去年',
            '本月': '本月',
            '上月': '上月',
            '下月': '下月',
            '今年': '今年',
            '去年': '去年'
        }
        for en_time, zh_time in timeframes.items():
            if en_time in q_lower or zh_time in question:
                entities['timeframe'] = zh_time
                break
        
        return entities
    
    def _refine_type(self, primary_type: str, entities: Dict, q_lower: str) -> str:
        """Refine question type based on extracted entities"""
        
        # If has 2+ months → likely comparison
        if len(entities['months']) >= 2:
            return 'comparison'
        
        # If has single month + category + "how much" → instant answer
        if entities['month'] and entities['category'] and ('多少' in q_lower or 'how much' in q_lower):
            return 'instant_answer'
        
        # If "forecast" or "下月" without current data → forecast
        if ('forecast' in q_lower or '預測' in q_lower or '下月' in q_lower or 'next month' in q_lower):
            return 'forecast'
        
        # Enhanced trend detection - catch trend questions that might be misclassified
        trend_indicators = [
            'trend', '趨勢', 'pattern', '模式',
            'changing', 'change', 'changed', '變化', '改變',
            'increasing', 'increase', 'decreasing', 'decrease',
            '增加', '減少', '上升', '下降',
            'growth', 'decline', 'rising', 'falling',
            'over time', 'recently', 'lately', '最近',
            'going up', 'going down', 'progression'
        ]
        
        # If has category + any trend indicator → it's a trend question
        if entities['category'] and any(indicator in q_lower for indicator in trend_indicators):
            return 'trend'
        
        # Even without category, strong trend keywords should classify as trend
        strong_trend_words = ['trend', '趨勢', 'over time', 'progression']
        if any(word in q_lower for word in strong_trend_words):
            return 'trend'
        
        # Keep original type
        return primary_type
    
    def get_stats(self) -> Dict:
        """Get classification statistics"""
        if not self.classification_history:
            return {'total': 0}
        
        type_counts = {}
        total_confidence = 0
        
        for item in self.classification_history:
            q_type = item['type']
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
            total_confidence += item['confidence']
        
        return {
            'total': len(self.classification_history),
            'type_distribution': type_counts,
            'avg_confidence': round(total_confidence / len(self.classification_history), 2),
            'most_common': max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        }

