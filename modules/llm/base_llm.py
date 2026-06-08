"""
Base LLM Interface
All LLM engines must implement this interface
"""

from abc import abstractmethod
from typing import Tuple, Any
from core.base_module import BaseModule

class BaseLLM(BaseModule):
    """Base class for all LLM engines"""

    OLLAMA_URL = 'http://localhost:11434/api/generate'

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.model_name = config.get('model', 'unknown')
        self.timeout = config.get('timeout', 60)
        self.temperature = config.get('temperature', 0.1)
        self.num_ctx = config.get('num_ctx', 4096)
    
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
        """
        Call Ollama via HTTP API (talks to the already-running server — no subprocess startup overhead).
        Retries up to 3 times on empty or failed responses.
        Temperature and num_ctx are passed per-call from instance settings.
        """
        import requests

        payload = {
            'model': self.model_name,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': self.temperature,
                'num_ctx': self.num_ctx,
            }
        }

        last_error = ''
        for attempt in range(3):
            try:
                response = requests.post(
                    self.OLLAMA_URL,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json().get('response', '').strip()
                if result:
                    return result
                last_error = 'empty response'
            except requests.exceptions.Timeout:
                last_error = f"timeout after {self.timeout}s"
            except requests.exceptions.ConnectionError:
                last_error = "Ollama not reachable at localhost:11434 — is it running?"
                break  # No point retrying a connection error
            except Exception as e:
                last_error = str(e)

        return f"ERROR: {last_error}"

