"""
Base Module Interface
All modules inherit from this to ensure consistency
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseModule(ABC):
    """Base class for all modules in the system"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.enabled = True
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the module
        Returns True if successful
        """
        if self._initialized:
            return True
        
        try:
            self._setup()
            self._initialized = True
            return True
        except Exception as e:
            print(f"❌ Failed to initialize {self.name}: {e}")
            return False
    
    def _setup(self):
        """Override this for custom setup logic"""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Main execution method
        Must be implemented by all modules
        """
        raise NotImplementedError(f"{self.name} must implement execute()")
    
    def cleanup(self):
        """Cleanup resources"""
        self._initialized = False
    
    def __str__(self):
        return f"{self.name} v{self.version} ({'enabled' if self.enabled else 'disabled'})"

