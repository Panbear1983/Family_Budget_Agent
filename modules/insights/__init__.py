"""
Budget Insights Module
Provides intelligent chat, insights, and analysis with visual capabilities
"""

from .budget_chat import BudgetChat
from .qwen_chat import QwenChat
from .visual_report_generator import VisualReportGenerator
from .terminal_graphs import TerminalGraphGenerator
from .gui_graphs import GUIGraphGenerator

__all__ = [
    'BudgetChat',
    'QwenChat',
    'VisualReportGenerator',
    'TerminalGraphGenerator',
    'GUIGraphGenerator'
]

