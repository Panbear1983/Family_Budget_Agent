"""
Simple LLM Orchestrator - Qwen 8B only
Simplified orchestrator for function-based chatbot architecture
"""

from typing import Dict, Any, Tuple
from .module_registry import registry
import config

class SimpleLLMOrchestrator:
    """
    Simplified orchestrator using only Qwen 8B for intent routing
    Focuses on function routing rather than complex LLM interactions
    """
    
    def __init__(self):
        self.qwen = None
        self.confidence_threshold = 0.8  # Higher threshold for function routing
    
    def initialize(self):
        """Load only Qwen 8B model"""
        # Get config for Qwen
        qwen_config = config.LLM_CONFIG.get('structured', {})
        
        self.qwen = registry.get_module('QwenEngine', config=qwen_config)
        
        if not self.qwen:
            raise RuntimeError("Failed to load Qwen engine")
        
        print("✅ Simple LLM Orchestrator initialized (Qwen 8B only)")
        return True
    
    def classify_intent(self, question: str) -> Dict:
        """
        Use Qwen 8B to classify user intent for function routing
        
        Args:
            question: User's question
        
        Returns:
            Classification result with intent and entities
        """
        prompt = f"""Classify this budget question and extract key information.

Question: {question}

Extract:
1. Intent: data_query, visualization, comparison, trend, instant_answer
2. Month(s): if mentioned
3. Category: if mentioned  
4. Amount: if mentioned

Respond in format: intent|month|category|amount

Example: data_query|七月|伙食費|15000"""

        response = self.qwen.call_model(prompt)
        
        # Parse response
        try:
            parts = response.split('|')
            intent = parts[0].strip() if len(parts) > 0 else 'data_query'
            month = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
            category = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
            amount = parts[3].strip() if len(parts) > 3 and parts[3].strip() else None
            
            return {
                'intent': intent,
                'month': month,
                'category': category,
                'amount': amount,
                'confidence': 0.8  # Default confidence for function routing
            }
        except:
            return {
                'intent': 'data_query',
                'month': None,
                'category': None,
                'amount': None,
                'confidence': 0.5
            }
    
    def extract_entities(self, question: str) -> Dict:
        """
        Extract entities from question using Qwen 8B
        
        Args:
            question: User's question
        
        Returns:
            Extracted entities
        """
        prompt = f"""Extract entities from this budget question.

Question: {question}

Extract and return:
- months: list of months mentioned
- category: spending category if mentioned
- amount: specific amount if mentioned
- timeframe: time period if mentioned

Format as JSON: {{"months": [], "category": null, "amount": null, "timeframe": null}}"""

        response = self.qwen.call_model(prompt)
        
        # Try to parse JSON response
        try:
            import json
            entities = json.loads(response)
            return entities
        except:
            # Fallback parsing
            entities = {
                'months': [],
                'category': None,
                'amount': None,
                'timeframe': None
            }
            
            # Simple keyword extraction
            if '七月' in question or 'july' in question.lower():
                entities['months'].append('七月')
            if '八月' in question or 'august' in question.lower():
                entities['months'].append('八月')
            if '伙食費' in question or 'food' in question.lower():
                entities['category'] = '伙食費'
            if '交通費' in question or 'transport' in question.lower():
                entities['category'] = '交通費'
            
            return entities
    
    def suggest_functions(self, intent: str, entities: Dict) -> list:
        """
        Suggest appropriate functions based on intent and entities
        
        Args:
            intent: Classified intent
            entities: Extracted entities
        
        Returns:
            List of suggested function names
        """
        suggestions = []
        
        if intent == 'data_query':
            if entities.get('months'):
                suggestions.extend(['show_monthly_table', 'display_monthly_sheet'])
            if entities.get('category'):
                suggestions.extend(['show_category_breakdown'])
        
        elif intent == 'visualization':
            suggestions.extend(['plot_pie_chart', 'plot_category_horizontal_bar'])
        
        elif intent == 'comparison':
            if len(entities.get('months', [])) >= 2:
                suggestions.extend(['show_comparison_table', 'plot_comparison_bars'])
        
        elif intent == 'trend':
            suggestions.extend(['plot_trend_line', 'show_trend_table'])
        
        elif intent == 'instant_answer':
            suggestions.extend(['show_monthly_table', 'show_category_breakdown'])
        
        # Default fallback
        if not suggestions:
            suggestions = ['show_monthly_table', 'show_category_breakdown']
        
        return suggestions
    
    def get_stats(self) -> Dict:
        """Get orchestrator statistics"""
        return {
            'model': 'qwen3:8b',
            'type': 'simple_orchestrator',
            'confidence_threshold': self.confidence_threshold
        }
