"""
Instant Answers - Python-only quick answers (no LLM needed)
Handles simple data queries for sub-second response times
"""

from typing import Optional, Dict
import json
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
            # Check if multi-month average (specific months)
            if len(entities.get('months', [])) >= 2:
                return self._multi_month_average(entities['months'], language)
            else:
                return self._average_monthly(language)
        
        # ═══════════════════════════════════════════════════════════
        # Pattern 7: Multi-month sum
        # "七月和八月總共多少？" / "Total of July and August?"
        # ═══════════════════════════════════════════════════════════
        if ('總' in question or 'total' in q_lower or 'sum' in q_lower) and len(entities.get('months', [])) >= 2:
            return self._multi_month_sum(entities['months'], language)
        
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
    
    def _multi_month_average(self, months: list, language: str) -> str:
        """Calculate average spending across specific months (Python-only, no LLM)"""
        try:
            totals = []
            valid_months = []
            
            for month in months:
                df = self.data_loader.load_month(month)
                if df is not None and not df.empty and 'amount' in df.columns:
                    total = df['amount'].sum()
                    totals.append(total)
                    valid_months.append(month)
            
            if not totals:
                return None
            
            average = sum(totals) / len(totals)
            
            if language == 'zh':
                month_list = '、'.join(valid_months)
                detail = '、'.join([f"{m}: NT${t:,.0f}" for m, t in zip(valid_months, totals)])
                return f"📊 {month_list} 的平均支出: NT${average:,.0f}\n\n   明細: {detail}"
            else:
                month_list = ', '.join(valid_months)
                detail = ', '.join([f"{m}: NT${t:,.0f}" for m, t in zip(valid_months, totals)])
                return f"📊 Average spending for {month_list}: NT${average:,.0f}\n\n   Breakdown: {detail}"
        
        except Exception as e:
            return None
    
    def _multi_month_sum(self, months: list, language: str) -> str:
        """Calculate total spending across specific months (Python-only, no LLM)"""
        try:
            total = 0
            month_details = []
            
            for month in months:
                df = self.data_loader.load_month(month)
                if df is not None and not df.empty and 'amount' in df.columns:
                    month_total = df['amount'].sum()
                    total += month_total
                    month_details.append(f"{month}: NT${month_total:,.0f}")
            
            if not month_details:
                return None
            
            if language == 'zh':
                detail = '、'.join(month_details)
                return f"📊 總支出: NT${total:,.0f}\n\n   明細: {detail}"
            else:
                detail = ', '.join(month_details)
                return f"📊 Total spending: NT${total:,.0f}\n\n   Breakdown: {detail}"
        
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
        TIER 2: Try answering with LLM using PRE-CALCULATED summary data
        LLM only interprets, does NOT calculate
        
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
        
        # PRE-CALCULATE relevant values based on entities
        calculated_results = {}
        
        # If specific months requested, pre-calculate their totals
        if entities.get('months'):
            monthly_totals = {}
            for month in entities['months']:
                df = self.data_loader.load_month(month)
                if df is not None and not df.empty and 'amount' in df.columns:
                    monthly_totals[month] = df['amount'].sum()
            
            calculated_results['monthly_totals'] = monthly_totals
            
            # If multiple months, pre-calculate average
            if len(monthly_totals) > 1:
                calculated_results['average'] = sum(monthly_totals.values()) / len(monthly_totals)
                calculated_results['total'] = sum(monthly_totals.values())
        
        # If specific category requested, pre-calculate
        if entities.get('category'):
            category = entities['category']
            cat_total = 0
            for month_data in self.data_loader.load_all_data().values():
                if 'category' in month_data.columns and 'amount' in month_data.columns:
                    cat_total += month_data[month_data['category'] == category]['amount'].sum()
            calculated_results['category_total'] = cat_total
        
        # Build focused prompt with PRE-CALCULATED results
        if language == 'zh':
            prompt = f"""用自然語言解釋這些已計算的結果。

問題: {question}

已計算結果（請勿重新計算）:
{json.dumps(calculated_results, ensure_ascii=False, indent=2) if calculated_results else '無特定計算'}

摘要統計:
- 總支出: NT${stats.get('total_spending', 0):,.0f}
- 可用月份: {list(stats.get('by_month', {}).keys())}
- 類別支出: {stats.get('by_category', {})}

任務: 用自然語言解釋結果。不要重新計算數字。"""
        else:
            prompt = f"""Explain these pre-calculated results in natural language.

Question: {question}

Pre-calculated Results (DO NOT recalculate):
{json.dumps(calculated_results, indent=2) if calculated_results else 'No specific calculations'}

Summary Statistics:
- Total spending: NT${stats.get('total_spending', 0):,.0f}
- Available months: {list(stats.get('by_month', {}).keys())}
- Category spending: {stats.get('by_category', {})}

Task: Explain results in natural language. Do NOT recalculate numbers."""
        
        # Use Qwen for fast interpretation (not calculation)
        answer = self.orchestrator.qwen.call_model(prompt)
        
        # Prepend calculated results to answer for transparency
        if calculated_results:
            if language == 'zh':
                result_summary = "計算結果:\n"
                if 'average' in calculated_results:
                    result_summary += f"  平均: NT${calculated_results['average']:,.0f}\n"
                if 'total' in calculated_results:
                    result_summary += f"  總計: NT${calculated_results['total']:,.0f}\n"
                if 'monthly_totals' in calculated_results:
                    result_summary += "  明細:\n"
                    for month, total in calculated_results['monthly_totals'].items():
                        result_summary += f"    {month}: NT${total:,.0f}\n"
                answer = result_summary + "\n" + answer
            else:
                result_summary = "Calculated Results:\n"
                if 'average' in calculated_results:
                    result_summary += f"  Average: NT${calculated_results['average']:,.0f}\n"
                if 'total' in calculated_results:
                    result_summary += f"  Total: NT${calculated_results['total']:,.0f}\n"
                if 'monthly_totals' in calculated_results:
                    result_summary += "  Breakdown:\n"
                    for month, total in calculated_results['monthly_totals'].items():
                        result_summary += f"    {month}: NT${total:,.0f}\n"
                answer = result_summary + "\n" + answer
        
        return answer
    
    def try_llm_with_full_data(self, question: str, entities: Dict, language: str = 'zh') -> str:
        """
        TIER 3: Answer with LLM using PRE-CALCULATED results from full Excel data
        LLM only interprets, does NOT calculate
        
        Args:
            question: User's question
            entities: Extracted entities
            language: Response language
        
        Returns:
            Comprehensive answer with pre-calculated results
        """
        if not self.orchestrator:
            return "❌ LLM not available"
        
        # PRE-CALCULATE all relevant statistics from full data
        calculated_stats = {}
        
        # Load full data for relevant month(s)
        if entities.get('month'):
            df = self.data_loader.load_month(entities['month'])
            if df is not None and not df.empty and 'amount' in df.columns:
                # Pre-calculate statistics
                calculated_stats['month'] = entities['month']
                calculated_stats['total'] = df['amount'].sum()
                calculated_stats['count'] = len(df)
                calculated_stats['average'] = df['amount'].mean()
                calculated_stats['max'] = df['amount'].max()
                calculated_stats['min'] = df['amount'].min()
                
                # Category breakdown if available
                if 'category' in df.columns:
                    calculated_stats['by_category'] = df.groupby('category')['amount'].sum().to_dict()
                
                # Sample transactions (for context, not calculation)
                calculated_stats['sample_transactions'] = df.head(5)[['date', 'description', 'amount', 'category']].to_dict('records') if 'description' in df.columns else []
        else:
            # Multiple months
            all_data = self.data_loader.load_all_data()
            calculated_stats['months'] = list(all_data.keys())
            calculated_stats['monthly_totals'] = {}
            
            for month, df in all_data.items():
                if 'amount' in df.columns:
                    calculated_stats['monthly_totals'][month] = df['amount'].sum()
            
            if calculated_stats['monthly_totals']:
                calculated_stats['overall_total'] = sum(calculated_stats['monthly_totals'].values())
                calculated_stats['overall_average'] = calculated_stats['overall_total'] / len(calculated_stats['monthly_totals'])
        
        # Build comprehensive prompt with PRE-CALCULATED stats
        if language == 'zh':
            prompt = f"""用完整的統計數據回答問題。所有數字已經計算好。

問題: {question}

已計算統計（請勿重新計算）:
{json.dumps(calculated_stats, ensure_ascii=False, indent=2)}

任務:
1. 使用上面已計算的數字
2. 用自然語言解釋
3. 提供見解和背景
4. 不要重新計算任何數字

回答:"""
        else:
            prompt = f"""Answer the question using complete statistics. All numbers are pre-calculated.

Question: {question}

Pre-calculated Statistics (DO NOT recalculate):
{json.dumps(calculated_stats, indent=2)}

Tasks:
1. Use the pre-calculated numbers above
2. Explain in natural language
3. Provide insights and context
4. Do NOT recalculate any numbers

Answer:"""
        
        # Use GPT-OSS for better reasoning with full data
        answer = self.orchestrator.gpt_oss.call_model(prompt)
        
        # Prepend key calculated results for transparency
        if language == 'zh':
            result_header = "📊 計算結果:\n"
            if 'total' in calculated_stats:
                result_header += f"  總支出: NT${calculated_stats['total']:,.0f}\n"
            if 'average' in calculated_stats:
                result_header += f"  平均: NT${calculated_stats['average']:,.0f}\n"
            if 'count' in calculated_stats:
                result_header += f"  交易筆數: {calculated_stats['count']}\n"
            if 'monthly_totals' in calculated_stats:
                result_header += "  月度明細:\n"
                for month, total in list(calculated_stats['monthly_totals'].items())[:5]:
                    result_header += f"    {month}: NT${total:,.0f}\n"
            answer = result_header + "\n" + answer
        else:
            result_header = "📊 Calculated Results:\n"
            if 'total' in calculated_stats:
                result_header += f"  Total Spending: NT${calculated_stats['total']:,.0f}\n"
            if 'average' in calculated_stats:
                result_header += f"  Average: NT${calculated_stats['average']:,.0f}\n"
            if 'count' in calculated_stats:
                result_header += f"  Transaction Count: {calculated_stats['count']}\n"
            if 'monthly_totals' in calculated_stats:
                result_header += "  Monthly Breakdown:\n"
                for month, total in list(calculated_stats['monthly_totals'].items())[:5]:
                    result_header += f"    {month}: NT${total:,.0f}\n"
            answer = result_header + "\n" + answer
        
        return answer

