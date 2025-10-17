# Modular Architecture - Usage Guide 🔌

## Overview

The new modular architecture allows you to:
- ✅ Dynamically load/unload modules
- ✅ Hot-swap modules without restarting
- ✅ Update individual modules independently
- ✅ Add new features as plugins

---

## Architecture Structure

```
_main_v2.py                    # Main orchestrator
    ↓
ModuleRegistry                 # Dynamic module loader
    ↓
├── LLM Modules
│   ├── QwenEngine           (qwen3:8b - structured tasks)
│   └── GptOssEngine         (gpt-oss:20b - reasoning)
│
├── Data Modules (future)
│   ├── CSVHandler
│   └── ExcelHandler
│
└── Analysis Modules (future)
    ├── Categorizer
    └── InsightGenerator
```

---

## How It Works

### 1. **Auto-Discovery**
```python
# System automatically finds all modules
registry.auto_discover('modules')

# Result:
# ✅ Registered module: QwenEngine
# ✅ Registered module: GptOssEngine
```

### 2. **Dynamic Loading**
```python
# Modules load on-demand
qwen = registry.get_module('QwenEngine')

# If not loaded yet, creates and initializes
# If already loaded, returns existing instance
```

### 3. **Smart Orchestration**
```python
orchestrator = LLMOrchestrator()

# Automatically uses right LLM for task
category, conf = orchestrator.categorize_transaction(tx)

# Qwen tries first (fast)
# If uncertain → GPT-OSS refines (smart)
```

---

## Key Features

### 🔄 **Module Swapping**

**Old Way** (Hardcoded):
```python
from BUDGET_QWEN import QwenAnalyzer
qwen = QwenAnalyzer()  # Tightly coupled
```

**New Way** (Modular):
```python
from core.module_registry import registry

# Get module dynamically
qwen = registry.get_module('QwenEngine')

# Easy to swap:
# - Update QwenEngine.py
# - Or replace with QwenEngine_v2
# - Or use different model entirely
```

### 🔁 **Hot Reload** (Development)

```python
# Made changes to QwenEngine?
registry.reload_module('QwenEngine')

# Module reloads without restarting app!
```

### ➕ **Adding New Modules**

1. Create new module:
```python
# modules/llm/claude_engine.py
from .base_llm import BaseLLM

class ClaudeEngine(BaseLLM):
    def _setup(self):
        self.model_name = 'claude-3'
    
    def categorize(self, transaction):
        # Implementation
        pass
```

2. That's it! Auto-discovered on next run.

3. Use it:
```python
claude = registry.get_module('ClaudeEngine')
```

---

## Workflow Examples

### Example 1: CSV Processing
```python
orchestrator = LLMOrchestrator()
orchestrator.initialize()

# Batch process with auto-handoff
results = orchestrator.batch_process(transactions)

# Qwen handles 88%
# GPT-OSS handles uncertain 12%
# Result: 100% categorized
```

### Example 2: Smart Q&A
```python
# User asks question
answer = orchestrator.answer_question(
    "Why did food costs increase?",
    budget_data
)

# System automatically:
# 1. Classifies question type (reasoning)
# 2. Routes to GPT-OSS:20b
# 3. Returns thoughtful answer
```

### Example 3: Dual Collaboration
```python
# Complex analysis uses both
insights = orchestrator.generate_insights(data)

# Flow:
# 1. Qwen calculates statistics (fast)
# 2. GPT-OSS analyzes trends (smart)
# 3. Combined result
```

---

## Module Standards

### Every Module Must:

1. **Inherit from BaseModule**
```python
from core.base_module import BaseModule

class MyModule(BaseModule):
    pass
```

2. **Implement execute()**
```python
def execute(self, *args, **kwargs):
    # Your logic here
    return result
```

3. **Handle initialization**
```python
def _setup(self):
    # Custom setup logic
    self.ready = True
```

---

## Configuration

### config.py Structure:
```python
# LLM Module Configuration
LLM_CONFIG = {
    'QwenEngine': {
        'model': 'qwen3:8b',
        'timeout': 30
    },
    'GptOssEngine': {
        'model': 'gpt-oss:20b',
        'timeout': 60
    }
}

# Orchestrator Settings
ORCHESTRATOR_CONFIG = {
    'confidence_threshold': 0.85,  # Hand off if below
    'max_retries': 3,
    'fallback_category': '其它'
}
```

---

## Version Updates

### Updating a Module:

**Option 1: In-place Update**
```bash
# Edit the module file
vim modules/llm/qwen_engine.py

# Reload in app (no restart needed)
registry.reload_module('QwenEngine')
```

**Option 2: New Version**
```bash
# Create v2
cp qwen_engine.py qwen_engine_v2.py

# Update config to use v2
config['default_qwen'] = 'QwenEngine_v2'
```

**Option 3: A/B Testing**
```python
# Load both versions
qwen_v1 = registry.get_module('QwenEngine')
qwen_v2 = registry.get_module('QwenEngine_v2')

# Compare results
result1 = qwen_v1.execute('categorize', tx)
result2 = qwen_v2.execute('categorize', tx)
```

---

## Migration Guide

### From Old to New:

**Old _main.py:**
```python
from BUDGET_QWEN import BudgetQwenAnalyzer
from BUDGET_GPT_OSS import BudgetGptOssEnhancer

qwen = BudgetQwenAnalyzer()
gpt = BudgetGptOssEnhancer()

# Hardcoded logic
category = qwen.match_category(desc)
```

**New _main_v2.py:**
```python
from core import LLMOrchestrator

orchestrator = LLMOrchestrator()
orchestrator.initialize()

# Smart routing
category, conf = orchestrator.categorize_transaction(tx)
```

---

## Running the New System

```bash
cd /Users/peter/Desktop/Old_Projects/GitHub/Family_Budget_Agent

# Activate venv
source venv/bin/activate

# Run new modular version
python _main_v2.py
```

---

## Benefits Summary

| Feature | Old System | New Modular System |
|---------|-----------|-------------------|
| **Add Feature** | Edit main file | Drop in new module |
| **Update LLM** | Change everywhere | Update one file |
| **Swap Model** | Refactor code | Change config |
| **Test New Version** | Duplicate everything | Load both, compare |
| **Rollback** | Git revert | Switch module |
| **Hot Reload** | ❌ Restart needed | ✅ Instant reload |

---

## Next Steps

1. ✅ Test new system
2. ✅ Migrate workflows
3. 📝 Add data modules (CSV, Excel)
4. 📝 Add analysis modules
5. 📝 Create UI modules
6. 🚀 Full migration

---

**The new modular system is ready to use!** 🎉

