"""
Budget Insights Module
Provides intelligent chat, insights, and analysis with visual capabilities
"""

from .budget_chat import BudgetChat
from .visual_report_generator import VisualReportGenerator
from .terminal_graphs import TerminalGraphGenerator
from .gui_graphs import GUIGraphGenerator

__all__ = [
    'BudgetChat',
    'VisualReportGenerator',
    'TerminalGraphGenerator',
    'GUIGraphGenerator'
]

