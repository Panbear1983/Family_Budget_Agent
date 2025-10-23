"""
Prompt Builder - Build focused, role-optimized prompts for LLMs
Qwen: Data extraction and structured tasks
GPT-OSS: Reasoning, explanation, and advice
"""

class PromptBuilder:
    """Build optimized prompts for each LLM's strengths"""
    
    def __init__(self):
        """Initialize prompt builder"""
        self.max_data_length = 800  # Max chars of data in prompt
    
    def build_qwen_prompt(self, question: str, data: dict, language: str = 'zh') -> str:
        """
        Build prompt for Qwen (structured data extraction)
        
        Args:
            question: User's question
            data: Preprocessed data
            language: Response language
        
        Returns:
            Optimized prompt for Qwen
        """
        # Qwen is best at: extraction, calculation, structured output
        
        if language == 'zh':
            prompt = f"""你是資料分析助手，專門從預算資料中提取關鍵資訊。

問題: {question}

可用資料: {self._condense_data(data)}

請提取回答問題所需的具體數據：
1. 相關金額和數字
2. 涉及的類別
3. 時間範圍
4. 關鍵變化

注意：直接陳述事實，不要說「使用者」或「用戶」，就像在直接回答提問者一樣。
只輸出事實和數字，不要解釋或建議。
格式: 簡潔的條列式資料"""
        
        else:  # English
            prompt = f"""You are a data analyst assistant extracting key information from budget data.

Question: {question}

Available data: {self._condense_data(data)}

Extract specific data needed to answer:
1. Relevant amounts and numbers
2. Categories involved
3. Time period
4. Key changes

IMPORTANT: State facts directly as if speaking to the person asking. DO NOT say "the user" or refer to them in third person.
Output facts and numbers only, no explanations or advice.
Format: Concise bullet points"""
        
        return prompt
    
    def build_gpt_oss_prompt(self, question: str, qwen_output: str, context: str, 
                            response_language: str = 'zh') -> str:
        """
        Build prompt for GPT-OSS (reasoning and advice)
        
        Args:
            question: User's question
            qwen_output: Data extracted by Qwen
            context: Conversation context
            response_language: Language for response
        
        Returns:
            Optimized prompt for GPT-OSS
        """
        # GPT-OSS is best at: reasoning, explanation, advice, natural language
        
        if response_language == 'zh':
            prompt = f"""你是雙語預算顧問 (中文/English)，直接與客戶對話。

問題: {question}

已提取的資料:
{qwen_output}

對話背景:
{context}

請提供:
1. 直接回答問題（含具體數字）
2. 簡要解釋（為什麼/如何）
3. 一個實用建議（如果相關）

要求:
- 使用自然、友善的語言，直接稱呼對方「您」或「你」
- 不要說「使用者」或「用戶」，直接回答就像面對面對話
- 保持在 150 字以內
- 確保數字準確（來自已提取資料）
- 適當混用中英文專業術語"""
        
        else:  # English
            prompt = f"""You are a bilingual budget advisor (中文/English) speaking directly to your client.

Question: {question}

Extracted data:
{qwen_output}

Conversation context:
{context}

Provide:
1. Direct answer (with specific numbers)
2. Brief explanation (why/how)
3. One actionable tip (if relevant)

Requirements:
- Use natural, friendly language speaking directly to the person (use "you", "your")
- DO NOT say "the user" or refer to them in third person - answer as if in a face-to-face conversation
- Keep under 150 words
- Ensure numbers are accurate (from extracted data)
- Mix Chinese category names where appropriate"""
        
        return prompt
    
    def build_insight_prompt(self, question: str, data: dict, language: str = 'zh') -> str:
        """
        Build prompt for generating insights (GPT-OSS direct)
        Used for "why" questions
        """
        if language == 'zh':
            prompt = f"""你是預算分析專家，直接與客戶對話。

問題: {question}

資料摘要:
{self._format_for_insight(data)}

請深入分析:
1. 識別模式和趨勢
2. 解釋背後原因
3. 提供具體建議

要求:
- 使用清晰、專業的語言，直接稱呼對方「您」或「你」
- 不要說「使用者」或「用戶」，像面對面對話一樣回答
- 結合數據支撐你的觀點"""
        
        else:
            prompt = f"""You are a budget analysis expert speaking directly to your client.

Question: {question}

Data summary:
{self._format_for_insight(data)}

Analyze deeply:
1. Identify patterns and trends
2. Explain underlying reasons
3. Provide specific recommendations

Requirements:
- Use clear, professional language speaking directly to the person (use "you", "your")
- DO NOT say "the user" - answer as if in a face-to-face conversation
- Support your points with data"""
        
        return prompt
    
    def build_advice_prompt(self, question: str, data: dict, language: str = 'zh') -> str:
        """
        Build prompt for giving advice (GPT-OSS)
        Used for "should", "recommend", "how to" questions
        """
        if language == 'zh':
            prompt = f"""你是家庭財務顧問，直接與客戶對話提供實用建議。

客戶問題: {question}

預算情況:
{self._format_for_advice(data)}

請提供:
1. 2-3 個具體可行的建議
2. 每個建議的預期效果（節省金額）
3. 實施的優先順序

要求:
- 直接稱呼對方「您」或「你」，不要說「使用者」或「用戶」
- 建議必須基於實際數據
- 具體可執行
- 考慮台灣的消費環境"""
        
        else:
            prompt = f"""You are a household finance advisor speaking directly to your client with practical advice.

Client's question: {question}

Budget situation:
{self._format_for_advice(data)}

Provide:
1. 2-3 specific actionable recommendations
2. Expected impact of each (savings amount)
3. Priority order for implementation

Requirements:
- Speak directly to the person using "you" and "your", DO NOT say "the user"
- Advice must be data-driven
- Specific and actionable
- Consider Taiwan's consumer context"""
        
        return prompt
    
    def build_comparison_prompt(self, data: dict, language: str = 'zh') -> str:
        """Build prompt for month comparison analysis"""
        comparison = data.get('relevant_stats', {}).get('comparison', {})
        
        if language == 'zh':
            prompt = f"""分析 {comparison.get('month1')} 和 {comparison.get('month2')} 的支出變化。

資料:
- {comparison.get('month1')}: NT${comparison.get('total1', 0):,.0f}
- {comparison.get('month2')}: NT${comparison.get('total2', 0):,.0f}
- 變化: {comparison.get('change_percent', 0):+.1f}%

主要類別變化:
{self._format_dict(comparison.get('biggest_changes', {}))}

請說明:
1. 總體變化趨勢
2. 主要變化原因
3. 是否需要關注"""
        
        else:
            prompt = f"""Analyze spending changes between {comparison.get('month1')} and {comparison.get('month2')}.

Data:
- {comparison.get('month1')}: NT${comparison.get('total1', 0):,.0f}
- {comparison.get('month2')}: NT${comparison.get('total2', 0):,.0f}
- Change: {comparison.get('change_percent', 0):+.1f}%

Main category changes:
{self._format_dict(comparison.get('biggest_changes', {}))}

Explain:
1. Overall trend
2. Main reasons for changes
3. Any concerns"""
        
        return prompt
    
    def build_forecast_prompt(self, forecast_data: dict, language: str = 'zh') -> str:
        """Build prompt for forecast explanation"""
        if language == 'zh':
            prompt = f"""解釋這個支出預測。

預測結果:
- 預測金額: NT${forecast_data.get('forecast_amount', 0):,.0f}
- 信心度: {forecast_data.get('confidence', 'unknown')}
- 基於: 最近 {forecast_data.get('based_on_months', 0)} 個月

趨勢背景:
{self._format_dict(forecast_data.get('trend_context', {}))}

請簡要說明:
1. 預測是否合理
2. 主要影響因素
3. 建議的預算金額（含緩衝）"""
        
        else:
            prompt = f"""Explain this spending forecast.

Forecast results:
- Predicted: NT${forecast_data.get('forecast_amount', 0):,.0f}
- Confidence: {forecast_data.get('confidence', 'unknown')}
- Based on: last {forecast_data.get('based_on_months', 0)} months

Trend context:
{self._format_dict(forecast_data.get('trend_context', {}))}

Briefly explain:
1. Is the forecast reasonable
2. Main influencing factors
3. Suggested budget amount (with buffer)"""
        
        return prompt
    
    # ═══════════════════════════════════════════════════════════════
    # Helper methods
    # ═══════════════════════════════════════════════════════════════
    
    def _condense_data(self, data: dict) -> str:
        """Condense data dict to string, no truncation"""
        data_str = str(data)
        # No truncation - return full data
        return data_str
    
    def _format_for_insight(self, data: dict) -> str:
        """Format data specifically for insight generation"""
        parts = []
        
        if 'relevant_stats' in data:
            stats = data['relevant_stats']
            
            if 'monthly' in stats:
                m = stats['monthly']
                parts.append(f"月度統計: 總額 NT${m.get('total', 0):,.0f}, {m.get('transaction_count', 0)} 筆交易")
            
            if 'overall' in stats:
                o = stats['overall']
                parts.append(f"整體: 總支出 NT${o.get('total_spending', 0):,.0f}, 平均每月 NT${o.get('avg_monthly', 0):,.0f}")
        
        if 'trends' in data and 'category' in data['trends']:
            t = data['trends']['category']
            parts.append(f"趨勢: {t.get('category')} {t.get('direction')}")
        
        return "\n".join(parts) if parts else str(data)
    
    def _format_for_advice(self, data: dict) -> str:
        """Format data specifically for advice giving"""
        parts = []
        
        if 'relevant_stats' in data and 'overall' in data['relevant_stats']:
            stats = data['relevant_stats']['overall']
            parts.append(f"總支出: NT${stats.get('total_spending', 0):,.0f}")
            parts.append(f"平均月支出: NT${stats.get('avg_monthly', 0):,.0f}")
            
            if stats.get('category_breakdown'):
                parts.append("\n主要類別:")
                for cat, amt in stats['category_breakdown'].items():  # No truncation
                    parts.append(f"  - {cat}: NT${amt:,.0f}")
        
        return "\n".join(parts) if parts else "資料不足"
    
    def _format_dict(self, d: dict) -> str:
        """Format dictionary for display in prompt"""
        if not d:
            return "(無)"
        
        lines = []
        for k, v in d.items():
            if isinstance(v, (int, float)):
                lines.append(f"- {k}: {v:,.0f}" if v > 100 else f"- {k}: {v}")
            else:
                lines.append(f"- {k}: {v}")
        
        return "\n".join(lines)

