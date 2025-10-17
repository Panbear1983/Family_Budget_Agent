# Family Budget Agent - System Architecture 🏗️

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Core Design Principles](#core-design-principles)
3. [Architecture Diagram](#architecture-diagram)
4. [Component Breakdown](#component-breakdown)
5. [LLM Strategy](#llm-strategy)
6. [Data Flow](#data-flow)
7. [Module Responsibilities](#module-responsibilities)
8. [Decision Matrix](#decision-matrix)

---

## 1. System Overview

### Purpose
A local, AI-powered family budget management system that:
- Intelligently processes monthly budget data (CSV → Excel)
- Provides deep financial insights using local LLMs
- Maintains data privacy (100% local execution)
- Syncs with OneDrive for accessibility

### Key Requirements
- **Privacy**: All processing happens locally (no cloud AI)
- **Intelligence**: Leverage 2 specialized LLMs for different tasks
- **Bilingual**: Support Chinese & English
- **User-Friendly**: Simple menu-driven interface
- **Reliable**: Auto-backup, error handling

---

## 2. Core Design Principles

### 🎯 Single Responsibility
Each module has ONE clear purpose:
- Data ingestion
- LLM processing
- Storage management
- User interface

### 🔄 Separation of Concerns
```
UI Layer → Business Logic → LLM Layer → Data Layer
```

### 🤖 LLM Specialization

**Installed Models:**
- **gpt-oss:20b** - 20B parameters (13 GB) - General purpose, strong reasoning
- **qwen3:8b** - 8B parameters (5.2 GB) - Analytical, good at structured tasks

**Strategic Assignment:**
- **GPT-OSS (20B)**: Conversational AI, complex reasoning, financial advice, explanations
- **Qwen3 (8B)**: Structured analysis, data parsing, pattern recognition, categorization

### 📦 Modularity
Components can be:
- Tested independently
- Replaced/upgraded easily
- Reused across features

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (_main.py)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Input    │  │ View     │  │ Analyze  │  │ Update   │   │
│  │ Menu     │  │ Menu     │  │ Menu     │  │ Menu     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Budget Controller (budget_agent.py)         │   │
│  │  - Coordinates workflows                            │   │
│  │  - Manages state                                    │   │
│  │  - Routes to appropriate LLM                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      LLM PROCESSING LAYER                    │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │   GPT-OSS Engine     │    │    Qwen Engine           │  │
│  │ (BUDGET_GPT_OSS.py)  │    │ (BUDGET_QWEN.py)         │  │
│  │                      │    │                          │  │
│  │ • Data Parsing       │    │ • Conversational AI      │  │
│  │ • Category Matching  │    │ • Deep Reasoning         │  │
│  │ • Pattern Recognition│    │ • Financial Advice       │  │
│  │ • Structured Tasks   │    │ • Trend Explanation      │  │
│  │ • Anomaly Detection  │    │ • Complex Queries        │  │
│  │ Model: qwen3:8b      │    │ Model: gpt-oss:20b       │  │
│  │ (8B params, 5.2GB)   │    │ (20B params, 13GB)       │  │
│  └──────────────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ CSV      │  │ Excel    │  │ Config   │  │ OneDrive │   │
│  │ Files    │  │ Storage  │  │ JSON     │  │ Sync     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Component Breakdown

### 4.1 User Interface Layer

**_main.py**
- Role: Menu system & user interaction
- Responsibilities:
  - Display menus
  - Capture user input
  - Route to appropriate controller
  - Display results
- Does NOT: Contain business logic or LLM calls

### 4.2 Orchestration Layer

**budget_agent.py (Controller)**
- Role: Workflow coordinator
- Responsibilities:
  - Load/save data
  - Coordinate CSV → Excel pipeline
  - Manage state between operations
  - Error handling & validation
- Decides: Which LLM to use for which task

### 4.3 LLM Processing Layer

**BUDGET_QWEN.py** (Renamed from GPT-OSS)
- Role: Structured data processing & pattern recognition
- Model: **qwen3:8b** (8B parameters, efficient)
- Strengths: Fast, structured analysis, good at categorization
- Use Cases:
  - CSV field parsing & validation
  - Category matching (English → Chinese)
  - Duplicate detection  
  - Pattern recognition
  - Data normalization
  - Quick structured queries

**BUDGET_GPT_OSS.py** (Renamed from Qwen)
- Role: Conversational AI & deep reasoning
- Model: **gpt-oss:20b** (20B parameters, powerful)
- Strengths: Strong reasoning, natural language, explanations
- Use Cases:
  - Spending trend analysis & explanation
  - Financial forecasting
  - Natural language Q&A
  - Complex budget advice
  - Period comparisons
  - "Why" questions (reasoning)

### 4.4 Data Layer

**Data Sources:**
- `me.csv` / `wife.csv` - Monthly input
- `2025年開銷表（NT）.xlsx` - Master budget (OneDrive)
- `category_map.json` - Category mappings
- `config.py` - System configuration

**Storage Strategy:**
- **Input**: CSV files (human-readable)
- **Processing**: Pandas DataFrames (in-memory)
- **Storage**: Excel (structured, OneDrive-synced)
- **Backup**: Timestamped copies before updates

---

## 5. LLM Strategy

### 5.1 When to Use Qwen3:8b (Structured Tasks)

**Criteria:**
- ✅ Structured data processing
- ✅ Pattern matching needed
- ✅ Clear input/output format
- ✅ Fast batch processing

**Examples:**
```python
# Category matching
"Starbucks coffee" → "伙食费"

# CSV parsing
Parse row: {date, amount, desc} → {normalized_data}

# Duplicate detection
Compare transactions → DUPLICATE/UNIQUE

# Data validation
Check amount range → VALID/INVALID
```

**Advantages:**
- Efficient (8B params)
- Good at structured tasks
- Fast response (~3-5 seconds)
- Reliable patterns
- Lower memory usage (5.2GB)

### 5.2 When to Use GPT-OSS:20b (Reasoning & Conversation)

**Criteria:**
- ✅ Requires deep reasoning
- ✅ Natural language queries
- ✅ Explanation needed
- ✅ Financial advice

**Examples:**
```python
# Trend explanation
"Why did spending increase 20% in July?"
→ Detailed analysis with context

# Forecasting with reasoning
"Predict next 3 months based on patterns"
→ Forecast + reasoning + confidence

# Conversational advice
"Can we afford to cap entertainment at NT$5000?"
→ Analysis + recommendation + trade-offs
```

**Advantages:**
- Strong reasoning (20B params)
- Natural conversations
- Contextual understanding
- Quality explanations
- Better for "why" questions

### 5.3 Hybrid Approach

**Best Practice: Use Both**
```python
# Step 1: Qwen3:8b - Fast structured parsing
categories = qwen.parse_csv(data)

# Step 2: GPT-OSS:20b - Deep reasoning & insights
insights = gpt_oss.analyze_trends(categories)
```

---

## 6. Data Flow

### 6.1 Input Flow (Monthly Update)

```
1. User uploads CSV files
   ↓
2. GPT-OSS parses & categorizes
   ├─ Normalize categories
   ├─ Detect duplicates
   └─ Validate data
   ↓
3. Controller merges with existing data
   ├─ Load Excel from OneDrive
   ├─ Append new transactions
   └─ Remove duplicates
   ↓
4. Save to Excel
   ├─ Create backup
   ├─ Update master file
   └─ OneDrive auto-sync
   ↓
5. Qwen performs initial analysis
   └─ Generate summary insights
```

### 6.2 Analysis Flow (User Queries)

```
1. User asks question
   ↓
2. Controller loads relevant data
   ↓
3. Qwen processes query
   ├─ Understand intent
   ├─ Extract data points
   └─ Generate insights
   ↓
4. Display formatted results
```

### 6.3 View Flow (Display Data)

```
1. User selects view option
   ↓
2. Controller loads data
   ↓
3. Format for display
   ├─ Excel grid view
   ├─ Monthly summary
   └─ Category breakdown
   ↓
4. Render in terminal
```

---

## 7. Module Responsibilities

### 7.1 Core Modules

| Module | Purpose | Dependencies | LLM Used |
|--------|---------|--------------|----------|
| `_main.py` | UI & Menu | All modules | None (UI only) |
| `budget_agent.py` | Controller | Data layer | Orchestrates LLMs |
| `BUDGET_QWEN.py` | Structured parsing | Ollama | qwen3:8b (8B) |
| `BUDGET_GPT_OSS.py` | Deep reasoning | Ollama | gpt-oss:20b (20B) |
| `config.py` | Configuration | None | None |

### 7.2 Helper Modules

| Module | Purpose | When to Use |
|--------|---------|-------------|
| `excel_view.py` | Display Excel grid | View full budget |
| `view_2025_summary.py` | Year overview | Monthly totals |
| `view_sheets.py` | Month details | Specific month |
| `test_onedrive.py` | Connection test | Setup/troubleshooting |
| `find_budget.py` | Locate files | Initial setup |

### 7.3 Data Files

| File | Type | Purpose | Update Frequency |
|------|------|---------|------------------|
| `me.csv` | Input | User's transactions | Monthly |
| `wife.csv` | Input | Partner's transactions | Monthly |
| `category_map.json` | Config | Category mappings | As needed |
| `2025年開銷表（NT）.xlsx` | Master | Complete budget | Monthly |

---

## 8. Decision Matrix

### 8.1 Which LLM for Which Task?

| Task | Qwen3:8b | GPT-OSS:20b | Reason |
|------|----------|-------------|--------|
| **Parse CSV row** | ✅ | ❌ | Structured data task |
| **Match category** | ✅ | ❌ | Pattern recognition |
| **Detect duplicate** | ✅ | ❌ | Comparison task |
| **Validate amount** | ✅ | ❌ | Data validation |
| **Normalize data** | ✅ | ❌ | Structured processing |
| Trend analysis | ❌ | ✅ | Requires deep reasoning |
| Anomaly explanation | ❌ | ✅ | Needs context & why |
| Forecasting | ❌ | ✅ | Complex prediction |
| Period comparison | ❌ | ✅ | Deep analysis |
| Natural Q&A | ❌ | ✅ | Conversational strength |
| Financial advice | ❌ | ✅ | Expert reasoning (20B) |

### 8.2 Processing Pipeline

```python
# PHASE 1: DATA INGESTION (Qwen3:8b - Structured)
- Parse CSV → Qwen3:8b
- Categorize → Qwen3:8b  
- Validate → Qwen3:8b
- Deduplicate → Qwen3:8b

# PHASE 2: DATA MERGE (Controller)
- Load existing Excel
- Merge new + old data
- Save to Excel
- Create backup

# PHASE 3: ANALYSIS (GPT-OSS:20b - Reasoning)
- Calculate trends → GPT-OSS:20b
- Explain anomalies → GPT-OSS:20b
- Generate insights → GPT-OSS:20b
- Answer questions → GPT-OSS:20b
```

### 8.3 Error Handling Strategy

**Fallback Hierarchy:**
```
1. Try LLM processing
   ↓
2. If LLM fails → Use rule-based fallback
   ↓
3. If rules fail → Use defaults
   ↓
4. Always log errors
```

**Example:**
```python
def categorize_transaction(desc):
    try:
        # Try Qwen3:8b first (good at structured tasks)
        category = qwen.match_category(desc)
        if category:
            return category
    except:
        pass
    
    # Fallback to rule-based pattern matching
    for pattern in PATTERNS:
        if pattern in desc.lower():
            return PATTERN_MAP[pattern]
    
    # Default fallback
    return "其它"
```

---

## 9. Implementation Roadmap

### Phase 1: Foundation ✅
- [x] Basic CSV loading
- [x] Excel integration
- [x] OneDrive sync
- [x] Menu system

### Phase 2: LLM Integration (CURRENT)
- [ ] Implement GPT-OSS module
- [ ] Implement Qwen module
- [ ] Integrate into controller
- [ ] Add error handling

### Phase 3: Advanced Features
- [ ] Learning from corrections
- [ ] Custom category rules
- [ ] Multi-currency support
- [ ] Budget goals & alerts

### Phase 4: Optimization
- [ ] Caching LLM responses
- [ ] Batch processing
- [ ] Performance tuning
- [ ] User feedback loop

---

## 10. Key Design Decisions

### 10.1 Why Two LLMs?

**Cost-Benefit Analysis:**

| Aspect | Single LLM | Dual LLM (Our Choice) |
|--------|------------|----------------------|
| Speed | Slow for all tasks | Fast for simple, powerful for complex |
| Resource | High constant usage | Optimized per task |
| Quality | Good average | Best per use case |
| Complexity | Simpler | More sophisticated |

**Verdict:** Dual LLM provides better user experience

### 10.2 Why Local Processing?

✅ **Privacy**: Budget data never leaves your Mac  
✅ **Cost**: No API fees  
✅ **Speed**: No network latency  
✅ **Reliability**: Works offline  
✅ **Control**: Full system control  

### 10.3 Why Ollama?

✅ Easy model management  
✅ Multiple model support  
✅ Good performance on Mac  
✅ Active community  
✅ Free & open source  

---

## 11. Success Metrics

### System Performance
- CSV parsing: < 5 seconds
- Analysis query: < 10 seconds
- Excel update: < 3 seconds
- Menu response: Instant

### User Experience
- Setup time: < 15 minutes
- Learning curve: < 1 hour
- Error rate: < 5%
- Satisfaction: High

### Technical Quality
- Code coverage: > 80%
- Documentation: Complete
- Error handling: Comprehensive
- Maintainability: High

---

## 12. Next Steps

### Immediate (This Session)
1. ✅ Review architecture
2. ⏳ Refine LLM responsibilities
3. ⏳ Finalize data flow
4. ⏳ Begin implementation

### Short-term (This Week)
1. Complete GPT-OSS module
2. Complete Qwen module
3. Integration testing
4. User testing

### Long-term (This Month)
1. Advanced features
2. Performance optimization
3. Documentation
4. Deployment guide

---

## 📝 Notes for Implementation

### Code Organization
```
Family_Budget_Agent/
├── Core/
│   ├── _main.py           # UI Layer
│   ├── budget_agent.py    # Controller
│   └── config.py          # Configuration
│
├── LLM/
│   ├── BUDGET_GPT_OSS.py  # Fast parsing
│   └── BUDGET_QWEN.py     # Deep analysis
│
├── Utils/
│   ├── excel_view.py
│   ├── view_*.py
│   └── test_*.py
│
└── Data/
    ├── me.csv
    ├── wife.csv
    └── category_map.json
```

### Testing Strategy
- Unit tests for each module
- Integration tests for workflows
- LLM response validation
- Edge case handling

---

**Architecture Version:** 1.0  
**Last Updated:** 2025-10-13  
**Status:** Ready for Implementation

