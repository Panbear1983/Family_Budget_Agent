# Improvements & Roadmap 🚧

Complete guide to features in progress, known issues, optimizations, and future vision for Family Budget Agent.

---

## 📋 Table of Contents

1. [Current Status](#current-status)
2. [Known Limitations](#known-limitations)
3. [Performance Bottlenecks](#performance-bottlenecks)
4. [Phase 2: Optimizations (v2.1)](#phase-2-optimizations-v21---in-progress)
5. [Phase 3: New Features (v2.2)](#phase-3-new-features-v22---planned)
6. [Phase 4: Advanced (v3.0)](#phase-4-advanced-v30---future-vision)
7. [Known Issues & Workarounds](#known-issues--workarounds)
8. [Contribution Opportunities](#contribution-opportunities)
9. [Experimental Features](#experimental-features)

---

## ✅ Current Status (v2.0)

### Production Ready Features

```
✅ Core System
├── CSV processing with dual-LLM pipeline
├── Monthly budget merging
├── Annual file management
├── OneDrive sync integration
└── Modular plugin architecture

✅ AI Chat System
├── 3-tier data access (Python → Summary → Full Data)
├── Confidence tracking (5-component scoring)
├── Bilingual support (中文/English auto-detect)
├── Guardrails (whitelist-only topic enforcement)
└── Response formatting with emojis

✅ Visualization
├── Rich terminal tables (with colors & trends)
├── Terminal graphs (ASCII charts via plotext)
├── GUI charts (matplotlib with Chinese fonts)
└── Interactive menus

✅ Dual-LLM Mix Model
├── Qwen3:8b (structured tasks, 5.2GB)
├── GPT-OSS:20b (deep reasoning, 13GB)
├── Smart orchestration & automatic handoff
└── Confidence-based collaboration
```

### System Metrics (Current)

| Component | Performance | Status |
|-----------|-------------|--------|
| CSV processing (45 tx) | ~8 seconds | ✅ Good |
| Simple chat query (Tier 1) | <1 second | ✅ Excellent |
| Medium query (Tier 2) | ~5 seconds | ✅ Good |
| Complex query (Tier 3) | ~15 seconds | ⚠️ Can optimize |
| GUI chart generation | 3-5 seconds | ⚠️ Can optimize |
| Language detection | ~0.1s, 95% acc | ✅ Good |
| Duplicate detection | 98% accuracy | ✅ Excellent |
| Category accuracy | 95%+ | ✅ Excellent |

---

## ⚠️ Known Limitations

### 1. AI Chat Complexity Limits 🤖

**Issue:**
- Max 15 words per question
- Single-part questions only
- No conditional reasoning ("if X then Y")
- No multi-step analysis

**Examples That Fail:**
```
❌ "如果減少伙食費，會省多少，還有應該怎麼做？"
   (Too many parts: if/save/what to do)

❌ "Can you tell me how much I spent on food in July 
   and also compare it with August and tell me why?"
   (Multi-part: ask + compare + explain)

❌ "你覺得哪個月最好？"
   (Opinion/subjective - no data basis)
```

**Current Workaround:**
Break into multiple simple questions:
```
✅ Q1: "七月伙食費多少？"
✅ Q2: "八月伙食費多少？"
✅ Q3: "為什麼八月增加？"
```

**Planned Fix:** 
- **v2.1** - Question decomposition engine
- Automatically break complex questions into simple ones
- Answer each part, combine results
- **Complexity:** High
- **ETA:** 2-3 months
- **Impact:** Answer 30% more questions

---

### 2. No LLM Response Caching 💾

**Issue:**
Every similar/repeated question queries LLM again

**Impact:**
```
Q1: "七月花了多少？" → 5s (Tier 2)
[Wait 1 minute]
Q2: "七月花了多少？" → 5s (Same query, no cache!)

Expected with cache: <0.5s
```

**Why It Matters:**
- Users often ask similar questions
- Wastes resources (tokens, time)
- Poor UX for repeated queries

**Planned Fix:**
- **v2.1** - Redis-like in-memory cache
- 1-hour TTL (Time To Live)
- Cache key: hash(question + relevant data)
- Invalidate on data update
- **Complexity:** Medium
- **ETA:** 1-2 months
- **Impact:** 40% speed improvement for repeated queries

---

### 3. GUI Charts Slow 📊

**Issue:**
- 3-5 seconds to generate matplotlib charts
- Blocks UI during generation
- Chinese font loading adds overhead

**Why:**
```
Chart Generation Process:
├── Matplotlib init: 1.5s
├── Chinese font load: 0.8s
├── Data processing: 0.3s
├── Rendering: 0.9s
└── Total: ~3.5s
```

**Current Workaround:**
Use terminal charts (instant, ASCII-based)

**Planned Fix:**
- **v2.2** - Async chart generation
- Generate in background thread
- Show progress indicator
- Cache rendered charts
- **Complexity:** Medium
- **ETA:** 3-4 months
- **Impact:** UI stays responsive, perceived speed 2x

---

### 4. Fuzzy Duplicate Detection Limited 🔍

**Issue:**
- Rule-based duplicate detection: 98% accurate
- LLM-assisted fuzzy matching: ~85% accurate
- Edge cases still need manual review

**Examples That Fail:**
```
Transaction 1: "家樂福 - 購物"  NT$1,523  2025-07-15
Transaction 2: "Carrefour"      NT$1,523  2025-07-15
→ Should be duplicate, but descriptions differ

Transaction 1: "Starbucks"  NT$150  2025-07-10 09:30
Transaction 2: "Starbucks"  NT$150  2025-07-10 14:20
→ Same day, same amount, but different transactions!
```

**Current Workaround:**
Manual review of flagged uncertain duplicates

**Planned Fix:**
- **v2.1** - Learning mode
- Log user corrections
- Improve patterns over time
- Confidence-weighted learning
- **Complexity:** Medium
- **ETA:** 2-3 months
- **Impact:** 95%+ accuracy after 3 months of learning

---

### 5. Multi-Year Analysis UI Incomplete 📅

**Issue:**
- Backend exists (`multi_year_data_loader.py`)
- Data loading works
- UI integration incomplete
- Can't compare 2024 vs 2025 in chat

**What Works:**
```python
# Backend (works):
loader = MultiYearDataLoader()
data = loader.load_years([2024, 2025])
comparison = loader.compare_years(2024, 2025)
```

**What Doesn't Work:**
```
User: "比較2024和2025年的伙食費"
AI: "抱歉，我沒有這個答案" (no UI routing)
```

**Current Workaround:**
Use Python console to access backend directly

**Planned Fix:**
- **v2.1** - Complete UI integration
- Add to AI Chat question classifier
- Add to visual reports menu
- Multi-year charts
- **Complexity:** Low (backend done)
- **ETA:** 1 month
- **Impact:** Year-over-year analysis available

---

### 6. Language Detection Edge Cases 🌍

**Issue:**
- ~95% accuracy (good but not perfect)
- Mixed language sentences problematic
- Very short questions harder to detect

**Examples:**
```
⚠️ "Show 七月 data"
   Detected as: English (60% conf)
   Should detect: Mixed → use context

⚠️ "多少？" (too short - 2 words)
   Detected with: Low confidence
   May default to wrong language

✅ "七月花了多少？" (clear Chinese)
   Detected correctly: 95% conf
```

**Current Workaround:**
- Use more keywords in preferred language
- Set default language in config

**Planned Fix:**
- **v2.1** - Improved detection algorithm
- Context-aware detection (conversation history)
- Mixed language support
- User preference learning
- **Complexity:** Medium
- **ETA:** 2 months
- **Impact:** 98%+ accuracy

---

### 7. No Relative Date Support 📆

**Issue:**
Only absolute dates/months work

**Examples That Don't Work:**
```
❌ "今天花了多少？" (today)
❌ "上週的支出" (last week)
❌ "這個月" (this month)
❌ "最近三個月" (recent 3 months)

✅ "7月15日"
✅ "七月"
✅ "2024年八月"
```

**Current Workaround:**
Calculate date manually, use explicit dates

**Planned Fix:**
- **v2.2** - Relative date parser
- Map "今天" → current date
- Map "上週" → last 7 days
- Map "這個月" → current month
- **Complexity:** Low
- **ETA:** 2-3 months
- **Impact:** More natural conversation

---

### 8. Context Window Limited 🧠

**Issue:**
- Only last 10 interactions remembered
- No long-term conversation memory
- Can't reference earlier topics

**Example:**
```
[After 15 questions]
You: "回到我們剛才說的那個問題"
AI: "我不記得了" (context lost after 10 turns)
```

**Current Workaround:**
Repeat relevant context in question

**Planned Fix:**
- **v2.2** - Vector-based long-term memory
- Embed all past conversations
- Semantic search over history
- Retrieve relevant past interactions
- **Complexity:** High
- **ETA:** 4-6 months
- **Impact:** Truly conversational AI

---

### 9. No PDF/Image Export 📄

**Issue:**
- Can't save charts as images
- Can't export reports to PDF
- Can't share insights easily

**Current Workaround:**
Screenshot manually

**Planned Fix:**
- **v2.1** - Export module
- Save charts as PNG/SVG
- Export conversations to PDF
- Email report functionality
- **Complexity:** Low
- **ETA:** 1-2 months
- **Impact:** Easy sharing & archival

---

### 10. Fixed Confidence Threshold ⚖️

**Issue:**
- Handoff threshold hardcoded (85%)
- Not adaptive to question type
- User risk tolerance ignored

**Current:**
```python
if qwen_confidence < 0.85:
    escalate_to_gpt_oss()
```

**Better:**
```python
# Adaptive thresholds:
if question_type == 'instant':
    threshold = 0.75  # More lenient
elif question_type == 'financial_advice':
    threshold = 0.95  # Very strict
```

**Planned Fix:**
- **v2.2** - Dynamic thresholds
- Per-question-type thresholds
- User preference setting
- Learn from feedback
- **Complexity:** Medium
- **ETA:** 3-4 months
- **Impact:** Better quality/speed trade-off

---

## 📊 Performance Bottlenecks

### Current Performance Profile

```
┌──────────────────────────────────────────────────────────┐
│ CSV Processing (45 transactions)                        │
├──────────────────────────────────────────────────────────┤
│ Load CSV:                0.1s  ✅                        │
│ Qwen categorization:     3.2s  ⚠️ CAN OPTIMIZE (batch)  │
│ GPT-OSS refinement:      4.5s  ⚠️ CAN OPTIMIZE (cache)  │
│ Merge to Excel:          0.3s  ✅                        │
│ Save Excel:              0.5s  ✅                        │
├──────────────────────────────────────────────────────────┤
│ TOTAL:                   8.6s                            │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ AI Chat Query (varies by tier)                          │
├──────────────────────────────────────────────────────────┤
│ Tier 1 (Python):         0.2s  ✅ OPTIMAL               │
│ Tier 2 (Summary):        5.3s  ⚠️ CAN CACHE             │
│ Tier 3 (Full Data):     18.7s  🔴 NEEDS OPTIMIZATION    │
├──────────────────────────────────────────────────────────┤
│ No caching currently - every query hits LLM             │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ Visual Reports                                           │
├──────────────────────────────────────────────────────────┤
│ Terminal charts:         0.5s  ✅ OPTIMAL               │
│ GUI charts:              3.2s  ⚠️ CAN LAZY LOAD         │
│ Rich tables:             0.1s  ✅ OPTIMAL               │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ Memory Usage (both LLMs loaded)                         │
├──────────────────────────────────────────────────────────┤
│ Qwen3:8b:                5.2GB                           │
│ GPT-OSS:20b:            13.0GB                           │
│ Python process:          0.5GB                           │
├──────────────────────────────────────────────────────────┤
│ TOTAL:                  18.7GB  ⚠️ High but manageable  │
└──────────────────────────────────────────────────────────┘
```

---

### Optimization Opportunities

#### 1. Batch Categorization 📦

**Current:**
```python
# Process one transaction at a time
for tx in transactions:
    category = qwen.categorize(tx)  # 45 LLM calls!
```

**Optimized:**
```python
# Process in batches of 10
for batch in chunk(transactions, 10):
    categories = qwen.categorize_batch(batch)  # 5 LLM calls
```

**Expected Impact:**
- Speed: 6x faster (8s → 1.5s for CSV processing)
- Quality: Same or better (context helps)
- **Complexity:** Low
- **ETA:** v2.1 (1 month)

---

#### 2. Response Caching 💾

**Current:**
```python
answer = llm.query(question)  # Always hits LLM
```

**Optimized:**
```python
cache_key = hash(question + data_hash)
if cache_key in cache:
    return cache[cache_key]  # < 0.5s
else:
    answer = llm.query(question)
    cache[cache_key] = answer
    return answer
```

**Expected Impact:**
- Speed: 10x faster for repeated queries
- Cache hit rate: ~70% (typical usage)
- **Complexity:** Medium
- **ETA:** v2.1 (2 months)

---

#### 3. Lazy Chart Generation 🎨

**Current:**
```python
# Generate all chart types
terminal_chart = generate_terminal_chart()  # 0.5s
gui_chart = generate_gui_chart()           # 3.5s
table = generate_table()                    # 0.1s
# Total: 4.1s
```

**Optimized:**
```python
# Generate only what user requests
table = generate_table()  # Always show (0.1s)
# User chooses: terminal or GUI
if user_choice == 'terminal':
    chart = generate_terminal_chart()  # 0.5s
elif user_choice == 'gui':
    chart = generate_gui_chart_async()  # 3.5s background
```

**Expected Impact:**
- Speed: 2x faster perceived performance
- Resource: Lower memory usage
- **Complexity:** Low
- **ETA:** v2.1 (1 month)

---

#### 4. Tier 3 Data Pruning ✂️

**Current:**
```python
# Send ALL transactions to LLM
data = load_month('七月')  # 100 transactions
answer = llm.analyze(question, data)  # 5000 tokens!
```

**Optimized:**
```python
# Filter first, send only relevant data
data = load_month('七月')
relevant = filter_by_entities(data, question)  # 15 transactions
answer = llm.analyze(question, relevant)  # 800 tokens
```

**Expected Impact:**
- Speed: 2x faster Tier 3 queries
- Accuracy: Higher (less noise)
- Cost: 85% fewer tokens
- **Complexity:** Medium
- **ETA:** v2.1 (2 months)

---

#### 5. Model Quantization 🗜️

**Current:**
```
qwen3:8b → 5.2GB (full precision)
gpt-oss:20b → 13GB (full precision)
Total: 18.2GB
```

**Optimized:**
```
qwen3:8b-Q4_K_M → 2.6GB (quantized)
gpt-oss:20b-Q4_K_M → 6.5GB (quantized)
Total: 9.1GB (50% smaller!)
```

**Expected Impact:**
- Memory: 50% reduction
- Speed: Same or slightly faster
- Quality: Minimal loss (<2%)
- **Complexity:** Low (just change model names)
- **ETA:** Can do now!

---

## 🔄 Phase 2: Optimizations (v2.1) - IN PROGRESS

**Timeline:** Next 1-3 months  
**Focus:** Speed, efficiency, quality improvements

### 1. LLM Response Caching 💾

**Status:** 🔴 Not Started  
**Priority:** 🔴 High  
**Difficulty:** Medium  
**ETA:** 2 months

**Goals:**
- Implement Redis-like in-memory cache
- 1-hour TTL (configurable)
- Cache invalidation on data update
- Hash-based cache keys

**Expected Impact:**
- 40% faster average response time
- 70% cache hit rate
- Better user experience for repeated queries

**Implementation Plan:**
```python
class ResponseCache:
    def __init__(self, ttl=3600):
        self.cache = {}  # {key: (value, timestamp)}
        self.ttl = ttl
    
    def get(self, question, data_hash):
        key = hash(question + data_hash)
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
        return None
    
    def set(self, question, data_hash, answer):
        key = hash(question + data_hash)
        self.cache[key] = (answer, time.time())
```

---

### 2. Question Decomposition 🧩

**Status:** 🟡 Researching  
**Priority:** 🔴 High  
**Difficulty:** High  
**ETA:** 3 months

**Goals:**
- Automatically break complex questions into simple ones
- Answer each sub-question
- Combine results intelligently

**Example:**
```
Input: "七月和八月的伙食費分別是多少，為什麼八月增加？"

Decomposition:
├─ Q1: "七月的伙食費是多少？"
├─ Q2: "八月的伙食費是多少？"
└─ Q3: "為什麼八月伙食費增加？"

Combined Answer:
"七月伙食費NT$15,420，八月NT$18,650 (增加21%)。
八月增加主要因為外食次數增加..."
```

**Expected Impact:**
- Answer 30% more questions
- No more "question too complex" rejections
- Better user experience

---

### 3. Batch Categorization 📦

**Status:** 🟢 Design Complete  
**Priority:** 🟡 Medium  
**Difficulty:** Low  
**ETA:** 1 month

**Goals:**
- Process 10 transactions per LLM call
- Maintain or improve accuracy

**Implementation:**
```python
# Current (45 calls for 45 transactions)
for tx in transactions:
    category = qwen.categorize(tx)

# New (5 calls for 45 transactions)
for batch in chunk(transactions, 10):
    categories = qwen.categorize_batch(batch)
```

**Expected Impact:**
- 6x faster CSV processing
- 8.6s → 1.5s processing time

---

### 4. Learning Mode 🎓

**Status:** 🟡 70% Complete (Backend Ready)  
**Priority:** 🟡 Medium  
**Difficulty:** Medium  
**ETA:** 2 months

**Goals:**
- Log user corrections to categorization
- Improve patterns over time
- Confidence-weighted learning

**What's Done:**
```python
# Backend exists:
class LearningModule:
    def log_correction(self, tx, wrong_cat, correct_cat):
        # Logs to corrections.jsonl
        pass
    
    def get_learned_patterns(self):
        # Returns improved patterns
        pass
```

**What's Needed:**
- UI to show & confirm corrections
- Pattern extraction algorithm
- Integration with categorizer

**Expected Impact:**
- 95%+ categorization accuracy after 3 months
- Fewer manual corrections needed

---

### 5. Multi-Year UI Integration 📅

**Status:** 🟡 70% Complete (Backend Ready)  
**Priority:** 🟡 Medium  
**Difficulty:** Low  
**ETA:** 1 month

**Goals:**
- Integrate `multi_year_data_loader.py` with AI Chat
- Enable year-over-year comparisons
- Multi-year charts

**What's Done:**
```python
# Backend works:
loader = MultiYearDataLoader()
data_2024 = loader.load_year(2024)
data_2025 = loader.load_year(2025)
comparison = loader.compare_years(2024, 2025)
```

**What's Needed:**
- Add to question classifier
- Add to visual reports menu
- Year selection UI

**Expected Impact:**
- Full year-over-year analysis
- Historical trend visibility

---

### 6. PDF Export 📄

**Status:** 🔴 Not Started  
**Priority:** 🟢 Low  
**Difficulty:** Low  
**ETA:** 1 month

**Goals:**
- Export conversations to PDF
- Save charts as PNG/SVG
- Email reports

**Libraries to Use:**
- `reportlab` - PDF generation
- `matplotlib.savefig()` - Chart export
- `smtplib` - Email (optional)

**Expected Impact:**
- Easy sharing & archival
- Professional reports

---

### 7. Improved Language Detection 🌍

**Status:** 🔴 Not Started  
**Priority:** 🟢 Low  
**Difficulty:** Medium  
**ETA:** 2 months

**Goals:**
- 98%+ accuracy (from 95%)
- Better mixed language support
- Context-aware detection

**Approach:**
- Use conversation history
- Weight by keyword count
- Fuzzy language matching

**Expected Impact:**
- Fewer language misdetections
- Better mixed language handling

---

## 🎯 Phase 3: New Features (v2.2) - PLANNED

**Timeline:** 3-6 months  
**Focus:** New capabilities, major enhancements

### 1. Budget Goals & Tracking 🎯

**Status:** 🔴 Not Started  
**Priority:** 🔴 High  
**Difficulty:** Medium  
**ETA:** 3 months

**Features:**
- Set monthly/yearly goals per category
- Real-time progress tracking
- Alert when approaching limits
- Goal achievement analytics

**Example UI:**
```
設定預算目標

伙食費: NT$15,000/月
目前支出: NT$12,300 (82%)
🟢 在預算內

交通費: NT$5,000/月
目前支出: NT$5,400 (108%)
🔴 已超支 NT$400

[設定提醒: 達到90%時通知]
```

---

### 2. Spending Alerts 🔔

**Status:** 🔴 Not Started  
**Priority:** 🟡 Medium  
**Difficulty:** Medium  
**ETA:** 4 months

**Features:**
- Real-time anomaly detection
- Proactive notifications
- Configurable thresholds
- Weekly/monthly summaries

**Examples:**
```
⚠️ 異常支出警告
8月15日 - 休閒/娛樂: NT$5,000
這是您平均支出的3倍
確認這筆交易？

💡 每週提醒
本週已花費 NT$3,200
距離週預算還剩 NT$800
建議節制外食
```

---

### 3. Relative Date Support 📆

**Status:** 🔴 Not Started  
**Priority:** 🟡 Medium  
**Difficulty:** Low  
**ETA:** 3 months

**Features:**
- Support "今天", "昨天", "上週"
- Support "這個月", "上個月"
- Support "最近3個月"

**Mapping:**
```python
"今天" → datetime.now().date()
"昨天" → datetime.now().date() - timedelta(days=1)
"上週" → last_7_days()
"這個月" → current_month()
"最近3個月" → last_3_months()
```

---

### 4. Long-term Memory (Vector Store) 🧠

**Status:** 🔴 Not Started  
**Priority:** 🟡 Medium  
**Difficulty:** High  
**ETA:** 5 months

**Features:**
- Embed all past conversations
- Semantic search over history
- Retrieve relevant past context
- Learning from interaction patterns

**Technology:**
- `sentence-transformers` - Embeddings
- `faiss` or `chromadb` - Vector storage
- Semantic similarity search

**Expected Impact:**
- Truly conversational AI
- Reference past topics
- Personalized responses

---

### 5. Async Chart Generation 🎨

**Status:** 🔴 Not Started  
**Priority:** 🟢 Low  
**Difficulty:** Medium  
**ETA:** 4 months

**Features:**
- Generate charts in background
- Show progress indicator
- Non-blocking UI
- Cache rendered charts

**Implementation:**
```python
import asyncio

async def generate_chart_async(data):
    # Generate in background
    chart = await asyncio.to_thread(matplotlib_render, data)
    return chart

# UI stays responsive
print("Generating chart...")
chart = await generate_chart_async(data)
print("Done!")
```

---

### 6. Dynamic Thresholds ⚖️

**Status:** 🔴 Not Started  
**Priority:** 🟢 Low  
**Difficulty:** Medium  
**ETA:** 4 months

**Features:**
- Per-question-type thresholds
- User risk tolerance setting
- Adaptive learning from feedback

**Example:**
```python
THRESHOLDS = {
    'instant': 0.75,           # More lenient
    'trend': 0.80,             # Moderate
    'forecast': 0.85,          # Strict
    'financial_advice': 0.95   # Very strict
}

if confidence < THRESHOLDS[question_type]:
    escalate_to_stronger_llm()
```

---

### 7. Custom Chart Themes 🎨

**Status:** 🔴 Not Started  
**Priority:** 🟢 Low  
**Difficulty:** Low  
**ETA:** 3 months

**Features:**
- User-selectable color schemes
- Custom fonts & sizes
- Save preferences
- Export themes

**Examples:**
- Dark mode
- Colorblind-friendly
- High contrast
- Professional (for presentations)

---

## 🔮 Phase 4: Advanced (v3.0) - FUTURE VISION

**Timeline:** 6-12 months  
**Focus:** Major architectural changes, new platforms

### 1. Web Interface 🌐

**Vision:**
- Browser-based UI
- Mobile responsive
- Real-time sync across devices
- No installation required

**Technology Stack:**
- Backend: FastAPI or Flask
- Frontend: React or Vue.js
- Database: PostgreSQL
- Deployment: Docker

**Expected Impact:**
- Accessible from anywhere
- Better UX than terminal
- Family collaboration easier

---

### 2. Collaborative Budgeting 👥

**Vision:**
- Multiple users (you + wife)
- Shared budgets & goals
- Role-based permissions
- Comments on transactions
- Approval workflows

**Features:**
```
User Roles:
├── Admin (you): Full access
├── Partner (wife): Full access
└── Viewer (kids?): Read-only

Workflows:
├── Flag suspicious transactions
├── Request budget adjustments
└── Approve large expenses
```

---

### 3. Bank API Integration 🏦

**Vision:**
- Direct bank account connection
- Auto-import transactions
- Real-time balance updates
- No more CSV exports

**Technology:**
- Plaid API (US/Europe)
- Open Banking APIs (Taiwan?)
- OAuth2 authentication

**Benefits:**
- Zero manual work
- Always up-to-date
- Instant insights

**Challenges:**
- Privacy concerns
- Bank API availability
- Security requirements

---

### 4. Investment Tracking 📈

**Vision:**
- Separate investment module
- Track portfolio performance
- Link to budget (dividend income)
- Net worth dashboard

**Features:**
- Stock/fund holdings
- P&L tracking
- Asset allocation
- Rebalancing suggestions

---

### 5. Voice Interface 🎤

**Vision:**
- Ask questions via voice
- Audio responses
- Smart speaker integration (Google Home, Alexa)
- Hands-free budgeting

**Technology:**
- Speech-to-text: Whisper
- Text-to-speech: ElevenLabs or local TTS
- Wake word: "Hey Budget"

**Example:**
```
You: "Hey Budget, 七月花了多少？"
AI: "七月總支出 NT$27,300"
```

---

### 6. Mobile App 📱

**Vision:**
- Native iOS/Android apps
- Photo receipt scanning (OCR)
- GPS-based expense logging
- Push notifications

**Technology:**
- React Native or Flutter
- OCR: Google Vision API
- Sync: Cloud backend

---

### 7. Three-Model Architecture 🤖🤖🤖

**Vision:**
- Small (qwen3:8b) → Medium (qwen2.5:14b) → Large (gpt-oss:20b)
- More granular escalation
- Better cost/quality optimization

**Flow:**
```
Question
  ↓
Small model tries (fast, cheap)
  ↓ if uncertain
Medium model tries (balanced)
  ↓ if uncertain
Large model (slow, accurate)
```

---

## 🐛 Known Issues & Workarounds

### Issue 1: GUI Charts Don't Show Over SSH

**Cause:** No display server available

**Workaround:** Use terminal charts (ASCII-based)

**Command:**
```
Choose terminal charts when prompted
or
Add to config: DEFAULT_CHART_TYPE = 'terminal'
```

**Status:** Won't fix (expected behavior)

---

### Issue 2: Confidence Sometimes 0% for Valid Budget Questions

**Cause:** Language detection failure or missing keywords

**Example:**
```
Q: "費用" (too vague)
→ Confidence: 0% (rejected as unclear)
```

**Workaround:** Add more context/keywords
```
✅ "七月的費用"
✅ "伙食費用"
```

**Status:** 🔧 Improved detection in v2.1

---

### Issue 3: Category Names Must Be Exact

**Cause:** No fuzzy matching implemented

**Example:**
```
❌ "伙食" (incomplete)
❌ "食物費" (synonym)
✅ "伙食费" (exact)
```

**Workaround:** Use exact category names from Excel

**Status:** 🔧 Fuzzy matching planned for v2.1

---

### Issue 4: Numeric Month Not Always Recognized

**Cause:** Question classifier prioritizes Chinese months

**Example:**
```
⚠️ "7月" sometimes not detected
✅ "七月" always works
✅ "July" always works
```

**Workaround:** Use Chinese characters or English

**Status:** 🔧 Fixed in v2.0 (should work now)

---

### Issue 5: Long Questions Timeout

**Cause:** LLM timeout (default 180s)

**When It Happens:**
- Very long questions (>50 words)
- Tier 3 queries with large datasets (>200 transactions)

**Workaround:** Increase timeout in config
```python
# config.py
LLM_CONFIG = {
    "reasoning": {
        "timeout": 300,  # 5 minutes
    }
}
```

**Status:** ⚠️ Rare occurrence, no fix planned

---

## 🤝 Contribution Opportunities

### 🔴 High Priority (Help Wanted!)

#### 1. LLM Response Caching
- **Skills:** Python, caching patterns
- **Difficulty:** Medium
- **Impact:** High (40% speed improvement)
- **Files:** `modules/insights/ai_chat.py`

#### 2. Question Decomposition
- **Skills:** NLP, LLM prompting
- **Difficulty:** High
- **Impact:** High (30% more questions answered)
- **Files:** `modules/insights/question_classifier.py`

#### 3. PDF Export
- **Skills:** Python, reportlab
- **Difficulty:** Low
- **Impact:** Medium (better sharing)
- **Files:** New module `modules/insights/export.py`

---

### 🟡 Medium Priority

#### 4. Multi-Year Charts
- **Skills:** Matplotlib, data visualization
- **Difficulty:** Medium
- **Impact:** Medium (historical insights)
- **Files:** `modules/insights/gui_graphs.py`

#### 5. Batch Categorization
- **Skills:** Python, LLM prompting
- **Difficulty:** Low
- **Impact:** High (6x faster processing)
- **Files:** `modules/llm/qwen_engine.py`

#### 6. Learning Mode UI
- **Skills:** Python, terminal UI
- **Difficulty:** Medium
- **Impact:** Medium (better accuracy)
- **Files:** `_main.py`, `modules/data/simple_categorizer.py`

---

### 🟢 Low Priority (Good First Issues)

#### 7. Custom Chart Themes
- **Skills:** CSS-like styling, matplotlib
- **Difficulty:** Low
- **Impact:** Low (aesthetic)
- **Files:** `modules/insights/gui_graphs.py`

#### 8. Relative Date Parser
- **Skills:** Python, regex, datetime
- **Difficulty:** Low
- **Impact:** Medium (better UX)
- **Files:** `modules/insights/question_classifier.py`

#### 9. Improved Error Messages
- **Skills:** Writing, Python
- **Difficulty:** Very Low
- **Impact:** Low (better UX)
- **Files:** Various

---

## 🔬 Experimental Features (Testing Phase)

### 1. Streaming Responses 🌊

**Status:** Prototype exists, not integrated

**Concept:** Show answer as it generates (like ChatGPT)

**Benefit:** Perceived faster response

**Risk:** Confidence tracking harder (need full response)

**Next Steps:**
- Test with simple questions
- Measure user satisfaction
- Implement confidence on stream complete

---

### 2. Multi-Model Voting 🗳️

**Status:** Research phase

**Concept:** Ask 3 models, take consensus

**Example:**
```
Question: "七月花了多少？"
├─ Model 1 (Qwen): NT$27,300
├─ Model 2 (GPT-OSS): NT$27,300
└─ Model 3 (Llama): NT$27,350

Consensus: NT$27,300 (2/3 agree)
Confidence: 95% (high agreement)
```

**Benefit:** Higher accuracy for critical decisions

**Risk:** 3x slower, 3x more expensive

**Use Case:** Financial advice, large transactions

**Timeline:** Experiment in v2.2

---

### 3. Local Embedding Search 🔎

**Status:** Not started

**Concept:** Semantic search over all transactions

**Technology:**
- `sentence-transformers` - Generate embeddings
- `faiss` - Fast similarity search

**Example:**
```
Question: "咖啡相關的支出"

Traditional: Exact match "咖啡" → 5 transactions

Semantic Search:
├─ "Starbucks" (0.92 similarity)
├─ "85度C" (0.89 similarity)
├─ "早餐店飲料" (0.75 similarity)
└─ Total: 15 transactions
```

**Benefit:** Better context for LLM, more complete answers

**Risk:** Requires vector database, more complexity

**Timeline:** Research in v2.2

---

## 📊 Progress Tracking

### v2.0 ✅ (Current - Complete)

```
✅ Core System (100%)
✅ Dual-LLM Mix Model (100%)
✅ AI Chat with 3-tier (100%)
✅ Confidence Tracking (100%)
✅ Visual Reports (100%)
✅ Bilingual Support (100%)
```

---

### v2.1 🔄 (In Progress - 0%)

```
🔴 LLM Response Caching (0%)
🟡 Question Decomposition (5% - research)
🟢 Batch Categorization (80% - design done)
🟡 Learning Mode (70% - backend done)
🟡 Multi-Year UI (70% - backend done)
🔴 PDF Export (0%)
🔴 Improved Language Detection (0%)
```

**Overall Progress:** 25% (design phase)  
**ETA:** 3 months

---

### v2.2 📋 (Planned - 0%)

```
🔴 Budget Goals & Tracking (0%)
🔴 Spending Alerts (0%)
🔴 Relative Date Support (0%)
🔴 Long-term Memory (0%)
🔴 Async Charts (0%)
🔴 Dynamic Thresholds (0%)
🔴 Custom Themes (0%)
```

**Overall Progress:** 0% (planning phase)  
**ETA:** 6 months

---

## 📞 Feedback & Suggestions

Have ideas for improvements? Found a bug?

1. **Issues:** Use for bugs, specific problems
2. **Discussions:** Use for feature requests, ideas
3. **Pull Requests:** Contribute directly!

**Priority areas for feedback:**
- AI Chat question types you want supported
- Performance bottlenecks you've experienced
- Features you'd use most
- Integration requests (banks, tools, etc.)

---

**Roadmap Version:** 1.0  
**Last Updated:** 2025-01-22  
**Status:** Living Document (Updated Regularly)

---

Built with continuous improvement in mind 🚀

