"""
Confidence Tracker - Track and communicate AI answer confidence
Provides transparency about answer reliability
"""

from typing import Tuple, Dict

class ConfidenceTracker:
    """Track and communicate confidence in AI responses"""
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.8      # >= 80% - confident
    MEDIUM_CONFIDENCE = 0.6    # 60-79% - moderate
    LOW_CONFIDENCE = 0.4       # 40-59% - uncertain
    # < 40% - very uncertain
    
    def __init__(self):
        self.confidence_components = {}
    
    def calculate_confidence(self, components: Dict) -> Tuple[float, str]:
        """
        Calculate overall confidence score
        
        Args:
            components: {
                'data_available': float (0-1),
                'question_clear': float (0-1),
                'llm_confident': float (0-1),
                'guardrail_passed': float (0-1),
                'response_verified': float (0-1)
            }
        
        Returns:
            (confidence_score, confidence_level)
        """
        weights = {
            'data_available': 0.40,      # Most important - do we have the data?
            'question_clear': 0.20,      # Is question unambiguous?
            'llm_confident': 0.20,       # Is LLM certain?
            'guardrail_passed': 0.10,    # Did it pass validation?
            'response_verified': 0.10     # Are numbers verified?
        }
        
        total_confidence = 0
        for key, weight in weights.items():
            total_confidence += components.get(key, 0.5) * weight
        
        # Determine confidence level
        if total_confidence >= self.HIGH_CONFIDENCE:
            level = 'high'
        elif total_confidence >= self.MEDIUM_CONFIDENCE:
            level = 'medium'
        elif total_confidence >= self.LOW_CONFIDENCE:
            level = 'low'
        else:
            level = 'very_low'
        
        self.confidence_components = components
        return total_confidence, level
    
    def get_uncertainty_message(self, confidence: float, reason: str, 
                                language: str = 'zh') -> str:
        """
        Get appropriate uncertainty message based on reason
        
        Args:
            confidence: Confidence score (0-1)
            reason: Reason for uncertainty
            language: Response language
        
        Returns:
            Uncertainty warning message
        """
        
        if confidence >= self.HIGH_CONFIDENCE:
            return ""  # No warning needed for high confidence
        
        messages = {
            'zh': {
                'no_data': "ℹ️ 我沒有找到相關資料，這個回答基於推測。",
                'unclear_question': "⚠️ 問題不太清楚，我盡力回答了，但可能不準確。",
                'llm_uncertain': "🤔 我不太確定這個答案，建議您驗證一下。",
                'off_topic': "🚫 這個問題超出我的專業範圍（預算分析），無法準確回答。",
                'partial_data': "📊 我只有部分資料，答案可能不完整。",
                'unverified': "⚠️ 這個答案包含未經驗證的資訊。",
                'general': "⚠️ 我對這個答案的信心度較低，請謹慎參考。"
            },
            'en': {
                'no_data': "ℹ️ I don't have relevant data. This answer is speculative.",
                'unclear_question': "⚠️ The question is unclear. I tried my best but may be inaccurate.",
                'llm_uncertain': "🤔 I'm not very confident about this answer. Please verify.",
                'off_topic': "🚫 This question is outside my expertise (budget analysis).",
                'partial_data': "📊 I only have partial data. The answer may be incomplete.",
                'unverified': "⚠️ This answer contains unverified information.",
                'general': "⚠️ I have low confidence in this answer. Please use with caution."
            }
        }
        
        return messages.get(language, messages['zh']).get(reason, 
                                                          messages[language].get('general', ''))
    
    def format_confidence_footer(self, confidence: float, level: str, 
                                 components: Dict, language: str = 'zh',
                                 verbose: bool = True) -> str:
        """
        Format confidence information for display
        
        Args:
            confidence: Confidence score (0-1)
            level: Confidence level (high/medium/low/very_low)
            components: Component scores dict
            language: Display language
            verbose: Show detailed breakdown
        
        Returns:
            Formatted confidence footer
        """
        
        # Confidence bar visualization
        bar_length = 20
        filled = int(confidence * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Color indicator emoji
        if level == 'high':
            indicator = "🟢"
            label = "高" if language == 'zh' else "High"
        elif level == 'medium':
            indicator = "🟡"
            label = "中等" if language == 'zh' else "Medium"
        elif level == 'low':
            indicator = "🟠"
            label = "偏低" if language == 'zh' else "Low"
        else:
            indicator = "🔴"
            label = "很低" if language == 'zh' else "Very Low"
        
        if language == 'zh':
            footer = f"\n\n{indicator} 信心度: {bar} {confidence*100:.0f}% ({label})"
            
            # Add breakdown for non-high confidence if verbose
            if verbose and confidence < self.HIGH_CONFIDENCE:
                footer += "\n   📋 詳細分析:"
                if components.get('data_available', 1) < 0.8:
                    footer += f"\n      • 資料可用性: {components.get('data_available', 0)*100:.0f}%"
                if components.get('question_clear', 1) < 0.8:
                    footer += f"\n      • 問題清晰度: {components.get('question_clear', 0)*100:.0f}%"
                if components.get('llm_confident', 1) < 0.8:
                    footer += f"\n      • AI確定性: {components.get('llm_confident', 0)*100:.0f}%"
                if components.get('response_verified', 1) < 0.9:
                    footer += f"\n      • 回應驗證: {components.get('response_verified', 0)*100:.0f}%"
        else:
            footer = f"\n\n{indicator} Confidence: {bar} {confidence*100:.0f}% ({label})"
            
            if verbose and confidence < self.HIGH_CONFIDENCE:
                footer += "\n   📋 Breakdown:"
                if components.get('data_available', 1) < 0.8:
                    footer += f"\n      • Data Availability: {components.get('data_available', 0)*100:.0f}%"
                if components.get('question_clear', 1) < 0.8:
                    footer += f"\n      • Question Clarity: {components.get('question_clear', 0)*100:.0f}%"
                if components.get('llm_confident', 1) < 0.8:
                    footer += f"\n      • AI Certainty: {components.get('llm_confident', 0)*100:.0f}%"
                if components.get('response_verified', 1) < 0.9:
                    footer += f"\n      • Response Verification: {components.get('response_verified', 0)*100:.0f}%"
        
        return footer
    
    def assess_data_availability(self, entities: Dict, available_data: Dict) -> float:
        """
        Assess if we have the required data for the question
        
        Args:
            entities: Extracted entities from question
            available_data: Available months and categories
        
        Returns:
            Data availability score (0-1)
        """
        
        score = 1.0  # Start optimistic
        
        # Check month availability
        if entities.get('month'):
            if entities['month'] not in available_data.get('months', []):
                score *= 0.2  # Major penalty - no data for requested month
        
        # Check category availability
        if entities.get('category'):
            if entities['category'] not in available_data.get('categories', []):
                score *= 0.5  # Moderate penalty - category not found
        
        # Check for comparison data (need multiple months)
        if entities.get('months') and len(entities['months']) >= 2:
            missing = [m for m in entities['months'] 
                      if m not in available_data.get('months', [])]
            if missing:
                # Proportional penalty based on missing data
                score *= (1 - len(missing) / len(entities['months']))
        
        # If no specific data requested, assume general query (medium confidence)
        if not entities.get('month') and not entities.get('category'):
            score = 0.7  # General queries are less certain
        
        return max(score, 0.0)
    
    def assess_question_clarity(self, classification: Dict) -> float:
        """
        Assess question clarity from classification confidence
        
        Args:
            classification: Question classification result
        
        Returns:
            Question clarity score (0-1)
        """
        
        # High classification confidence = clear question
        classifier_confidence = classification.get('confidence', 0.5)
        
        if classifier_confidence >= 0.8:
            return 0.95  # Very clear question
        elif classifier_confidence >= 0.6:
            return 0.75  # Moderately clear
        elif classifier_confidence >= 0.4:
            return 0.55  # Somewhat unclear
        else:
            return 0.35  # Very unclear
    
    def assess_llm_confidence(self, response: str) -> float:
        """
        Detect LLM uncertainty from response text
        
        Args:
            response: LLM's response text
        
        Returns:
            LLM confidence score (0-1)
        """
        
        # Uncertainty phrases that indicate low confidence
        uncertain_zh = ['可能', '大概', '也許', '不確定', '我猜', '估計', '似乎', '好像']
        uncertain_en = ['maybe', 'perhaps', 'possibly', 'unsure', 'guess', 
                       'estimate', 'might', 'could be', 'probably']
        
        response_lower = response.lower()
        
        # Count uncertainty indicators
        uncertainty_count = 0
        for phrase in uncertain_zh + uncertain_en:
            uncertainty_count += response_lower.count(phrase)
        
        # More uncertainty phrases = lower confidence
        if uncertainty_count == 0:
            return 0.95  # No uncertainty markers
        elif uncertainty_count == 1:
            return 0.75  # One uncertainty marker
        elif uncertainty_count == 2:
            return 0.55  # Two uncertainty markers
        else:
            return 0.35  # Multiple uncertainty markers
    
    def determine_uncertainty_reason(self, components: Dict) -> str:
        """
        Determine primary reason for low confidence
        
        Args:
            components: Confidence component scores
        
        Returns:
            Reason code for uncertainty message
        """
        
        # Find the lowest scoring component
        min_component = min(components.items(), key=lambda x: x[1])
        component_name, score = min_component
        
        # Map component to reason
        reason_map = {
            'data_available': 'no_data' if score < 0.5 else 'partial_data',
            'question_clear': 'unclear_question',
            'llm_confident': 'llm_uncertain',
            'guardrail_passed': 'off_topic',
            'response_verified': 'unverified'
        }
        
        return reason_map.get(component_name, 'general')

