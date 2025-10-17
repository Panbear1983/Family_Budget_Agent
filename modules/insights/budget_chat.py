"""
Budget Chat - Main chat module integrating all insights components
"""

from typing import Dict, Any
from core.base_module import BaseModule
from .data_loader import DataLoader
from .context_manager import ContextManager
from .insight_generator import InsightGenerator
from .trend_analyzer import TrendAnalyzer
from .report_generator import ReportGenerator
from .visual_report_generator import VisualReportGenerator
from .terminal_graphs import TerminalGraphGenerator
from .gui_graphs import GUIGraphGenerator

class BudgetChat(BaseModule):
    """Main Budget Chat module - integrates all insight components"""
    
    def _setup(self):
        """Initialize all sub-components"""
        budget_file = self.config.get('budget_file')
        if not budget_file:
            raise ValueError("budget_file required in config")
        
        # Initialize components
        self.data_loader = DataLoader(budget_file)
        self.context_manager = ContextManager()
        self.insight_generator = InsightGenerator(self.data_loader)
        self.trend_analyzer = TrendAnalyzer(self.data_loader)
        self.report_generator = ReportGenerator()
        
        # Visual components
        self.visual_report = VisualReportGenerator()
        self.terminal_graph = TerminalGraphGenerator(self.data_loader)
        self.gui_graph = GUIGraphGenerator(self.data_loader)
        
        # LLM orchestrator (set externally)
        self.orchestrator = None
        
        print("✅ Budget Chat module initialized (with visual capabilities)")
    
    def set_orchestrator(self, orchestrator):
        """Set LLM orchestrator"""
        self.orchestrator = orchestrator
    
    def execute(self, task: str, *args, **kwargs) -> Any:
        """Execute chat task"""
        task_map = {
            'chat': self.chat,
            'generate_insight': self.generate_insight,
            'compare_months': self.compare_months,
            'yearly_summary': self.yearly_summary,
            'analyze_trend': self.analyze_trend,
            'forecast': self.forecast,
            # Visual tasks
            'show_monthly_table': self.show_monthly_table,
            'show_category_table': self.show_category_table,
            'show_comparison_table': self.show_comparison_table,
            'show_yearly_table': self.show_yearly_table,
            'show_trend_table': self.show_trend_table,
            # Graph tasks
            'plot_terminal': self.plot_terminal,
            'plot_gui': self.plot_gui
        }
        
        handler = task_map.get(task)
        if not handler:
            raise ValueError(f"Unknown task: {task}")
        
        return handler(*args, **kwargs)
    
    def chat(self, question: str) -> str:
        """Main chat interface"""
        # Load fresh data
        all_data = self.data_loader.load_all_data()
        stats = self.data_loader.get_summary_stats()
        
        # Get conversation context
        context_summary = self.context_manager.get_context_summary()
        relevant_history = self.context_manager.get_relevant_history(question)
        
        # Build enriched data for LLM
        enriched_data = {
            'stats': stats,
            'context': context_summary,
            'history': relevant_history,
            'available_months': list(all_data.keys())
        }
        
        # Use orchestrator to answer
        if self.orchestrator:
            answer = self.orchestrator.answer_question(question, enriched_data)
        else:
            answer = "Error: LLM orchestrator not set"
        
        # Store in context
        self.context_manager.add_interaction(question, answer)
        
        return answer
    
    def generate_insight(self, month: str) -> str:
        """Generate insights for a month"""
        insights = self.insight_generator.generate_monthly_insights(month)
        return self.report_generator.format_monthly_report(insights)
    
    def compare_months(self, month1: str, month2: str) -> str:
        """Compare two months"""
        comparison = self.insight_generator.generate_comparison(month1, month2)
        return self.report_generator.format_comparison(comparison)
    
    def yearly_summary(self) -> str:
        """Generate yearly summary"""
        summary = self.insight_generator.generate_yearly_summary()
        return self.report_generator.format_summary(summary)
    
    def analyze_trend(self, category: str) -> Dict:
        """Analyze trend for category"""
        return self.trend_analyzer.analyze_category_trend(category)
    
    def forecast(self, category: str = None) -> Dict:
        """Forecast next month"""
        return self.trend_analyzer.forecast_next_month(category)
    
    # Visual display methods
    def show_monthly_table(self, month: str) -> None:
        """Show monthly transactions table"""
        df = self.data_loader.load_month(month)
        self.visual_report.show_monthly_table(month, df)
    
    def show_category_table(self, month: str) -> None:
        """Show category breakdown table"""
        insights = self.insight_generator.generate_monthly_insights(month)
        self.visual_report.show_category_breakdown_table(insights)
    
    def show_comparison_table(self, month1: str, month2: str) -> None:
        """Show comparison table"""
        comparison = self.insight_generator.generate_comparison(month1, month2)
        self.visual_report.show_monthly_comparison_table(comparison)
    
    def show_yearly_table(self) -> None:
        """Show yearly summary table"""
        summary = self.insight_generator.generate_yearly_summary()
        self.visual_report.show_yearly_summary_table(summary)
    
    def show_trend_table(self, category: str) -> None:
        """Show trend analysis table"""
        trend_result = self.trend_analyzer.analyze_category_trend(category)
        self.visual_report.show_trend_table(trend_result['trend_data'], category)
    
    def plot_terminal(self, chart_type: str, *args, **kwargs) -> None:
        """Plot terminal graph"""
        if chart_type == 'monthly_bar':
            summary = self.insight_generator.generate_yearly_summary()
            self.terminal_graph.plot_monthly_bar(summary)
        elif chart_type == 'category_bar':
            month = args[0] if args else '七月'
            insights = self.insight_generator.generate_monthly_insights(month)
            self.terminal_graph.plot_category_horizontal_bar(insights)
        elif chart_type == 'trend_line':
            category = args[0] if args else '伙食费'
            trend_result = self.trend_analyzer.analyze_category_trend(category)
            self.terminal_graph.plot_trend_line(trend_result['trend_data'], category)
        elif chart_type == 'comparison':
            month1, month2 = args[0], args[1]
            comparison = self.insight_generator.generate_comparison(month1, month2)
            self.terminal_graph.plot_comparison_bars(comparison)
        elif chart_type == 'stacked':
            summary = self.insight_generator.generate_yearly_summary()
            self.terminal_graph.plot_stacked_trend(summary)
    
    def plot_gui(self, chart_type: str, *args, **kwargs) -> None:
        """Plot GUI graph"""
        if chart_type == 'pie':
            month = args[0] if args else '七月'
            insights = self.insight_generator.generate_monthly_insights(month)
            self.gui_graph.plot_pie_chart(insights)
        elif chart_type == 'donut':
            summary = self.insight_generator.generate_yearly_summary()
            self.gui_graph.plot_donut_chart(summary)
        elif chart_type == 'monthly_bar':
            summary = self.insight_generator.generate_yearly_summary()
            self.gui_graph.plot_monthly_bar(summary)
        elif chart_type == 'comparison':
            month1, month2 = args[0], args[1]
            comparison = self.insight_generator.generate_comparison(month1, month2)
            self.gui_graph.plot_comparison_grouped_bars(comparison)
        elif chart_type == 'trend_line':
            category = args[0] if args else '伙食费'
            trend_result = self.trend_analyzer.analyze_category_trend(category)
            self.gui_graph.plot_trend_line(trend_result['trend_data'], category)
        elif chart_type == 'stacked_area':
            summary = self.insight_generator.generate_yearly_summary()
            self.gui_graph.plot_stacked_area(summary)

