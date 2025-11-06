"""
LLM Orchestrator - Intelligent routing between Qwen and GPT-OSS
Implements the optimized dual-LLM workflow
"""

from typing import Dict, Any, Tuple
from .module_registry import registry
import config

class LLMOrchestrator:
    """
    Orchestrates collaboration between Qwen3:8b and GPT-OSS:20b
    Implements confidence-based handoff and smart routing
    """
    
    def __init__(self):
        self.qwen = None
        self.gpt_oss = None
        self.confidence_threshold = 0.85  # Hand off to GPT-OSS if below this
    
    def initialize(self):
        """Load LLM modules from registry"""
        # Get config with timeout settings
        qwen_config = config.LLM_CONFIG.get('structured', {})
        gpt_config = config.LLM_CONFIG.get('reasoning', {})
        
        self.qwen = registry.get_module('QwenEngine', config=qwen_config)
        self.gpt_oss = registry.get_module('GptOssEngine', config=gpt_config)
        
        if not self.qwen or not self.gpt_oss:
            raise RuntimeError("Failed to load LLM engines")
        
        print("✅ LLM Orchestrator initialized")
        return True
    
    def categorize_transaction(self, transaction: Dict) -> Tuple[str, float]:
        """
        Categorize with confidence-based handoff
        Returns: (category, confidence)
        """
        # Step 1: Qwen first pass (fast)
        category, confidence = self.qwen.execute('categorize', transaction)
        
        # Step 2: If uncertain, ask GPT-OSS (smart)
        if confidence < self.confidence_threshold:
            print(f"  ⚡ Qwen uncertain ({confidence:.0%}) → Handing off to GPT-OSS")
            category, confidence = self.gpt_oss.execute('categorize', transaction)
        
        return category, confidence
    
    def detect_duplicate(self, tx1: Dict, tx2: Dict) -> Tuple[bool, str]:
        """
        Duplicate detection with smart handoff
        Returns: (is_duplicate, reason)
        """
        # Step 1: Qwen exact match (fast)
        is_dup, confidence = self.qwen.execute('check_duplicate', tx1, tx2)
        
        if confidence >= 0.95:
            # Qwen is very confident
            return is_dup, "Exact match" if is_dup else "Clear difference"
        
        # Step 2: GPT-OSS fuzzy match (smart)
        print(f"  ⚡ Potential duplicate → GPT-OSS analyzing")
        is_dup, reason = self.gpt_oss.execute('fuzzy_duplicate', tx1, tx2)
        return is_dup, reason
    
    def validate_outlier(self, transaction: Dict, context: Dict) -> Tuple[bool, str]:
        """
        Validate unusual transactions
        Returns: (is_valid, explanation)
        """
        # Always use GPT-OSS for outlier validation (needs context)
        return self.gpt_oss.execute('validate_outlier', transaction, context)
    
    def generate_insights(self, data: Dict) -> str:
        """
        Generate financial insights
        Uses both LLMs: Qwen for stats, GPT-OSS for reasoning
        """
        # Step 1: Qwen calculates statistics (fast)
        stats = self.qwen.execute('calculate_stats', data)
        
        # Step 2: GPT-OSS generates insights from stats (reasoning)
        insights = self.gpt_oss.execute('analyze_trends', stats)
        
        return insights
    
    def answer_question(self, question: str, data: Dict) -> str:
        """
        Answer user questions with smart routing
        """
        # Check if topic filtering is enabled and validate budget-related topic
        topic_filter = config.AI_CHAT_CONFIG.get('topic_filter', {})
        if topic_filter.get('enabled', False):
            if not self._is_budget_related(question):
                return topic_filter.get('decline_message', 
                    "Hey, I'm your budget consultant, not your everything consultant. Stick to money, spending, and budget questions, okay? 😏")
        
        # Analyze question type (preserves keyword routing for data access)
        question_type = self._classify_question(question)
        
        if question_type == 'simple_query':
            # Route to Qwen (fast data extraction)
            return self.qwen.execute('query', question, data)
        
        elif question_type == 'reasoning':
            # Route to GPT-OSS (needs understanding)
            return self.gpt_oss.execute('answer', question, data)
        
        elif question_type == 'complex':
            # Use both: Qwen extracts → GPT-OSS reasons
            extracted = self.qwen.execute('extract_data', question, data)
            answer = self.gpt_oss.execute('reason', question, extracted)
            return answer
        
        # Default: Use GPT-OSS
        return self.gpt_oss.execute('answer', question, data)
    
    def _is_budget_related(self, question: str) -> bool:
        """
        Check if question is budget-related
        Uses keyword matching to identify budget topics
        """
        question_lower = question.lower()
        
        # Budget-related keywords (preserves same keyword structure for data access)
        budget_keywords = [
            # English keywords
            'budget', 'spending', 'expense', 'expenditure', 'cost', 'money', 'spent', 'spend',
            'category', 'categories', 'month', 'monthly', 'year', 'yearly', 'annual',
            'food', 'transportation', 'entertainment', 'household', 'other',
            'total', 'sum', 'amount', 'payment', 'transaction', 'purchase',
            'trend', 'pattern', 'analysis', 'comparison', 'compare',
            'saving', 'save', 'financial', 'finance', 'costs', 'price',
            # Chinese keywords (preserves Chinese month/category access)
            '預算', '支出', '開銷', '花費', '金錢', '費用', '花錢', '花',
            '分類', '月份', '年度', '月度', '月度', '月', '年',
            '交通费', '伙食费', '休闲/娱乐', '休闲', '娱乐', '家务', '其它',
            '總', '總額', '總計', '合計', '金額', '數額',
            '趨勢', '比較', '對比', '分析', '統計',
            '節省', '省', '財務', '金融'
        ]
        
        return any(kw in question_lower for kw in budget_keywords)
    
    def _classify_question(self, question: str) -> str:
        """
        Classify question type for routing
        Preserves keyword-based routing for data access
        """
        question_lower = question.lower()
        
        # Simple queries (Qwen) - preserves keyword structure
        simple_keywords = ['how much', '多少', 'total', '總', 'sum', 'count']
        if any(kw in question_lower for kw in simple_keywords):
            return 'simple_query'
        
        # Reasoning questions (GPT-OSS)
        reasoning_keywords = ['why', '為什麼', 'should', '應該', 'recommend', 'advice']
        if any(kw in question_lower for kw in reasoning_keywords):
            return 'reasoning'
        
        # Complex (both)
        complex_keywords = ['compare', 'forecast', '預測', '比較']
        if any(kw in question_lower for kw in complex_keywords):
            return 'complex'
        
        # Default
        return 'reasoning'
    
    def batch_process(self, transactions: list) -> list:
        """
        Process multiple transactions efficiently
        Qwen handles bulk, GPT-OSS handles edge cases
        """
        results = []
        uncertain = []
        
        print(f"📊 Processing {len(transactions)} transactions...")
        
        # Step 1: Qwen processes all (fast)
        for tx in transactions:
            category, confidence = self.qwen.execute('categorize', tx)
            
            if confidence >= self.confidence_threshold:
                results.append({**tx, 'category': category, 'confidence': confidence})
            else:
                uncertain.append({**tx, 'qwen_guess': category, 'confidence': confidence})
        
        print(f"  ✅ Qwen: {len(results)} confident ({len(results)/len(transactions)*100:.0f}%)")
        
        # Step 2: GPT-OSS handles uncertain cases
        if uncertain:
            print(f"  🤔 GPT-OSS refining {len(uncertain)} uncertain cases...")
            for tx in uncertain:
                category, confidence = self.gpt_oss.execute('categorize', tx)
                results.append({**tx, 'category': category, 'confidence': confidence})
        
        return results

