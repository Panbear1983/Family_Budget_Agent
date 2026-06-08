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
        # Reasoning tasks: expressive temperature + large context window
        if 'temperature' not in self.config:
            self.config['temperature'] = 0.7
        if 'num_ctx' not in self.config:
            self.config['num_ctx'] = 8192
        self.temperature = self.config['temperature']
        self.num_ctx = self.config['num_ctx']
        print(f"  🧠 GPT-OSS Engine loaded: {self.model_name} (temp={self.temperature}, ctx={self.num_ctx})")
    
    def call_model(self, prompt: str) -> str:
        """Call GPT-OSS model"""
        return self._call_ollama(prompt)
    
    def _trim_context(self, data: dict, max_chars: int = 4000) -> str:
        """
        Build a focused data context string capped at max_chars.
        If requested_months is set, only include rollup data for those months
        to avoid flooding a 20B local model with irrelevant data.
        """
        requested_months = data.get('requested_months', [])
        monthly_rollup = data.get('monthly_rollup', {})

        # Filter rollup to requested months only (+ latest if none specified)
        if requested_months:
            filtered_rollup = {k: v for k, v in monthly_rollup.items()
                               if any(m in k for m in requested_months)}
        else:
            # Default: last 4 months instead of 3
            keys = sorted(monthly_rollup.keys())[-4:]
            filtered_rollup = {k: monthly_rollup[k] for k in keys}

        data_source = data.get('data_source', 'Annual Excel Budget File')
        available_months = data.get('available_months', [])
        months_with_data = data.get('months_with_data', [])
        latest_month = data.get('latest_month_with_data', 'None')
        consultant_flags = data.get('consultant_flags', {})
        comparison_summary = data.get('comparison_summary', {})
        precomputed_views = data.get('precomputed_views', {})

        parts = [
            f"Source: {data_source}",
            f"Available months: {', '.join(available_months) if available_months else 'None'}",
            f"Months with data: {', '.join(months_with_data) if months_with_data else 'None'}",
            f"Latest month: {latest_month}",
            f"Monthly rollup (relevant): {str(filtered_rollup)[:1500]}", # Increased from 600
            f"Consultant flags: {str(consultant_flags)[:500]}",        # Increased from 300
            f"Comparison summary: {str(comparison_summary)[:400]}",    # Increased from 200
            f"Daily summaries: {str(precomputed_views.get('daily_category_summaries', {}))[:800]}", # Increased from 300
        ]

        context = '\n'.join(parts)
        if len(context) > max_chars:
            context = context[:max_chars] + '\n[... truncated to fit context window]'
        return context

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
        personality += "8. When giving advice, organize thoughts in short sections so the user can skim\n"
        
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

Categorize into ONE of these Traditional Chinese categories:
- 交通費 (transportation)
- 伙食費 (food/dining)
- 休閒/娛樂 (entertainment)
- 家務 (household)
- 阿幫 (pet)
- 其它 (other)

Respond: category|confidence|reasoning
Example: 伙食費|0.95|This is clearly a food expense at a restaurant"""

        response = self.call_model(prompt)

        try:
            parts = response.split('|')
            if len(parts) >= 2:
                return parts[0].strip(), float(parts[1].strip())
        except:
            pass

        categories = ['交通費', '伙食費', '休閒/娛樂', '家務', '阿幫', '其它']
        category = next((c for c in categories if c in response), '其它')
        return category, 0.9
    
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
        response_language = data.get('response_language', 'en')
        months_without_data = data.get('months_without_data', [])

        data_context = self._trim_context(data)
        
        if response_language == 'zh-traditional':
            language_instruction = "請全程使用繁體中文回覆，保持語氣自然。"
        else:
            language_instruction = "Respond in English only."
        
        prompt = f"""{personality_context}

**User Question:** {question}

{data_context}

**Your Response Style:**
- {language_instruction}
- Be concise but friendly, and use swear words sparingly for emphasis (if enabled).
- Reference specific numbers from the Excel data above; cite the month/category you are referencing.
- Always base your answer on the Excel data - NEVER invent facts.
- Do NOT include your internal reasoning or planning steps—only the final paragraphs the user should read.
- If the user asks for a month listed in "Months without data" or a month where monthly_rollup[...] has_data is False, clearly say that month has no recorded transactions and do not fabricate numbers.
- Structure your reply as three short paragraphs (no bullet points):
  1. Snapshot / headline numbers
  2. Drivers or notable shifts (use the precomputed summaries)
  3. Recommendations or next steps
- Each paragraph should be 2-3 sentences max.

Now answer the question using ONLY the data above:"""
        
        return self.call_model(prompt)
    
    def reason(self, question: str, data: dict) -> str:
        """
        Provide deep reasoning and advice - Budget Advisor style
        """
        personality_context = self._get_personality_prompt()

        # Handle both dict and extracted data formats
        if isinstance(data, dict) and 'extracted' in data:
            data_context = (
                f"**Extracted Data from Excel:**\n{data.get('extracted', '')}\n"
                f"**Source:** {data.get('source', 'qwen3:8b')}"
            )
            response_language = 'en'
            months_without_data = []
        else:
            response_language = data.get('response_language', 'en')
            months_without_data = data.get('months_without_data', [])
            data_context = self._trim_context(data)
        
        if response_language == 'zh-traditional':
            language_instruction = "請以繁體中文撰寫回覆，保持段落清楚。"
        else:
            language_instruction = "Respond in English only."
        
        prompt = f"""{personality_context}

You're analyzing spending patterns with personality and data-driven insights.

**Question:** {question}

{data_context}

**Your Task:**
1. What's really being asked? (Is it budget-related?)
2. What does the Excel data tell us? (Cite specific numbers from months/categories)
3. What should the user do? (Be direct, humorous, but data-backed)

{language_instruction}
If the user asks for a month listed in "Months without data" or a month where monthly_rollup[...] has_data is False, explicitly state that the sheet has no recorded transactions and do not invent figures.
Use the daily_category_summaries to answer "which day/category" style questions—cite the exact day and amount.
Do NOT reveal your internal reasoning or thought process—only provide the final three paragraphs the user should read.
Think through this, but respond as three short paragraphs (no bullet points): Snapshot, Drivers, Recommendations. Each paragraph should be 2-3 sentences and reference specific data from the Excel file:"""
        
        return self.call_model(prompt)

