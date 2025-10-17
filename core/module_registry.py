"""
Module Registry - Dynamic module loading and management
"""

import importlib
import inspect
from typing import Dict, Type, Optional
from .base_module import BaseModule

class ModuleRegistry:
    """Centralized registry for all modules"""
    
    def __init__(self):
        self.modules: Dict[str, Type[BaseModule]] = {}
        self.instances: Dict[str, BaseModule] = {}
        self.config = {}
    
    def register(self, name: str, module_class: Type[BaseModule]):
        """Register a module class"""
        if not issubclass(module_class, BaseModule):
            raise TypeError(f"{module_class} must inherit from BaseModule")
        
        self.modules[name] = module_class
        print(f"✅ Registered module: {name}")
    
    def get_module(self, name: str, config: Dict = None) -> Optional[BaseModule]:
        """
        Get module instance (creates if doesn't exist)
        """
        # Return existing instance if available
        if name in self.instances:
            return self.instances[name]
        
        # Create new instance
        if name not in self.modules:
            print(f"❌ Module '{name}' not found in registry")
            return None
        
        module_class = self.modules[name]
        module_config = config or self.config.get(name, {})
        
        try:
            instance = module_class(module_config)
            if instance.initialize():
                self.instances[name] = instance
                return instance
            else:
                return None
        except Exception as e:
            print(f"❌ Failed to create {name}: {e}")
            return None
    
    def auto_discover(self, package_name: str):
        """
        Auto-discover and register modules from a package
        """
        try:
            package = importlib.import_module(package_name)
            package_path = package.__path__[0]
            
            # Find all module files
            import os
            for root, dirs, files in os.walk(package_path):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        # Import module
                        module_path = os.path.join(root, file)
                        relative_path = os.path.relpath(module_path, package_path)
                        module_name = relative_path.replace(os.sep, '.').replace('.py', '')
                        
                        full_module_name = f"{package_name}.{module_name}"
                        
                        try:
                            mod = importlib.import_module(full_module_name)
                            
                            # Find BaseModule subclasses
                            for name, obj in inspect.getmembers(mod, inspect.isclass):
                                if issubclass(obj, BaseModule) and obj != BaseModule:
                                    self.register(name, obj)
                        except Exception as e:
                            print(f"⚠️  Could not import {full_module_name}: {e}")
        
        except Exception as e:
            print(f"❌ Auto-discovery failed for {package_name}: {e}")
    
    def list_modules(self):
        """List all registered modules"""
        print("\n📋 Registered Modules:")
        for name, module_class in self.modules.items():
            status = "🟢" if name in self.instances else "⚪"
            print(f"  {status} {name} ({module_class.__module__})")
    
    def reload_module(self, name: str):
        """Reload a module (useful for development)"""
        if name in self.instances:
            self.instances[name].cleanup()
            del self.instances[name]
        
        # Get new instance
        return self.get_module(name)

# Global registry instance
registry = ModuleRegistry()

