"""
Language Detector - Auto-detect user's preferred language
Supports Chinese (zh) and English (en) with conversation memory
"""

import re
from typing import Tuple, Optional

class LanguageDetector:
    """Detect and manage conversation language preferences"""
    
    # Language indicators (words that strongly indicate a language)
    INDICATORS = {
        'zh': [
            '的', '是', '嗎', '什麼', '為什麼', '怎麼', '多少', '哪', 
            '請', '幫我', '給我', '看', '顯示', '月', '費', '總共',
            '伙食', '交通', '支出', '預算', '分析', '趨勢', '比較'
        ],
        'en': [
            'the', 'is', 'are', 'what', 'why', 'how', 'show', 'please',
            'tell', 'give', 'can', 'would', 'month', 'expense', 'total',
            'food', 'transport', 'spending', 'budget', 'analyze', 'trend', 'compare'
        ]
    }
    
    # Character ranges for detection
    CJK_RANGE = re.compile(r'[\u4e00-\u9fff]')  # Chinese characters
    ENGLISH_WORD = re.compile(r'\b[a-zA-Z]{3,}\b')  # English words (3+ chars)
    
    def __init__(self, default_language: str = 'auto'):
        """
        Initialize language detector
        
        Args:
            default_language: 'auto', 'zh', or 'en'
        """
        self.default_language = default_language
        self.conversation_language: Optional[str] = None  # Learned from conversation
        self.confidence_history: list = []  # Track confidence over time
    
    def detect(self, text: str) -> Tuple[str, float]:
        """
        Detect language from text
        
        Args:
            text: User input text
        
        Returns:
            (language_code, confidence) e.g., ('zh', 0.95)
        """
        # Force language if configured (not auto)
        if self.default_language in ['zh', 'en']:
            return self.default_language, 1.0
        
        # Use conversation language for very simple queries (continuity)
        if self.conversation_language and self._is_simple_query(text):
            return self.conversation_language, 0.8
        
        # Detect language using multiple signals
        scores = {'zh': 0, 'en': 0}
        text_lower = text.lower()
        
        # ═══════════════════════════════════════════════════════════
        # Signal 1: Indicator words (strong signal)
        # ═══════════════════════════════════════════════════════════
        for lang, indicators in self.INDICATORS.items():
            for indicator in indicators:
                if indicator in text_lower:
                    scores[lang] += 1
        
        # ═══════════════════════════════════════════════════════════
        # Signal 2: Character detection (very strong signal)
        # ═══════════════════════════════════════════════════════════
        has_cjk = bool(self.CJK_RANGE.search(text))
        if has_cjk:
            scores['zh'] += 5  # Strong signal for Chinese
        
        # ═══════════════════════════════════════════════════════════
        # Signal 3: English words count
        # ═══════════════════════════════════════════════════════════
        english_words = len(self.ENGLISH_WORD.findall(text))
        if english_words > 2:
            scores['en'] += 3
        elif english_words > 0:
            scores['en'] += 1
        
        # ═══════════════════════════════════════════════════════════
        # Signal 4: Question patterns
        # ═══════════════════════════════════════════════════════════
        if '?' in text or '？' in text:
            if '？' in text:
                scores['zh'] += 1
            if '?' in text and not has_cjk:
                scores['en'] += 1
        
        # ═══════════════════════════════════════════════════════════
        # Determine winner with confidence calculation
        # ═══════════════════════════════════════════════════════════
        total_score = scores['zh'] + scores['en']
        
        if total_score == 0:
            # No clear signals - use default or previous
            detected = self.conversation_language or 'zh'
            confidence = 0.5
        elif scores['zh'] > scores['en']:
            detected = 'zh'
            confidence = min(scores['zh'] / total_score, 0.95)
        elif scores['en'] > scores['zh']:
            detected = 'en'
            confidence = min(scores['en'] / total_score, 0.95)
        else:
            # Tie - prefer previous language or default
            detected = self.conversation_language or 'zh'
            confidence = 0.5
        
        # ═══════════════════════════════════════════════════════════
        # Remember for conversation continuity
        # ═══════════════════════════════════════════════════════════
        if confidence > 0.7:
            self.conversation_language = detected
        
        # Track confidence history
        self.confidence_history.append((detected, confidence))
        if len(self.confidence_history) > 10:
            self.confidence_history = self.confidence_history[-10:]
        
        return detected, confidence
    
    def _is_simple_query(self, text: str) -> bool:
        """Check if text is a simple query (few words, likely follow-up)"""
        word_count = len(text.split())
        return word_count <= 5
    
    def get_response_language(self, user_language: str, allow_mixed: bool = True) -> str:
        """
        Determine what language to respond in
        
        Args:
            user_language: Detected user language ('zh' or 'en')
            allow_mixed: Allow mixed language responses
        
        Returns:
            Response language code
        """
        if not allow_mixed:
            return user_language
        
        # Mixed mode recommendations
        if user_language == 'zh':
            # Chinese with English/NT$ terms (natural for Taiwan)
            return 'zh'
        else:
            # English (keep pure for clarity)
            return 'en'
    
    def reset_conversation(self):
        """Reset conversation language (e.g., new session)"""
        self.conversation_language = None
        self.confidence_history = []
    
    def get_confidence_trend(self) -> str:
        """Get recent language confidence trend"""
        if not self.confidence_history:
            return "No history"
        
        recent = self.confidence_history[-5:]
        avg_confidence = sum(c for _, c in recent) / len(recent)
        
        if avg_confidence > 0.8:
            return "High"
        elif avg_confidence > 0.6:
            return "Medium"
        else:
            return "Low"
    
    def get_stats(self) -> dict:
        """Get language detection statistics"""
        if not self.confidence_history:
            return {
                'total_detections': 0,
                'avg_confidence': 0,
                'primary_language': None
            }
        
        zh_count = sum(1 for lang, _ in self.confidence_history if lang == 'zh')
        en_count = len(self.confidence_history) - zh_count
        avg_conf = sum(c for _, c in self.confidence_history) / len(self.confidence_history)
        
        return {
            'total_detections': len(self.confidence_history),
            'zh_count': zh_count,
            'en_count': en_count,
            'avg_confidence': round(avg_conf, 2),
            'primary_language': 'zh' if zh_count > en_count else 'en',
            'confidence_trend': self.get_confidence_trend()
        }

