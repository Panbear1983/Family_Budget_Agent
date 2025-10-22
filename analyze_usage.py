#!/usr/bin/env python3
"""
Usage Analysis Script
Analyzes logged interactions to identify patterns and improvement opportunities
"""

import json
from pathlib import Path
from collections import Counter
from datetime import datetime

def load_logs(log_file="data/usage_log.jsonl"):
    """Load all logged interactions"""
    log_path = Path(log_file)
    
    if not log_path.exists():
        print(f"❌ Log file not found: {log_file}")
        print(f"   Usage logging will start when you use the AI Chat feature.")
        return []
    
    logs = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except:
                pass  # Skip malformed lines
    
    return logs

def analyze_patterns(logs):
    """Analyze usage patterns from logs"""
    if not logs:
        print("\n📊 No usage data yet. Start using the agent to collect data!\n")
        return
    
    print("\n" + "="*70)
    print(" 📊 BUDGET AGENT USAGE ANALYSIS ".center(70))
    print("="*70 + "\n")
    
    # Basic stats
    total_questions = len(logs)
    successful = sum(1 for log in logs if log.get('success', False))
    failed = total_questions - successful
    success_rate = (successful / total_questions * 100) if total_questions > 0 else 0
    
    print(f"📈 OVERALL STATISTICS:")
    print(f"   Total Questions: {total_questions}")
    print(f"   Successful:      {successful} ({success_rate:.1f}%)")
    print(f"   Failed:          {failed} ({100-success_rate:.1f}%)")
    
    # Time range
    if logs:
        timestamps = [datetime.fromisoformat(log['timestamp']) for log in logs]
        first_use = min(timestamps)
        last_use = max(timestamps)
        days_active = (last_use - first_use).days + 1
        
        print(f"\n📅 TIME RANGE:")
        print(f"   First use:  {first_use.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Last use:   {last_use.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Days active: {days_active}")
        print(f"   Avg questions/day: {total_questions/days_active:.1f}")
    
    # Question types
    question_types = Counter(log.get('question_type', 'unknown') for log in logs)
    print(f"\n🏷️  QUESTION TYPES (what you ask most):")
    for qtype, count in question_types.most_common():
        percentage = (count / total_questions * 100)
        bar = "█" * int(percentage / 2)
        print(f"   {qtype:20s}: {count:3d} ({percentage:5.1f}%) {bar}")
    
    # Handler distribution
    handlers = Counter(log.get('handler', 'unknown') for log in logs)
    print(f"\n⚙️  HANDLERS USED:")
    for handler, count in handlers.most_common():
        percentage = (count / total_questions * 100)
        print(f"   {handler:20s}: {count:3d} ({percentage:5.1f}%)")
    
    # Entity analysis
    print(f"\n🔍 ENTITY USAGE (what you ask about):")
    
    months_asked = []
    categories_asked = []
    
    for log in logs:
        entities = log.get('entities', {})
        if entities.get('month'):
            months_asked.append(entities['month'])
        if entities.get('months'):
            months_asked.extend(entities['months'])
        if entities.get('category'):
            categories_asked.append(entities['category'])
    
    if months_asked:
        print(f"\n   Most queried months:")
        for month, count in Counter(months_asked).most_common(5):
            print(f"      {month}: {count} times")
    
    if categories_asked:
        print(f"\n   Most queried categories:")
        for cat, count in Counter(categories_asked).most_common(5):
            print(f"      {cat}: {count} times")
    
    # Failed questions (most important for improvement!)
    failed_logs = [log for log in logs if not log.get('success', False)]
    
    if failed_logs:
        print(f"\n❌ FAILED QUESTIONS (opportunities for improvement):")
        print(f"   Total failures: {len(failed_logs)}")
        
        # Group similar failures
        failed_questions = [log['question'] for log in failed_logs]
        failed_counter = Counter(failed_questions)
        
        print(f"\n   Top 10 failed questions:")
        for i, (question, count) in enumerate(failed_counter.most_common(10), 1):
            print(f"   {i:2d}. [{count}x] {question[:60]}...")
        
        # Analyze failure patterns
        print(f"\n   Failed question types:")
        failed_types = Counter(log.get('question_type', 'unknown') for log in failed_logs)
        for qtype, count in failed_types.most_common(5):
            print(f"      {qtype}: {count} failures")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    recommendations = []
    
    # Check for repeated failures
    if failed_logs:
        failed_questions = [log['question'] for log in failed_logs]
        repeated_failures = [q for q, c in Counter(failed_questions).items() if c >= 2]
        
        if repeated_failures:
            recommendations.append(
                f"❗ {len(repeated_failures)} questions failed multiple times - add Python patterns for these"
            )
    
    # Check for pattern opportunities
    if len(months_asked) > len(set(months_asked)) * 2:
        recommendations.append(
            "✨ You frequently ask about specific months - consider adding month shortcuts"
        )
    
    if len(categories_asked) > len(set(categories_asked)) * 2:
        recommendations.append(
            "✨ You frequently ask about specific categories - consider adding category shortcuts"
        )
    
    # Check success rate by type
    for qtype in question_types:
        type_logs = [log for log in logs if log.get('question_type') == qtype]
        type_success = sum(1 for log in type_logs if log.get('success', False))
        type_rate = (type_success / len(type_logs) * 100) if type_logs else 0
        
        if type_rate < 50 and len(type_logs) >= 3:
            recommendations.append(
                f"⚠️  '{qtype}' questions have low success rate ({type_rate:.0f}%) - needs improvement"
            )
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print(f"   ✅ Everything looks good! Keep using the agent to collect more data.")
    
    print("\n" + "="*70 + "\n")

def show_recent_questions(logs, n=10):
    """Show recent questions for context"""
    if not logs:
        return
    
    print(f"📋 LAST {n} QUESTIONS:")
    for log in logs[-n:]:
        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%m-%d %H:%M')
        question = log['question'][:50]
        status = "✅" if log.get('success') else "❌"
        qtype = log.get('question_type', '?')
        print(f"   {timestamp} {status} [{qtype:12s}] {question}...")
    print()

def main():
    """Main analysis function"""
    logs = load_logs()
    
    if logs:
        analyze_patterns(logs)
        show_recent_questions(logs, n=10)
        
        print("💾 Log file location: data/usage_log.jsonl")
        print(f"📊 Analyzed {len(logs)} interactions\n")
    else:
        print("\n💡 TIP: Start using the AI Chat feature to generate usage data.")
        print("   The agent will automatically log your questions and identify patterns.\n")

if __name__ == '__main__':
    main()

