# AI Chat - Quick Reference Card 📋

## 🚀 **START HERE**

```bash
python _main.py
→ [3] Budget Chat & Insights
→ [1] AI Chat
→ Start asking!
```

---

## ✅ **What You Can Ask**

### **1. Spending Queries** 💰
```
七月花了多少？
7月的伙食費是多少？
How much in July?
What's the total spending?
```

### **2. Comparisons** 🔍
```
比較七月和八月
七月跟八月差多少？
Compare July and August
```

### **3. Visualizations** 📊
```
給我看圖表
顯示伙食費趨勢
Show me a chart
```

### **4. Forecasts** 🔮
```
預測下個月支出
Forecast next month
```

---

## ❌ **What Doesn't Work**

### **Complex Questions:**
```
❌ 如果減少伙食費，會省多少，還有應該怎麼做？
❌ Can you tell me... (>15 words)
❌ 你覺得哪個月最好？
```

### **Off-Topic:**
```
❌ 今天天氣怎麼樣？
❌ Should I invest in stocks?
❌ Tell me a joke
```

---

## 🎯 **How Fast?**

| Type | Time | Example |
|------|------|---------|
| Simple | **<1s** ⚡ | "七月花了多少？" |
| Medium | ~5s | "7月和8月差多少？" |
| Complex | ~15s | "超過1000的交易有哪些？" |

---

## 🔍 **Confidence Scores**

```
🟢 80%+ = Trust it
🟡 60-79% = Verify it
🟠 40-59% = Use caution
🔴 <40% = Don't rely on it
```

---

## 💡 **Pro Tips**

1. **Be Specific**
   - ✅ "七月的伙食費是多少？"
   - ❌ "花了多少？" (which month?)

2. **One Question at a Time**
   - ✅ "七月花了多少？" then "八月呢？"
   - ❌ "七月花了多少，還有八月？"

3. **Use Numbers**
   - ✅ "7月" or "七月" (both work!)
   - ✅ "July" or "Jul" (both work!)

4. **Check Confidence**
   - Low confidence? Ask more specifically
   - Very low? Question might be too complex

---

## 📂 **Data Source**

**All data comes from:**
```
/Users/peter/Library/CloudStorage/OneDrive-Personal/Documents/2025年開銷表（NT）.xlsx
```

- ☁️ Synced with OneDrive
- 🔄 Refreshed every 5 minutes
- 📊 Full access to all sheets and transactions

---

## ⚙️ **Toggle Settings** (config.py)

```python
# Hide confidence scores:
AI_CHAT_CONFIG = {
    "show_confidence": False
}

# Force English:
LANGUAGE_CONFIG = {
    "default_language": "en"
}
```

---

## 🐛 **If Something's Wrong**

1. **Wrong answer** → Check confidence score
2. **No answer** → Simplify question
3. **Off-topic rejected** → Use budget keywords
4. **Slow** → Normal for complex questions (Tier 3)

---

## 📚 **Full Documentation**

See `/modules/insights/` for complete docs:
- `AI_CHAT_COMPLETE.md` - Full system overview
- `3_TIER_APPROACH.md` - Data access strategy
- `CONFIDENCE_TRACKING.md` - Confidence system
- `SIMPLIFIED_CHAT.md` - Simplified approach

---

**Your AI Budget Assistant is ready! Ask away! 💬✨**

