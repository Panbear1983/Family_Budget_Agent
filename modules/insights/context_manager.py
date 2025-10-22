"""
Context Manager - Manages conversation history and context
"""

from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json

class ContextManager:
    """Manages conversation context and history"""
    
    def __init__(self, max_history: int = 10):
        self.history: List[Dict] = []
        self.max_history = max_history
        self.session_start = datetime.now()
        self.current_focus = None  # Current month/category being discussed
        
        # Usage logging for pattern learning
        self.log_file = Path("data/usage_log.jsonl")
        self.log_file.parent.mkdir(exist_ok=True)
        print(f"  📊 Usage logging enabled: {self.log_file}")
    
    def add_interaction(self, question: str, answer: str, metadata: Dict = None):
        """Add Q&A to history and log for pattern learning"""
        interaction = {
            'timestamp': datetime.now(),
            'question': question,
            'answer': answer,
            'metadata': metadata or {}
        }
        
        self.history.append(interaction)
        
        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Update focus based on question
        self._update_focus(question)
        
        # Log for pattern learning
        self._log_interaction(question, answer, metadata)
    
    def get_context_summary(self) -> str:
        """Get summary of recent conversation"""
        if not self.history:
            return "New conversation"
        
        recent = self.history[-3:]  # Last 3 interactions
        summary = "Recent topics:\n"
        for item in recent:
            summary += f"- {item['question'][:50]}...\n"
        
        if self.current_focus:
            summary += f"\nCurrent focus: {self.current_focus}"
        
        return summary
    
    def get_relevant_history(self, question: str, limit: int = 3) -> List[Dict]:
        """Get relevant past interactions"""
        # Simple keyword matching for now
        keywords = question.lower().split()
        
        relevant = []
        for item in reversed(self.history):
            q_lower = item['question'].lower()
            if any(kw in q_lower for kw in keywords):
                relevant.append(item)
                if len(relevant) >= limit:
                    break
        
        return relevant
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []
        self.current_focus = None
    
    def _update_focus(self, question: str):
        """Update current focus based on question"""
        months = ['一月', '二月', '三月', '四月', '五月', '六月',
                 '七月', '八月', '九月', '十月', '十一月', '十二月']
        
        for month in months:
            if month in question:
                self.current_focus = month
                return
        
        categories = ['交通费', '伙食费', '休闲/娱乐', '家务', '其它']
        for cat in categories:
            if cat in question:
                self.current_focus = cat
                return
    
    def _log_interaction(self, question: str, answer: str, metadata: Dict = None):
        """Log interaction for pattern learning (append to JSONL file)"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'question': question,
                'answer_preview': answer[:200] if answer else '',  # First 200 chars
                'question_type': metadata.get('type') if metadata else 'unknown',
                'handler': metadata.get('handler') if metadata else 'unknown',
                'entities': metadata.get('entities') if metadata else {},
                'success': self._detect_success(answer)
            }
            
            # Append to JSONL file (one JSON object per line)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        except Exception as e:
            # Don't let logging errors crash the agent
            print(f"  ⚠️  Logging error: {e}")
    
    def _detect_success(self, answer: str) -> bool:
        """Simple heuristic to detect if answer was successful"""
        if not answer:
            return False
        
        # Check for error indicators
        error_indicators = ['error', 'sorry', '抱歉', '无法', '不能', '没有找到', 
                          'not found', 'cannot', "can't", 'unable']
        answer_lower = answer.lower()
        
        return not any(indicator in answer_lower for indicator in error_indicators)

