# Budget Insights Module 💡

A comprehensive insights and chat module for intelligent budget analysis.

## 📁 Module Structure

```
modules/insights/
├── __init__.py              # Module exports
├── budget_chat.py           # Main coordinator (BaseModule)
├── data_loader.py           # Excel data loading & caching
├── context_manager.py       # Conversation history
├── insight_generator.py     # Structured insights
├── trend_analyzer.py        # Trend analysis & forecasting
└── report_generator.py      # Report formatting
```

## 🎯 Features

### 1. **Data Loader** (`data_loader.py`)
- ✅ Loads Excel budget data efficiently
- ✅ Caches data for 5 minutes (configurable TTL)
- ✅ Supports all 12 monthly sheets
- ✅ Generates summary statistics

### 2. **Context Manager** (`context_manager.py`)
- ✅ Maintains conversation history (last 10 interactions)
- ✅ Tracks current focus (month/category)
- ✅ Finds relevant past interactions
- ✅ Provides context summaries

### 3. **Insight Generator** (`insight_generator.py`)
- ✅ Monthly insights (totals, averages, categories)
- ✅ Month-to-month comparisons
- ✅ Yearly summaries
- ✅ Top expenses and warnings

### 4. **Trend Analyzer** (`trend_analyzer.py`)
- ✅ Category trend analysis (increasing/decreasing/stable)
- ✅ Anomaly detection (outlier transactions)
- ✅ Next month forecasting (with confidence levels)

### 5. **Report Generator** (`report_generator.py`)
- ✅ Formatted monthly reports
- ✅ Comparison reports
- ✅ Yearly summary reports
- ✅ Rich console output

### 6. **Budget Chat** (`budget_chat.py`)
- ✅ Main integration module
- ✅ LLM-powered Q&A
- ✅ Special commands (/insight, /compare, /summary, /forecast)
- ✅ Context-aware conversations

## 🚀 Usage

### Basic Chat
```python
from core.module_registry import registry

# Initialize
chat_module = registry.get_module('BudgetChat', config={
    'budget_file': '/path/to/budget.xlsx'
})
chat_module.set_orchestrator(orchestrator)

# Ask questions
answer = chat_module.execute('chat', "七月的伙食費是多少?")
```

### Special Commands
```python
# Generate monthly insights
report = chat_module.execute('generate_insight', '七月')

# Compare two months
comparison = chat_module.execute('compare_months', '七月', '八月')

# Yearly summary
summary = chat_module.execute('yearly_summary')

# Forecast next month
forecast = chat_module.execute('forecast')

# Analyze category trend
trend = chat_module.execute('analyze_trend', '伙食费')
```

## 🎮 In-App Commands

When running in the main app (option 3), you can use:

- `/insight 七月` - Deep analysis of a month
- `/compare 七月 八月` - Compare two months
- `/summary` - Full year overview
- `/forecast` - Predict next month spending
- `/clear` - Clear conversation history

## 🔧 Configuration

### Timeout Settings (`config.py`)
```python
LLM_CONFIG = {
    "structured": {
        "timeout": 60,  # 1 minute for Qwen
    },
    "reasoning": {
        "timeout": 120,  # 2 minutes for GPT-OSS
    }
}
```

### Cache TTL (`data_loader.py`)
```python
self.ttl = 300  # 5 minutes (adjustable)
```

## 🔌 Integration

The module integrates seamlessly with the existing system:

1. **Detachable**: Can be removed without breaking main app
2. **Graceful fallback**: Falls back to basic mode if unavailable
3. **Auto-discovery**: Automatically registered by module registry
4. **BaseModule compliant**: Follows standard module interface

## 📊 Data Flow

```
User Question
    ↓
BudgetChat.chat()
    ↓
DataLoader.load_all_data() → Cache (5 min TTL)
    ↓
ContextManager → Recent history + focus
    ↓
LLM Orchestrator → Qwen (fast) / GPT-OSS (smart)
    ↓
InsightGenerator → Structured analysis
    ↓
ReportGenerator → Formatted output
    ↓
User receives answer
```

## 🎯 Why This Architecture?

✅ **Separation of Concerns**: Each module has one clear responsibility  
✅ **Testable**: Components can be tested independently  
✅ **Reusable**: Sub-modules can be used in other contexts  
✅ **Maintainable**: Easy to update individual components  
✅ **Performant**: Intelligent caching reduces Excel reads  
✅ **Extensible**: Easy to add new analysis features  

## 🔮 Future Enhancements

- [ ] Add data visualization (charts/graphs)
- [ ] Support multiple budget files
- [ ] Export reports to PDF/HTML
- [ ] Add budget goal tracking
- [ ] Implement spending alerts
- [ ] Add category budget limits
- [ ] Multi-year comparisons
- [ ] ML-based spending predictions

## 📝 Notes

- **Cache Management**: Data is cached for 5 minutes to reduce Excel I/O
- **Conversation History**: Limited to last 10 interactions to maintain context
- **LLM Routing**: System automatically chooses best LLM based on question type
- **Error Handling**: Graceful fallback ensures system always works

## 🐛 Troubleshooting

### Module not loading?
- Check if pandas and openpyxl are installed
- Verify budget file path in config
- Check module registry: `registry.list_modules()`

### Timeout errors?
- Increase timeout in `config.py` (LLM_CONFIG)
- Try simpler questions
- Check if Ollama is running

### No data loaded?
- Verify Excel file exists
- Check sheet names match (一月, 二月, etc.)
- Ensure correct column structure

---

**Created**: 2025-01-16  
**Version**: 1.0  
**Author**: Budget Agent Development Team

