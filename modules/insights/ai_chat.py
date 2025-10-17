"""
AI Chat - Main controller orchestrating all smart components
Unified conversational interface for budget analysis
"""

from typing import Optional
from .language_detector import LanguageDetector
from .question_classifier import QuestionClassifier
from .instant_answers import InstantAnswers
from .data_preprocessor import DataPreprocessor
from .prompt_builder import PromptBuilder
from .response_formatter import ResponseFormatter
from .guardrails import Guardrails
from .localized_templates import LocalizedTemplates as T

class AIChat:
    """Main AI Chat controller - orchestrates all smart components"""
    
    def __init__(self, data_loader, orchestrator, context_manager,
                 insight_generator, trend_analyzer):
        """
        Initialize AI Chat system (Text-only conversational AI)
        
        Args:
            data_loader: DataLoader instance
            orchestrator: LLM orchestrator
            context_manager: ContextManager instance
            insight_generator: InsightGenerator instance
            trend_analyzer: TrendAnalyzer instance
        """
        # Core dependencies
        self.data_loader = data_loader
        self.orchestrator = orchestrator
        self.context_manager = context_manager
        self.insight_generator = insight_generator
        self.trend_analyzer = trend_analyzer
        
        # Initialize smart components
        self.lang_detector = LanguageDetector(default_language='auto')
        self.classifier = QuestionClassifier()
        self.instant = InstantAnswers(data_loader, orchestrator)  # Pass orchestrator for LLM fallback
        self.preprocessor = DataPreprocessor(data_loader, insight_generator, trend_analyzer)
        self.prompt_builder = PromptBuilder()
        self.formatter = ResponseFormatter(self.lang_detector)
        self.guardrails = Guardrails(data_loader, self.lang_detector)
        
        # Initialize confidence tracker
        from .confidence_tracker import ConfidenceTracker
        self.confidence_tracker = ConfidenceTracker()
        
        # Load config
        import config
        self.chat_config = getattr(config, 'AI_CHAT_CONFIG', {
            'show_confidence': True,
            'confidence_threshold': 0.6,
            'verbose_uncertainty': True,
            'show_uncertainty_warning': True
        })
        
        print("✅ AI Chat initialized with full intelligence stack + confidence tracking")
    
    def answer_question(self, question: str) -> str:
        """
        Universal question answering with full intelligence pipeline + confidence tracking
        
        Args:
            question: User's question
        
        Returns:
            Formatted answer with confidence score
        """
        # ═══════════════════════════════════════════════════════════
        # Initialize confidence tracking
        # ═══════════════════════════════════════════════════════════
        confidence_components = {
            'data_available': 1.0,
            'question_clear': 1.0,
            'llm_confident': 1.0,
            'guardrail_passed': 1.0,
            'response_verified': 1.0
        }
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: Detect Language
        # ═══════════════════════════════════════════════════════════
        user_lang, lang_confidence = self.lang_detector.detect(question)
        response_lang = self.lang_detector.get_response_language(user_lang, allow_mixed=True)
        
        # ═══════════════════════════════════════════════════════════
        # LAYER 1: Topic Relevance Check (WHITELIST-ONLY)
        # ═══════════════════════════════════════════════════════════
        is_allowed, topic_cat, redirect_msg = self.guardrails.check_topic_relevance(
            question, user_lang
        )
        
        if not is_allowed:
            # Off-topic → Polite redirect with 0% confidence
            if self.chat_config.get('show_confidence'):
                redirect_msg += self.confidence_tracker.format_confidence_footer(
                    0.0, 'very_low', {'guardrail_passed': 0.0}, user_lang, False
                )
            return redirect_msg
        
        # ═══════════════════════════════════════════════════════════
        # LAYER 1.5: Conversation Drift Check
        # ═══════════════════════════════════════════════════════════
        allow_continue, boundary_msg = self.guardrails.enforce_conversation_boundary(
            question,
            self.context_manager.history,
            user_lang
        )
        
        if not allow_continue:
            return boundary_msg
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: Classify Question Type & Extract Entities
        # ═══════════════════════════════════════════════════════════
        classification = self.classifier.classify(question)
        q_type = classification['type']
        handler = classification['handler']
        entities = classification['entities']
        
        # Assess question clarity from classification
        confidence_components['question_clear'] = self.confidence_tracker.assess_question_clarity(
            classification
        )
        
        # ═══════════════════════════════════════════════════════════
        # LAYER 2: Data Scope Validation
        # ═══════════════════════════════════════════════════════════
        is_valid, error_msg = self.guardrails.validate_data_scope(entities, user_lang)
        
        # Assess data availability
        available_data = {
            'months': list(self.data_loader.load_all_data().keys()),
            'categories': self.guardrails.available_categories
        }
        confidence_components['data_available'] = self.confidence_tracker.assess_data_availability(
            entities, available_data
        )
        
        if not is_valid:
            # Requested data doesn't exist → Show with low confidence
            if self.chat_config.get('show_confidence'):
                error_msg += self.confidence_tracker.format_confidence_footer(
                    0.3, 'very_low', {'data_available': 0.0}, user_lang, False
                )
            return error_msg
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3: Route to Appropriate Handler
        # ═══════════════════════════════════════════════════════════
        
        # Handle complex questions with simple fallback
        if handler == 'no_answer':
            return T.get('redirects', 'no_answer', user_lang)
        
        # Redirect visualization requests to Mode 2
        if handler == 'redirect_visual':
            if user_lang == 'zh':
                return "📊 圖表和視覺化功能請使用「視覺化分析」模式\n\n💡 請返回主選單，選擇選項 [2] 📊 視覺化分析"
            else:
                return "📊 For charts and visualizations, please use 'Visual Analysis' mode\n\n💡 Return to main menu and select option [2] Visual Analysis"
        
        if handler == 'instant':
            # ═══════════════════════════════════════════════════════════
            # 3-TIER APPROACH: Python → Summary LLM → Full Data LLM
            # ═══════════════════════════════════════════════════════════
            
            # TIER 1: Try instant answer (Python-only, no LLM) ⚡
            answer = self.instant.try_answer(question, entities, user_lang)
            
            if answer:
                # Python succeeded - high confidence
                confidence_components['llm_confident'] = 1.0
                confidence_components['response_verified'] = 1.0
                tier_used = "Tier 1 (Python)"
            else:
                # TIER 2: Python failed, try LLM with summary data 🧠
                print("  ⚡ Tier 1 failed → Trying Tier 2 (LLM + Summary)...", end='', flush=True)
                answer = self.instant.try_llm_with_summary(question, entities, user_lang)
                
                if answer and len(answer) > 10:  # Got a reasonable answer
                    confidence_components['llm_confident'] = 0.8
                    confidence_components['response_verified'] = 0.8
                    tier_used = "Tier 2 (Summary)"
                else:
                    # TIER 3: Summary failed, use FULL Excel data 📊
                    print("\r  ⚡ Tier 2 uncertain → Using Tier 3 (Full Data)...", end='', flush=True)
                    answer = self.instant.try_llm_with_full_data(question, entities, user_lang)
                    confidence_components['llm_confident'] = 0.7
                    confidence_components['response_verified'] = 0.7
                    tier_used = "Tier 3 (Full Data)"
            
            # Calculate confidence
            conf_score, conf_level = self.confidence_tracker.calculate_confidence(
                confidence_components
            )
            
            # Format with confidence
            formatted = self.formatter.format(answer, classification, user_lang)
            
            if self.chat_config.get('show_confidence'):
                formatted += self.confidence_tracker.format_confidence_footer(
                    conf_score, conf_level, confidence_components, user_lang,
                    self.chat_config.get('verbose_uncertainty', True)
                )
            
            # Add tier info for debugging (if verbose)
            if self.chat_config.get('verbose_uncertainty') and conf_score < 0.8:
                formatted += f"\n   ℹ️ {tier_used}"
            
            self._store_interaction(question, formatted, classification)
            return formatted
        
        if handler == 'forecast':
            # Handle forecast request
            return self._handle_forecast(entities, user_lang, classification)
        
        if handler == 'compare':
            # Handle comparison request
            return self._handle_comparison(entities, user_lang, classification)
        
        if handler == 'optimize':
            # Handle optimization/savings request (uses dual pipeline if enabled)
            return self._handle_optimization(user_lang, classification, entities)
        
        # ═══════════════════════════════════════════════════════════
        # STEP 4: Prepare Data for LLM (if needed)
        # ═══════════════════════════════════════════════════════════
        prepared_data = self.preprocessor.prepare_for_llm(question, entities)
        
        # ═══════════════════════════════════════════════════════════
        # STEP 5: Route to Appropriate LLM Pipeline
        # ═══════════════════════════════════════════════════════════
        
        # Check dual pipeline configuration
        use_dual = self.chat_config.get('use_dual_pipeline', True)
        dual_mode = self.chat_config.get('dual_pipeline_mode', 'smart')
        
        if handler in ['data', 'trend']:
            # Qwen only (fast data extraction) - no dual pipeline needed
            prompt = self.prompt_builder.build_qwen_prompt(question, prepared_data, user_lang)
            raw_answer = self.orchestrator.qwen.call_model(prompt)
        
        elif handler in ['insight', 'advice']:
            # Always use dual LLM: Qwen extracts → GPT-OSS reasons
            print("  ⚡ Using dual pipeline (Qwen → GPT-OSS)...", flush=True)
            raw_answer = self._dual_llm_pipeline(question, prepared_data, user_lang, q_type)
        
        elif dual_mode == 'always' and use_dual:
            # ALWAYS MODE: Use dual pipeline for ALL question types
            print("  ⚡ Using dual pipeline (Qwen → GPT-OSS) [always mode]...", flush=True)
            raw_answer = self._dual_llm_pipeline(question, prepared_data, user_lang, q_type)
        
        else:
            # Default: GPT-OSS for complex questions (single pipeline)
            prompt = self.prompt_builder.build_insight_prompt(question, prepared_data, user_lang)
            raw_answer = self.orchestrator.gpt_oss.call_model(prompt)
        
        # Assess LLM confidence from response
        confidence_components['llm_confident'] = self.confidence_tracker.assess_llm_confidence(
            raw_answer
        )
        
        # ═══════════════════════════════════════════════════════════
        # LAYER 3: Response Validation (Guardrails)
        # ═══════════════════════════════════════════════════════════
        is_valid, validated_answer, warnings = self.guardrails.validate_response(
            raw_answer,
            prepared_data,
            user_lang
        )
        
        # Update confidence based on guardrail results
        confidence_components['guardrail_passed'] = 1.0 if is_valid else 0.6
        confidence_components['response_verified'] = 1.0 if len(warnings) == 0 else 0.7
        
        # ═══════════════════════════════════════════════════════════
        # Calculate Overall Confidence
        # ═══════════════════════════════════════════════════════════
        conf_score, conf_level = self.confidence_tracker.calculate_confidence(
            confidence_components
        )
        
        # ═══════════════════════════════════════════════════════════
        # Add Uncertainty Warning if Needed
        # ═══════════════════════════════════════════════════════════
        if (self.chat_config.get('show_uncertainty_warning') and 
            conf_score < self.chat_config.get('confidence_threshold', 0.6)):
            
            # Determine reason for uncertainty
            reason = self.confidence_tracker.determine_uncertainty_reason(confidence_components)
            uncertainty_msg = self.confidence_tracker.get_uncertainty_message(
                conf_score, reason, user_lang
            )
            if uncertainty_msg:
                validated_answer = uncertainty_msg + "\n\n" + validated_answer
        
        # Add validation warnings if any
        if warnings:
            validated_answer += "\n\n" + "  ".join(warnings)
        
        # ═══════════════════════════════════════════════════════════
        # STEP 6: Format & Enhance Response
        # ═══════════════════════════════════════════════════════════
        formatted_answer = self.formatter.format(validated_answer, classification, user_lang)
        
        # ═══════════════════════════════════════════════════════════
        # Add Confidence Footer
        # ═══════════════════════════════════════════════════════════
        if self.chat_config.get('show_confidence'):
            formatted_answer += self.confidence_tracker.format_confidence_footer(
                conf_score, conf_level, confidence_components, user_lang,
                self.chat_config.get('verbose_uncertainty', True)
            )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 7: Store in Context
        # ═══════════════════════════════════════════════════════════
        self._store_interaction(question, formatted_answer, classification)
        
        return formatted_answer
    
    def _dual_llm_pipeline(self, question: str, prepared_data: dict, 
                           language: str, q_type: str) -> str:
        """
        Dual LLM pipeline: Qwen extracts → GPT-OSS reasons
        
        Args:
            question: User's question
            prepared_data: Preprocessed data
            language: Response language
            q_type: Question type (insight/advice)
        
        Returns:
            Final answer from GPT-OSS
        """
        # Step 1: Qwen extracts data
        qwen_prompt = self.prompt_builder.build_qwen_prompt(question, prepared_data, language)
        qwen_output = self.orchestrator.qwen.call_model(qwen_prompt)
        
        # Step 2: Get conversation context
        context = self.context_manager.get_context_summary()
        
        # Step 3: GPT-OSS provides reasoning/advice
        if q_type == 'advice':
            gpt_prompt = self.prompt_builder.build_advice_prompt(question, prepared_data, language)
        else:
            gpt_prompt = self.prompt_builder.build_gpt_oss_prompt(
                question, qwen_output, context, language
            )
        
        gpt_answer = self.orchestrator.gpt_oss.call_model(gpt_prompt)
        
        return gpt_answer
    
    def _handle_forecast(self, entities: dict, language: str, classification: dict) -> str:
        """Handle forecast requests"""
        
        category = entities.get('category', None)
        forecast_data = self.preprocessor.prepare_for_forecast(category)
        
        if 'error' in forecast_data:
            return T.get('errors', 'insufficient_data', language, required=3)
        
        # Build forecast prompt for GPT-OSS explanation
        prompt = self.prompt_builder.build_forecast_prompt(forecast_data, language)
        explanation = self.orchestrator.gpt_oss.call_model(prompt)
        
        # Format with template
        forecast_summary = T.get('forecast', 'full', language,
                                amount=forecast_data.get('forecast_amount', 0),
                                confidence=forecast_data.get('confidence', 'medium'),
                                months=forecast_data.get('based_on_months', 3),
                                suggested=forecast_data.get('suggested_budget', 0))
        
        return f"{forecast_summary}\n\n{explanation}"
    
    def _handle_comparison(self, entities: dict, language: str, classification: dict) -> str:
        """Handle month comparison"""
        
        months = entities.get('months', [])
        
        if len(months) < 2:
            if language == 'zh':
                return "❌ 請指定要比較的月份，例如：'比較七月和八月'"
            else:
                return "❌ Please specify months to compare, e.g., 'compare July and August'"
        
        comparison = self.insight_generator.generate_comparison(months[0], months[1])
        
        if 'error' in comparison:
            return T.get('errors', 'no_comparison', language, month1=months[0], month2=months[1])
        
        # Build comparison prompt
        prepared_data = {'relevant_stats': {'comparison': comparison}}
        prompt = self.prompt_builder.build_comparison_prompt(prepared_data, language)
        analysis = self.orchestrator.gpt_oss.call_model(prompt)
        
        # Add formatted table
        table = self.formatter.format_comparison_table(comparison, language)
        
        return f"{table}\n\n{analysis}"
    
    def _handle_optimization(self, language: str, classification: dict, entities: dict) -> str:
        """
        Handle optimization/savings requests using dual pipeline
        Qwen extracts spending patterns → GPT-OSS provides strategic advice
        """
        
        opt_data = self.preprocessor.prepare_for_optimization()
        
        if 'error' in opt_data:
            return "❌ " + opt_data['error']
        
        # Check if dual pipeline is enabled
        use_dual = self.chat_config.get('use_dual_pipeline', True)
        dual_mode = self.chat_config.get('dual_pipeline_mode', 'smart')
        
        if use_dual and dual_mode in ['smart', 'always']:
            # ═══════════════════════════════════════════════════════════
            # DUAL PIPELINE: Qwen extracts → GPT-OSS advises
            # ═══════════════════════════════════════════════════════════
            
            # STAGE 1: Qwen extracts spending patterns and data
            if language == 'zh':
                qwen_prompt = f"""從預算資料中提取支出模式和關鍵數據。

資料:
- 異常交易: {len(opt_data.get('anomalies', []))} 筆
- 高比例類別: {opt_data.get('high_percentage_categories', {})}
- 總支出: NT${opt_data.get('total_spending', 0):,.0f}
- 月度趨勢: {opt_data.get('monthly_trends', {})}

任務: 列出所有高支出類別、異常交易、和支出趨勢。只提取數據，不要給建議。"""
            else:
                qwen_prompt = f"""Extract spending patterns and key data from budget.

Data:
- Anomalies: {len(opt_data.get('anomalies', []))} transactions
- High-% categories: {opt_data.get('high_percentage_categories', {})}
- Total spending: NT${opt_data.get('total_spending', 0):,.0f}
- Monthly trends: {opt_data.get('monthly_trends', {})}

Task: List all high-spending categories, anomalies, and trends. Extract data only, no advice."""
            
            print("  ⚡ Stage 1: Qwen extracting spending patterns...", end='', flush=True)
            qwen_output = self.orchestrator.qwen.call_model(qwen_prompt)
            print("\r  ✓ Stage 1: Complete                              ", flush=True)
            
            # STAGE 2: GPT-OSS provides strategic optimization advice
            context = self.context_manager.get_context_summary()
            
            if language == 'zh':
                gpt_prompt = f"""根據支出分析，提供優化建議。

【Qwen 提取的數據】
{qwen_output}

【對話歷史】
{context}

【任務】
提供:
1. 主要問題分析 (為什麼支出高？)
2. 3-5個具體可行的建議
3. 預估每個建議能節省的金額
4. 優先順序排序

使用清晰、具體、可執行的語言。聚焦在實際可行的方案。"""
            else:
                gpt_prompt = f"""Provide optimization advice based on spending analysis.

【Data Extracted by Qwen】
{qwen_output}

【Conversation Context】
{context}

【Task】
Provide:
1. Root cause analysis (why spending is high?)
2. 3-5 specific actionable recommendations
3. Estimated savings for each recommendation
4. Priority ranking

Use clear, specific, actionable language. Focus on practical solutions."""
            
            print("  🧠 Stage 2: GPT-OSS generating strategic advice...", end='', flush=True)
            advice = self.orchestrator.gpt_oss.call_model(gpt_prompt)
            print("\r  ✓ Stage 2: Complete                                 ", flush=True)
            
        else:
            # ═══════════════════════════════════════════════════════════
            # SINGLE PIPELINE: GPT-OSS only (fallback)
            # ═══════════════════════════════════════════════════════════
            if language == 'zh':
                prompt = f"""分析這個預算資料，找出可以節省的地方。

資料:
- 異常交易: {len(opt_data.get('anomalies', []))} 筆
- 高比例類別: {opt_data.get('high_percentage_categories', {})}
- 總支出: NT${opt_data.get('total_spending', 0):,.0f}

提供:
1. 主要問題 (高支出類別)
2. 具體建議 (如何減少)
3. 預估節省金額

使用清晰、具體的語言。"""
            else:
                prompt = f"""Analyze this budget data to find savings opportunities.

Data:
- Anomalies: {len(opt_data.get('anomalies', []))} transactions
- High-% categories: {opt_data.get('high_percentage_categories', {})}
- Total spending: NT${opt_data.get('total_spending', 0):,.0f}

Provide:
1. Main issues (high-spending categories)
2. Specific recommendations (how to reduce)
3. Estimated savings amount

Use clear, specific language."""
            
            advice = self.orchestrator.gpt_oss.call_model(prompt)
        
        # Format with action items
        formatted = self.formatter.add_action_items(advice, 'optimization', language)
        
        return f"🔍 {'節省機會分析:' if language == 'zh' else 'Savings Analysis:'}\n\n{formatted}"
    
    def _store_interaction(self, question: str, answer: str, classification: dict):
        """Store interaction in context manager"""
        metadata = {
            'type': classification.get('type'),
            'handler': classification.get('handler'),
            'entities': classification.get('entities')
        }
        
        self.context_manager.add_interaction(question, answer, metadata)

