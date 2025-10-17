# Confidence Tracking Implementation

## ✅ **What Was Added**

A complete **confidence tracking system** that shows transparency and uncertainty in AI responses.

---

## 📁 **New/Updated Files**

### **1. confidence_tracker.py** ✅ (NEW)
- Calculates confidence scores based on 5 components
- Provides uncertainty messages in Chinese/English
- Formats confidence footers with visual bars

### **2. config.py** ✅ (UPDATED)
- Added `AI_CHAT_CONFIG` section
- Toggle options for confidence display
- Threshold settings for warnings

### **3. ai_chat.py** ✅ (UPDATED)
- Integrated confidence tracking throughout answer pipeline
- Tracks: data availability, question clarity, LLM confidence, guardrail results
- Shows confidence footer on every response

---

## 🎯 **How Confidence is Calculated**

### **5 Components (Weighted):**

```python
Confidence Score = Weighted Average of:
├─ Data Availability (40%) - Do we have the requested data?
├─ Question Clarity (20%)   - Is the question unambiguous?
├─ LLM Confidence (20%)     - Is the LLM certain?
├─ Guardrail Passed (10%)   - Did it pass validation?
└─ Response Verified (10%)  - Are numbers verified?
```

### **Confidence Levels:**
- 🟢 **High (80%+)**: Confident, reliable answer
- 🟡 **Medium (60-79%)**: Moderate confidence
- 🟠 **Low (40-59%)**: Uncertain, use with caution
- 🔴 **Very Low (<40%)**: Not reliable

---

## 💬 **Example Outputs**

### **High Confidence (90%+)**
```
您: 七月的伙食費是多少？
助手: 七月的伙食費總共 NT$15,420

🟢 信心度: ████████████████████ 95% (高)
```

### **Medium Confidence (70%)**
```
您: 八月跟上個月比呢？
助手: ⚠️ 問題不太清楚，我盡力回答了，但可能不準確。

八月比七月多支出 NT$5,200 (增加19%)

🟡 信心度: ██████████████░░░░░░ 72% (中等)
   📋 詳細分析:
      • 問題清晰度: 55%
```

### **Low Confidence (50%)**
```
您: 下個月會不會超支？
助手: 🤔 我不太確定這個答案，建議您驗證一下。

基於最近趨勢，可能會...

🟠 信心度: ██████████░░░░░░░░░░ 52% (偏低)
   📋 詳細分析:
      • 資料可用性: 70%
      • AI確定性: 45%
```

### **Very Low / Off-Topic (0%)**
```
您: 今天天氣怎麼樣？
助手: 🚫 這個問題超出我的專業範圍（預算分析），無法準確回答。

我是專門的預算分析助手...

🔴 信心度: ░░░░░░░░░░░░░░░░░░░░ 0% (很低)
```

---

## ⚙️ **Configuration (config.py)**

```python
AI_CHAT_CONFIG = {
    "show_confidence": True,           # Show confidence scores
    "confidence_threshold": 0.6,        # Warn if below 60%
    "verbose_uncertainty": True,        # Show detailed breakdown
    "show_uncertainty_warning": True,   # Show warning messages
    "min_confidence_for_action": 0.7    # Min for recommendations
}
```

### **To Disable Confidence Display:**
```python
AI_CHAT_CONFIG = {
    "show_confidence": False,  # Hide all confidence scores
    ...
}
```

### **To Show Only Low Confidence Warnings:**
```python
AI_CHAT_CONFIG = {
    "show_confidence": True,
    "confidence_threshold": 0.5,    # Only warn below 50%
    "verbose_uncertainty": False,   # No detailed breakdown
    ...
}
```

---

## 🔍 **Uncertainty Detection**

### **LLM Uncertainty Phrases Detected:**
**Chinese:**
- 可能 (maybe)
- 大概 (probably)
- 也許 (perhaps)
- 不確定 (unsure)
- 我猜 (I guess)
- 估計 (estimate)

**English:**
- maybe
- perhaps
- possibly
- unsure
- guess
- might

**More phrases detected → Lower confidence**

---

## 📊 **Confidence Component Breakdown**

### **1. Data Availability (40% weight)**
```python
Score = 1.0  # Start optimistic

# Penalties:
- No data for requested month → 0.2 (80% penalty)
- Category not found → 0.5 (50% penalty)
- Missing comparison data → Proportional penalty
- General query (no specifics) → 0.7
```

### **2. Question Clarity (20% weight)**
```python
Based on classifier confidence:
- High (80%+) → 0.95
- Medium (60-79%) → 0.75
- Low (40-59%) → 0.55
- Very Low (<40%) → 0.35
```

### **3. LLM Confidence (20% weight)**
```python
Based on uncertainty phrases in response:
- 0 phrases → 0.95
- 1 phrase → 0.75
- 2 phrases → 0.55
- 3+ phrases → 0.35
```

### **4. Guardrail Passed (10% weight)**
```python
- Passed all checks → 1.0
- Failed some checks → 0.6
- Failed (off-topic) → 0.0
```

### **5. Response Verified (10% weight)**
```python
- No warnings → 1.0
- Some warnings → 0.7
- Many warnings → 0.5
```

---

## 🎨 **Visual Confidence Bar**

```
🟢 信心度: ████████████████████ 95% (高)
           20-char bar, filled based on %
           
🟡 信心度: ██████████████░░░░░░ 72% (中等)
           
🟠 信心度: ██████████░░░░░░░░░░ 52% (偏低)
           
🔴 信心度: ░░░░░░░░░░░░░░░░░░░░ 0% (很低)
```

---

## 💡 **Best Practices**

### **For High-Stakes Decisions:**
1. ✅ Only act on **High Confidence (80%+)** answers
2. ⚠️ Verify **Medium Confidence (60-79%)** answers
3. ❌ Don't rely on **Low Confidence (<60%)** answers

### **Understanding Warnings:**
- **資料可用性偏低** → Missing data, answer is speculative
- **問題表述不夠清晰** → Rephrase question more specifically
- **AI模型不太確定** → LLM used uncertain language
- **回應驗證失敗** → Numbers don't match source data

---

## 🧪 **Testing Confidence Tracking**

### **Test High Confidence:**
```
您: 七月花了多少？
Expected: 🟢 95%+ (has data, clear question, Python answer)
```

### **Test Medium Confidence:**
```
您: 上個月比這個月多嗎？
Expected: 🟡 60-75% (unclear which months, needs interpretation)
```

### **Test Low Confidence:**
```
您: 明年會花多少？
Expected: 🟠 40-55% (no future data, pure speculation)
```

### **Test Very Low:**
```
您: 股票會漲嗎？
Expected: 🔴 0% (off-topic, rejected by guardrails)
```

---

## 📈 **Benefits**

1. **Transparency** 🔍
   - Users know when to trust answers
   - Clear about limitations

2. **Honesty** 💯
   - AI admits uncertainty
   - No overconfident hallucinations

3. **Education** 📚
   - Shows why confidence is low
   - Helps users ask better questions

4. **Trust** 🤝
   - More reliable than always confident
   - Professional UX (like medical AI)

5. **Safety** 🛡️
   - Prevents blind trust in uncertain answers
   - Encourages verification

---

## 🔧 **Troubleshooting**

### **Problem: All answers show low confidence**
**Solution**: Check if data is loading correctly
```python
# In ai_chat.py, check:
available_data = {
    'months': list(self.data_loader.load_all_data().keys()),
    'categories': self.guardrails.available_categories
}
print(f"Available: {available_data}")  # Debug
```

### **Problem: Confidence scores not showing**
**Solution**: Check config
```python
# In config.py:
AI_CHAT_CONFIG = {
    "show_confidence": True,  # Must be True
    ...
}
```

### **Problem: Too many warnings**
**Solution**: Adjust threshold
```python
AI_CHAT_CONFIG = {
    "confidence_threshold": 0.5,  # Lower = fewer warnings
    ...
}
```

---

## 🚀 **Integration Status**

- ✅ confidence_tracker.py created
- ✅ config.py updated with AI_CHAT_CONFIG
- ✅ ai_chat.py integrated with confidence tracking
- ✅ All confidence components tracked
- ✅ Uncertainty warnings implemented
- ✅ Visual confidence bars added
- ✅ Bilingual support (zh/en)
- ✅ No linting errors

**Status: COMPLETE AND READY TO USE** 🎉

---

## 📝 **Next Steps (Optional)**

1. **Calibration** - Fine-tune weights based on user feedback
2. **Learning** - Track which confidence scores were accurate
3. **Adaptive** - Adjust thresholds based on user's risk tolerance
4. **Logging** - Log confidence scores for analysis

---

**Built with transparency and user trust in mind** 💚

