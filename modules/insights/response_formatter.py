"""
Response Formatter - Parse and enhance LLM output
Adds visualizations, emojis, structure, and follow-up suggestions
"""

import re
from typing import Dict, List
from .localized_templates import LocalizedTemplates as T

class ResponseFormatter:
    """Enhance and format LLM responses for better UX"""
    
    def __init__(self, language_detector=None):
        """
        Initialize formatter
        
        Args:
            language_detector: LanguageDetector instance (optional)
        """
        self.lang_detector = language_detector
    
    def format(self, raw_response: str, classification: Dict, language: str = 'zh') -> str:
        """
        Format and enhance LLM response
        
        Args:
            raw_response: Raw response from LLM
            classification: Question classification dict
            language: Response language
        
        Returns:
            Enhanced, formatted response
        """
        formatted = raw_response
        
        # ═══════════════════════════════════════════════════════════
        # Step 1: Add contextual emoji indicators
        # ═══════════════════════════════════════════════════════════
        formatted = self._add_emoji_indicators(formatted)
        
        # ═══════════════════════════════════════════════════════════
        # Step 2: Format numbers for readability
        # ═══════════════════════════════════════════════════════════
        formatted = self._format_numbers(formatted)
        
        # ═══════════════════════════════════════════════════════════
        # Step 3: Add structure (bullet points, sections)
        # ═══════════════════════════════════════════════════════════
        formatted = self._add_structure(formatted)
        
        # ═══════════════════════════════════════════════════════════
        # Step 4: Add follow-up suggestions based on question type
        # ═══════════════════════════════════════════════════════════
        follow_ups = self._suggest_followups(classification, language)
        if follow_ups:
            formatted += f"\n\n{follow_ups}"
        
        # ═══════════════════════════════════════════════════════════
        # Step 5: Add mini-charts if appropriate
        # ═══════════════════════════════════════════════════════════
        if self._should_add_mini_chart(classification):
            chart = self._create_mini_chart(classification.get('entities', {}))
            if chart:
                formatted += f"\n\n{chart}"
        
        return formatted
    
    def _add_emoji_indicators(self, text: str) -> str:
        """Add emoji indicators for trends and sentiments"""
        
        # Trend indicators
        if any(word in text for word in ['增加', '上升', 'increase', 'up', 'rising']):
            if not text.startswith('📈'):
                text = "📈 " + text
        
        elif any(word in text for word in ['減少', '下降', 'decrease', 'down', 'falling']):
            if not text.startswith('📉'):
                text = "📉 " + text
        
        elif any(word in text for word in ['穩定', 'stable', 'steady']):
            if not text.startswith('➡️'):
                text = "➡️ " + text
        
        # Warning indicators
        if any(word in text for word in ['警告', '注意', 'warning', 'caution', '異常']):
            text = text.replace('警告', '⚠️ 警告')
            text = text.replace('warning', '⚠️ Warning')
            text = text.replace('注意', '⚠️ 注意')
        
        # Positive indicators
        if any(word in text for word in ['節省', '優化', 'save', 'optimize', '改善']):
            text = text.replace('節省', '💰 節省')
            text = text.replace('save', '💰 Save')
        
        return text
    
    def _format_numbers(self, text: str) -> str:
        """Format numbers with thousand separators"""
        
        # Find NT$ amounts without commas
        pattern = r'NT\$\s*(\d{4,})'
        
        def format_match(match):
            number = int(match.group(1))
            return f'NT${number:,}'
        
        text = re.sub(pattern, format_match, text)
        
        # Also handle standalone large numbers
        pattern2 = r'(\d{4,})(?!\d)'
        
        def format_standalone(match):
            number = match.group(1)
            # Only format if it looks like a currency amount
            if len(number) >= 4:
                return f'{int(number):,}'
            return number
        
        text = re.sub(pattern2, format_standalone, text)
        
        return text
    
    def _add_structure(self, text: str) -> str:
        """Add structure with bullet points and sections"""
        
        # If response has numbered points but no line breaks
        if re.search(r'[1-3]\.\s+', text) and text.count('\n') < 2:
            # Add line breaks before numbered points
            text = re.sub(r'([。！？])\s*([1-3]\.)', r'\1\n\n\2', text)
        
        # Add line breaks after Chinese periods in long responses
        if len(text) > 200 and text.count('\n') < 3:
            text = re.sub(r'([。！？])\s+([^1-9\n])', r'\1\n\2', text)
        
        return text
    
    def _suggest_followups(self, classification: Dict, language: str) -> str:
        """Suggest follow-up questions based on classification"""
        
        q_type = classification.get('type')
        entities = classification.get('entities', {})
        
        suggestions = []
        
        # Type-specific suggestions
        if q_type == 'instant_answer':
            # After showing a number, suggest visualization
            suggestions.append(T.get('follow_ups', 'see_chart', language))
        
        elif q_type == 'comparison':
            # After comparison, suggest optimization
            suggestions.append(T.get('follow_ups', 'optimize', language))
        
        elif q_type == 'trend':
            # After trend, suggest forecast
            suggestions.append(T.get('follow_ups', 'forecast', language))
        
        elif q_type in ['insight', 'advice']:
            # After advice, suggest specific action
            if entities.get('category'):
                suggestions.append(T.get('follow_ups', 'breakdown', language, 
                                       category=entities['category']))
        
        # Entity-specific suggestions
        if entities.get('month') and not entities.get('months'):
            # Has single month, suggest comparison
            suggestions.append(T.get('follow_ups', 'compare', language))
        
        # Return formatted suggestions
        if suggestions:
            if language == 'zh':
                return "💡 " + " | ".join(suggestions[:2])  # Max 2 suggestions
            else:
                return "💡 " + " | ".join(suggestions[:2])
        
        return ""
    
    def _should_add_mini_chart(self, classification: Dict) -> bool:
        """Determine if a mini-chart would be helpful"""
        
        q_type = classification.get('type')
        entities = classification.get('entities', {})
        
        # Add charts for comparisons or trends with numbers
        if q_type in ['comparison', 'trend'] and len(entities.get('months', [])) >= 2:
            return True
        
        return False
    
    def _create_mini_chart(self, entities: Dict) -> str:
        """Create a simple ASCII mini-chart"""
        
        # Simple bar chart for comparison
        months = entities.get('months', [])
        
        if len(months) >= 2:
            # Placeholder - would need actual data
            # For now, just indicate chart availability
            return "📊 [圖表建議: 輸入 'gui圖表' 查看完整視覺化]"
        
        return ""
    
    def clean_llm_artifacts(self, text: str) -> str:
        """Remove common LLM artifacts and formatting issues"""
        
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove common LLM prefixes
        prefixes_to_remove = [
            'Here is', 'Here\'s', '根據', 'Based on',
            'The answer is:', '答案是:', '回答:'
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                if text.startswith(':'):
                    text = text[1:].strip()
        
        return text
    
    def highlight_important_numbers(self, text: str) -> str:
        """Highlight important numbers in the response"""
        
        # Find large amounts (>10000) and bold them (for terminal that supports it)
        pattern = r'NT\$\s*([\d,]+)'
        
        def highlight_large(match):
            amount_str = match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
                if amount >= 10000:
                    # Return with emphasis (works in some terminals)
                    return f'**NT${amount:,}**'
            except:
                pass
            return match.group(0)
        
        return re.sub(pattern, highlight_large, text)
    
    def add_action_items(self, text: str, q_type: str, language: str = 'zh') -> str:
        """Add action items for advice-type responses"""
        
        if q_type in ['advice', 'optimization']:
            # Check if response already has action items
            if '建議' not in text and 'recommend' not in text.lower():
                return text
            
            # Response has advice, ensure it's actionable
            if language == 'zh':
                footer = "\n\n📋 下一步: 選擇一個建議開始實施"
            else:
                footer = "\n\n📋 Next step: Choose one recommendation to implement"
            
            return text + footer
        
        return text
    
    def format_comparison_table(self, comparison_data: Dict, language: str = 'zh') -> str:
        """Format comparison data as a simple table"""
        
        if not comparison_data:
            return ""
        
        month1 = comparison_data.get('month1', '')
        month2 = comparison_data.get('month2', '')
        total1 = comparison_data.get('total1', 0)
        total2 = comparison_data.get('total2', 0)
        change_pct = comparison_data.get('change_percent', 0)
        
        if language == 'zh':
            table = f"""
📊 對比摘要:
┌─────────┬──────────────┬──────────────┬────────┐
│         │   {month1:^10s} │   {month2:^10s} │  變化  │
├─────────┼──────────────┼──────────────┼────────┤
│ 總支出  │ NT${total1:>9,.0f} │ NT${total2:>9,.0f} │ {change_pct:>5.1f}% │
└─────────┴──────────────┴──────────────┴────────┘
"""
        else:
            table = f"""
📊 Comparison:
┌─────────┬──────────────┬──────────────┬────────┐
│         │   {month1:^10s} │   {month2:^10s} │ Change │
├─────────┼──────────────┼──────────────┼────────┤
│  Total  │ NT${total1:>9,.0f} │ NT${total2:>9,.0f} │ {change_pct:>5.1f}% │
└─────────┴──────────────┴──────────────┴────────┘
"""
        
        return table.strip()

