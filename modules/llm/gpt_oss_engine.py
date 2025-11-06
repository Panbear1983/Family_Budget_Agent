"""
GPT-OSS:20b Engine - Deep reasoning and conversation
Powerful, good at explanations and financial advice
"""

from typing import Tuple, Dict
from .base_llm import BaseLLM
import config

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
    
    def _get_personality_prompt(self) -> str:
        """
        Build personality context based on config
        Returns role description and style guidelines
        """
        personality_config = config.AI_CHAT_CONFIG.get('personality', {})
        
        if not personality_config.get('enabled', False):
            return ""  # No personality if disabled
        
        style = personality_config.get('style', 'humorous_casual')
        allow_swear = personality_config.get('allow_swear_words', True)
        swear_freq = personality_config.get('swear_frequency', 'sparing')
        use_humor = personality_config.get('use_humor', True)
        bilingual = personality_config.get('bilingual', True)
        short_paragraphs = personality_config.get('short_paragraphs', True)
        data_citation = personality_config.get('data_citation', True)
        
        personality = "You are a budget spending consultant with a fun, humorous personality. "
        
        if use_humor:
            personality += "You're friendly, direct, and keep things real. "
        
        if allow_swear:
            if swear_freq == 'sparing':
                personality += "You swear occasionally (fuck, shit, damn, etc.) to add flavor - use sparingly, not every sentence. "
            elif swear_freq == 'moderate':
                personality += "You swear moderately (fuck, shit, damn, etc.) when it fits. "
            elif swear_freq == 'frequent':
                personality += "You swear freely (fuck, shit, damn, etc.) to keep it real. "
        
        if bilingual:
            personality += "Use both Chinese and English naturally in your responses. "
        
        personality += "\n\n**CRITICAL RULES:**\n"
        personality += "1. ONLY answer questions related to budget, spending, expenses, or financial data\n"
        personality += "2. If asked about non-budget topics, politely decline\n"
        
        if data_citation:
            personality += "3. ALWAYS base your answer on the Excel file data provided - NEVER make up numbers or invent facts\n"
            personality += "4. If the data doesn't contain what's needed, say so clearly: 'Damn, I don't see that in your Excel file, so I can't give you an answer'\n"
            personality += "5. Reference specific months/categories from the data when giving advice (e.g., 'In 七月, you spent NT$50k on 伙食费')\n"
        
        if short_paragraphs:
            personality += "6. For spending feedback/analysis, keep paragraphs SHORT (2-3 sentences max)\n"
        
        personality += "7. Be conversational, use contractions, and throw in some humor when appropriate\n"
        
        return personality
    
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
        Generate insights from statistics - Budget Advisor style
        """
        personality_context = self._get_personality_prompt()
        
        prompt = f"""{personality_context}

You're reviewing spending trends from the Excel file with personality.

**Statistics from Excel File:**
{stats.get('response', '')}

**Your Task:**
1. Key spending patterns (cite specific months/categories from Excel, e.g., "In 七月 vs 八月, 伙食费 went from NT$30k to NT$50k")
2. Concerns (be direct, maybe swear if it's bad: "Holy shit, you spent NT$30k on food in July!")
3. Recommendations (short and actionable - 2-3 sentences max per insight)

Keep it real, keep it short, keep it budget-focused. Always reference specific data from the Excel file:"""
        
        return self.call_model(prompt)
    
    def answer(self, question: str, data: dict) -> str:
        """
        Answer complex questions with reasoning - Budget Advisor with personality
        """
        personality_context = self._get_personality_prompt()
        
        # Build data context with proper labeling (preserves keyword structure)
        data_summary = str(data.get('stats', {}))
        available_months = data.get('available_months', [])
        data_source = data.get('data_source', 'Annual Excel Budget File')
        
        # Format data with clear labels for hallucination prevention
        data_context = f"""**Your Excel Budget Data (from {data_source}):**
{data_summary[:800]}

**Available Months in Excel:** {', '.join(available_months) if available_months else 'None'}

**Data Structure (use these labels):**
- stats: Statistics from Excel file
- available_months: List of months with data (format: "2025-七月", "2025-八月", etc.)
- by_category: Spending breakdown by category (交通费, 伙食费, 休闲/娱乐, 家务, 其它)
- monthly_totals: Total spending per month"""
        
        prompt = f"""{personality_context}

**User Question:** {question}

{data_context}

**Your Response Style:**
- Be concise but friendly
- Use swear words sparingly for emphasis (if enabled)
- Reference specific numbers from the Excel data above
- Cite which month/category you're referencing (e.g., "In 七月, you spent NT$50k on 伙食费")
- If spending is high, be direct but humorous: "Damn, you spent NT$50k on food this month? That's... a lot, bro."
- Keep spending feedback short - 2-3 sentences max
- Always base your answer on the Excel data - NEVER invent facts

Now answer the question using ONLY the data above:"""
        
        return self.call_model(prompt)
    
    def reason(self, question: str, data: dict) -> str:
        """
        Provide deep reasoning and advice - Budget Advisor style
        """
        personality_context = self._get_personality_prompt()
        
        # Handle both dict and extracted data formats
        if isinstance(data, dict) and 'extracted' in data:
            # This is from complex queries - Qwen extracted data
            data_context = f"""**Extracted Data from Excel:**
{data.get('extracted', '')}

**Source:** {data.get('source', 'qwen3:8b')}"""
        else:
            # Standard data format
            data_summary = str(data.get('stats', {}))
            available_months = data.get('available_months', [])
            data_source = data.get('data_source', 'Annual Excel Budget File')
            
            data_context = f"""**Your Excel Budget Data (from {data_source}):**
{data_summary[:800]}

**Available Months in Excel:** {', '.join(available_months) if available_months else 'None'}"""
        
        prompt = f"""{personality_context}

You're analyzing spending patterns with personality and data-driven insights.

**Question:** {question}

{data_context}

**Your Task:**
1. What's really being asked? (Is it budget-related?)
2. What does the Excel data tell us? (Cite specific numbers from months/categories)
3. What should the user do? (Be direct, humorous, but data-backed)

Think through this, but keep your response concise and reference specific data from the Excel file:"""
        
        return self.call_model(prompt)

