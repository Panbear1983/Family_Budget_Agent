"""
Localized Templates - Multilingual response templates
Pre-written patterns for consistent, fast responses in multiple languages
"""

class LocalizedTemplates:
    """Centralized multilingual response templates"""
    
    TEMPLATES = {
        # ═══════════════════════════════════════════════════════════════
        # INSTANT ANSWERS (No LLM needed - Python computation only)
        # ═══════════════════════════════════════════════════════════════
        'instant': {
            'zh': {
                'total': "{month}總支出 NT${amount:,.0f}",
                'category_total': "{month}的{category}總共 NT${amount:,.0f}",
                'avg': "{period}平均支出 NT${amount:,.0f}",
                'count': "{month}共有 {count} 筆交易",
                'range': "{start} 至 {end} 總支出 NT${amount:,.0f}",
            },
            'en': {
                'total': "{month} total: NT${amount:,.0f}",
                'category_total': "{category} in {month}: NT${amount:,.0f}",
                'avg': "{period} average: NT${amount:,.0f}",
                'count': "{count} transactions in {month}",
                'range': "{start} to {end} total: NT${amount:,.0f}",
            }
        },
        
        # ═══════════════════════════════════════════════════════════════
        # TRENDS (Computed patterns with direction indicators)
        # ═══════════════════════════════════════════════════════════════
        'trends': {
            'zh': {
                'up': "📈 {category}上升 {percent:.1f}% (NT${start:,.0f} → NT${end:,.0f})",
                'down': "📉 {category}下降 {percent:.1f}% (NT${start:,.0f} → NT${end:,.0f})",
                'stable': "➡️ {category}保持穩定，平均 NT${avg:,.0f}",
                'trend_summary': "{category}趨勢: {direction}，{insight}"
            },
            'en': {
                'up': "📈 {category} up {percent:.1f}% (NT${start:,.0f} → NT${end:,.0f})",
                'down': "📉 {category} down {percent:.1f}% (NT${start:,.0f} → NT${end:,.0f})",
                'stable': "➡️ {category} stable, averaging NT${avg:,.0f}",
                'trend_summary': "{category} trend: {direction}, {insight}"
            }
        },
        
        # ═══════════════════════════════════════════════════════════════
        # COMPARISONS (Month-to-month analysis)
        # ═══════════════════════════════════════════════════════════════
        'comparison': {
            'zh': {
                'header': "📊 {month1} vs {month2} 對比:",
                'total_change': "總支出: NT${amt1:,.0f} → NT${amt2:,.0f} ({change:+.1f}%)",
                'category_change': "• {category}: {change:+,.0f} ({percent:+.1f}%)",
                'summary': "主要變化: {insight}"
            },
            'en': {
                'header': "📊 {month1} vs {month2} Comparison:",
                'total_change': "Total: NT${amt1:,.0f} → NT${amt2:,.0f} ({change:+.1f}%)",
                'category_change': "• {category}: {change:+,.0f} ({percent:+.1f}%)",
                'summary': "Main changes: {insight}"
            }
        },
        
        # ═══════════════════════════════════════════════════════════════
        # FORECASTS (Predictions with confidence)
        # ═══════════════════════════════════════════════════════════════
        'forecast': {
            'zh': {
                'prediction': "🔮 預測{month}支出: NT${amount:,.0f}",
                'confidence': "信心度: {confidence}",
                'basis': "基於: 最近 {months} 個月資料",
                'suggestion': "建議預算: NT${suggested:,.0f} (含{buffer}%緩衝)",
                'full': "🔮 預測結果:\n• 預測金額: NT${amount:,.0f}\n• 信心度: {confidence}\n• 基於: 最近{months}個月\n• 建議預算: NT${suggested:,.0f}"
            },
            'en': {
                'prediction': "🔮 {month} forecast: NT${amount:,.0f}",
                'confidence': "Confidence: {confidence}",
                'basis': "Based on: last {months} months",
                'suggestion': "Suggested budget: NT${suggested:,.0f} ({buffer}% buffer)",
                'full': "🔮 Forecast:\n• Predicted: NT${amount:,.0f}\n• Confidence: {confidence}\n• Based on: last {months} months\n• Suggested: NT${suggested:,.0f}"
            }
        },
        
        # ═══════════════════════════════════════════════════════════════
        # ERRORS & VALIDATION (User guidance)
        # ═══════════════════════════════════════════════════════════════
        'errors': {
            'zh': {
                'no_data': "❌ {month}暫無資料。可用月份: {available}",
                'invalid_category': "❌ 找不到類別 '{category}'。可用類別: {available}",
                'invalid_month': "❌ '{month}' 不是有效月份",
                'no_comparison': "❌ 無法比較，{month1} 或 {month2} 無資料",
                'insufficient_data': "❌ 資料不足，需要至少 {required} 個月"
            },
            'en': {
                'no_data': "❌ No data for {month}. Available: {available}",
                'invalid_category': "❌ Category '{category}' not found. Available: {available}",
                'invalid_month': "❌ '{month}' is not a valid month",
                'no_comparison': "❌ Cannot compare, no data for {month1} or {month2}",
                'insufficient_data': "❌ Insufficient data, need at least {required} months"
            }
        },
        
        # ═══════════════════════════════════════════════════════════════
        # OFF-TOPIC REDIRECTS (Guardrails messages)
        # ═══════════════════════════════════════════════════════════════
        'redirects': {
            'zh': {
                'generic': """抱歉，這個問題超出我的專業範圍。

我是專門的**預算分析助手**，只能回答關於您的2025年度預算資料的問題。

✅ 我能回答的問題類型：
• 💰 支出查詢 (例：「七月花了多少？」)
• 📊 趨勢分析 (例：「伙食費趨勢如何？」)
• 🔍 比較分析 (例：「比較七月和八月」)
• 🔮 預測規劃 (例：「預測下月支出」)
• 💡 節省建議 (例：「哪裡可以省錢？」)

請問有什麼**預算相關**的問題嗎？""",
                
                'no_answer': """抱歉，我沒有這個答案。

我只能回答簡單、明確的預算問題：

✅ 我能回答:
• 「七月花了多少？」
• 「七月的伙食費是多少？」
• 「比較七月和八月」
• 「給我看圖表」

❌ 我不能回答:
• 複雜的分析問題
• 需要推測的問題
• 預算以外的話題

請用簡單、具體的問題重新問我。""",
                
                'general_chat': """抱歉，我無法回答關於{topic}的問題。

我專注於**您的2025年度預算分析**。

💡 我能幫您：
• 📊 查詢某月/某類別的支出
• 📈 分析趨勢和比較
• 🔮 預測未來開銷
• 💰 提供節省建議

請問有什麼**預算相關**的問題嗎？""",
                
                'finance_adjacent': """我理解您對{topic}感興趣，但這超出我的專業範圍。

我專注於**家庭預算分析**，不涉及投資理財建議。

💡 我可以幫您：
• 分析當前支出模式
• 找出節省機會  
• 優化預算分配

要不要看看您的預算分析？""",
                
                'topic_drift': """看起來我們偏離預算話題了 😅

讓我們回到您的2025預算分析吧！

💡 最近可以關注：
• 您的總支出趨勢
• 哪些類別可以優化
• 下個月預算規劃

想從哪裡開始？"""
            },
            'en': {
                'generic': """Sorry, that question is outside my scope.

I'm a specialized **budget analysis assistant** for your 2025 budget data.

✅ I can answer:
• 💰 Spending queries (e.g., "How much in July?")
• 📊 Trend analysis (e.g., "Food expense trend?")
• 🔍 Comparisons (e.g., "Compare July and August")
• 🔮 Forecasts (e.g., "Predict next month")
• 💡 Savings tips (e.g., "Where can I save?")

Do you have any **budget-related** questions?""",
                
                'no_answer': """Sorry, I don't have that answer.

I can only answer simple, specific budget questions:

✅ I can answer:
• "How much in July?"
• "How much did I spend on food in July?"
• "Compare July and August"
• "Show me a chart"

❌ I cannot answer:
• Complex analysis questions
• Questions requiring speculation
• Topics outside budget data

Please ask me a simple, specific question.""",
                
                'general_chat': """Sorry, I can't answer questions about {topic}.

I focus on **your 2025 budget analysis**.

💡 I can help with:
• 📊 Monthly/category spending
• 📈 Trend analysis
• 🔮 Forecasting
• 💰 Savings suggestions

Any **budget-related** questions?""",
                
                'finance_adjacent': """I understand you're interested in {topic}, but that's outside my scope.

I focus on **household budget analysis**, not investment advice.

💡 I can help you:
• Analyze spending patterns
• Find savings opportunities
• Optimize budget allocation

Want to see your budget analysis?""",
                
                'topic_drift': """Looks like we drifted off-topic 😅

Let's get back to your 2025 budget analysis!

💡 We could focus on:
• Your spending trends
• Categories to optimize
• Next month's budget

Where should we start?"""
            }
        },
        
        # ═══════════════════════════════════════════════════════════════
        # FOLLOW-UPS (Proactive suggestions)
        # ═══════════════════════════════════════════════════════════════
        'follow_ups': {
            'zh': {
                'more_details': "💡 需要更詳細的分析嗎？",
                'see_chart': "📊 要看圖表嗎？",
                'compare': "🔍 要跟其他月份比較嗎？",
                'forecast': "🔮 要預測下個月嗎？",
                'optimize': "💰 要找節省機會嗎？",
                'breakdown': "📋 要看{category}明細嗎？"
            },
            'en': {
                'more_details': "💡 Need more detailed analysis?",
                'see_chart': "📊 Want to see a chart?",
                'compare': "🔍 Compare with other months?",
                'forecast': "🔮 Forecast next month?",
                'optimize': "💰 Find savings opportunities?",
                'breakdown': "📋 See {category} breakdown?"
            }
        },
        
        # ═══════════════════════════════════════════════════════════════
        # CONFIRMATIONS (Action confirmations)
        # ═══════════════════════════════════════════════════════════════
        'confirmations': {
            'zh': {
                'chart_shown': "✅ 已顯示圖表",
                'analysis_complete': "✅ 分析完成",
                'data_loaded': "✅ 已載入資料",
                'forecast_ready': "✅ 預測完成"
            },
            'en': {
                'chart_shown': "✅ Chart displayed",
                'analysis_complete': "✅ Analysis complete",
                'data_loaded': "✅ Data loaded",
                'forecast_ready': "✅ Forecast ready"
            }
        }
    }
    
    @staticmethod
    def get(section: str, key: str, language: str = 'zh', **kwargs) -> str:
        """
        Get and fill template
        
        Args:
            section: Template section (instant, trends, errors, etc.)
            key: Template key within section
            language: Language code (zh, en)
            **kwargs: Values to fill into template
        
        Returns:
            Formatted string in specified language
        """
        try:
            template = LocalizedTemplates.TEMPLATES[section][language][key]
            return template.format(**kwargs)
        except KeyError:
            # Fallback to Chinese if template not found
            try:
                template = LocalizedTemplates.TEMPLATES[section]['zh'][key]
                return template.format(**kwargs)
            except:
                return f"[Template not found: {section}.{key}]"
    
    @staticmethod
    def get_available_sections() -> list:
        """Get list of all template sections"""
        return list(LocalizedTemplates.TEMPLATES.keys())
    
    @staticmethod
    def get_available_keys(section: str) -> list:
        """Get list of all template keys in a section"""
        if section in LocalizedTemplates.TEMPLATES:
            # Return keys from Chinese version (all languages have same keys)
            return list(LocalizedTemplates.TEMPLATES[section]['zh'].keys())
        return []

