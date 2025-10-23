"""
Qwen-Only Orchestrator - Simplified LLM routing
Uses only Qwen for natural language to function command routing
"""

from typing import Dict, Any, Tuple
from .module_registry import registry
import config

class QwenOrchestrator:
    """
    Simplified orchestrator using only Qwen 8B
    Routes natural language to existing functions
    """
    
    def __init__(self):
        self.qwen = None
    
    def initialize(self):
        """Load only Qwen model"""
        # Get config for Qwen
        qwen_config = config.LLM_CONFIG.get('structured', {})
        
        self.qwen = registry.get_module('QwenEngine', config=qwen_config)
        
        if not self.qwen:
            raise RuntimeError("Failed to load Qwen engine")
        
        print("✅ Qwen-Only Orchestrator initialized")
        return True
    
    def classify_intent(self, question: str) -> Dict[str, Any]:
        """
        Use Qwen to classify user intent and extract entities
        Returns structured command for function routing
        """
        prompt = f"""Classify this budget question and extract entities.

Question: "{question}"

Classify into ONE of these intents:
- data_query: Show specific data (monthly, yearly, category)
- visualization: Create charts/graphs
- comparison: Compare months or categories
- trend: Analyze trends over time

Extract entities:
- month: Chinese month name (一月, 二月, etc.) or English (July, August)
- category: Category name (交通费, 伙食费, 休闲/娱乐, 家务, 其它)
- chart_type: Type of chart (pie, bar, line, table)

Respond in JSON format:
{{
    "intent": "intent_name",
    "entities": {{
        "month": "month_name",
        "category": "category_name",
        "chart_type": "chart_type"
    }},
    "suggested_functions": ["function1", "function2"]
}}"""

        response = self.qwen.call_model(prompt)
        
        # Parse response (simple fallback if JSON parsing fails)
        try:
            import json
            result = json.loads(response)
        except:
            # Fallback parsing
            result = self._parse_fallback(question, response)
        
        return result
    
    def _parse_fallback(self, question: str, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON fails"""
        question_lower = question.lower()
        
        # Determine intent
        if any(word in question_lower for word in ['show', 'display', '多少', '支出', 'spending']):
            intent = 'data_query'
        elif any(word in question_lower for word in ['chart', 'graph', '图', '表']):
            intent = 'visualization'
        elif any(word in question_lower for word in ['compare', '比较', '对比']):
            intent = 'comparison'
        elif any(word in question_lower for word in ['trend', '趋势', '变化']):
            intent = 'trend'
        else:
            intent = 'data_query'  # Default
        
        # Extract month
        months = ['一月', '二月', '三月', '四月', '五月', '六月', 
                 '七月', '八月', '九月', '十月', '十一月', '十二月']
        month = None
        for m in months:
            if m in question:
                month = m
                break
        
        # If no month found, try to extract from English
        if month is None:
            english_months = ['january', 'february', 'march', 'april', 'may', 'june',
                            'july', 'august', 'september', 'october', 'november', 'december']
            for i, em in enumerate(english_months):
                if em in question_lower:
                    month = months[i]
                    break
        
        # Extract category
        categories = ['交通费', '伙食费', '休闲/娱乐', '家务', '其它']
        category = None
        for c in categories:
            if c in question:
                category = c
                break
        
        # If no category found, try English
        if category is None:
            english_categories = ['transportation', 'food', 'entertainment', 'housework', 'other']
            category_mapping = {
                'transportation': '交通费',
                'food': '伙食费', 
                'entertainment': '休闲/娱乐',
                'housework': '家务',
                'other': '其它'
            }
            for ec in english_categories:
                if ec in question_lower:
                    category = category_mapping[ec]
                    break
        
        # Suggest functions based on intent
        if intent == 'data_query':
            suggested_functions = ['show_monthly_table', 'display_monthly_sheet']
        elif intent == 'visualization':
            suggested_functions = ['plot_monthly_bar', 'show_category_breakdown']
        elif intent == 'comparison':
            suggested_functions = ['show_comparison_table', 'plot_comparison_bars']
        else:
            suggested_functions = ['show_trend_table', 'plot_trend_line']
        
        # Add menu routing suggestion for fallback
        if not month and not category:
            # If no specific entities found, suggest menu routing
            suggested_functions.append('menu_routing')
        
        return {
            "intent": intent,
            "entities": {
                "month": month,
                "category": category,
                "chart_type": None
            },
            "suggested_functions": suggested_functions
        }
    
    def route_to_function(self, classification: Dict[str, Any]) -> str:
        """
        Route classified intent to appropriate function
        Returns function name to execute
        """
        intent = classification.get('intent', 'data_query')
        suggested_functions = classification.get('suggested_functions', [])
        
        # Return the first suggested function
        if suggested_functions:
            return suggested_functions[0]
        
        # Default routing
        if intent == 'data_query':
            return 'show_monthly_table'
        elif intent == 'visualization':
            return 'plot_monthly_bar'
        elif intent == 'comparison':
            return 'show_comparison_table'
        else:
            return 'show_trend_table'
    
    def answer_question(self, question: str, data: Dict) -> str:
        """
        Simplified question answering using function routing
        """
        # Classify the question
        classification = self.classify_intent(question)
        
        # Route to function
        function_name = self.route_to_function(classification)
        
        # Return the function name for execution
        return f"ROUTE_TO_FUNCTION:{function_name}"
