"""
Qwen3:8b Engine - Structured data processing
Fast, efficient, good at categorization and pattern matching
"""

from typing import Tuple, Dict
from .base_llm import BaseLLM
import re

class QwenEngine(BaseLLM):
    """Qwen3:8b - Optimized for structured tasks"""
    
    def _setup(self):
        """Initialize Qwen engine"""
        if 'model' not in self.config:
            self.config['model'] = 'qwen3:8b'
        self.model_name = self.config['model']
        # Structured tasks: deterministic + larger context window than Ollama default (2048)
        if 'temperature' not in self.config:
            self.config['temperature'] = 0.1
        if 'num_ctx' not in self.config:
            self.config['num_ctx'] = 4096
        self.temperature = self.config['temperature']
        self.num_ctx = self.config['num_ctx']
        print(f"  🤖 Qwen Engine loaded: {self.model_name} (temp={self.temperature}, ctx={self.num_ctx})")

    def call_model(self, prompt: str) -> str:
        """Call Qwen model — prepend /no_think to skip chain-of-thought for structured tasks"""
        return self._call_ollama(f"/no_think\n{prompt}")
    
    def categorize(self, transaction: dict) -> Tuple[str, float]:
        """
        Categorize transaction with confidence score
        """
        desc = transaction.get('description', '')
        original_cat = transaction.get('category', '')
        
        prompt = f"""Categorize this transaction into ONE category.

Description: {desc}
Original Category: {original_cat}

Choose ONLY from these categories:
- 交通費 (transportation)
- 伙食費 (food/dining)
- 休閒/娛樂 (entertainment)
- 家務 (household)
- 阿幫 (pet)
- 其它 (other)

Respond ONLY with the Traditional Chinese category name and confidence (0-1).
Format: category|confidence

Example: 伙食費|0.95"""

        response = self.call_model(prompt)

        try:
            if '|' in response:
                parts = response.split('|')
                category = parts[0].strip()
                confidence = float(parts[1].strip())
            else:
                categories = ['交通費', '伙食費', '休閒/娛樂', '家務', '阿幫', '其它']
                category = next((c for c in categories if c in response), '其它')
                confidence = 0.7
            return category, confidence
        except:
            return '其它', 0.5
    
    def check_duplicate(self, tx1: dict, tx2: dict) -> Tuple[bool, float]:
        """
        Check if two transactions are duplicates
        Returns high confidence only for exact/near-exact matches
        """
        # Quick checks
        if tx1.get('date') != tx2.get('date'):
            return False, 1.0  # Different dates = definitely not duplicate
        
        amt_diff = abs(float(tx1.get('amount', 0)) - float(tx2.get('amount', 0)))
        if amt_diff > 1:  # More than NT$1 difference
            return False, 0.95
        
        # Same date, same amount - check descriptions
        desc1 = tx1.get('description', '').lower()
        desc2 = tx2.get('description', '').lower()
        
        if desc1 == desc2:
            return True, 1.0  # Exact match
        
        # Similar but not exact - low confidence (hand off to GPT-OSS)
        return True, 0.6  # Uncertain
    
    def calculate_stats(self, data: dict) -> dict:
        """
        Calculate statistical summary (Qwen's strength)
        """
        # Increased limit from 500 to 2000
        prompt = f"""Analyze this budget data and provide statistics.

Data: {str(data)[:2000]}  

Calculate:
1. Total spending
2. Category breakdown
3. Month-over-month change
4. Top spending categories

Return as structured data."""
        
        response = self.call_model(prompt)
        
        # Parse structured response
        stats = {
            'response': response,
            'source': 'qwen3:8b'
        }
        return stats
    
    def query(self, question: str, data: dict) -> str:
        """
        Answer simple data queries - Brief responses with data citation
        """
        # Extract labeled data for hallucination prevention
        # Increased limit from 500 to 2500
        data_summary = str(data.get('stats', {}))[:2500]
        available_months = data.get('available_months', [])
        data_source = data.get('data_source', 'Annual Excel Budget File')
        
        prompt = f"""Answer this question using ONLY the budget data from the Excel file.

Question: {question}

**Excel Budget Data (from {data_source}):**
{data_summary}

**Available Months:** {', '.join(available_months) if available_months else 'None'}
**Precomputed daily category summaries:** {str(data.get('precomputed_views', {}).get('daily_category_summaries', {}))[:1000]}

**CRITICAL:** Only use numbers and facts from the data above. If the data doesn't contain the answer, say so clearly.

Provide a concise, factual answer with specific numbers from the Excel file.
Do NOT include your reasoning steps or thought process—only output the final answer."""
        
        return self.call_model(prompt)
    
    def extract_data(self, question: str, data: dict) -> dict:
        """
        Extract relevant data for a question
        """
        # Increased limit from 500 to 2000
        prompt = f"""Extract data needed to answer this question.

Question: {question}
Data: {str(data)[:2000]}

Return relevant numbers, categories, and dates."""
        
        response = self.call_model(prompt)
        
        return {
            'extracted': response,
            'source': 'qwen3:8b'
        }

