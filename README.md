# Family Budget Agent v2.0 💰

> **A comprehensive AI-powered family budget management system built to solve the real challenge of tracking household finances across multiple bank accounts, multiple people, and multiple languages—while keeping all data processing completely private and local.**

---

## 🎯 The Vision

Managing family finances shouldn't be complicated. Yet for bilingual households juggling multiple bank accounts (Peter's account, wife's account), mixed-language transaction descriptions (English + Chinese), and scattered monthly CSV exports, traditional budgeting tools fall short. 

**This agent was built to solve that exact problem:** Transform messy, distributed financial data into actionable insights using intelligent AI—without sacrificing privacy or control.

### Why This Exists

**The Problem:**
- Monthly bank exports in different formats (Peter's Excel, wife's CSV)
- Transaction descriptions in mixed languages (Starbucks, 家樂福, Uber)
- Manual categorization is tedious and error-prone
- No easy way to ask "Why did we spend more this month?"
- Cloud budget apps expose sensitive financial data to third parties

**The Solution:**
This comprehensive agent tool that parses monthly nudget sheets into an aggregated annual sheet, while uses dual local LLM intelligence to automatically process, categorize, analyze, and answer questions about your family budget—all running 100% on your machine.

---

## 🌟 Current Capabilities

### What It Does Today (Production Ready ✅)

1. **Self-Parsing Budget Processing**
   - Automatically merges monthly CSV/Excel exports from multiple people
```
     2025年開銷表（NT）.xlsx
┌─────────────────┐
│ 類別 (Category)   │
├─────────────────┤
│ 交通費           │ ← Peter's Transportation + Dolly's 交通
│ 伙食費           │ ← Peter's Food + Dolly's 吃吃喝喝
│ 休閒/娛樂        │ ← Peter's Leisure + Dolly's 交際娛樂
│ 家務            │ ← Peter's Home & Housing + Dolly's 5 categories
│ 阿幫            │ ← Peter's Pet + Dolly's 幫比
│ 其它            │ ← Peter's Others + Dolly's 分期付款
└─────────────────┘
```
   - LLM-powered categorization with 95%+ accuracy
   - Handles bilingual transaction descriptions seamlessly
   - Detects duplicates and outliers with explanations
   - Updates **`[YEAR]年開銷表（NT）.xlsx`** on OneDrive automatically (year-based naming)

2. **Conversational Budget Analysis**
   - Ask questions in natural language (中文 or English)
   - Get instant answers about spending patterns, trends, and anomalies
   - Visual reports and charts (both terminal ASCII and GUI matplotlib)
   - Confidence tracking on every answer (know when to trust the AI)

3. **Flexible Excel Editing**
   - **Automated:** CSV merge writes directly to Excel via LLM categorization
   - **Manual:** Cell-by-cell editor with preview and validation
   - Both methods use `openpyxl` to modify the master OneDrive file
   - Auto-fill dates, edit expenses by category, all with change previews

4. **AI-Powered Intelligence**
   - **Qwen3:8b** handles all AI tasks (parsing, categorization, reasoning)
   - Natural language routing to existing functions
   - Simplified single-model approach for reliability
   - Function-based responses for consistent results

5. **Privacy-First Architecture**
   - Zero data leaves your computer (no cloud AI APIs)
   - No API keys or subscriptions required
   - Local Ollama LLM models process everything
   - Only storage: Your personal OneDrive (your control)

### Performance Snapshot

| Capability | Speed | Reliability |
|------------|-------|-------------|
| Process 45 transactions (CSV → Excel) | 3-8 seconds | High (dictionary + LLM fallback) |
| Answer simple budget question | 1-3 seconds | Function-based routing |
| Complex trend analysis with charts | 5-15 seconds | Data-driven insights |
| Detect duplicate transactions | 2-5 seconds | Dictionary + fuzzy matching |
| Bilingual transaction handling | Real-time | Seamless |

---

## 📸 Screenshots

> **Main Menu Interface**
<img width="735" height="604" alt="image" src="https://github.com/user-attachments/assets/601d8ff0-74f2-4e6c-9532-caf1331ac423" />


> **Budget View Terminal**
<img width="722" height="1051" alt="image" src="https://github.com/user-attachments/assets/8b05f46f-7330-4196-8663-c40c81981431" />


> **Excel File Structure (Parser Feature)**
> 
> *Insert screenshot showing the OneDrive Excel file with monthly sheets (一月-十二月) and the annual summary sheet*

> **Visual Charts (GUI)**
<img width="791" height="644" alt="image" src="https://github.com/user-attachments/assets/9586d29a-0680-4bc8-a49f-65cba73e8ab2" />
<img width="708" height="285" alt="image" src="https://github.com/user-attachments/assets/5d4e4de2-fc18-4111-84a7-79ccddcb1cb3" />
<img width="1385" height="686" alt="image" src="https://github.com/user-attachments/assets/17d12812-f2d8-48ab-abf6-7f268623380e" />
<img width="853" height="759" alt="image" src="https://github.com/user-attachments/assets/a6bd9422-7eae-468a-b581-88876edded28" />


> **Excel Sheet Parser Pipeline**
<img width="719" height="858" alt="image" src="https://github.com/user-attachments/assets/9f6b2581-f141-4574-b821-843d0d91b2e3" />
<img width="854" height="930" alt="image" src="https://github.com/user-attachments/assets/a4a7181b-5bfb-444f-8bc4-f49219d37507" />



> **AI Chat Interface**
<img width="505" height="857" alt="image" src="https://github.com/user-attachments/assets/bdf091e1-e5fb-4ca5-9522-bb3ceaf6ac0e" />
<img width="884" height="614" alt="image" src="https://github.com/user-attachments/assets/c36b92e2-38c3-4307-8c83-969760cb9c01" />
<img width="683" height="196" alt="image" src="https://github.com/user-attachments/assets/6efd3837-58ec-45ee-a3a1-b74a8f625f80" />


---

## 🏗️ Operating Environment

### Where It Runs
- **Platform:** macOS (primary), Linux compatible
- **Runtime:** Python 3.11+ with virtual environment
- **AI Engine:** Ollama (local LLM server)
- **Storage:** OneDrive Excel file → **`[YEAR]年開銷表（NT）.xlsx`** (auto-updates yearly)
- **Models:** Qwen3:8b (5.2GB) only
- **RAM Required:** ~5.2GB with Qwen model loaded

### Data Flow Architecture

```
MONTHLY BANK EXPORTS                 PROCESSING                         STORAGE & EDITING
┌──────────────────────┐             ┌──────────────┐                  ┌─────────────────────┐
│ peter_august.xlsx    │─┐           │   Qwen3:8b   │   Automated     │   OneDrive Excel    │
│ (Bank of Taiwan)     │ │           │   (Parse &   │   Write ──────▶ │                     │
└──────────────────────┘ ├─────────▶ │  Categorize) │                  │ 2025年開銷表        │
                         │           └──────────────┘                  │  （NT）.xlsx        │
┌──────────────────────┐ │                  ↓                          │                     │
│ wife_august.csv      │─┘           ┌──────────────┐                  │ Sheet: 8月          │
│ (Carrefour + Misc)   │             │   Qwen3:8b   │◀──Read/Analyze──│ Sheet: 年總計       │
└──────────────────────┘             │ (Process &   │                  └─────────────────────┘
                                     │  Analyze)    │                           ↕
       Manual Entry ────────────────────────┐       │                  ┌─────────────────────┐
┌──────────────────────┐                    │       │                  │ Cell-by-Cell Editor │
│ Direct Cell Edit     │                    ↓       │                  │ (utils/edit_cells)  │
│ (Auto-fill dates,    │─────────────▶  openpyxl   │                  │ • Manual write      │
│  Edit expenses)      │                Write ──────┘                  │ • Preview changes   │
└──────────────────────┘                                               │ • Validation        │
                                                                        └─────────────────────┘
                                              ↓
                                     ┌──────────────────┐
                                     │  AI Chat         │
                                     │  Interface       │
                                     │ (Ask questions,  │
                                     │  get insights)   │
                                     └──────────────────┘
```

### 🗓️ Annual Year Transition System

The system automatically handles year transitions with **zero manual intervention**:

**How It Works:**
1. **Dynamic File Naming:** Budget file follows current year → `[YEAR]年開銷表（NT）.xlsx`
   - 2025: `2025年開銷表（NT）.xlsx`
   - 2026: `2026年開銷表（NT）.xlsx`
   - 2027: `2027年開銷表（NT）.xlsx`

2. **Automatic Detection:** On system startup, checks current date and loads appropriate year file

3. **January 1st Behavior:**
   - System detects new year has arrived
   - Automatically creates `[NEW_YEAR]年開銷表（NT）.xlsx` from template
   - All 12 monthly sheets initialized with dates auto-filled
   - Previous year's file remains accessible for comparisons

4. **Manual Control:** Can manually create next year via **System Tools → [5] Create Next Year Budget**

**Multi-Year Support:**
- System tracks all available years (2025+)
- **View Budget** menu shows all years with monthly breakdown
- AI Chat can analyze trends across multiple years
- Seamless year-over-year comparisons

---

## 📊 System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                       │
│                      (_main.py)                         │
│  View Budget | Update Monthly | Budget Chat | Tools    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER (Core)                 │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │ Module Registry  │    │  LLM Orchestrator        │  │
│  │ (Plugin Loader)  │    │  (Smart Routing)         │  │
│  └──────────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  MODULE LAYER                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │   Data   │  │   LLM    │  │     Insights         │  │
│  │ Modules  │  │ Engines  │  │     (AI Chat)        │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     DATA LAYER                          │
│   CSV Files → Excel Storage → OneDrive Cloud Sync      │
│   Master File: 2025年開銷表（NT）.xlsx (OneDrive)        │
│   Location: ~/Library/CloudStorage/OneDrive-Personal/   │
└─────────────────────────────────────────────────────────┘
```

### The Qwen-Only AI Strategy

```
USER INPUT (CSV or Question)
        ↓
   ORCHESTRATOR routes to Qwen
        ↓
    ┌───────────────────────────────┐
    │   TASK TYPE CLASSIFICATION    │
    └───────────────────────────────┘
        ↓
  ALL TASKS → QWEN3:8B
        ↓
┌──────────────────────────────┐
│         Qwen3:8b             │
│        (5.2GB)                │
├──────────────────────────────┤
│ • CSV parse & categorize     │
│ • Natural language routing   │
│ • Function-based responses   │
│ • Data analysis & insights   │
│ Speed: ~3-8s                 │
│ Reliability: High            │
└──────────────────────────────┘
        ↓
   FUNCTION ROUTING
   (Existing capabilities)
        ↓
    DIRECT RESULTS
   (Fast & consistent)
```

**Why This Works:**
- ⚡ **100% of tasks** use reliable Qwen (consistent results)
- 🎯 **Function routing** for predictable responses
- 🔧 **Simplified architecture** for better reliability
- 💰 **Resource efficient** (single model, lower RAM usage)

---

## 🎯 Main Features

### 1. View Budget 📊
```
View your OneDrive Excel file:
- Monthly details (daily entries)
- Year summary (totals by month)
- Category breakdowns
- Quick statistics
```

### 2. Update Monthly Budget 📥
```
Merge your + wife's CSV exports:
1. Select target month
2. Provide file paths
3. LLM categorizes automatically
4. Preview before applying
5. Excel updated on OneDrive
```

**Processing Pipeline:**
```
CSV Files (Me + Wife)
    ↓
Qwen3:8b parses & categorizes
    ↓
Dictionary mapping (95% handled)
    ↓
LLM fallback for edge cases (5%)
    ↓
Merge with existing Excel
    ↓
Update OneDrive file
    ↓
Function-based insights generated
```

### 3. Budget Chat & Insights 💬
```
AI-powered chat with your budget data:
- Ask questions in Chinese or English
- Get instant answers via function routing
- See visual reports & graphs
- Receive data-driven insights
```

### 4. System Tools ⚙️
```
- View module status
- Check LLM configuration
- Test OneDrive connection
- Reload modules (development)
- Create next year's budget file
```

---

## 🚀 Quick Start

Get started in under 2 minutes:

```bash
# 1. Navigate to project
cd /Users/peter/Desktop/Old_Projects/GitHub/Family_Budget_Agent

# 2. Activate environment
source venv/bin/activate

# 3. Run the agent
python _main.py
```

**That's it!** The interactive menu will guide you through:
- **[1] View Budget** - Display any month from 2025+ or annual summaries
- **[2] Update Monthly Budget** - Two options:
  - **Automated:** Merge family CSV exports (LLM categorizes and writes to Excel)
  - **Manual:** Cell-by-cell editor with date auto-fill and expense entry
- **[3] Budget Chat** - AI-powered Q&A with visual analysis
- **[4] System Tools** - Config, module status, create next year's file

**First-time setup?** See [Setup & Installation](#-setup--installation) below.

---

## 📁 Project Structure

```
Family_Budget_Agent/
│
├── _main.py                 # Main entry point
├── config.py                # ⭐ Configuration (swap LLMs here!)
├── category_mapping.json    # Category dictionary
├── README.md                # This file
│
├── core/                    # Core infrastructure
│   ├── base_module.py       # Module interface
│   ├── module_registry.py   # Plugin loader
│   ├── orchestrator.py      # LLM orchestration
│   ├── qwen_orchestrator.py # Qwen-specific orchestrator
│   └── simple_orchestrator.py # Simplified orchestrator
│
├── modules/                 # Plugin modules (auto-discovered)
│   ├── data/                # Data processing modules
│   │   ├── annual_manager.py
│   │   ├── file_parser.py
│   │   ├── monthly_merger.py
│   │   └── simple_categorizer.py
│   │
│   ├── insights/            # AI Chat & analysis
│   │   ├── budget_chat.py   # Main AI chat controller
│   │   ├── chat_menus.py    # Chat interface menus
│   │   ├── data_loader.py   # Excel data loader
│   │   ├── multi_year_data_loader.py # Multi-year data support
│   │   ├── insight_generator.py # Generate insights and summaries
│   │   ├── trend_analyzer.py # Analyze category trends over time
│   │   ├── gui_graphs.py    # Matplotlib charts
│   │   ├── terminal_graphs.py # ASCII charts
│   │   ├── visual_report_generator.py # Rich terminal reports
│   │   ├── function_registry.py # Chat function registry
│   │   └── qwen_chat.py     # Qwen-specific chat implementation
│   │
│   └── llm/                 # LLM engines
│       ├── base_llm.py      # LLM interface
│       ├── qwen_engine.py   # Qwen3:8b
│       └── gpt_oss_engine.py # GPT-OSS:20b
│
└── utils/                   # Helper scripts
    ├── edit_cells.py
    └── view_sheets.py
```

---

## ⚙️ Configuration

### LLM Configuration

Edit `config.py`:

```python
# Current configuration (Qwen-only):
STRUCTURED_LLM = "qwen3:8b"      # Fast structured tasks
REASONING_LLM = "qwen3:8b"       # Use Qwen for both structured and reasoning tasks

# Alternative options:
# STRUCTURED_LLM = "qwen2.5:14b"  # Larger Qwen model
# REASONING_LLM = "qwen2.5:14b"  # Use larger model for both
```

Restart → New models active!

### OneDrive Path Configuration

The system uses **year-based dynamic file naming** that updates automatically:

```python
# config.py
ONEDRIVE_PATH = "/Users/peter/Library/CloudStorage/OneDrive-Personal/Documents"

# File naming follows current year (updated automatically)
from datetime import datetime
current_year = datetime.now().year
BUDGET_FILE = f"{current_year}年開銷表（NT）.xlsx"  # ⭐ Year-dynamic filename

# Examples:
# 2025 → "2025年開銷表（NT）.xlsx"
# 2026 → "2026年開銷表（NT）.xlsx"
# 2027 → "2027年開銷表（NT）.xlsx"

# Combined path:
BUDGET_PATH = f"{ONEDRIVE_PATH}/{BUDGET_FILE}"
# → /Users/peter/Library/CloudStorage/OneDrive-Personal/Documents/2025年開銷表（NT）.xlsx
```

**🗓️ Year Transition Behavior:**
- **January 1st:** System automatically detects new year and creates `[NEW_YEAR]年開銷表（NT）.xlsx`
- **Template source:** Uses `20XX年開銷表（NT）.xlsx` as the template
- **Auto-initialization:** All 12 monthly sheets pre-created with dates auto-filled
- **Previous years:** Remain accessible for multi-year analysis and comparisons
- **Manual creation:** Can also create next year's file via **System Tools → [5] Create Next Year Budget**

**Required File Structure:**
- Contains 12 monthly sheets (一月 through 十二月)
- Contains annual summary sheet (年總計)
- Must follow the template structure from `20XX年開銷表（NT）.xlsx`

### Category Mappings

Edit `category_mapping.json` to add your own mappings:
```json
{
  "person_specific_mappings": {
    "peter": {
      "Starbucks": "伙食费",
      "Uber": "交通费"
    },
    "wife": {
      "家樂福": "伙食费"
    }
  }
}
```

---

## 🔧 Setup & Installation

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai/) installed
- macOS (primary) or Linux

### 1. Clone & Setup
```bash
cd /Users/peter/Desktop/Old_Projects/GitHub/Family_Budget_Agent
source venv/bin/activate  # If venv exists
# Or create new: python3 -m venv venv && source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Key packages:
- `pandas` - Data processing
- `openpyxl` - Excel handling
- `rich` - Beautiful terminal output
- `matplotlib` - GUI charts
- `plotext` - Terminal charts

### 3. Install Ollama Models
```bash
ollama pull qwen3:8b       # AI model (5.2GB)
```

### 4. Configure OneDrive Path
```bash
# Update config.py with your OneDrive path:
# ONEDRIVE_PATH = "/Users/yourname/Library/CloudStorage/OneDrive-Personal/Documents"
```

### 5. Run!
```bash
python _main.py
```

---

## 💡 Usage Examples

### Example 1: Monthly CSV Upload

```
1. Export bank transactions → peter_august.xlsx, wife_august.xlsx
2. Run: python _main.py
3. Choose: [2] Update Monthly Budget
4. Select month: 8 (August)
5. Provide file paths
6. System processes:
   ✅ Qwen categorizes 42/45 transactions (93%)
   📊 Dictionary mapping handles 40/45 (89%)
   🤖 LLM fallback handles 5/45 (11%)
   ✅ Merged to Excel
   💡 Function-based insights: "August ↑15% vs July, mainly food"
7. Done! (~3 minutes total)
```

### Example 2: AI Budget Chat

```
You: 七月花了多少？
Assistant: 七月總支出 NT$27,300

You: 為什麼八月增加？
Assistant: 📈 八月支出增加 15% 主要因為:
• 伙食費 ↑ NT$3,200 (更多外食)
• 休閒娛樂 ↑ NT$2,000 (8/15 特殊支出)
建議: 檢視週五外食頻率

You: Show me a chart
Assistant: [Terminal bar chart appears]
```

### Example 3: Quick Insights

```
Choose: [3] Budget Chat → [2] Visual Analysis
Select: Monthly Analysis
Choose month: 7 (July)

📊 七月支出分析
┌─────────────┬──────────┬────────┬─────────┐
│ 類別        │ 金額     │ 佔比   │ 趨勢    │
├─────────────┼──────────┼────────┼─────────┤
│ 伙食費      │ 15,420   │ 56%    │ ↑ +12%  │
│ 交通費      │  4,200   │ 15%    │ → 持平  │
│ 休閒/娛樂   │  5,500   │ 20%    │ ↑ +25%  │
│ 家務        │  2,180   │  8%    │ ↓ -5%   │
└─────────────┴──────────┴────────┴─────────┘

[Option: Show chart? Y/N]
```

---

## 🎓 Key Concepts

### Plugin System
- Drop modules in `modules/` → Auto-discovered on startup
- No code changes needed in main file
- Hot-reload in development mode
- Version modules independently

### Smart LLM Orchestration
- System picks best LLM automatically based on task
- Confidence-based handoff (< 85% → escalate to stronger model)
- Hybrid workflows (Qwen extracts → GPT-OSS reasons)
- Optimal performance & cost

### 3-Tier Data Access (AI Chat)
- **Tier 1**: Python calculations (free, instant, 100% accurate)
- **Tier 2**: LLM + summary stats (fast, 85% accurate)
- **Tier 3**: LLM + full Excel data (comprehensive, 90% accurate)
- Automatic escalation when needed

### Confidence Tracking
- Every AI answer shows confidence score
- 5-component calculation (data, clarity, LLM certainty, validation)
- Transparent about uncertainty
- Helps you know when to trust answers

---

## 🔄 Typical Monthly Workflow

```
📅 MONTH START
├─ Day 1-5: Normal spending, transactions in banks
│
📥 MONTH END (Day 28-31)
├─ Export your bank CSV
├─ Export wife's bank CSV
├─ Run: python _main.py → [2] Update Monthly
├─ System processes (~3 min)
└─ Excel updated on OneDrive ✅
│
💬 MONTH REVIEW (Next month Day 1-3)
├─ Run: python _main.py → [3] Budget Chat
├─ Ask: "上個月花了多少？"
├─ Ask: "為什麼比上上個月多？"
├─ Ask: "給我看圖表"
└─ Insights → Adjust spending behavior
│
🔁 REPEAT MONTHLY
```

**Time investment:** ~10 minutes per month  
**Value:** Complete budget control & insights

---

## 📊 System Metrics

| Metric | Performance |
|--------|-------------|
| CSV parsing (45 tx) | 3-8 seconds |
| Dictionary mapping | 95% of transactions |
| LLM fallback | 5% of transactions |
| Simple chat query | 1-3 seconds |
| Complex analysis | 5-15 seconds |
| Module reload | Instant |
| Memory usage | ~5.2GB (Qwen only) |

---

## 🚧 Current Status

### ✅ Production Ready
- ✅ CSV processing with Qwen + dictionary mapping
- ✅ Monthly budget merging
- ✅ Annual file management
- ✅ OneDrive sync integration
- ✅ AI Chat (function-based routing)
- ✅ Visual reports (terminal + GUI)
- ✅ Bilingual support (中文/English)

### ⚠️ Known Limitations
- AI Chat complexity (max 15 words, single-part questions)
- No LLM response caching yet (slower repeated queries)
- GUI charts take 3-5 seconds
- Fuzzy duplicate detection ~85% accurate
- Multi-year analysis UI incomplete (backend ready)

### 🚧 In Progress
- Performance optimizations (cache TTL increased to 30 minutes)
- Font optimization for Chinese characters
- Enhanced error handling
- Improved user experience

---

## 🐛 Troubleshooting

### LLM not found?
```bash
ollama list                 # Check installed models
ollama pull qwen3:8b        # Install if missing
```

### OneDrive file not found?

The system looks for a **year-based filename**: **`[CURRENT_YEAR]年開銷表（NT）.xlsx`**

**Examples:**
- In 2025: `2025年開銷表（NT）.xlsx`
- In 2026: `2026年開銷表（NT）.xlsx`

```bash
# Check if current year's file exists
YEAR=$(date +%Y)
ls -la ~/Library/CloudStorage/OneDrive-Personal/Documents/${YEAR}年開銷表（NT）.xlsx

# For 2025 specifically:
ls -la ~/Library/CloudStorage/OneDrive-Personal/Documents/2025年開銷表（NT）.xlsx

# Check if file exists manually

# Then update ONEDRIVE_PATH in config.py if needed
```

**If file doesn't exist:**
1. **Option A:** Create it from template using **System Tools → [5] Create Next Year Budget**
2. **Option B:** Manually copy `20XX年開銷表（NT）.xlsx` template and rename to current year
3. **Option C:** System will auto-create on January 1st if template exists

**Note:** File name must be exact, including Chinese characters and parentheses `（NT）`

### Module not loading?
```python
# In _main.py or Python console:
from core.module_registry import registry
print(registry.list_modules())  # Check discovered modules
```

### Slow performance?
- Check if both LLMs are running: `ollama ps`
- Reduce to single model in config.py
- Use terminal charts instead of GUI charts
- Clear OneDrive sync conflicts
- Cache TTL increased to 30 minutes for better performance

### Category not mapping?
```
Add to category_mapping.json:
{
  "person_specific_mappings": {
    "peter": {
      "YourNewCategory": "伙食费"
    }
  }
}
```

---

## 🤝 Contributing

### Priority Areas
1. 🔴 **High**: LLM response caching
2. 🔴 **High**: Question decomposition (AI Chat)
3. 🟡 **Medium**: PDF report export
4. 🟡 **Medium**: Multi-year analysis UI
5. 🟢 **Low**: Custom chart themes

### Development Guidelines
- Follow the plugin system architecture
- Test with both LLM models
- Maintain bilingual support
- Keep privacy-first approach

---

## 📞 Support

**Questions?** Check:
1. This README (overview)
2. Troubleshooting section above
3. System Tools → Module Status
4. Check logs for detailed error messages

---

## 📜 License

Personal project - feel free to adapt for your own use.

---

**Version:** 2.0.0  
**Architecture:** Modular Plugin System with Qwen-Only AI  
**LLM:** Qwen3:8b (all tasks)  
**Status:** Production Ready ✅  

---

Built with ❤️ for intelligent, privacy-first family budgeting.
