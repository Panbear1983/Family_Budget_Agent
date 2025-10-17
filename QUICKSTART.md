# Quick Start Guide 🚀

## ✅ System is Ready!

Everything is built and working. Here's how to use it:

---

## 🎯 Run the System

```bash
cd /Users/peter/Desktop/Old_Projects/GitHub/Family_Budget_Agent
./start.sh
```

---

## 📋 Main Menu

```
💰 家庭預算管理系統 - FAMILY BUDGET AGENT v2.0
════════════════════════════════════════════════════════════

📋 主選單 MAIN MENU:

   1️⃣  📊 查看 2025 年預算表 (View 2025 Budget)
   2️⃣  📥 更新每月預算 (Update Monthly Budget - Me + Wife)
   3️⃣  💬 預算分析對話 (Budget Chat & Insights)
   4️⃣  ⚙️  系統工具 (System Tools)
   0️⃣  退出 (Exit)
```

---

## 📖 How to Use Each Feature

### **Option 1: View 2025 Budget** 📊

View your 2025年開銷表（NT） file:
- Choose month (1-12) to see detailed daily entries
- Choose 13 for year summary
- Choose 14 to ask LLM to find specific data

**Example:**
```
Choose: 1
  → Select: 7 (七月 - July)
  → See July's daily expenses in Excel-style grid
```

---

### **Option 2: Update Monthly Budget** 📥

Merge your + wife's monthly exports:

**Steps:**
1. Choose option 2
2. Select target month (e.g., 8 for August)
3. Provide YOUR export file path
4. Provide WIFE's export file path
5. System processes:
   - Dictionary categorizes (95% instant)
   - LLM handles edge cases (5%)
   - Shows preview
6. Confirm to apply
7. Done! Updated in OneDrive

**File Format:**
Your exports should have columns: `date`, `amount`, `category`, `description`

**Category Mapping:**
- Automatic via `category_mapping.json`
- Your "Groceries" → Main "伙食费"
- Wife's "Food-Stuff" → Main "伙食费"

---

### **Option 3: Budget Chat** 💬

Ask questions about your budget:

**Examples:**
```
您: 七月的伙食費是多少?
助手: NT$31,865 (based on 七月 tab, 伙食费 column)

您: Why did spending increase in August?
助手: August increased 15% mainly due to...

您: Can I afford a NT$10,000 vacation?
助手: Based on your patterns, yes if you...
```

---

### **Option 4: System Tools** ⚙️

- View module status
- View LLM configuration  
- Test OneDrive connection
- Reload modules (development)

---

## 🔧 Configuration

### **Swap LLM Models**

Edit `config.py` (lines 14-15):
```python
STRUCTURED_LLM = "qwen3:8b"      # ← Change to upgrade
REASONING_LLM = "gpt-oss:20b"    # ← Change to upgrade
```

Restart system → New models active!

### **Add Category Mappings**

Edit `category_mapping.json`:
```json
{
  "person_specific_mappings": {
    "peter": {
      "YourNewCategory": "伙食费"  // ← Add here
    },
    "wife": {
      "WifeNewCategory": "交通费"  // ← Add here
    }
  }
}
```

No restart needed - reloads automatically!

---

## 📊 System Architecture

```
User Interface (_main.py)
    ↓
Dictionary Lookup (95% fast)
    ↓
LLM Fallback (5% smart)
    ↓
Qwen3:8b (structured) ←→ GPT-OSS:20b (reasoning)
    ↓
Excel Update (OneDrive sync)
```

---

## 🎯 Monthly Workflow

**Every month:**

1. Export your bank transactions → `peter_august.xlsx`
2. Export wife's transactions → `wife_august.xlsx`  
3. Run: `./start.sh`
4. Choose: 2 (Update Monthly)
5. Select: 8 (August)
6. Provide file paths
7. Confirm → Done!

**Time:** ~2-3 minutes total

---

## 📁 Key Files

| File | Purpose | Edit When |
|------|---------|-----------|
| `config.py` | LLM selection, paths | Swap models or change paths |
| `category_mapping.json` | Category dictionary | Add new labels |
| `_main.py` | Main system | Never (unless extending) |
| `start.sh` | Launcher | Never |

---

## 🆘 Troubleshooting

**LLM not found?**
```bash
ollama pull qwen3:8b
ollama pull gpt-oss:20b
```

**OneDrive file not found?**
```bash
python utils/find_budget.py
# Then update ONEDRIVE_PATH in config.py
```

**Category not mapping?**
```
Add to category_mapping.json
→ person_specific_mappings.peter or .wife
```

---

## ✅ You're Ready!

**Everything is built:**
- ✅ 3 workflows (View, Update, Chat)
- ✅ 3 features (Annual, Monthly, LLM Swap)
- ✅ Dictionary-first (fast & accurate)
- ✅ Dual-LLM (Qwen + GPT-OSS)

**Run: `./start.sh` and start budgeting!** 💰🎉

