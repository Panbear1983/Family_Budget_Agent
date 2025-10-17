# Family Budget Agent - High-Level Workflow 🔄

## 📋 Table of Contents
1. [Complete User Journey](#complete-user-journey)
2. [Monthly Update Workflow](#monthly-update-workflow)
3. [Analysis Workflow](#analysis-workflow)
4. [LLM Integration Points](#llm-integration-points)
5. [Decision Flow](#decision-flow)

---

## 1. Complete User Journey

### Starting Point → End Goal
```
📥 CSV Files (Me + Wife) 
    ↓
🤖 Intelligent Processing (LLMs)
    ↓
📊 Updated Excel (OneDrive)
    ↓
💡 Financial Insights (LLMs)
    ↓
🎯 Better Budget Decisions
```

---

## 2. Monthly Update Workflow

### **PHASE 1: User Input** 📥
```
┌─────────────────────────────────────┐
│  USER ACTION                        │
│  1. Export bank transactions        │
│  2. Save as me.csv & wife.csv       │
│  3. Place in Budget Agent folder    │
│  4. Run: ./start_main.sh            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  MAIN MENU                          │
│  Choose: Option 2 (Smart Parsing)   │
└─────────────────────────────────────┘
```

### **PHASE 2: CSV Parsing** 🤖 *[LLM: Qwen3:8b]*
```
┌─────────────────────────────────────────────────┐
│  QWEN3:8B - STRUCTURED DATA PROCESSING         │
│                                                 │
│  For each transaction in CSV:                  │
│                                                 │
│  1. Parse Fields                               │
│     Input:  "2025-08-01,150,Food-Stuff,午餐"    │
│     ↓ Qwen3:8b analyzes                        │
│     Output: {                                  │
│       date: "2025-08-01",                      │
│       amount: 150,                             │
│       category: "伙食费",  ← Intelligently mapped│
│       description: "午餐"                       │
│     }                                          │
│                                                 │
│  2. Category Matching                          │
│     "Starbucks" → Qwen3:8b → "伙食费"           │
│     "Uber" → Qwen3:8b → "交通费"                │
│     "Movie" → Qwen3:8b → "休闲/娱乐"            │
│                                                 │
│  3. Duplicate Detection                        │
│     Compare: Transaction A vs B                │
│     ↓ Qwen3:8b analyzes similarity            │
│     Decision: DUPLICATE / UNIQUE               │
│                                                 │
│  4. Data Validation                            │
│     Check: Amount, Date, Category              │
│     ↓ Qwen3:8b validates                       │
│     Status: VALID / FLAG_FOR_REVIEW            │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  RESULT                             │
│  ✅ Parsed: 45 transactions         │
│  ✅ Categorized: 100%               │
│  ✅ Duplicates removed: 3           │
│  ✅ Ready for merge                 │
└─────────────────────────────────────┘
```

### **PHASE 3: Data Merge** 🔄 *[No LLM - Controller Logic]*
```
┌─────────────────────────────────────┐
│  CONTROLLER (budget_agent.py)       │
│                                     │
│  1. Load existing OneDrive Excel    │
│     📂 2025年開銷表（NT）.xlsx        │
│                                     │
│  2. Merge Data                      │
│     Old (Jan-Jul) + New (Aug)       │
│     = Combined dataset              │
│                                     │
│  3. Remove Global Duplicates        │
│     (Based on: date, amount, desc)  │
│                                     │
│  4. Create Backup                   │
│     📦 2025_backup_20250813.xlsx    │
│                                     │
│  5. Update Master Excel             │
│     💾 Save to OneDrive             │
│     ☁️  Auto-sync to cloud          │
└─────────────────────────────────────┘
```

### **PHASE 4: Initial Analysis** 🧠 *[LLM: GPT-OSS:20b]*
```
┌─────────────────────────────────────────────────┐
│  GPT-OSS:20B - DEEP REASONING                  │
│                                                 │
│  Automatic Post-Update Analysis:               │
│                                                 │
│  1. Trend Detection                            │
│     Question: "What changed this month?"       │
│     ↓ GPT-OSS:20b analyzes full dataset       │
│     Answer: "August spending ↑15% vs July     │
│              Main driver: 伙食费 (+NT$2,400)   │
│              Likely due to more dining out"    │
│                                                 │
│  2. Anomaly Flagging                           │
│     ↓ GPT-OSS:20b detects outliers            │
│     Alert: "Aug 15: NT$5,000 entertainment    │
│             (3x normal average)"               │
│     Reason: "Possibly special event/vacation"  │
│                                                 │
│  3. Quick Summary                              │
│     ↓ GPT-OSS:20b generates insight           │
│     "August Total: NT$18,500                   │
│      On track for monthly goal.                │
│      Consider reviewing entertainment budget." │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  DISPLAY TO USER                    │
│  📊 Updated successfully            │
│  💡 Key insights shown              │
│  ✅ Ready for analysis              │
└─────────────────────────────────────┘
```

---

## 3. Analysis Workflow

### **USER INITIATES ANALYSIS**
```
┌─────────────────────────────────────┐
│  USER                               │
│  Selects: Option 3 (Qwen Analysis)  │
│  or Option 6 (Chat Mode)            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  CONTROLLER                         │
│  1. Load full budget data           │
│  2. Prepare context                 │
│  3. Route to appropriate LLM        │
└─────────────────────────────────────┘
```

### **ANALYSIS OPTIONS**

#### **Option A: Structured Analysis** *[LLM: Qwen3:8b]*
```
┌─────────────────────────────────────────────────┐
│  QWEN3:8B - STRUCTURED QUERIES                 │
│                                                 │
│  Use Case: Quick, structured questions         │
│                                                 │
│  Example 1: Category Breakdown                 │
│    Query: "Show spending by category"          │
│    ↓ Qwen3:8b processes                        │
│    Output:                                     │
│      伙食费: NT$45,200 (35%)                   │
│      交通费: NT$12,800 (10%)                   │
│      家务:   NT$38,900 (30%)                   │
│      ...                                       │
│                                                 │
│  Example 2: Month Comparison                   │
│    Query: "Compare July vs August"             │
│    ↓ Qwen3:8b extracts & compares             │
│    Output:                                     │
│      July:   NT$15,200                         │
│      August: NT$18,500 (+22%)                  │
│      Diff:   +NT$3,300                         │
└─────────────────────────────────────────────────┘
```

#### **Option B: Deep Reasoning** *[LLM: GPT-OSS:20b]*
```
┌─────────────────────────────────────────────────┐
│  GPT-OSS:20B - DEEP REASONING & ADVICE         │
│                                                 │
│  Use Case: Complex questions requiring thought │
│                                                 │
│  Example 1: "Why did spending increase?"       │
│    ↓ GPT-OSS:20b analyzes multiple factors    │
│    Response:                                   │
│      "Your August spending increased by 22%    │
│       compared to July. Key factors:           │
│                                                 │
│       1. Food (伙食费) ↑ 45% - You dined out   │
│          more frequently (15 times vs 8)       │
│                                                 │
│       2. Entertainment ↑ 180% - Large expense  │
│          on Aug 15 (NT$5,000) - was this       │
│          planned?                              │
│                                                 │
│       3. Transportation stable - no change     │
│                                                 │
│       Recommendation: Review recurring dining   │
│       expenses and set entertainment budget."   │
│                                                 │
│  Example 2: "Can I afford a NT$10,000 trip?"   │
│    ↓ GPT-OSS:20b does financial analysis      │
│    Response:                                   │
│      "Based on your spending patterns:         │
│                                                 │
│       Current avg: NT$16,200/month             │
│       Projected year: NT$194,400               │
│       Available: ~NT$45,600 buffer             │
│                                                 │
│       A NT$10,000 trip is feasible if:         │
│       - You reduce dining by 30% (NT$2,500)    │
│       - Keep entertainment under NT$3,000      │
│       - Spread payment over 2 months           │
│                                                 │
│       Would you like a detailed savings plan?" │
└─────────────────────────────────────────────────┘
```

---

## 4. LLM Integration Points

### **Complete System Map**

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                           (_main.py)                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                          │
│                    (budget_agent.py)                            │
│                                                                 │
│  Decides which LLM to use based on:                            │
│  1. Task type (structured vs reasoning)                        │
│  2. Input complexity                                           │
│  3. Required output format                                     │
└─────────────────────────────────────────────────────────────────┘
                    ↙                           ↘
┌──────────────────────────────┐    ┌──────────────────────────────┐
│     🤖 QWEN3:8B              │    │    🧠 GPT-OSS:20B            │
│   (Structured Tasks)         │    │   (Deep Reasoning)           │
│                              │    │                              │
│  WHEN:                       │    │  WHEN:                       │
│  • Parsing CSV               │    │  • Explaining trends         │
│  • Category matching         │    │  • Forecasting               │
│  • Data validation           │    │  • Financial advice          │
│  • Duplicate detection       │    │  • Complex Q&A               │
│  • Quick queries             │    │  • "Why" questions           │
│                              │    │                              │
│  SPEED: ~3-5 seconds         │    │  SPEED: ~8-15 seconds        │
│  SIZE: 5.2 GB                │    │  SIZE: 13 GB                 │
└──────────────────────────────┘    └──────────────────────────────┘
                    ↘                           ↙
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                              │
│   CSV Files → Excel Storage → OneDrive Sync                    │
└─────────────────────────────────────────────────────────────────┘
```

### **LLM Usage Matrix**

| User Action | Goes To | LLM Used | Purpose |
|------------|---------|----------|---------|
| Upload CSV | → Controller → | **Qwen3:8b** | Parse & categorize |
| Ask "How much spent?" | → Controller → | **Qwen3:8b** | Quick data query |
| Ask "Why increase?" | → Controller → | **GPT-OSS:20b** | Explain reasoning |
| Request forecast | → Controller → | **GPT-OSS:20b** | Predict & advise |
| Compare months | → Controller → | **Qwen3:8b** | Extract & compare |
| Ask "Can I afford X?" | → Controller → | **GPT-OSS:20b** | Financial analysis |
| View categories | → Controller | None | Direct data display |
| Update Excel | → Controller | None | File operations |

---

## 5. Decision Flow

### **How Controller Decides Which LLM**

```python
def route_to_llm(user_request, data):
    """
    Intelligent routing based on request type
    """
    
    # PATTERN 1: Structured data tasks
    if request_type in [
        'parse_csv',
        'categorize',
        'validate',
        'extract_value',
        'simple_comparison'
    ]:
        return qwen3_8b.process(user_request, data)
        # Fast, efficient, structured
    
    # PATTERN 2: Reasoning tasks
    elif request_type in [
        'explain_trend',
        'forecast',
        'financial_advice',
        'complex_analysis',
        'why_question'
    ]:
        return gpt_oss_20b.analyze(user_request, data)
        # Deep thinking, explanations
    
    # PATTERN 3: Hybrid (use both)
    elif request_type == 'comprehensive_analysis':
        # Step 1: Qwen extracts data
        structured_data = qwen3_8b.extract(data)
        
        # Step 2: GPT-OSS reasons over it
        insights = gpt_oss_20b.reason(structured_data)
        
        return insights
```

### **Real Examples**

#### **Example 1: Monthly Update**
```
1. User: Uploads me.csv + wife.csv
   ↓
2. Controller: "This is CSV parsing task"
   ↓
3. Routes to: Qwen3:8b
   ↓
4. Qwen3:8b: 
   - Parses 45 rows
   - Maps categories
   - Finds 3 duplicates
   ↓
5. Controller: Merges with Excel
   ↓
6. Routes to: GPT-OSS:20b (for summary)
   ↓
7. GPT-OSS:20b: "August up 15%, mainly dining"
   ↓
8. Display to user
```

#### **Example 2: "Why did food cost increase?"**
```
1. User: Types question
   ↓
2. Controller: "This is a WHY question - needs reasoning"
   ↓
3. Routes to: GPT-OSS:20b
   ↓
4. GPT-OSS:20b analyzes:
   - Historical food spending
   - Recent patterns
   - Contributing factors
   ↓
5. GPT-OSS:20b responds:
   "Food costs increased 45% because:
    • 7 more dining out instances
    • Average meal cost ↑ from NT$150 → NT$220
    • Two large grocery trips (NT$2,000+ each)
    
    This is abnormal. Consider:
    • Meal planning to reduce dining out
    • Bulk shopping instead of daily trips"
   ↓
6. Display to user
```

#### **Example 3: "Show me August breakdown"**
```
1. User: Simple data query
   ↓
2. Controller: "Structured query - extract and format"
   ↓
3. Routes to: Qwen3:8b
   ↓
4. Qwen3:8b:
   - Filters August data
   - Groups by category
   - Calculates totals
   ↓
5. Returns structured data:
   {
     "伙食费": 8500,
     "交通费": 2200,
     ...
   }
   ↓
6. Display as table
```

---

## 6. Complete Workflow Summary

### **Monthly Cycle**

```
WEEK 1: DATA COLLECTION
├─ Export bank transactions
└─ Save as CSV files

WEEK 2: PROCESSING (LLMs)
├─ Qwen3:8b parses CSVs         [3-5 min]
├─ Controller merges data        [1 min]
├─ GPT-OSS:20b analyzes          [2-3 min]
└─ Excel updated + OneDrive sync [1 min]

WEEK 3-4: ANALYSIS (LLMs)
├─ User asks questions
├─ Qwen3:8b: Quick data queries
├─ GPT-OSS:20b: Deep insights
└─ Make budget decisions

REPEAT MONTHLY
```

### **Time Breakdown**

| Step | Duration | LLM Used | Resource |
|------|----------|----------|----------|
| CSV Upload | 30s | None | Manual |
| Parse & Categorize | 2-3 min | Qwen3:8b | 5.2GB RAM |
| Merge & Save | 30s | None | Disk I/O |
| Initial Analysis | 1-2 min | GPT-OSS:20b | 13GB RAM |
| User Q&A (each) | 5-15s | Both | As needed |

**Total Monthly Processing: ~5-10 minutes**

---

## 7. Key Takeaways

### **LLM Strategy**
1. ✅ **Qwen3:8b** = Fast lane for structured work
2. ✅ **GPT-OSS:20b** = Deep thinking for insights
3. ✅ **Controller** = Smart traffic cop (routes appropriately)

### **Efficiency**
- 🚀 Right model for right task
- 💰 No wasted compute
- ⚡ Optimal speed vs quality

### **User Experience**
- 📥 Simple: Drop CSVs, get insights
- 🤖 Intelligent: LLMs handle complexity
- 💡 Actionable: Get real financial advice
- 🔒 Private: All local, no cloud AI

---

**Workflow Version:** 1.0  
**Last Updated:** 2025-10-13  
**Status:** Architecture Complete

