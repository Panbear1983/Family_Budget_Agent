"""
Base LLM Interface
All LLM engines must implement this interface
"""

from abc import abstractmethod
from typing import Tuple, Any
from core.base_module import BaseModule
import subprocess

class BaseLLM(BaseModule):
    """Base class for all LLM engines"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.model_name = config.get('model', 'unknown')
        self.timeout = config.get('timeout', 30)
    
    def execute(self, task: str, *args, **kwargs) -> Any:
        """
        Execute a task using the LLM
        Routes to specific task handlers
        """
        task_map = {
            'categorize': self.categorize,
            'check_duplicate': self.check_duplicate,
            'fuzzy_duplicate': self.fuzzy_duplicate,
            'validate_outlier': self.validate_outlier,
            'calculate_stats': self.calculate_stats,
            'analyze_trends': self.analyze_trends,
            'query': self.query,
            'answer': self.answer,
            'extract_data': self.extract_data,
            'reason': self.reason
        }
        
        handler = task_map.get(task)
        if not handler:
            raise ValueError(f"Unknown task: {task}")
        
        return handler(*args, **kwargs)
    
    # Task handlers (must override in subclasses)
    @abstractmethod
    def categorize(self, transaction: dict) -> Tuple[str, float]:
        """Return (category, confidence)"""
        pass
    
    @abstractmethod
    def call_model(self, prompt: str) -> str:
        """Call the LLM and return response"""
        pass
    
    # Optional task handlers (have defaults, can override)
    def check_duplicate(self, tx1: dict, tx2: dict) -> Tuple[bool, float]:
        """Return (is_duplicate, confidence) - Default implementation"""
        # Simple exact match check
        if tx1.get('date') != tx2.get('date'):
            return False, 1.0
        if abs(float(tx1.get('amount', 0)) - float(tx2.get('amount', 0))) > 1:
            return False, 0.95
        if tx1.get('description') == tx2.get('description'):
            return True, 1.0
        return False, 0.5  # Uncertain, low confidence
    
    def fuzzy_duplicate(self, tx1: dict, tx2: dict) -> Tuple[bool, str]:
        """Return (is_duplicate, reason)"""
        return False, "Not implemented"
    
    def validate_outlier(self, transaction: dict, context: dict) -> Tuple[bool, str]:
        """Return (is_valid, explanation)"""
        return True, "Not implemented"
    
    def calculate_stats(self, data: dict) -> dict:
        """Return statistical summary"""
        return {}
    
    def analyze_trends(self, stats: dict) -> str:
        """Return trend analysis"""
        return ""
    
    def query(self, question: str, data: dict) -> str:
        """Answer simple queries"""
        return ""
    
    def answer(self, question: str, data: dict) -> str:
        """Answer complex questions"""
        return ""
    
    def extract_data(self, question: str, data: dict) -> dict:
        """Extract relevant data"""
        return {}
    
    def reason(self, question: str, data: dict) -> str:
        """Provide reasoning"""
        return ""
    
    def _call_ollama(self, prompt: str) -> str:
        """Helper to call Ollama"""
        try:
            result = subprocess.run(
                ['ollama', 'run', self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return f"ERROR: Timeout after {self.timeout}s"
        except Exception as e:
            return f"ERROR: {str(e)}"

