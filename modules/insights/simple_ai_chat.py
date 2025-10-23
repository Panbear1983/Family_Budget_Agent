"""
Simple AI Chat - Qwen 8B focused chatbot with function routing
Streamlined architecture using existing functions
"""

from typing import Optional, Dict, Any, List
from .language_detector import LanguageDetector
from .simple_question_classifier import SimpleQuestionClassifier
from .function_registry import FunctionRegistry
from .response_formatter import ResponseFormatter
from .guardrails import Guardrails
from .localized_templates import LocalizedTemplates as T

class SimpleAIChat:
    """Simplified AI Chat using Qwen 8B for intent routing to existing functions"""
    
    def __init__(self, data_loader, orchestrator, context_manager):
        """
        Initialize simplified AI Chat system
        
        Args:
            data_loader: DataLoader instance
            orchestrator: LLM orchestrator (only Qwen needed)
            context_manager: ContextManager instance
        """
        # Core dependencies
        self.data_loader = data_loader
        self.orchestrator = orchestrator
        self.context_manager = context_manager
        
        # Initialize simplified components
        self.lang_detector = LanguageDetector(default_language='auto')
        self.classifier = SimpleQuestionClassifier()
        self.function_registry = FunctionRegistry()
        self.formatter = ResponseFormatter(self.lang_detector)
        self.guardrails = Guardrails(data_loader, self.lang_detector)
        
        # Set data loader for graph generators
        self.function_registry.set_data_loader(data_loader)
        
        # Load config
        import config
        self.chat_config = getattr(config, 'AI_CHAT_CONFIG', {
            'show_confidence': True,
            'confidence_threshold': 0.6,
            'verbose_uncertainty': True,
            'show_uncertainty_warning': True
        })
        
        print("✅ Simple AI Chat initialized with Qwen 8B + function routing")
    
    def answer_question(self, question: str) -> str:
        """
        Simplified question answering using function routing
        
        Args:
            question: User's question
        
        Returns:
            Formatted answer from function execution
        """
        print(f"🔍 DEBUG: Starting answer_question for: '{question}'")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: Detect Language
        # ═══════════════════════════════════════════════════════════
        user_lang, lang_confidence = self.lang_detector.detect(question)
        response_lang = self.lang_detector.get_response_language(user_lang, allow_mixed=True)
        print(f"🔍 DEBUG: Language detected: {user_lang} (confidence: {lang_confidence})")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: Topic Relevance Check
        # ═══════════════════════════════════════════════════════════
        is_allowed, topic_cat, redirect_msg = self.guardrails.check_topic_relevance(
            question, user_lang
        )
        
        if not is_allowed:
            return redirect_msg
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3: Classify Intent & Extract Entities
        # ═══════════════════════════════════════════════════════════
        print(f"🔍 DEBUG: Classifying question...")
        classification = self.classifier.classify(question)
        intent = classification['intent']
        entities = classification['entities']
        suggested_functions = classification['suggested_functions']
        print(f"🔍 DEBUG: Classification result: intent={intent}, entities={entities}, functions={suggested_functions}")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 4: Data Scope Validation
        # ═══════════════════════════════════════════════════════════
        print(f"🔍 DEBUG: Validating data scope...")
        is_valid, error_msg = self.guardrails.validate_data_scope(entities, user_lang)
        print(f"🔍 DEBUG: Data scope validation: valid={is_valid}, error={error_msg}")
        
        if not is_valid:
            print(f"🔍 DEBUG: Data scope validation failed, returning error message")
            return error_msg
        
        # ═══════════════════════════════════════════════════════════
        # STEP 5: Route to Appropriate Function
        # ═══════════════════════════════════════════════════════════
        
        # Try to execute suggested functions
        result = self._execute_function_chain(
            question, intent, entities, suggested_functions, user_lang
        )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 6: Format Response
        # ═══════════════════════════════════════════════════════════
        formatted_result = self._format_function_result(
            result, classification, user_lang
        )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 7: Store in Context
        # ═══════════════════════════════════════════════════════════
        self._store_interaction(question, formatted_result, classification)
        
        return formatted_result
    
    def _execute_function_chain(self, question: str, intent: str, entities: Dict, 
                               suggested_functions: List[str], user_lang: str) -> str:
        """Execute the most appropriate function based on intent and entities"""
        
        # Get data for function execution
        print(f"🔍 DEBUG: Loading data for question: '{question}'")
        all_data = self.data_loader.load_all_data()
        
        # Debug: Show what data was loaded
        print(f"🔍 DEBUG: Loaded {len(all_data)} months of data")
        if all_data:
            for month_key, df in all_data.items():
                print(f"  📅 {month_key}: {len(df)} transactions")
        else:
            print("  ⚠️ No data loaded - this will cause 'no results'")
        
        # Debug: Show entities and suggested functions
        print(f"🔍 DEBUG: Entities: {entities}")
        print(f"🔍 DEBUG: Suggested functions: {suggested_functions}")
        print(f"🔍 DEBUG: Function registry has {len(self.function_registry.functions)} functions")
        print(f"🔍 DEBUG: Available functions: {list(self.function_registry.functions.keys())}")
        
        # Try each suggested function until one succeeds
        for function_name in suggested_functions:
            print(f"🔍 DEBUG: Trying function: {function_name}")
            try:
                result = self._execute_single_function(
                    function_name, question, entities, all_data, user_lang
                )
                print(f"🔍 DEBUG: Function {function_name} returned: {type(result)} - {str(result)[:100]}...")
                if result and result != "Error executing function":
                    print(f"✅ DEBUG: Function {function_name} succeeded")
                    return result
                else:
                    print(f"⚠️ DEBUG: Function {function_name} returned empty/error result")
            except Exception as e:
                print(f"  ⚠️ Function {function_name} failed: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # If all functions fail, provide a helpful message
        print(f"❌ DEBUG: All functions failed for intent: {intent}")
        if intent == 'data_query':
            return self._generate_fallback_response(entities, user_lang)
        else:
            return f"❌ Unable to process your request. Available functions: {', '.join(suggested_functions)}"
    
    def _execute_single_function(self, function_name: str, question: str, 
                                entities: Dict, all_data: Dict, user_lang: str) -> str:
        """Execute a single function with appropriate parameters"""
        
        print(f"🔍 DEBUG: Executing function {function_name}")
        
        # Get the function
        func = self.function_registry.get_function(function_name)
        if not func:
            print(f"❌ DEBUG: Function {function_name} not found in registry")
            return f"Function {function_name} not found"
        
        print(f"✅ DEBUG: Function {function_name} found: {func}")
        
        # Prepare parameters based on function type
        if 'monthly' in function_name or 'month' in function_name:
            # Monthly functions need month and data
            month = entities.get('month', '七月')  # Default to July
            print(f"🔍 DEBUG: Monthly function - looking for month: {month}")
            print(f"🔍 DEBUG: Available months: {list(all_data.keys())}")
            
            # Try to find matching month (handle year prefix)
            matching_key = None
            print(f"🔍 DEBUG: Searching for month '{month}' in keys...")
            for key in all_data.keys():
                print(f"🔍 DEBUG: Checking key '{key}' - contains '{month}': {month in key}")
                if month in key:  # "七月" matches "2025-七月"
                    matching_key = key
                    print(f"✅ DEBUG: Found matching key: {matching_key}")
                    break
            
            if matching_key:
                df = all_data[matching_key]
                print(f"🔍 DEBUG: Found data for {matching_key}: {len(df)} rows")
                if len(df) == 0:
                    print(f"⚠️ DEBUG: DataFrame for {matching_key} is empty")
                    return f"❌ No transactions found for {month}"
                
                if hasattr(func, '__self__') and hasattr(func.__self__, 'data_loader'):
                    # Set data loader if needed
                    func.__self__.data_loader = self.data_loader
                    print(f"🔍 DEBUG: Set data_loader for function")
                
                print(f"🔍 DEBUG: Calling function with month='{month}' and {len(df)} rows")
                result = func(month, df)
                print(f"🔍 DEBUG: Function returned: {type(result)}")
                return result
            else:
                print(f"❌ DEBUG: Month {month} not found in data")
                available_months = [m.split('-')[1] for m in all_data.keys()]  # Extract month names
                return f"❌ No data available for {month}. Available months: {', '.join(set(available_months))}"
        
        elif 'category' in function_name or 'breakdown' in function_name:
            # Category functions need insights data
            month = entities.get('month', '七月')
            if month in all_data:
                # Generate insights for the month
                from .insight_generator import InsightGenerator
                insight_gen = InsightGenerator(self.data_loader, self.orchestrator)
                insights = insight_gen.generate_insights(month)
                return func(insights)
            else:
                return f"❌ No data available for {month}"
        
        elif 'comparison' in function_name:
            # Comparison functions need two months
            months = entities.get('months', [])
            if len(months) >= 2:
                from .insight_generator import InsightGenerator
                insight_gen = InsightGenerator(self.data_loader, self.orchestrator)
                comparison = insight_gen.generate_comparison(months[0], months[1])
                return func(comparison)
            else:
                return "❌ Please specify two months to compare"
        
        elif 'trend' in function_name:
            # Trend functions need category and trend data
            category = entities.get('category', '伙食費')
            from .trend_analyzer import TrendAnalyzer
            trend_analyzer = TrendAnalyzer(self.data_loader)
            trend_data = trend_analyzer.analyze_category_trend(category)
            return func(trend_data, category)
        
        elif 'yearly' in function_name or 'annual' in function_name:
            # Yearly functions need summary data
            from .insight_generator import InsightGenerator
            insight_gen = InsightGenerator(self.data_loader, self.orchestrator)
            summary = insight_gen.generate_yearly_summary()
            return func(summary)
        
        else:
            # Default execution
            return func()
    
    def _generate_fallback_response(self, entities: Dict, user_lang: str) -> str:
        """Generate a fallback response when functions fail"""
        
        month = entities.get('month', '本月')
        category = entities.get('category', '')
        
        if user_lang == 'zh':
            if category:
                return f"📊 {month}{category}支出資訊\n\n❌ 無法顯示詳細資料，請檢查資料是否存在"
            else:
                return f"📊 {month}預算資訊\n\n❌ 無法顯示詳細資料，請檢查資料是否存在"
        else:
            if category:
                return f"📊 {month} {category} spending information\n\n❌ Unable to display detailed data, please check if data exists"
            else:
                return f"📊 {month} budget information\n\n❌ Unable to display detailed data, please check if data exists"
    
    def _format_function_result(self, result: str, classification: Dict, user_lang: str) -> str:
        """Format the function result into a human-like response"""
        
        # If result is already formatted (from Rich tables, etc.), return as-is
        if isinstance(result, str) and ('┌' in result or '╭' in result or '📊' in result):
            return result
        
        # Otherwise, format using the response formatter
        formatted = self.formatter.format(result, classification, user_lang)
        
        # Add confidence footer if enabled
        if self.chat_config.get('show_confidence'):
            confidence = classification.get('confidence', 0.8)
            if confidence >= 0.8:
                conf_level = "高信心度"
            elif confidence >= 0.6:
                conf_level = "中等信心度"
            else:
                conf_level = "低信心度"
            
            formatted += f"\n\n[信心度: {confidence:.0%} - {conf_level}]"
        
        return formatted
    
    def _store_interaction(self, question: str, answer: str, classification: Dict):
        """Store interaction in context manager"""
        if self.context_manager:
            metadata = {
                'intent': classification.get('intent'),
                'entities': classification.get('entities'),
                'suggested_functions': classification.get('suggested_functions')
            }
            
            self.context_manager.add_interaction(question, answer, metadata)
    
    def get_available_functions(self) -> Dict[str, str]:
        """Get list of available functions"""
        return self.function_registry.list_all_functions()
    
    def get_classification_stats(self) -> Dict:
        """Get classification statistics"""
        return self.classifier.get_stats()
