"""
Instant Answers - Python-only quick answers (no LLM needed)
Handles simple data queries for sub-second response times
"""

from typing import Optional, Dict
from .localized_templates import LocalizedTemplates as T

class InstantAnswers:
    """Provide instant answers using Python calculations only"""
    
    def __init__(self, data_loader, orchestrator=None):
        """
        Initialize with data loader
        
        Args:
            data_loader: DataLoader instance for accessing budget data
            orchestrator: LLM orchestrator for fallback (optional)
        """
        self.data_loader = data_loader
        self.orchestrator = orchestrator
        self.cache = {}  # Simple cache for frequently accessed data
    
    def try_answer(self, question: str, entities: Dict, language: str = 'zh') -> Optional[str]:
        """
        Try to answer question instantly with Python
        
        Args:
            question: User's question (for context)
            entities: Extracted entities from classifier
            language: Response language
        
        Returns:
            Answer string if possible, None if needs LLM
        """
        # ═══════════════════════════════════════════════════════════
        # Pattern 1: Month + Category total
        # "七月的伙食費是多少？" / "How much food in July?"
        # ═══════════════════════════════════════════════════════════
        if entities.get('month') and entities.get('category'):
            return self._month_category_total(
                entities['month'], 
                entities['category'], 
                language
            )
        
        # ═══════════════════════════════════════════════════════════
        # Pattern 2: Month total only
        # "七月花了多少？" / "How much in July?"
        # ═══════════════════════════════════════════════════════════
        if entities.get('month') and not entities.get('category'):
            return self._month_total(entities['month'], language)
        
        # ═══════════════════════════════════════════════════════════
        # Pattern 3: Category total (across all months)
        # "伙食費總共多少？" / "Total food expense?"
        # ═══════════════════════════════════════════════════════════
        if entities.get('category') and not entities.get('month'):
            return self._category_total_all(entities['category'], language)
        
        # ═══════════════════════════════════════════════════════════
        # Pattern 4: Overall total
        # "總支出多少？" / "Total spending?"
        # ═══════════════════════════════════════════════════════════
        q_lower = question.lower()
        if ('總' in question or 'total' in q_lower) and not entities.get('month'):
            return self._overall_total(language)
        
        # ═══════════════════════════════════════════════════════════
        # Pattern 5: Transaction count
        # "七月有幾筆交易？" / "How many transactions in July?"
        # ═══════════════════════════════════════════════════════════
        if ('幾筆' in question or 'how many' in q_lower or 'count' in q_lower):
            if entities.get('month'):
                return self._transaction_count(entities['month'], language)
        
        # ═══════════════════════════════════════════════════════════
        # Pattern 6: Average spending
        # "平均每月花多少？" / "Average monthly spending?"
        # ═══════════════════════════════════════════════════════════
        if '平均' in question or 'average' in q_lower or 'avg' in q_lower:
            return self._average_monthly(language)
        
        # Cannot answer instantly - needs LLM
        return None
    
    def _month_category_total(self, month: str, category: str, language: str) -> str:
        """Get total for specific month and category"""
        try:
            df = self.data_loader.load_month(month)
            
            if df is None or df.empty:
                return T.get('errors', 'no_data', language, 
                           month=month, 
                           available=', '.join(self._get_available_months()))
            
            if 'category' not in df.columns or 'amount' not in df.columns:
                return None  # Need LLM to handle this
            
            total = df[df['category'] == category]['amount'].sum()
            
            return T.get('instant', 'category_total', language,
                        month=month,
                        category=category,
                        amount=total)
        
        except Exception as e:
            return None  # Fall back to LLM
    
    def _month_total(self, month: str, language: str) -> str:
        """Get total for specific month"""
        try:
            df = self.data_loader.load_month(month)
            
            if df is None or df.empty:
                return T.get('errors', 'no_data', language,
                           month=month,
                           available=', '.join(self._get_available_months()))
            
            if 'amount' not in df.columns:
                return None
            
            total = df['amount'].sum()
            
            return T.get('instant', 'total', language,
                        month=month,
                        amount=total)
        
        except Exception as e:
            return None
    
    def _category_total_all(self, category: str, language: str) -> str:
        """Get total for category across all months"""
        try:
            all_data = self.data_loader.load_all_data()
            
            total = 0
            month_count = 0
            
            for month, df in all_data.items():
                if 'category' in df.columns and 'amount' in df.columns:
                    cat_total = df[df['category'] == category]['amount'].sum()
                    if cat_total > 0:
                        total += cat_total
                        month_count += 1
            
            if month_count == 0:
                available_cats = self._get_available_categories()
                return T.get('errors', 'invalid_category', language,
                           category=category,
                           available=', '.join(available_cats))
            
            # Format with month info
            if language == 'zh':
                return f"{category}總共 NT${total:,.0f} (跨 {month_count} 個月)"
            else:
                return f"Total {category}: NT${total:,.0f} (across {month_count} months)"
        
        except Exception as e:
            return None
    
    def _overall_total(self, language: str) -> str:
        """Get overall total spending"""
        try:
            stats = self.data_loader.get_summary_stats()
            
            if stats and 'total_spending' in stats:
                total = stats['total_spending']
                month_count = stats.get('months_with_data', 0)
                
                if language == 'zh':
                    return f"總支出 NT${total:,.0f} (共 {month_count} 個月)"
                else:
                    return f"Total spending: NT${total:,.0f} ({month_count} months)"
            
            return None
        
        except Exception as e:
            return None
    
    def _transaction_count(self, month: str, language: str) -> str:
        """Get transaction count for month"""
        try:
            df = self.data_loader.load_month(month)
            
            if df is None or df.empty:
                return T.get('errors', 'no_data', language,
                           month=month,
                           available=', '.join(self._get_available_months()))
            
            count = len(df)
            
            return T.get('instant', 'count', language,
                        month=month,
                        count=count)
        
        except Exception as e:
            return None
    
    def _average_monthly(self, language: str) -> str:
        """Get average monthly spending"""
        try:
            stats = self.data_loader.get_summary_stats()
            
            if stats and 'total_spending' in stats and 'months_with_data' in stats:
                total = stats['total_spending']
                months = stats['months_with_data']
                
                if months > 0:
                    avg = total / months
                    
                    return T.get('instant', 'avg', language,
                                period='每月',
                                amount=avg)
            
            return None
        
        except Exception as e:
            return None
    
    def _get_available_months(self) -> list:
        """Get list of available months"""
        try:
            all_data = self.data_loader.load_all_data()
            return list(all_data.keys())
        except:
            return []
    
    def _get_available_categories(self) -> list:
        """Get list of available categories"""
        try:
            all_data = self.data_loader.load_all_data()
            categories = set()
            
            for df in all_data.values():
                if 'category' in df.columns:
                    categories.update(df['category'].unique())
            
            return sorted(list(categories))
        except:
            return ['交通費', '伙食費', '休閒/娛樂', '家務', '其它']
    
    def clear_cache(self):
        """Clear answer cache"""
        self.cache = {}
    
    def try_llm_with_summary(self, question: str, entities: Dict, language: str = 'zh') -> Optional[str]:
        """
        TIER 2: Try answering with LLM using summary data
        Used when Python fails but question seems simple
        
        Args:
            question: User's question
            entities: Extracted entities
            language: Response language
        
        Returns:
            Answer string or None if needs full data
        """
        if not self.orchestrator:
            return None
        
        # Get summary stats
        stats = self.data_loader.get_summary_stats()
        
        # Build focused prompt
        if language == 'zh':
            prompt = f"""從預算摘要中回答問題。

問題: {question}

預算摘要:
- 總支出: NT${stats.get('total_spending', 0):,.0f}
- 月份資料: {list(stats.get('by_month', {}).keys())}
- 類別支出: {stats.get('by_category', {})}

直接回答問題，只需要數字和簡短說明。"""
        else:
            prompt = f"""Answer the question using budget summary.

Question: {question}

Budget summary:
- Total spending: NT${stats.get('total_spending', 0):,.0f}
- Available months: {list(stats.get('by_month', {}).keys())}
- Category spending: {stats.get('by_category', {})}

Answer directly with numbers and brief explanation."""
        
        # Use Qwen for fast extraction
        answer = self.orchestrator.qwen.call_model(prompt)
        return answer
    
    def try_llm_with_full_data(self, question: str, entities: Dict, language: str = 'zh') -> str:
        """
        TIER 3: Answer with LLM using full Excel data
        Used for complex questions or when summary isn't enough
        
        Args:
            question: User's question
            entities: Extracted entities
            language: Response language
        
        Returns:
            Comprehensive answer from full data
        """
        if not self.orchestrator:
            return "❌ LLM not available"
        
        # Load full data for relevant month(s)
        if entities.get('month'):
            full_data = self.data_loader.load_month(entities['month'])
            if full_data is not None and not full_data.empty:
                data_dict = full_data.to_dict('records')[:100]  # Limit to first 100 transactions
            else:
                data_dict = []
        else:
            # Load all available data (limited)
            all_data = self.data_loader.load_all_data()
            data_dict = {}
            for month, df in list(all_data.items())[:3]:  # Only last 3 months to avoid token limit
                data_dict[month] = df.to_dict('records')[:20]  # 20 transactions per month
        
        # Build comprehensive prompt
        if language == 'zh':
            prompt = f"""從完整的預算資料中回答問題。

問題: {question}

完整資料:
{data_dict}

要求:
1. 直接從資料中提取答案
2. 給出具體數字
3. 簡短回答（不超過2句話）

回答:"""
        else:
            prompt = f"""Answer the question using full budget data.

Question: {question}

Full data:
{data_dict}

Requirements:
1. Extract answer directly from data
2. Provide specific numbers
3. Brief answer (max 2 sentences)

Answer:"""
        
        # Use GPT-OSS for better reasoning with full data
        answer = self.orchestrator.gpt_oss.call_model(prompt)
        return answer

