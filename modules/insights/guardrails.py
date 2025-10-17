"""
Guardrails - Keep conversations focused on budget data (WHITELIST-ONLY MODE)
Three-layer protection: Topic Filter → Data Scope Validator → Response Sanitizer
"""

import re
from typing import Tuple, List, Dict, Optional
from .localized_templates import LocalizedTemplates as T

class Guardrails:
    """Enforce conversation boundaries and data integrity - WHITELIST-ONLY"""
    
    # ═══════════════════════════════════════════════════════════════
    # ALLOWED TOPICS (WHITELIST) - Only these are permitted
    # ═══════════════════════════════════════════════════════════════
    ALLOWED_TOPICS = {
        'spending': ['花費', '支出', 'spending', 'expense', '開銷', '費用', '花', '用'],
        'budget': ['預算', 'budget', '規劃', 'planning', '計劃'],
        'category': ['伙食', '交通', '娱乐', '家务', '其它', 'food', 'transport', 'entertainment', '類別', 'category'],
        'analysis': ['分析', '趨勢', '比較', 'analyze', 'trend', 'compare', '統計', 'stats'],
        'forecast': ['預測', '預計', 'forecast', 'predict', '估計', '未來'],
        'savings': ['節省', '省錢', 'save', 'reduce', '優化', '減少', '降低'],
        'transaction': ['交易', '帳單', 'transaction', 'bill', '收據', '記錄', '明細'],
        'month': ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月', 'month', '月'],
        'total': ['總', '全部', 'total', 'all', '合計', '加總'],
        'details': ['詳細', '明細', 'detail', 'breakdown', '列出', 'show', '顯示', '看'],
        'question_words': ['多少', '什麼', '為什麼', '怎麼', '如何', 'how', 'what', 'why', 'when', 'which', 'where']
    }
    
    # ═══════════════════════════════════════════════════════════════
    # FORBIDDEN TOPICS (For specific error messages)
    # ═══════════════════════════════════════════════════════════════
    FORBIDDEN_TOPICS = {
        'general_chat': {
            'keywords': ['你好', '天氣', 'weather', '新聞', 'news', '怎麼樣', 'how are you', '聊天', '閒聊'],
            'message': '閒聊'
        },
        'unrelated_finance': {
            'keywords': ['股票', 'stock', '投資', 'invest', '加密', 'crypto', '基金', 'fund', '利率', 'interest rate', '房貸', 'mortgage'],
            'message': '投資理財'
        },
        'personal': {
            'keywords': ['年齡', 'age', '住址', 'address', '電話', 'phone', '密碼', 'password', '個人資料'],
            'message': '個人資訊'
        },
        'technical': {
            'keywords': ['代碼', 'code', 'bug', 'error', '系統', 'system', '資料庫', 'database', '程式'],
            'message': '技術問題'
        },
        'entertainment': {
            'keywords': ['電影', 'movie', '音樂', 'music', '遊戲', 'game', '運動', 'sport', '旅遊', 'travel'],
            'message': '娛樂'
        },
        'general_knowledge': {
            'keywords': ['歷史', 'history', '地理', 'geography', '科學', 'science', '數學', 'math'],
            'message': '一般知識'
        }
    }
    
    def __init__(self, data_loader, language_detector=None):
        """
        Initialize guardrails
        
        Args:
            data_loader: DataLoader instance
            language_detector: LanguageDetector instance (optional)
        """
        self.data_loader = data_loader
        self.lang_detector = language_detector
        self.available_months = []
        self.available_categories = []
        self._load_data_scope()
    
    def _load_data_scope(self):
        """Load available months and categories from actual data"""
        try:
            all_data = self.data_loader.load_all_data()
            self.available_months = list(all_data.keys())
            
            # Extract unique categories
            categories_set = set()
            for df in all_data.values():
                if 'category' in df.columns:
                    categories_set.update(df['category'].unique())
            self.available_categories = sorted(list(categories_set))
        except:
            # Fallback defaults (Traditional Chinese to match Excel)
            self.available_months = ['七月', '八月', '九月']
            self.available_categories = ['伙食費', '交通費', '休閒/娛樂', '家務', '其它']
    
    # ═══════════════════════════════════════════════════════════════
    # LAYER 1: TOPIC FILTER (Pre-processing) - WHITELIST-ONLY
    # ═══════════════════════════════════════════════════════════════
    
    def check_topic_relevance(self, question: str, language: str = 'zh') -> Tuple[bool, str, str]:
        """
        WHITELIST-ONLY MODE: Only allowed topics pass through
        
        Args:
            question: User's question
            language: User's language
        
        Returns:
            (is_allowed, category, redirect_message)
        """
        q_lower = question.lower()
        
        # ─────────────────────────────────────────────────────────
        # STEP 1: Check if question contains ANY allowed keywords
        # ─────────────────────────────────────────────────────────
        has_allowed_keyword = False
        matched_topics = []
        
        for topic_name, keywords in self.ALLOWED_TOPICS.items():
            if any(kw in q_lower for kw in keywords):
                has_allowed_keyword = True
                matched_topics.append(topic_name)
        
        # ─────────────────────────────────────────────────────────
        # STEP 2: If NO allowed keywords → REJECT (Deny by Default)
        # ─────────────────────────────────────────────────────────
        if not has_allowed_keyword:
            # Check if it matches a known forbidden category
            forbidden_category = self._identify_forbidden_category(q_lower)
            
            if forbidden_category:
                # Specific rejection message
                return False, 'forbidden', T.get('redirects', forbidden_category, language, 
                                                topic=self.FORBIDDEN_TOPICS[forbidden_category]['message'])
            else:
                # Generic rejection (anything not in whitelist)
                return False, 'not_allowed', T.get('redirects', 'generic', language)
        
        # ─────────────────────────────────────────────────────────
        # STEP 3: Has allowed keywords → Additional validation
        # ─────────────────────────────────────────────────────────
        
        # Check if it ALSO contains forbidden keywords (mixed intent)
        forbidden_category = self._identify_forbidden_category(q_lower)
        
        if forbidden_category and len(matched_topics) < 2:
            # Mostly forbidden, little allowed → REJECT
            return False, 'mixed_forbidden', T.get('redirects', forbidden_category, language,
                                                  topic=self.FORBIDDEN_TOPICS[forbidden_category]['message'])
        
        elif has_allowed_keyword:
            # Sufficient allowed keywords → ALLOW
            primary_topic = matched_topics[0] if matched_topics else 'general_budget'
            return True, primary_topic, ''
        
        # Fallback: Deny by default
        return False, 'unknown', T.get('redirects', 'generic', language)
    
    def _identify_forbidden_category(self, question: str) -> Optional[str]:
        """Identify which forbidden category (if any)"""
        for category, info in self.FORBIDDEN_TOPICS.items():
            if any(kw in question for kw in info['keywords']):
                return category
        return None
    
    # ═══════════════════════════════════════════════════════════════
    # LAYER 2: DATA SCOPE VALIDATOR (Mid-processing)
    # ═══════════════════════════════════════════════════════════════
    
    def validate_data_scope(self, entities: Dict, language: str = 'zh') -> Tuple[bool, str]:
        """
        Validate that requested data exists
        
        Args:
            entities: Extracted entities from classifier
            language: Response language
        
        Returns:
            (is_valid, error_message)
        """
        # Check month existence
        if 'month' in entities and entities['month']:
            month = entities['month']
            if month not in self.available_months:
                return False, T.get('errors', 'no_data', language,
                                  month=month,
                                  available=', '.join(self.available_months))
        
        # Check category existence
        if 'category' in entities and entities['category']:
            category = entities['category']
            if category not in self.available_categories:
                return False, T.get('errors', 'invalid_category', language,
                                  category=category,
                                  available=', '.join(self.available_categories))
        
        # Check month range for comparisons
        if 'months' in entities and entities['months']:
            months = entities['months']
            invalid_months = [m for m in months if m not in self.available_months]
            if invalid_months:
                return False, T.get('errors', 'no_data', language,
                                  month=', '.join(invalid_months),
                                  available=', '.join(self.available_months))
        
        return True, ''
    
    # ═══════════════════════════════════════════════════════════════
    # LAYER 3: RESPONSE SANITIZER (Post-processing)
    # ═══════════════════════════════════════════════════════════════
    
    def validate_response(self, response: str, source_data: Dict, language: str = 'zh') -> Tuple[bool, str, List[str]]:
        """
        Validate LLM response against source data
        
        Args:
            response: LLM's response
            source_data: Source data used for response
            language: Response language
        
        Returns:
            (is_valid, corrected_response, warnings)
        """
        warnings = []
        corrected = response
        
        # ─────────────────────────────────────────────────────────
        # CHECK 1: Verify numbers match source data
        # ─────────────────────────────────────────────────────────
        cited_numbers = self._extract_numbers(response)
        for num in cited_numbers:
            if num > 100:  # Only check significant numbers (NT$)
                if not self._verify_number_in_data(num, source_data):
                    if language == 'zh':
                        warnings.append(f"⚠️ 數字 {num:,.0f} 未在資料中確認")
                    else:
                        warnings.append(f"⚠️ Number {num:,.0f} not verified in data")
        
        # ─────────────────────────────────────────────────────────
        # CHECK 2: Verify month/category references
        # ─────────────────────────────────────────────────────────
        mentioned_months = self._extract_months(response)
        for month in mentioned_months:
            if month not in self.available_months:
                if language == 'zh':
                    warnings.append(f"⚠️ {month}無資料")
                else:
                    warnings.append(f"⚠️ No data for {month}")
                corrected = corrected.replace(month, f"{month}(無資料)")
        
        # ─────────────────────────────────────────────────────────
        # CHECK 3: No hallucinated recommendations
        # ─────────────────────────────────────────────────────────
        if '建議' in response or 'recommend' in response.lower():
            if not self._has_data_support(response, source_data):
                if language == 'zh':
                    warnings.append("⚠️ 建議可能基於推測而非實際資料")
                else:
                    warnings.append("⚠️ Advice may be speculative, not data-based")
        
        # ─────────────────────────────────────────────────────────
        # CHECK 4: No external data references
        # ─────────────────────────────────────────────────────────
        external_refs = ['根據市場', '平均水平', '一般來說', 'typically', 'usually', 'generally']
        if any(ref in response for ref in external_refs):
            if language == 'zh':
                warnings.append("ℹ️ 回應包含一般性建議(非您的資料)")
            else:
                warnings.append("ℹ️ Response includes general advice (not your data)")
        
        # ─────────────────────────────────────────────────────────
        # CHECK 5: Ensure stays in scope (no off-topic content)
        # ─────────────────────────────────────────────────────────
        off_topic_content = ['股票', '投資報酬', '利率', 'stock', 'investment return', '房地產']
        if any(content in response for content in off_topic_content):
            if language == 'zh':
                return False, "❌ 回應超出預算範圍", ['Response went off-topic']
            else:
                return False, "❌ Response out of scope", ['Response went off-topic']
        
        is_valid = len(warnings) == 0
        return is_valid, corrected, warnings
    
    # ═══════════════════════════════════════════════════════════════
    # LAYER 4: CONVERSATION BOUNDARY ENFORCEMENT
    # ═══════════════════════════════════════════════════════════════
    
    def enforce_conversation_boundary(self, question: str, context_history: List[Dict], 
                                      language: str = 'zh') -> Tuple[bool, str]:
        """
        Prevent topic drift over conversation
        
        Args:
            question: Current question
            context_history: List of previous interactions
            language: Response language
        
        Returns:
            (allow, message)
        """
        # Track topic consistency over last 5 interactions
        if len(context_history) < 3:
            return True, ''  # Allow exploration early in conversation
        
        recent = context_history[-5:]
        off_topic_count = 0
        
        for interaction in recent:
            q = interaction.get('question', '')
            is_allowed, _, _ = self.check_topic_relevance(q, language)
            if not is_allowed:
                off_topic_count += 1
        
        # If 3+ off-topic questions recently, enforce boundary
        if off_topic_count >= 3:
            return False, T.get('redirects', 'topic_drift', language)
        
        return True, ''
    
    # ═══════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text"""
        # Match NT$1,234 or 1234 or 1,234.56
        pattern = r'NT?\$?[\d,]+\.?\d*'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            # Clean and convert
            clean = match.replace('NT$', '').replace('$', '').replace(',', '')
            try:
                numbers.append(float(clean))
            except:
                pass
        
        return numbers
    
    def _extract_months(self, text: str) -> List[str]:
        """Extract month mentions from text"""
        months = ['一月', '二月', '三月', '四月', '五月', '六月',
                 '七月', '八月', '九月', '十月', '十一月', '十二月']
        
        found = []
        for month in months:
            if month in text:
                found.append(month)
        
        return found
    
    def _verify_number_in_data(self, number: float, source_data: Dict, tolerance: float = 0.01) -> bool:
        """Check if number appears in source data (within tolerance)"""
        # Check in all nested values
        for value in self._flatten_dict(source_data):
            if isinstance(value, (int, float)):
                if abs(value - number) / max(number, 1) < tolerance:
                    return True
        
        return False
    
    def _flatten_dict(self, d: Dict) -> List:
        """Flatten nested dict to list of values"""
        values = []
        for v in d.values():
            if isinstance(v, dict):
                values.extend(self._flatten_dict(v))
            elif isinstance(v, list):
                values.extend(v)
            else:
                values.append(v)
        return values
    
    def _has_data_support(self, response: str, source_data: Dict) -> bool:
        """Check if recommendations are based on actual data"""
        # Simple heuristic: if response mentions numbers and they're verified, assume supported
        numbers = self._extract_numbers(response)
        if not numbers:
            return False  # No data cited
        
        verified_count = sum(1 for num in numbers if self._verify_number_in_data(num, source_data))
        return verified_count / len(numbers) > 0.5  # At least 50% verified

