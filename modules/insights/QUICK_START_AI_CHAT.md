# AI Chat - Quick Start Guide

## 🚀 Getting Started (3 Steps)

### Step 1: Activate Environment
```bash
cd /Users/peter/Desktop/Old_Projects/GitHub/Family_Budget_Agent
source venv/bin/activate
```

### Step 2: Run the System
```bash
python _main.py
```

### Step 3: Select AI Chat
- Choose **[3] 💬 預算分析對話 (Budget Chat & Insights)**
- Start asking questions!

---

## 💬 What You Can Ask

### 📊 **Data Queries** (Instant - <1 second)
```
七月花了多少？
How much in July?
七月的伙食費是多少？
Total food expense in July?
平均每月花多少？
```

### 📈 **Trends & Analysis** (Fast - 2-5 seconds)
```
伙食費趨勢如何？
What's the food expense trend?
八月為什麼增加？
Why did August spending go up?
```

### 🔍 **Comparisons** (Smart - 5-10 seconds)
```
比較七月和八月
Compare July and August
七月和八月差多少？
```

### 🔮 **Forecasts** (Predictive - 8-12 seconds)
```
預測下個月支出
Forecast next month spending
九月會花多少？
```

### 📊 **Visualizations** (Interactive)
```
給我看每月支出圖表
Show me monthly spending chart
顯示伙食費趨勢圖
Display food expense trend
```

### 💡 **Advice & Optimization** (Strategic - 10-15 seconds)
```
幫我規劃九月預算
Help me plan September budget
哪裡可以節省？
Where can I save money?
建議我怎麼減少開銷？
```

---

## 🌍 Language Support

### **Automatic Detection**
- Just ask in your preferred language
- System auto-detects Chinese or English
- Responds in the same language

### **Examples:**
```
You: How much in July?
Assistant: Total July spending: NT$27,300

您: 七月花了多少？
助手: 七月總支出 NT$27,300
```

---

## 🛡️ What's NOT Allowed (Guardrails)

### ❌ Will Be Rejected:
- **Off-topic**: "What's the weather?" 
- **Investment advice**: "Should I buy stocks?"
- **General chat**: "Tell me a joke"
- **Technical support**: "How do I fix this bug?"

### ✅ Response:
```
抱歉，這個問題超出我的專業範圍。

我是專門的**預算分析助手**，只能回答關於您的2025年度預算資料的問題。

✅ 我能回答的問題類型：
• 💰 支出查詢 (例：「七月花了多少？」)
• 📊 趨勢分析 (例：「伙食費趨勢如何？」)
...
```

---

## 🎯 Pro Tips

### **1. Be Specific**
❌ "花了多少?" (too vague)
✅ "七月的伙食費是多少?" (specific month + category)

### **2. Use Follow-ups**
```
You: 七月花了多少？
Assistant: NT$27,300 💡 要看圖表嗎？
You: 要
Assistant: [Shows chart]
```

### **3. Ask "Why"**
```
You: 八月為什麼增加？
Assistant: 八月支出增加主要因為伙食費 +NT$3,200...
[Detailed explanation with insights]
```

### **4. Request Visualization Anytime**
```
You: 給我看圖表
You: Show me a chart
You: gui圖表 (for graphical window)
```

### **5. Chain Questions**
```
You: 七月花了多少？
Assistant: NT$27,300
You: 跟八月比呢？
Assistant: 八月比七月多 NT$5,200 (增加19%)
You: 為什麼？
Assistant: 主要原因是...
```

---

## 🔧 Customization

### Change Default Language (config.py)
```python
LANGUAGE_CONFIG = {
    "default_language": "zh",  # Force Chinese
    # OR
    "default_language": "en",  # Force English
    # OR
    "default_language": "auto",  # Auto-detect (default)
}
```

### Adjust Guardrails Strictness
In `modules/insights/guardrails.py`:
```python
# Current: Whitelist-only (strictest)
# To allow more ambiguous questions:
if not has_allowed_keyword:
    return True, 'ambiguous', ''  # Allow instead of reject
```

---

## 🐛 Troubleshooting

### **Problem**: "❌ 無法載入AI助手"
**Solution**: Make sure all new modules are present in `modules/insights/`:
- localized_templates.py
- language_detector.py
- question_classifier.py
- instant_answers.py
- data_preprocessor.py
- prompt_builder.py
- response_formatter.py
- guardrails.py
- ai_chat.py

### **Problem**: Questions rejected as off-topic
**Solution**: Add keywords to `ALLOWED_TOPICS` in `guardrails.py`

### **Problem**: Wrong language detected
**Solution**: 
1. Use more keywords from that language
2. Or set `default_language` in config.py

### **Problem**: Slow responses
**Solution**: 
- Simple queries should be <1s (instant answers)
- Complex questions 8-15s (LLM reasoning)
- Check LLM timeout settings in config.py

---

## 📊 Architecture Overview

```
User Question
    ↓
Language Detector (auto-detect zh/en)
    ↓
Guardrails Layer 1: Topic Check (whitelist-only)
    ↓ (if allowed)
Question Classifier (type + entities)
    ↓
Route to Handler:
    ├─→ Instant Answers (Python only, <1s)
    ├─→ Visualization (show charts)
    ├─→ Forecast (predict future)
    ├─→ Comparison (analyze differences)
    ├─→ LLM Pipeline:
    │      ├─→ Data Preprocessor (compute stats)
    │      ├─→ Qwen (extract data)
    │      └─→ GPT-OSS (reason & advise)
    ↓
Guardrails Layer 2: Data Scope (validate entities)
Guardrails Layer 3: Response Check (verify accuracy)
    ↓
Response Formatter (emojis, structure, follow-ups)
    ↓
Output to User
```

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Simple questions answered in <1 second
- ✅ Off-topic questions politely redirected
- ✅ English and Chinese both work
- ✅ Numbers formatted with commas (NT$27,300)
- ✅ Responses include emojis and follow-ups
- ✅ Charts appear when requested
- ✅ Forecasts provide predictions with confidence

---

## 📞 Support

For issues or questions:
1. Check `AI_CHAT_IMPLEMENTATION.md` for details
2. Review module docstrings for API reference
3. Check linter: `pylint modules/insights/ai_chat.py`

---

**Happy Chatting! 💬🎉**

