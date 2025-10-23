"""
Qwen Chat - Simplified chatbot using Qwen for function routing
Routes natural language to existing view and visual analysis functions
"""

from typing import Optional, Dict, Any, List
from .language_detector import LanguageDetector
from .function_registry import FunctionRegistry
from .response_formatter import ResponseFormatter
from .guardrails import Guardrails

class QwenChat:
    """Simplified chatbot using Qwen for natural language to function routing"""
    
    def __init__(self, data_loader, orchestrator, context_manager=None):
        """
        Initialize Qwen-based chatbot
        
        Args:
            data_loader: DataLoader instance
            orchestrator: Qwen orchestrator
            context_manager: Optional context manager
        """
        # Core dependencies
        self.data_loader = data_loader
        self.orchestrator = orchestrator
        self.context_manager = context_manager
        
        # Initialize components
        self.lang_detector = LanguageDetector(default_language='auto')
        self.function_registry = FunctionRegistry()
        self.formatter = ResponseFormatter(self.lang_detector)
        self.guardrails = Guardrails(data_loader, self.lang_detector)
        
        # Set data loader for function registry
        self.function_registry.set_data_loader(data_loader)
        
        print("✅ Qwen Chat initialized - Natural language routing to existing functions")
    
    def answer_question(self, question: str) -> str:
        """
        Answer question by routing to existing functions
        
        Args:
            question: User's question
        
        Returns:
            Formatted answer from function execution
        """
        print(f"🔍 Processing: '{question}'")
        
        # Step 1: Detect language
        user_lang, _ = self.lang_detector.detect(question)
        
        # Step 2: Check topic relevance
        is_allowed, _, redirect_msg = self.guardrails.check_topic_relevance(question, user_lang)
        if not is_allowed:
            return redirect_msg
        
        # Step 3: Classify intent using Qwen
        print("🤖 Qwen classifying intent...")
        classification = self.orchestrator.classify_intent(question)
        print(f"📋 Intent: {classification['intent']}, Entities: {classification['entities']}")
        
        # Step 4: Execute appropriate function
        result = self._execute_function_chain(question, classification)
        
        # Step 5: Format response
        if isinstance(result, str) and ('┌' in result or '╭' in result or '📊' in result):
            # Already formatted (Rich tables, etc.)
            return result
        else:
            # Format using response formatter
            return self.formatter.format(result, classification, user_lang)
    
    def _execute_function_chain(self, question: str, classification: Dict[str, Any]) -> str:
        """Execute the most appropriate function based on classification"""
        
        # Get data
        all_data = self.data_loader.load_all_data()
        print(f"📊 Loaded {len(all_data)} months of data")
        
        # Get entities
        entities = classification.get('entities', {})
        suggested_functions = classification.get('suggested_functions', [])
        
        print(f"🎯 Suggested functions: {suggested_functions}")
        
        # Try each suggested function
        for function_name in suggested_functions:
            print(f"🔄 Trying function: {function_name}")
            try:
                result = self._execute_single_function(
                    function_name, question, entities, all_data
                )
                if result and result != "Error executing function":
                    print(f"✅ Function {function_name} succeeded")
                    return result
            except Exception as e:
                print(f"⚠️ Function {function_name} failed: {e}")
                continue
        
        # Fallback response
        return self._generate_fallback_response(entities)
    
    def _execute_single_function(self, function_name: str, question: str, 
                                entities: Dict, all_data: Dict) -> str:
        """Execute a single function with appropriate parameters"""
        
        # Get the function
        func = self.function_registry.get_function(function_name)
        if not func:
            return f"Function {function_name} not found"
        
        print(f"🔧 Executing {function_name}")
        
        # Prepare parameters based on function type
        if function_name.startswith('plot_'):
            # Graph functions - call directly, they handle data loading internally
            return func()
        
        elif 'monthly' in function_name or 'month' in function_name:
            # Monthly functions need month and data
            month = entities.get('month', '七月')  # Default to July
            
            # Ensure month is not None before string comparison
            if month is None:
                month = '七月'  # Fallback default
            
            # Find matching month key
            matching_key = None
            for key in all_data.keys():
                if month and month in key:  # "七月" matches "2025-七月"
                    matching_key = key
                    break
            
            if matching_key and len(all_data[matching_key]) > 0:
                df = all_data[matching_key]
                
                # Set data loader if needed
                if hasattr(func, '__self__') and hasattr(func.__self__, 'data_loader'):
                    func.__self__.data_loader = self.data_loader
                
                # Call function with month and data
                if function_name in ['display_monthly_sheet']:
                    # This function needs file path and month name
                    from modules.data.annual_manager import AnnualManager
                    import config
                    annual_mgr = AnnualManager(config={
                        'onedrive_path': config.ONEDRIVE_PATH,
                        'template_file': '20XX年開銷表（NT）.xlsx'
                    })
                    budget_file = annual_mgr.get_active_budget_file()
                    return func(budget_file, month)
                else:
                    return func(month, df)
            else:
                return f"❌ No data available for {month}"
        
        elif 'category' in function_name or 'breakdown' in function_name:
            # Category functions
            month = entities.get('month', '七月')
            
            # Ensure month is not None
            if month is None:
                month = '七月'
            
            # Find matching month key
            matching_key = None
            for key in all_data.keys():
                if month and month in key:
                    matching_key = key
                    break
            
            if matching_key and matching_key in all_data:
                return func(month, all_data[matching_key])
            else:
                return f"❌ No data available for {month}"
        
        elif 'comparison' in function_name:
            # Comparison functions need two months
            months = list(all_data.keys())
            if len(months) >= 2:
                # Extract month names from keys (e.g., "2025-七月" -> "七月")
                month1_key = months[0]
                month2_key = months[1]
                
                # Extract month name from key
                month1_name = month1_key.split('-')[1] if '-' in month1_key else month1_key
                month2_name = month2_key.split('-')[1] if '-' in month2_key else month2_key
                
                return func(month1_name, month2_name)
            else:
                return "❌ Need at least 2 months for comparison"
        
        elif 'trend' in function_name:
            # Trend functions need category
            category = entities.get('category', '伙食费')
            
            # Ensure category is not None
            if category is None:
                category = '伙食费'
            
            return func(category)
        
        else:
            # Default execution
            return func()
    
    def _generate_fallback_response(self, entities: Dict) -> str:
        """Generate fallback response when functions fail"""
        month = entities.get('month', '本月')
        category = entities.get('category', '')
        
        # Ensure values are not None
        if month is None:
            month = '本月'
        if category is None:
            category = ''
        
        # Instead of just showing error, provide smart menu routing
        return self._generate_menu_routing_response(month, category)
    
    def _generate_menu_routing_response(self, month: str, category: str) -> str:
        """Generate response that directs user to appropriate menu"""
        
        response = "🍽️ 我了解您的需求！讓我為您指引到正確的功能位置：\n\n"
        
        # Determine what the user is looking for
        if month != '本月':
            if category:
                # Specific month + category request
                response += f"📍 **您想要查看 {month} 的 {category} 數據**\n\n"
                response += "🎯 **請前往：**\n"
                response += "   主選單 → [1] 查看預算表\n"
                response += "   或 主選單 → [3] 預算分析對話 → [2] 視覺化分析\n\n"
                response += "💡 **您將找到：**\n"
                response += f"   • {month} 的詳細交易記錄\n"
                response += f"   • {category} 分類統計\n"
                response += "   • 圖表和視覺化分析\n"
            else:
                # Specific month request
                response += f"📍 **您想要查看 {month} 的數據**\n\n"
                response += "🎯 **請前往：**\n"
                response += "   主選單 → [1] 查看預算表\n\n"
                response += "💡 **您將找到：**\n"
                response += f"   • {month} 的完整預算表\n"
                response += "   • 詳細的交易記錄\n"
                response += "   • 分類支出統計\n"
        else:
            # General request
            if category:
                # Category-specific request
                response += f"📍 **您想要查看 {category} 相關數據**\n\n"
                response += "🎯 **請前往：**\n"
                response += "   主選單 → [3] 預算分析對話 → [2] 視覺化分析\n\n"
                response += "💡 **您將找到：**\n"
                response += f"   • {category} 趨勢分析\n"
                response += "   • 分類比較圖表\n"
                response += "   • 視覺化統計資料\n"
            else:
                # General data request
                response += "📍 **您想要查看預算數據**\n\n"
                response += "🎯 **請前往：**\n"
                response += "   主選單 → [1] 查看預算表 (瀏覽數據)\n"
                response += "   主選單 → [3] 預算分析對話 → [2] 視覺化分析 (圖表)\n\n"
                response += "💡 **您將找到：**\n"
                response += "   • 完整的預算表格\n"
                response += "   • 各種圖表和視覺化\n"
                response += "   • 比較分析功能\n"
        
        response += "\n🔄 **提示：** 返回主選單按 'x' 即可"
        
        return response
    
    def get_available_functions(self) -> Dict[str, str]:
        """Get list of available functions"""
        return self.function_registry.list_all_functions()
