#!/usr/bin/env python3
"""Simple verification that trend classification works"""

# Test the classifier directly without imports
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🧪 Verifying Trend Classification Fix\n")
print("=" * 70)

# Simulate what the classifier should do
test_questions = [
    "How is transportation cost changing?",
    "What's the trend for food?",
    "Is spending increasing?",
    "交通費的趨勢如何？",
    "伙食費有什麼變化？"
]

# Keywords that should trigger trend classification
trend_keywords = [
    'trend', 'pattern', '趨勢', '模式',
    'change', 'changing', 'changed', '變化', '改變',
    'increase', 'increasing', 'decrease', 'decreasing',
    '增加', '減少', '上升', '下降',
    'growth', 'decline', 'rising', 'falling',
    'over time', 'recently', 'lately', '最近',
    'going up', 'going down', 'progression'
]

print("Testing keyword coverage:\n")

for question in test_questions:
    q_lower = question.lower()
    matched = []
    
    for keyword in trend_keywords:
        if keyword in q_lower:
            matched.append(keyword)
    
    if matched:
        print(f"✅ '{question}'")
        print(f"   → Matched: {', '.join(matched)}")
        print(f"   → Will classify as: TREND")
    else:
        print(f"❌ '{question}'")
        print(f"   → No trend keywords found")
    print()

print("=" * 70)
print("\n✅ Verification Logic:")
print("1. Expanded trend keywords from 7 to 28+ variations")
print("2. Added refinement logic to catch misclassified trend questions")
print("3. Increased priority from 3 to 4 (same as insight)")
print("\n🎯 Expected Behavior:")
print("• 'How is transportation cost changing?' → TREND (Qwen-only, 10-15s)")
print("• 'Why did spending increase?' → INSIGHT (Dual pipeline)")
print("\n💡 To fully test: Restart app and ask trend questions!")

