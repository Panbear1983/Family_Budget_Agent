"""
GPT-OSS:20b Engine - Deep reasoning and conversation
Powerful, good at explanations and financial advice
"""

from typing import Tuple, Dict
from .base_llm import BaseLLM

class GptOssEngine(BaseLLM):
    """GPT-OSS:20b - Optimized for reasoning tasks"""
    
    def _setup(self):
        """Initialize GPT-OSS engine"""
        if 'model' not in self.config:
            self.config['model'] = 'gpt-oss:20b'
        
        self.model_name = self.config['model']
        print(f"  🧠 GPT-OSS Engine loaded: {self.model_name}")
    
    def call_model(self, prompt: str) -> str:
        """Call GPT-OSS model"""
        return self._call_ollama(prompt)
    
    def categorize(self, transaction: dict) -> Tuple[str, float]:
        """
        Intelligent categorization with reasoning
        """
        desc = transaction.get('description', '')
        amount = transaction.get('amount', 0)
        qwen_guess = transaction.get('qwen_guess', '')
        
        prompt = f"""You are a financial expert categorizing expenses.

Transaction:
- Description: {desc}
- Amount: NT${amount}
- AI suggestion: {qwen_guess}

Categorize into ONE of these:
- 交通费 (transportation)
- 伙食费 (food/dining)  
- 休闲/娱乐 (entertainment)
- 家務 (household)
- 其它 (other)

Think step by step:
1. What type of expense is this?
2. What's the primary purpose?
3. Which category fits best?

Respond: category|confidence|reasoning

Example: 伙食费|0.95|This is clearly a food expense at a restaurant"""
        
        response = self.call_model(prompt)
        
        # Parse response
        try:
            parts = response.split('|')
            if len(parts) >= 2:
                category = parts[0].strip()
                confidence = float(parts[1].strip())
                return category, confidence
        except:
            pass
        
        # Extract category from response
        categories = ['交通费', '伙食费', '休闲/娱乐', '家务', '其它']
        category = next((c for c in categories if c in response), '其它')
        return category, 0.9  # High confidence for GPT-OSS
    
    def check_duplicate(self, tx1: dict, tx2: dict) -> Tuple[bool, float]:
        """
        Enhanced duplicate detection (uses parent's simple check first)
        """
        is_dup, confidence = super().check_duplicate(tx1, tx2)
        
        # If highly confident from simple check, return
        if confidence > 0.95:
            return is_dup, confidence
        
        # Otherwise, use fuzzy matching
        is_dup, reason = self.fuzzy_duplicate(tx1, tx2)
        return is_dup, 0.9  # High confidence from GPT-OSS
    
    def fuzzy_duplicate(self, tx1: dict, tx2: dict) -> Tuple[bool, str]:
        """
        Intelligent duplicate detection with reasoning
        """
        prompt = f"""Are these two transactions duplicates?

Transaction 1:
- Date: {tx1.get('date')}
- Amount: NT${tx1.get('amount')}
- Description: {tx1.get('description')}

Transaction 2:
- Date: {tx2.get('date')}
- Amount: NT${tx2.get('amount')}
- Description: {tx2.get('description')}

Consider:
- Same merchant/vendor?
- Same purpose?
- Could this be the same purchase?

Answer: YES or NO, then explain why in one sentence."""
        
        response = self.call_model(prompt)
        
        is_duplicate = 'YES' in response.upper()[:20]
        reason = response.split('\n')[0] if '\n' in response else response
        
        return is_duplicate, reason
    
    def validate_outlier(self, transaction: dict, context: dict) -> Tuple[bool, str]:
        """
        Validate unusual transactions with context
        """
        prompt = f"""Validate this unusual transaction.

Transaction:
- Amount: NT${transaction.get('amount')}
- Category: {transaction.get('category')}
- Description: {transaction.get('description')}
- Date: {transaction.get('date')}

Context:
- Historical average: NT${context.get('avg_amount', 0)}
- This is {context.get('times_avg', '?')}x the normal amount

Is this transaction valid or suspicious?
Provide reasoning."""
        
        response = self.call_model(prompt)
        
        is_valid = 'VALID' in response.upper() or 'LEGITIMATE' in response.upper()
        explanation = response[:200]  # First 200 chars
        
        return is_valid, explanation
    
    def analyze_trends(self, stats: dict) -> str:
        """
        Generate insights from statistics (GPT-OSS's strength)
        """
        prompt = f"""You are a financial advisor analyzing budget trends.

Statistics:
{stats.get('response', '')}

Provide:
1. Key spending patterns
2. Potential concerns
3. Specific recommendations

Be concise and actionable. Use both Chinese and English where helpful."""
        
        return self.call_model(prompt)
    
    def answer(self, question: str, data: dict) -> str:
        """
        Answer complex questions with reasoning
        """
        prompt = f"""You are a budget advisor. Answer this question using the data.

Question: {question}

Budget Data: {str(data)[:1000]}

Provide a thoughtful answer with:
- Specific numbers
- Clear reasoning
- Actionable advice

Keep under 200 words."""
        
        return self.call_model(prompt)
    
    def reason(self, question: str, data: dict) -> str:
        """
        Provide deep reasoning and advice
        """
        prompt = f"""Analyze this question deeply and provide expert advice.

Question: {question}
Data: {str(data)[:1000]}

Think through:
1. What's really being asked?
2. What does the data tell us?
3. What should the user do?

Provide detailed, actionable guidance."""
        
        return self.call_model(prompt)

