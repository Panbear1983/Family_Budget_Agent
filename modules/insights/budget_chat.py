"""
Budget Chat - Main chat module integrating all insights components
"""

from typing import Dict, Any
from core.base_module import BaseModule
from .data_loader import DataLoader
from .visual_report_generator import VisualReportGenerator
from .terminal_graphs import TerminalGraphGenerator
from .gui_graphs import GUIGraphGenerator
from .insight_generator import InsightGenerator
from .trend_analyzer import TrendAnalyzer

class BudgetChat(BaseModule):
    """Main Budget Chat module - integrates all insight components"""
    
    def _setup(self):
        """Initialize all sub-components"""
        budget_file = self.config.get('budget_file')
        if not budget_file:
            raise ValueError("budget_file required in config")
        
        # Initialize components
        self.data_loader = DataLoader(budget_file)
        
        # Visual components
        self.visual_report = VisualReportGenerator()
        self.terminal_graph = TerminalGraphGenerator(self.data_loader)
        self.gui_graph = GUIGraphGenerator(self.data_loader)
        
        # Analysis components
        self.insight_generator = InsightGenerator(self.data_loader)
        self.trend_analyzer = TrendAnalyzer(self.data_loader)
        
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
        
        # Build enriched data for LLM
        enriched_data = {
            'stats': stats,
            'available_months': list(all_data.keys())
        }
        
        # Use orchestrator to answer
        if self.orchestrator:
            answer = self.orchestrator.answer_question(question, enriched_data)
        else:
            answer = "Error: LLM orchestrator not set"
        
        
        return answer
    
    
    # Visual display methods
    def show_monthly_table(self, month: str) -> None:
        """Show monthly transactions table"""
        # Extract month name from format like "2025-九月" -> "九月"
        month_name = month.split('-')[1] if '-' in month else month
        df = self.data_loader.load_month(month_name)
        self.visual_report.show_monthly_table(month, df)
    
    def show_category_table(self, month: str) -> None:
        """Show category breakdown table"""
        # Extract month name from format like "2025-九月" -> "九月"
        month_name = month.split('-')[1] if '-' in month else month
        insights = self.insight_generator.generate_monthly_insights(month_name)
        self.visual_report.show_category_breakdown_table(insights)
    
    def show_comparison_table(self, month1: str, month2: str) -> str:
        """Show comparison table"""
        # Extract month names from keys (e.g., "2025-二月" -> "二月")
        month1_name = month1.split('-')[1] if '-' in month1 else month1
        month2_name = month2.split('-')[1] if '-' in month2 else month2
        
        try:
            # Load data directly using the same approach as function_registry.py
            df1 = self.data_loader.load_month(month1_name)
            df2 = self.data_loader.load_month(month2_name)
            
            # Check if data was loaded successfully
            if df1 is None or df2 is None:
                return f"❌ No data available for {month1_name} or {month2_name}"
            
            if len(df1) == 0 or len(df2) == 0:
                return f"❌ Empty data for {month1_name} or {month2_name}"
            
            # Create category changes data (same as function_registry.py)
            cat1 = df1.groupby('category')['amount'].sum()
            cat2 = df2.groupby('category')['amount'].sum()
            
            # Get all categories from both months
            all_categories = set(cat1.index) | set(cat2.index)
            category_changes = {}
            
            for cat in all_categories:
                val1 = cat1.get(cat, 0)
                val2 = cat2.get(cat, 0)
                change = val2 - val1
                category_changes[cat] = {
                    'month1': val1,
                    'month2': val2,
                    'change': change
                }
            
            # Calculate totals
            total1 = df1['amount'].sum()
            total2 = df2['amount'].sum()
            total_change = total2 - total1
            
            comparison = {
                'month1': month1_name,
                'month2': month2_name,
                'category_changes': category_changes,
                'total1': total1,
                'total2': total2,
                'change': total_change
            }
            
            self.visual_report.show_monthly_comparison_table(comparison)
            return f"✅ Comparison table displayed for {month1_name} vs {month2_name}"
        except Exception as e:
            return f"❌ Error in comparison: {e}"
    
    def show_yearly_table(self) -> None:
        """Show yearly summary table"""
        summary = self.insight_generator.generate_yearly_summary()
        self.visual_report.show_yearly_summary_table(summary)
    
    def show_trend_table(self, category: str) -> None:
        """Show trend analysis table"""
        trend_result = self.trend_analyzer.analyze_category_trend(category)
        self.visual_report.show_trend_table(trend_result['trend_data'], category)
    
    def plot_terminal(self, chart_type: str, *args, **kwargs) -> str:
        """Plot terminal graph"""
        if chart_type == 'monthly_bar':
            summary = self.insight_generator.generate_yearly_summary()
            return self.terminal_graph.plot_monthly_bar(summary)
        elif chart_type == 'category_bar':
            month = args[0] if args else '七月'
            insights = self.insight_generator.generate_monthly_insights(month)
            return self.terminal_graph.plot_category_horizontal_bar(insights)
        elif chart_type == 'trend_line':
            category = args[0] if args else '伙食费'
            trend_result = self.trend_analyzer.analyze_category_trend(category)
            return self.terminal_graph.plot_trend_line(trend_result['trend_data'], category)
        elif chart_type == 'comparison':
            month1, month2 = args[0], args[1]
            # Extract month names from keys (e.g., "2025-二月" -> "二月")
            month1_name = month1.split('-')[1] if '-' in month1 else month1
            month2_name = month2.split('-')[1] if '-' in month2 else month2
            comparison = self.insight_generator.generate_comparison(month1_name, month2_name)
            return self.terminal_graph.plot_comparison_bars(comparison)
        elif chart_type == 'stacked':
            summary = self.insight_generator.generate_yearly_summary()
            return self.terminal_graph.plot_stacked_trend(summary)
        else:
            return f"❌ Unknown terminal chart type: {chart_type}"
    
    def plot_gui(self, chart_type: str, *args, **kwargs) -> str:
        """Plot GUI graph"""
        if chart_type == 'pie':
            month = args[0] if args else '七月'
            insights = self.insight_generator.generate_monthly_insights(month)
            self.gui_graph.plot_pie_chart(insights)
            return "✅ GUI pie chart displayed"
        elif chart_type == 'donut':
            summary = self.insight_generator.generate_yearly_summary(silent=True)
            self.gui_graph.plot_donut_chart(summary)
            return "✅ GUI donut chart displayed"
        elif chart_type == 'monthly_bar':
            summary = self.insight_generator.generate_yearly_summary(silent=True)
            self.gui_graph.plot_monthly_bar(summary)
            return "✅ GUI monthly bar chart displayed"
        elif chart_type == 'comparison':
            month1, month2 = args[0], args[1]
            # Extract month names from keys (e.g., "2025-二月" -> "二月")
            month1_name = month1.split('-')[1] if '-' in month1 else month1
            month2_name = month2.split('-')[1] if '-' in month2 else month2
            comparison = self.insight_generator.generate_comparison(month1_name, month2_name)
            self.gui_graph.plot_comparison_grouped_bars(comparison)
            return "✅ GUI comparison chart displayed"
        elif chart_type == 'trend_line':
            category = args[0] if args else '伙食费'
            trend_result = self.trend_analyzer.analyze_category_trend(category)
            self.gui_graph.plot_trend_line(trend_result['trend_data'], category)
            return "✅ GUI trend line chart displayed"
        elif chart_type == 'stacked_area':
            summary = self.insight_generator.generate_yearly_summary(silent=True)
            self.gui_graph.plot_stacked_area(summary)
            return "✅ GUI stacked area chart displayed"
        else:
            return f"❌ Unknown GUI chart type: {chart_type}"

