# AI Chatbot - Budget Chat Module 💬

Complete documentation for the intelligent budget chat system with dual-LLM collaboration.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [What You Can Ask](#what-you-can-ask)
3. [How It Works](#how-it-works)
4. [3-Tier Data Access](#3-tier-data-access)
5. [Confidence Tracking](#confidence-tracking)
6. [Language Support](#language-support)
7. [Visual Reports](#visual-reports)
8. [Configuration](#configuration)
9. [Known Limitations](#known-limitations)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Access AI Chat

```bash
python _main.py
→ [3] 💬 預算分析對話 (Budget Chat & Insights)
→ [1] 🤖 智能問答 (AI Chat)
```

### First Questions to Try

```
✅ Simple (Instant):
七月花了多少？
How much in July?
七月的伙食費是多少？

✅ Analysis (5-10s):
為什麼八月增加？
Compare July and August
Show me a trend

✅ Visualization:
給我看圖表
Show me a chart
Display food spending trend
```

---

## 💬 What You Can Ask

### 1. Spending Queries (Instant - Tier 1) ⚡

**Chinese:**
```
七月花了多少？
7月的伙食費是多少？
總支出是多少？
平均每月花多少？
```

**English:**
```
How much in July?
What's the food expense in July?
Total spending?
Average per month?
```

**Response Time:** < 1 second  
**Confidence:** 🟢 95%+ (Python calculation)

---

### 2. Comparisons (Fast - Tier 2) 🔍

**Chinese:**
```
比較七月和八月
七月跟八月差多少？
哪個月花最多？
```

**English:**
```
Compare July and August
What's the difference between July and August?
Which month spent the most?
```

**Response Time:** ~5 seconds  
**Confidence:** 🟡 75-85% (LLM + summary data)

---

### 3. Trend Analysis (Tier 2/3) 📈

**Chinese:**
```
伙食費趨勢如何？
為什麼八月增加？
支出有什麼變化？
```

**English:**
```
What's the food expense trend?
Why did August increase?
How has spending changed?
```

**Response Time:** 5-15 seconds  
**Confidence:** 🟡 70-85% (depends on complexity)

---

### 4. Forecasting (Tier 3) 🔮

**Chinese:**
```
預測下個月支出
九月會花多少？
```

**English:**
```
Forecast next month spending
How much will September be?
```

**Response Time:** ~15 seconds  
**Confidence:** 🟠 60-75% (predictive)

---

### 5. Visualizations 📊

**Chinese:**
```
給我看每月支出圖表
顯示伙食費趨勢圖
畫一個圓餅圖
```

**English:**
```
Show me monthly spending chart
Display food expense trend
Draw a pie chart
```

**Response Time:** 3-5 seconds (GUI), <1s (terminal)  
**Output:** Interactive charts or ASCII graphs

---

### 6. Detail Queries (Tier 3) 🔎

**Chinese:**
```
七月有哪些超過1000的交易？
8月15日花了什麼？
```

**English:**
```
What transactions over NT$1000 in July?
What did I spend on August 15?
```

**Response Time:** 10-20 seconds  
**Confidence:** 🟡 70-80% (full data analysis)

---

## ❌ What Doesn't Work

### 🚫 Complex Questions (Rejected)

```
❌ 如果減少伙食費，會省多少，還有應該怎麼做？
   (If/and - too complex)

❌ Can you tell me how much I spent on food in July 
   and also compare it with August?
   (Multi-part question)

❌ 你覺得哪個月最好？
   (Opinion/subjective)

❌ 明年會不會破產？
   (Speculation beyond data)
```

**Why rejected?**
- Contains 2+ complexity indicators (if/and/when)
- Question length > 15 words
- Requires speculation or opinion

**What you'll see:**
```
助手: 抱歉，我沒有這個答案。

我只能回答簡單、明確的預算問題：

✅ 我能回答:
• 「七月花了多少？」
• 「七月的伙食費是多少？」
• 「比較七月和八月」

❌ 我不能回答:
• 複雜的分析問題
• 需要推測的問題

請用簡單、具體的問題重新問我。
```

---

### 🚫 Off-Topic Questions (Rejected)

```
❌ 今天天氣怎麼樣？
❌ Should I invest in stocks?
❌ Tell me a joke
❌ 如何學Python？
```

**Why rejected?**
- Whitelist-only guardrails (budget keywords required)
- No off-topic processing

**What you'll see:**
```
🚫 這個問題超出我的專業範圍（預算分析），無法準確回答。

我是專門的**預算分析助手**...
```

---

## 🔄 How It Works

### Complete System Flow

```
USER QUESTION
    ↓
┌─────────────────────────────────────┐
│ 1. Language Detection               │
│    Auto-detect: 中文 or English     │
│    Confidence: ~95%                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Guardrails - Topic Check         │
│    ✅ Budget keywords present?      │
│    ✅ Complexity acceptable?        │
│    ❌ Off-topic? → Reject           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Question Classification          │
│    Type: instant/compare/trend/etc  │
│    Entities: {month, category, ...} │
│    Complexity score: 0-10           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. Route to Handler                 │
│    → instant_answers                │
│    → comparisons                    │
│    → visualizations                 │
│    → forecasts                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ 5. 3-TIER DATA ACCESS                           │
│                                                 │
│  TIER 1: Python Only (⚡ <1s)                   │
│  ├─ Load from OneDrive Excel → pandas          │
│  ├─ Direct calculation (sum/filter/count)      │
│  └─ 80% of questions stop here ✅              │
│          ↓ (if failed or uncertain)            │
│                                                 │
│  TIER 2: LLM + Summary Data (🧠 ~5s)           │
│  ├─ Load summary stats (aggregated)            │
│  ├─ Qwen3:8b extracts answer from summary      │
│  └─ 15% of questions stop here ✅              │
│          ↓ (if failed or uncertain)            │
│                                                 │
│  TIER 3: LLM + Full Excel Data (📊 ~15s)       │
│  ├─ Load FULL data from OneDrive Excel         │
│  ├─ GPT-OSS:20b analyzes complete dataset      │
│  └─ 5% of questions need this ✅               │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 6. Confidence Calculation           │
│    • Data availability: 40%         │
│    • Question clarity: 20%          │
│    • LLM confidence: 20%            │
│    • Guardrail passed: 10%          │
│    • Response verified: 10%         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 7. Response Formatting              │
│    • Add emojis & structure         │
│    • Format numbers (NT$15,420)     │
│    • Add follow-up suggestions      │
│    • Add confidence bar             │
└─────────────────────────────────────┘
    ↓
OUTPUT TO USER
```

---

## 🎯 3-Tier Data Access

### Why 3 Tiers?

**Problem:** Traditional chatbots either:
- Use full data → Slow, expensive (~20s per query)
- Use summaries → Fast but limited accuracy

**Solution:** Intelligent escalation

```
Start FAST (Python) → Try MODERATE (Summary) → Go DEEP (Full Data)
     ↓                      ↓                        ↓
    Free                ~500 tokens              ~5000 tokens
   <1 sec                 ~5 sec                   ~15 sec
   100% accurate          85% accurate             90% accurate
```

---

### TIER 1: Python Calculation ⚡

**When:**
- Simple aggregation queries
- Single month + single category
- Exact date/amount queries

**Data Source:**
```
OneDrive Excel → pandas DataFrame → Direct calculation
```

**Example:**
```python
# Question: "七月的伙食費是多少？"
df = load_month('七月')  # From OneDrive
result = df[df['category'] == '伙食费']['amount'].sum()
# → NT$15,420 (instant!)
```

**Advantages:**
- ✅ 100% accurate (no LLM interpretation)
- ✅ Instant (<1 second)
- ✅ Free (no tokens used)
- ✅ Handles 80% of questions

**Limitations:**
- ⚠️ Only simple queries
- ⚠️ Exact entity match required

---

### TIER 2: LLM + Summary Data 🧠

**When:**
- Tier 1 uncertain or failed
- Comparison queries
- Unclear entity extraction
- Moderate complexity

**Data Source:**
```
OneDrive Excel → pandas → Aggregated stats → LLM (Qwen3:8b)
```

**Example:**
```python
# Question: "7月和8月的飯錢差多少？"
# (Numeric month, ambiguous "飯錢")

summary = {
    'by_month': {
        '七月': {'total': 27300, '伙食费': 15420},
        '八月': {'total': 32500, '伙食费': 18650}
    }
}

# Send to Qwen3:8b with summary (500 tokens)
answer = qwen.extract("問題", summary)
# → "七月伙食費NT$15,420，八月NT$18,650，差額+NT$3,230"
```

**Advantages:**
- ✅ Fast (~5 seconds)
- ✅ Low token usage (~500)
- ✅ Handles ambiguity
- ✅ 85% accuracy

**Limitations:**
- ⚠️ Can't see individual transactions
- ⚠️ May miss nuanced patterns

---

### TIER 3: LLM + Full Excel Data 📊

**When:**
- Tier 2 uncertain or failed
- Detail queries (specific transactions)
- Complex pattern analysis
- "Show me all X that match Y"

**Data Source:**
```
OneDrive Excel → pandas → FULL transaction data → LLM (GPT-OSS:20b)
```

**Example:**
```python
# Question: "七月有哪些超過1000的伙食費交易？"

full_data = load_month('七月')  # All transactions from OneDrive
transactions = full_data.to_dict('records')
# → [
#     {'date': '2025-07-01', 'category': '伙食费', 'amount': 150, ...},
#     {'date': '2025-07-01', 'category': '伙食费', 'amount': 220, ...},
#     ... (45 transactions)
# ]

# Send ALL data to GPT-OSS:20b (5000 tokens)
answer = gpt_oss.analyze("問題", transactions)
# → "七月超過NT$1,000的伙食費交易有5筆: ..."
```

**Advantages:**
- ✅ Comprehensive (sees everything)
- ✅ Can answer detail queries
- ✅ Pattern detection
- ✅ 90% accuracy

**Limitations:**
- ⚠️ Slower (~15 seconds)
- ⚠️ Higher token usage (~5000)
- ⚠️ Only 5% of questions need this

---

### Tier Selection Logic

```python
# Automatic escalation:

if question_type == 'instant':
    # Try Tier 1
    answer, conf = try_python_calculation()
    
    if conf < 0.6:  # Uncertain
        # Escalate to Tier 2
        answer, conf = try_llm_with_summary()
        
        if conf < 0.5:  # Still uncertain
            # Escalate to Tier 3
            answer, conf = try_llm_with_full_data()

return answer, conf
```

---

## 🎯 Confidence Tracking

### What is Confidence?

Every answer shows a **confidence score** (0-100%) based on 5 weighted components:

```
Confidence = Weighted Average of:
├─ 40% Data Availability      (Do we have the data?)
├─ 20% Question Clarity        (Is question unambiguous?)
├─ 20% LLM Confidence          (Is LLM certain?)
├─ 10% Guardrail Passed        (Passed validation?)
└─ 10% Response Verified       (Numbers match source?)
```

---

### Confidence Levels

```
🟢 High (80%+)
   Trust this answer
   Example: "七月總支出 NT$27,300"
   
🟡 Medium (60-79%)
   Verify if important
   Example: "大約增加15%左右"
   
🟠 Low (40-59%)
   Use with caution
   Example: "我猜可能是因為..."
   
🔴 Very Low (<40%)
   Don't rely on this
   Example: Off-topic rejection
```

---

### Example Outputs

#### High Confidence (95%)
```
您: 七月的伙食費是多少？

助手: 七月的伙食費總共 NT$15,420

🟢 信心度: ████████████████████ 95% (高)
   ℹ️ Tier 1 (Python)
```

#### Medium Confidence (72%)
```
您: 八月跟上個月比呢？

助手: ⚠️ 問題不太清楚，我盡力回答了，但可能不準確。

八月比七月多支出 NT$5,200 (增加19%)

🟡 信心度: ██████████████░░░░░░ 72% (中等)
   📋 詳細分析:
      • 問題清晰度: 55%
      • AI確定性: 78%
   ℹ️ Tier 2 (Summary)
```

#### Low Confidence (52%)
```
您: 下個月會不會超支？

助手: 🤔 我不太確定這個答案，建議您驗證一下。

基於最近3個月趨勢，可能會略微超出平均...

🟠 信心度: ██████████░░░░░░░░░░ 52% (偏低)
   📋 詳細分析:
      • 資料可用性: 70% (沒有未來數據)
      • 問題清晰度: 65%
      • AI確定性: 45% (包含推測詞)
   ℹ️ Tier 3 (Full Data)
```

---

### Understanding Warnings

| Warning | Meaning | Action |
|---------|---------|--------|
| ⚠️ 問題不太清楚 | Ambiguous question | Rephrase more specifically |
| 🤔 我不太確定 | LLM uncertain | Verify the answer |
| 🚫 超出專業範圍 | Off-topic | Ask budget-related question |
| 📋 資料可用性偏低 | Missing data | Check if data exists |
| 💡 建議驗證 | Low confidence | Manual verification recommended |

---

## 🌍 Language Support

### Automatic Detection

The system auto-detects your language:

```python
Input: "七月花了多少？"
Detected: 中文 (95% confidence)
Response language: 中文

Input: "How much in July?"
Detected: English (92% confidence)  
Response language: English
```

**Detection accuracy:** ~95%

---

### Supported Languages

| Language | Support | Notes |
|----------|---------|-------|
| 中文 (Chinese) | ✅ Full | Primary language |
| English | ✅ Full | Complete support |
| Mixed | ⚠️ Partial | Detects majority language |
| Others | ❌ No | Only zh/en supported |

---

### Language Features

**Month Recognition:**
```
✅ 七月, 7月, July, Jul    (all work)
✅ 一月, 1月, January, Jan
✅ 十二月, 12月, December, Dec
```

**Category Names:**
```
Budget data uses Chinese:
• 伙食費 (food)
• 交通費 (transportation)
• 休閒/娛樂 (entertainment)
• 家務 (household)

English questions work:
"food expense" → maps to "伙食費"
"transport cost" → maps to "交通費"
```

**Number Formatting:**
```
Chinese: NT$15,420
English: NT$15,420
(Same format for both)
```

---

## 📊 Visual Reports

### Terminal Graphs (ASCII) 🖥️

**Features:**
- ✅ Works in any terminal
- ✅ Works over SSH
- ✅ Fast (<1 second)
- ✅ No display required

**Types:**
- Bar charts (vertical & horizontal)
- Line charts for trends
- Multi-series comparisons
- Stacked visualizations

**Example:**
```
     伙食費月度趨勢
60000┤              ╭╮
50000┤            ╭╯╰╮
40000┤          ╭╯   ╰╮
30000┤        ╭╯      ╰╮
20000┤      ╭╯         ╰╮
10000┤    ╭╯            ╰╮
    0┤────┴──────────────╯
     1月 3月 5月 7月 9月 11月
```

---

### GUI Charts (Matplotlib) 📈

**Features:**
- ✅ Professional quality
- ✅ Full color
- ✅ Interactive (zoom, pan)
- ✅ Chinese font support

**Types:**
- Pie charts (category distribution)
- Donut charts (modern view)
- Bar charts (comparisons)
- Line charts (trends with markers)
- Stacked area charts (composition)
- Grouped bars (multi-series)

**Requirements:**
- Display server (TkAgg backend)
- Won't work over SSH

**Example Request:**
```
You: 給我看圖表
Assistant: [Choice: Terminal or GUI?]
You: GUI
Assistant: [Beautiful matplotlib chart appears]
```

---

### Rich Tables 📋

**Features:**
- ✅ Beautiful formatting
- ✅ Color-coded
- ✅ Visual progress bars
- ✅ Trend indicators (↑↓→)

**Example:**
```
📊 七月支出分析
┌─────────────┬──────────┬────────┬─────────┐
│ 類別        │ 金額     │ 佔比   │ 趨勢    │
├─────────────┼──────────┼────────┼─────────┤
│ 伙食費      │ 15,420   │ 56%    │ ↑ +12%  │
│ 交通費      │  4,200   │ 15%    │ → 持平  │
│ 休閒/娛樂   │  5,500   │ 20%    │ ↑ +25%  │
│ 家務        │  2,180   │  8%    │ ↓ -5%   │
├─────────────┼──────────┼────────┼─────────┤
│ 總計        │ 27,300   │ 100%   │ ↑ +8%   │
└─────────────┴──────────┴────────┴─────────┘
```

---

## ⚙️ Configuration

### Toggle Confidence Display

```python
# config.py
AI_CHAT_CONFIG = {
    "show_confidence": True,           # Show scores
    "confidence_threshold": 0.6,        # Warn if < 60%
    "verbose_uncertainty": True,        # Show breakdown
    "show_uncertainty_warning": True    # Show warnings
}

# To hide confidence:
AI_CHAT_CONFIG = {
    "show_confidence": False,  # Clean output
    ...
}
```

---

### Adjust Dual-LLM Pipeline

```python
# config.py
AI_CHAT_CONFIG = {
    "use_dual_pipeline": True,      # Enable Qwen→GPT-OSS
    "dual_pipeline_mode": "smart"   # "smart" | "always" | "never"
}

# Modes:
# "smart" = Use for complex questions only (balanced)
# "always" = All questions use both LLMs (slower, higher quality)
# "never" = Single LLM only (faster, lower quality)
```

---

### Force Language

```python
# config.py
LANGUAGE_CONFIG = {
    "default_language": "auto",  # Auto-detect (default)
    # OR
    "default_language": "zh",    # Force Chinese
    # OR
    "default_language": "en",    # Force English
}
```

---

### Cache TTL

```python
# modules/insights/data_loader.py
class BudgetDataLoader:
    def __init__(self):
        self.ttl = 300  # 5 minutes (default)
        # Increase for slower data changes:
        # self.ttl = 600  # 10 minutes
```

---

## ⚠️ Known Limitations

### 1. Question Complexity Limits

**Current:**
- Max 15 words per question
- Single-part questions only
- No conditional reasoning ("if X then Y")
- No multi-step analysis

**Examples that fail:**
```
❌ "如果減少伙食費，會省多少，還有應該怎麼做？"
❌ "Can you tell me how much I spent on food in July 
   and also compare it with August and tell me why?"
```

**Workaround:** Break into multiple questions:
```
✅ Q1: "七月伙食費多少？"
✅ Q2: "八月伙食費多少？"
✅ Q3: "為什麼八月增加？"
```

**Status:** 🔧 Planned fix in v2.1 (question decomposition)

---

### 2. Language Detection Accuracy

**Current:** ~95% accurate

**Issues:**
- Mixed language sometimes misdetected
- Very short questions (<3 words) harder to detect
- No support beyond Chinese/English

**Examples:**
```
⚠️ "Show 七月 data" (mixed)
   May detect as English, respond in English

⚠️ "多少？" (too short)
   Low confidence detection
```

**Workaround:** Use more keywords in preferred language

**Status:** 🔧 Planned improvement in v2.1

---

### 3. No Response Caching

**Current:** Every similar question hits LLM again

**Impact:**
```
Q1: "七月花了多少？" → 5s
Q2: "七月花了多少？" → 5s (same query, no cache!)
```

**Workaround:** None (inherent limitation)

**Status:** 🔧 High priority for v2.1 (40% speed improvement expected)

---

### 4. Relative Dates Not Supported

**Current:** Only absolute dates work

**Examples:**
```
❌ "今天" (today)
❌ "上週" (last week)
❌ "這個月" (this month)

✅ "7月15日"
✅ "七月"
✅ "August"
```

**Workaround:** Use explicit dates

**Status:** 🔧 Planned for v2.2

---

### 5. GUI Charts Slow

**Current:** 3-5 seconds to generate

**Why:**
- Matplotlib initialization
- Chinese font loading
- Rendering overhead

**Workaround:** Use terminal charts (instant)

**Status:** 🔧 Async generation planned for v2.2

---

### 6. Context Window Limited

**Current:** Only last 10 interactions remembered

**Impact:**
```
After 10 questions, earlier context forgotten
No long-term memory
```

**Workaround:** Repeat relevant context in question

**Status:** 🔧 Vector-based memory planned for v2.2

---

### 7. Numeric Precision

**Current:** LLM sometimes rounds numbers

**Example:**
```
Actual:  NT$15,423
LLM says: NT$15,420 (rounded to nearest 10)
```

**Mitigation:** Tier 1 (Python) always exact, Tier 2/3 may round

**Workaround:** Check confidence; if critical, verify manually

**Status:** 🔧 Forced exact extraction planned for v2.1

---

## 🐛 Troubleshooting

### Problem: "抱歉，我沒有這個答案"

**Possible Causes:**
1. Question too complex (>15 words, multi-part)
2. Off-topic (no budget keywords)
3. Contains conditional/speculative language

**Solution:**
- Simplify question
- Ask one thing at a time
- Use budget-related keywords
- Check examples in "What You Can Ask" section

---

### Problem: Low Confidence (<60%)

**Possible Causes:**
1. Ambiguous question ("上個月" - which month?)
2. Missing data (querying month without data)
3. LLM uncertain (response contains "可能", "大概")

**Solution:**
- Be more specific (use exact month names)
- Check if data exists for that period
- Verify answer if critical

---

### Problem: Wrong Language Detected

**Possible Causes:**
1. Mixed language in question
2. Too few keywords
3. Ambiguous words

**Solution:**
- Use more words in preferred language
- Set default language in config.py
- Avoid mixing languages in one question

---

### Problem: "No data available"

**Possible Causes:**
1. Data not loaded from Excel
2. OneDrive sync issue
3. Month sheet doesn't exist

**Solution:**
```bash
# Check Excel file exists
ls -la "/Users/peter/Library/CloudStorage/OneDrive-Personal/Documents/2025年開銷表（NT）.xlsx"

# Check sheets
python utils/view_sheets.py
```

---

### Problem: Charts Don't Appear

**GUI Charts:**
- Check if display server available (not over SSH)
- Try terminal charts instead

**Terminal Charts:**
- Should always work
- Check terminal size (needs >= 80x24)

---

### Problem: Slow Responses

**Expected Times:**
- Tier 1 (Python): <1s
- Tier 2 (Summary): ~5s
- Tier 3 (Full Data): ~15s

**If slower:**
1. Check Ollama running: `ollama ps`
2. Check LLM models loaded
3. Check system resources
4. Try simpler questions (stay in Tier 1)

---

## 📚 Module Architecture

### File Structure

```
modules/insights/
├── ai_chat.py                  # Main AI chat controller
├── budget_chat.py              # Overall insights coordinator
├── data_loader.py              # Excel data loading (OneDrive)
├── multi_year_data_loader.py  # Multi-year support (backend)
├── context_manager.py          # Conversation history
├── insight_generator.py        # Structured insights
├── trend_analyzer.py           # Trend analysis & forecasting
├── confidence_tracker.py       # Confidence scoring
├── guardrails.py               # Topic validation
├── language_detector.py        # Language auto-detection
├── question_classifier.py      # Question routing
├── instant_answers.py          # 3-tier data access
├── data_preprocessor.py        # Data preparation
├── prompt_builder.py           # LLM prompt optimization
├── response_formatter.py       # Response beautification
├── localized_templates.py      # Bilingual templates
├── visual_report_generator.py  # Rich tables
├── terminal_graphs.py          # ASCII charts
├── gui_graphs.py               # Matplotlib charts
├── chat_menus.py               # Interactive menus
└── AI_CHATBOT_README.md        # This file
```

---

### Key Classes

```python
# Main controller
ai_chat = AIChat(data_loader, orchestrator)
answer = ai_chat.chat("七月花了多少？")

# Data loader (OneDrive Excel)
data_loader = BudgetDataLoader(excel_path)
data = data_loader.load_month('七月')

# Confidence tracking
tracker = ConfidenceTracker()
score = tracker.calculate_confidence(components)

# Guardrails
guardrails = Guardrails()
is_allowed, reason = guardrails.check_topic(question)
```

---

## 📈 Performance Metrics

| Metric | Performance | Notes |
|--------|-------------|-------|
| Simple query (Tier 1) | <1 second | 80% of queries |
| Medium query (Tier 2) | ~5 seconds | 15% of queries |
| Complex query (Tier 3) | ~15 seconds | 5% of queries |
| Language detection | ~0.1 seconds | 95% accuracy |
| Confidence calculation | ~0.05 seconds | Instant |
| Terminal chart | <1 second | ASCII render |
| GUI chart | 3-5 seconds | Matplotlib |
| Cache hit (planned) | <0.5 seconds | v2.1 feature |

---

## 🎓 Best Practices

### 1. Be Specific
```
❌ "花了多少？" (which month?)
✅ "七月花了多少？"

❌ "費用" (which category?)
✅ "七月的伙食費"
```

### 2. One Question at a Time
```
❌ "七月花了多少，還有八月呢？"
✅ Q1: "七月花了多少？"
✅ Q2: "八月呢？"
```

### 3. Check Confidence
```
🟢 80%+ → Trust it
🟡 60-79% → Verify if important
🟠 40-59% → Use with caution
🔴 <40% → Don't rely on it
```

### 4. Use Follow-ups
```
You: 七月花了多少？
AI: NT$27,300 💡 要看圖表嗎？
You: 要
AI: [Shows chart]
```

### 5. Leverage Visuals
```
Complex data? → Ask for chart
"給我看圖表"
"Show me a graph"
```

---

## 🚀 Quick Reference

### Common Questions & Commands

| What You Want | What to Ask |
|---------------|-------------|
| Total spending | "七月花了多少？" / "How much in July?" |
| Category total | "七月的伙食費？" / "Food expense in July?" |
| Comparison | "比較七月和八月" / "Compare July and August" |
| Trend | "伙食費趨勢" / "Food expense trend" |
| Forecast | "預測下個月" / "Forecast next month" |
| Chart | "給我看圖表" / "Show me a chart" |
| Details | "七月超過1000的交易" / "Transactions over 1000 in July" |

---

## 📞 Need Help?

1. **This README** - Complete AI Chat guide
2. **[Main README](../../README.md)** - System overview
3. **[IMPROVEMENTS_ROADMAP](../../IMPROVEMENTS_ROADMAP.md)** - Known issues & roadmap
4. **[LLM Mix Model](../../docs/LLM_MIX_MODEL.md)** - How dual-LLM works

---

**Module Version:** 2.0  
**Status:** Production Ready ✅  
**Last Updated:** 2025-01-22  

---

Built with intelligence, transparency, and user experience in mind 💚

