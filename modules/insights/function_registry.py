"""
Function Registry - Maps intents to existing functions
Simplified chatbot architecture using Qwen 8B for intent routing
"""

from typing import Dict, List, Callable, Any
import sys
import os

# Add utils to path for function imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'utils'))

class FunctionRegistry:
    """Registry for mapping intents to existing functions"""
    
    def __init__(self):
        self.functions = {}
        self.intent_mappings = {}
        self.data_loader = None
        self._register_core_functions()
    
    def _register_core_functions(self):
        """Register core visualization and table functions"""
        
        # Import existing functions
        try:
            from utils.view_sheets import display_monthly_sheet_from_file, display_annual_summary
            from modules.insights.visual_report_generator import VisualReportGenerator
            from modules.insights.terminal_graphs import TerminalGraphGenerator
            from modules.insights.gui_graphs import GUIGraphGenerator
            
            # Register table functions
            self.functions['display_monthly_sheet'] = display_monthly_sheet_from_file
            self.functions['display_annual_summary'] = display_annual_summary
            
            # Register visual report functions with data loading wrappers
            self.visual_reporter = VisualReportGenerator()
            self.functions['show_monthly_table'] = self._show_monthly_table_wrapper
            self.functions['show_category_breakdown'] = self._show_category_breakdown_wrapper
            self.functions['show_category_table'] = self._show_category_breakdown_wrapper  # Alias
            self.functions['show_comparison_table'] = self._show_comparison_table_wrapper
            self.functions['show_yearly_summary'] = self._show_yearly_summary_wrapper
            self.functions['show_yearly_table'] = self._show_yearly_summary_wrapper  # Alias
            self.functions['show_trend_table'] = self._show_trend_table_wrapper
            
            # Register terminal graph functions
            self.terminal_graphs = TerminalGraphGenerator(None)  # Will be set with data_loader
            self.functions['plot_monthly_bar'] = self._plot_monthly_bar_terminal
            self.functions['plot_category_horizontal_bar'] = self._plot_category_horizontal_bar_terminal
            self.functions['plot_trend_line'] = self._plot_trend_line_terminal
            self.functions['plot_comparison_bars'] = self._plot_comparison_bars_terminal
            self.functions['plot_stacked_trend'] = self._plot_stacked_trend_terminal
            
            # Register GUI graph functions
            self.gui_graphs = GUIGraphGenerator(None)  # Will be set with data_loader
            self.functions['plot_pie_chart'] = self._plot_pie_chart_gui
            self.functions['plot_donut_chart'] = self._plot_donut_chart_gui
            
            # Add wrapper functions for the visual analysis menu
            self.functions['plot_gui'] = self._plot_gui_wrapper
            self.functions['plot_terminal'] = self._plot_terminal_wrapper
            
            # Add menu routing function
            self.functions['menu_routing'] = self._menu_routing_wrapper
            
            # Add chart options menu function
            self.functions['chart_options_menu'] = self._chart_options_menu_wrapper
            
        except ImportError as e:
            print(f"Warning: Could not import some functions: {e}")
        
        # Define intent mappings
        self.intent_mappings = {
            'data_query': [
                'show_monthly_table',
                'display_monthly_sheet',
                'show_category_breakdown'
            ],
            'budget_analysis': [
                'show_category_breakdown',
                'show_yearly_summary',
                'display_annual_summary'
            ],
            'visualization': [
                'plot_pie_chart',
                'plot_category_horizontal_bar',
                'plot_monthly_bar'
            ],
            'comparison': [
                'show_comparison_table',
                'plot_comparison_bars'
            ],
            'trend': [
                'plot_trend_line',
                'show_trend_table',
                'plot_stacked_trend'
            ],
            'instant_answer': [
                'show_monthly_table',
                'show_category_breakdown'
            ],
            'menu_routing': [
                'menu_routing'
            ],
            'chart_options': [
                'chart_options_menu'
            ]
        }
    
    def set_data_loader(self, data_loader):
        """Set data loader for graph generators"""
        self.data_loader = data_loader
        if hasattr(self, 'terminal_graphs'):
            self.terminal_graphs.data_loader = data_loader
        if hasattr(self, 'gui_graphs'):
            self.gui_graphs.data_loader = data_loader
    
    def _plot_gui_wrapper(self, chart_type, *args):
        """Wrapper function for GUI plotting with different chart types"""
        if not hasattr(self, 'gui_graphs') or not self.gui_graphs:
            return "❌ GUI graph generator not available"
        
        if not self.data_loader:
            return "❌ Data loader not available"
        
        try:
            if chart_type == 'pie':
                # args[0] should be month
                month = args[0] if args and args[0] is not None else '七月'
                df = self.data_loader.load_month(month)
                category_totals = df.groupby('category')['amount'].sum().to_dict()
                summary = {
                    'month': month,
                    'category_breakdown': category_totals,
                    'total_spending': df['amount'].sum()
                }
                return self.gui_graphs.plot_pie_chart(summary)
            elif chart_type == 'donut':
                # Create yearly summary for donut chart
                available_months = self.data_loader.get_available_months()
                monthly_trend = {}
                category_breakdown = {}
                
                for month in available_months:
                    df = self.data_loader.load_month(month)
                    amount = df['amount'].sum()
                    monthly_trend[month] = amount
                    
                    # Aggregate category data
                    month_categories = df.groupby('category')['amount'].sum()
                    for cat, cat_amount in month_categories.items():
                        category_breakdown[cat] = category_breakdown.get(cat, 0) + cat_amount
                
                summary = {
                    'monthly_trend': monthly_trend,
                    'category_breakdown': category_breakdown
                }
                return self.gui_graphs.plot_donut_chart(summary)
            elif chart_type == 'monthly_bar':
                # Create monthly trend data
                available_months = self.data_loader.get_available_months()
                monthly_trend = {}
                for month in available_months:
                    df = self.data_loader.load_month(month)
                    monthly_trend[month] = df['amount'].sum()
                summary = {'monthly_trend': monthly_trend}
                return self.gui_graphs.plot_monthly_bar(summary)
            elif chart_type == 'stacked_area':
                # Create stacked area data with proper structure
                available_months = self.data_loader.get_available_months()
                monthly_trend = {}
                for month in available_months:
                    df = self.data_loader.load_month(month)
                    monthly_trend[month] = df['amount'].sum()
                
                # Create summary with monthly_trend for the chart
                summary = {'monthly_trend': monthly_trend}
                
                # Temporarily add load_all_data method to data_loader if it doesn't exist
                if not hasattr(self.data_loader, 'load_all_data'):
                    def load_all_data():
                        all_data = {}
                        for month in available_months:
                            all_data[month] = self.data_loader.load_month(month)
                        return all_data
                    self.data_loader.load_all_data = load_all_data
                
                return self.gui_graphs.plot_stacked_area(summary)
            elif chart_type == 'trend_line':
                # args[0] should be category
                category = args[0] if args and args[0] is not None else '伙食费'
                available_months = self.data_loader.get_available_months()
                trend_data = []
                for month in available_months:
                    df = self.data_loader.load_month(month)
                    category_df = df[df['category'] == category]
                    amount = category_df['amount'].sum()
                    trend_data.append({'month': month, 'amount': amount})
                return self.gui_graphs.plot_trend_line(trend_data, category)
            elif chart_type == 'comparison':
                # args[0] and args[1] should be month1, month2
                month1 = args[0] if args and len(args) > 0 and args[0] is not None else '七月'
                month2 = args[1] if args and len(args) > 1 and args[1] is not None else '八月'
                
                # Handle both month names and month keys
                if '-' in str(month1):
                    month1 = str(month1).split('-')[1]
                if '-' in str(month2):
                    month2 = str(month2).split('-')[1]
                
                df1 = self.data_loader.load_month(month1)
                df2 = self.data_loader.load_month(month2)
                
                # Create category changes data (same structure as comparison table)
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
                
                comparison = {
                    'month1': month1,
                    'month2': month2,
                    'category_changes': category_changes
                }
                return self.gui_graphs.plot_comparison_grouped_bars(comparison)
            else:
                return f"❌ Unknown GUI chart type: {chart_type}"
        except Exception as e:
            return f"❌ Error plotting GUI {chart_type}: {e}"
    
    def _plot_terminal_wrapper(self, chart_type, *args):
        """Wrapper function for terminal plotting with different chart types"""
        if not hasattr(self, 'terminal_graphs') or not self.terminal_graphs:
            return "❌ Terminal graph generator not available"
        
        if not self.data_loader:
            return "❌ Data loader not available"
        
        try:
            if chart_type == 'category_bar':
                # args[0] should be month
                month = args[0] if args and args[0] is not None else '七月'
                df = self.data_loader.load_month(month)
                category_totals = df.groupby('category')['amount'].sum().to_dict()
                summary = {
                    'month': month,
                    'category_breakdown': category_totals,
                    'total_spending': df['amount'].sum()
                }
                return self.terminal_graphs.plot_category_horizontal_bar(summary)
            elif chart_type == 'monthly_bar':
                # Create monthly trend data
                available_months = self.data_loader.get_available_months()
                monthly_trend = {}
                for month in available_months:
                    df = self.data_loader.load_month(month)
                    monthly_trend[month] = df['amount'].sum()
                summary = {'monthly_trend': monthly_trend}
                return self.terminal_graphs.plot_monthly_bar(summary)
            elif chart_type == 'trend_line':
                # args[0] should be category
                category = args[0] if args and args[0] is not None else '伙食费'
                available_months = self.data_loader.get_available_months()
                trend_data = []
                for month in available_months:
                    df = self.data_loader.load_month(month)
                    category_df = df[df['category'] == category]
                    amount = category_df['amount'].sum()
                    trend_data.append({'month': month, 'amount': amount})
                return self.terminal_graphs.plot_trend_line(trend_data, category)
            elif chart_type == 'comparison':
                # args[0] and args[1] should be month1, month2
                month1 = args[0] if args and len(args) > 0 and args[0] is not None else '七月'
                month2 = args[1] if args and len(args) > 1 and args[1] is not None else '八月'
                
                # Handle both month names and month keys
                if '-' in str(month1):
                    month1 = str(month1).split('-')[1]
                if '-' in str(month2):
                    month2 = str(month2).split('-')[1]
                
                df1 = self.data_loader.load_month(month1)
                df2 = self.data_loader.load_month(month2)
                
                # Create category changes data (same structure as comparison table)
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
                
                comparison = {
                    'month1': month1,
                    'month2': month2,
                    'category_changes': category_changes
                }
                return self.terminal_graphs.plot_comparison_bars(comparison)
            elif chart_type == 'stacked_trend':
                # Create stacked trend data
                available_months = self.data_loader.get_available_months()
                stacked_data = {}
                for month in available_months:
                    df = self.data_loader.load_month(month)
                    category_totals = df.groupby('category')['amount'].sum().to_dict()
                    stacked_data[month] = category_totals
                return self.terminal_graphs.plot_stacked_trend(stacked_data)
            else:
                return f"❌ Unknown terminal chart type: {chart_type}"
        except Exception as e:
            return f"❌ Error plotting terminal {chart_type}: {e}"
    
    def _show_monthly_table_wrapper(self, month: str):
        """Wrapper for show_monthly_table with data loading"""
        if not self.data_loader:
            return "❌ Data loader not available"
        
        # Ensure month is not None
        if month is None:
            month = '七月'  # Default fallback
        
        try:
            df = self.data_loader.load_month(month)
            self.visual_reporter.show_monthly_table(month, df)
            return "✅ Monthly table displayed"
        except Exception as e:
            return f"❌ Error loading monthly data: {e}"
    
    def _show_category_breakdown_wrapper(self, month: str):
        """Wrapper for show_category_breakdown with data loading"""
        if not self.data_loader:
            return "❌ Data loader not available"
        
        # Ensure month is not None
        if month is None:
            month = '七月'  # Default fallback
        
        try:
            # Create a simple insights dict for category breakdown
            df = self.data_loader.load_month(month)
            category_totals = df.groupby('category')['amount'].sum().to_dict()
            insights = {
                'month': month,
                'categories': category_totals,  # Fixed: use 'categories' not 'category_breakdown'
                'total_spending': df['amount'].sum()
            }
            self.visual_reporter.show_category_breakdown_table(insights)
            return "✅ Category breakdown displayed"
        except Exception as e:
            return f"❌ Error loading category data: {e}"
    
    def _show_comparison_table_wrapper(self, month1: str, month2: str):
        """Wrapper for show_comparison_table with data loading"""
        if not self.data_loader:
            return "❌ Data loader not available"
        
        # Ensure months are not None
        if month1 is None:
            month1 = '七月'
        if month2 is None:
            month2 = '八月'
        
        try:
            df1 = self.data_loader.load_month(month1)
            df2 = self.data_loader.load_month(month2)
            
            # Check if data was loaded successfully
            if df1 is None or df2 is None:
                return f"❌ No data available for {month1} or {month2}"
            
            if len(df1) == 0 or len(df2) == 0:
                return f"❌ Empty data for {month1} or {month2}"
            
            # Create category changes data
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
                'month1': month1,
                'month2': month2,
                'category_changes': category_changes,
                'total1': total1,
                'total2': total2,
                'change': total_change
            }
            self.visual_reporter.show_monthly_comparison_table(comparison)
            return "✅ Comparison table displayed"
        except Exception as e:
            return f"❌ Error loading comparison data: {e}"
    
    def _show_yearly_summary_wrapper(self):
        """Wrapper for show_yearly_summary with data loading"""
        if not self.data_loader:
            return "❌ Data loader not available"
        try:
            # Get all available months and create yearly summary
            all_months = self.data_loader.get_available_months()
            # Filter to exclude 2024 data specifically, but allow current and previous year
            available_months = [m for m in all_months if not m.startswith('2024')]
            monthly_trend = {}
            total_spending = 0
            category_breakdown = {}
            
            for month in available_months:
                df = self.data_loader.load_month(month)
                amount = df['amount'].sum()
                monthly_trend[month] = amount
                total_spending += amount
                
                # Aggregate category data
                month_categories = df.groupby('category')['amount'].sum()
                for cat, cat_amount in month_categories.items():
                    category_breakdown[cat] = category_breakdown.get(cat, 0) + cat_amount
            
            avg_monthly_spending = total_spending / len(available_months) if available_months else 0
            
            summary = {
                'monthly_trend': monthly_trend,
                'avg_monthly_spending': avg_monthly_spending,
                'total_spending': total_spending,
                'months_with_data': len(available_months),
                'category_breakdown': category_breakdown
            }
            
            self.visual_reporter.show_yearly_summary_table(summary)
            return "✅ Yearly summary displayed"
        except Exception as e:
            return f"❌ Error loading yearly data: {e}"
    
    def _show_trend_table_wrapper(self, category: str):
        """Wrapper for show_trend_table with data loading"""
        if not self.data_loader:
            return "❌ Data loader not available"
        
        # Ensure category is not None
        if category is None:
            category = '伙食费'  # Default fallback
        
        try:
            # Get trend data for the category
            available_months = self.data_loader.get_available_months()
            trend_data = []
            for month in available_months:
                df = self.data_loader.load_month(month)
                category_df = df[df['category'] == category]
                amount = category_df['amount'].sum()
                trend_data.append({
                    'month': month,
                    'amount': amount
                })
            
            self.visual_reporter.show_trend_table(trend_data, category)
            return "✅ Trend table displayed"
        except Exception as e:
            return f"❌ Error loading trend data: {e}"
    
    # Terminal graph wrapper functions
    def _plot_monthly_bar_terminal(self, *args):
        """Wrapper for terminal monthly bar chart"""
        return self._plot_terminal_wrapper('monthly_bar', *args)
    
    def _plot_category_horizontal_bar_terminal(self, *args):
        """Wrapper for terminal category horizontal bar chart"""
        return self._plot_terminal_wrapper('category_bar', *args)
    
    def _plot_trend_line_terminal(self, *args):
        """Wrapper for terminal trend line chart"""
        return self._plot_terminal_wrapper('trend_line', *args)
    
    def _plot_comparison_bars_terminal(self, *args):
        """Wrapper for terminal comparison bars chart"""
        return self._plot_terminal_wrapper('comparison', *args)
    
    def _plot_stacked_trend_terminal(self, *args):
        """Wrapper for terminal stacked trend chart"""
        return self._plot_terminal_wrapper('stacked_trend', *args)
    
    # GUI graph wrapper functions
    def _plot_pie_chart_gui(self, *args):
        """Wrapper for GUI pie chart"""
        return self._plot_gui_wrapper('pie', *args)
    
    def _plot_donut_chart_gui(self, *args):
        """Wrapper for GUI donut chart"""
        return self._plot_gui_wrapper('donut', *args)
    
    def _menu_routing_wrapper(self, *args):
        """Wrapper for menu routing - provides general menu guidance"""
        return """
🍽️ 我了解您想要查看預算相關資訊！

📍 **請選擇您需要的功能：**

🎯 **查看數據表格：**
   主選單 → [1] 查看預算表
   • 瀏覽每月預算數據
   • 查看詳細交易記錄
   • 年度總覽

🎯 **圖表和視覺化：**
   主選單 → [3] 預算分析對話 → [2] 視覺化分析
   • 圓餅圖、柱狀圖
   • 趨勢分析圖表
   • 比較分析圖表

🎯 **自然語言查詢：**
   主選單 → [3] 預算分析對話 → [1] 智能問答
   • 用自然語言問問題
   • 獲得即時回答

💡 **提示：** 返回主選單按 'x' 即可
"""
    
    def _chart_options_menu_wrapper(self, *args):
        """Wrapper for chart options menu"""
        if not self.data_loader:
            return "❌ Data loader not available"
        
        try:
            # Import the chart options menu function
            from .chat_menus import chart_options_menu
            
            # Get available months and categories
            all_data = self.data_loader.load_all_data()
            available_months = list(all_data.keys())
            
            # Get categories from the first available month
            categories = []
            if available_months:
                first_month_data = all_data[available_months[0]]
                if 'category' in first_month_data.columns:
                    categories = first_month_data['category'].unique().tolist()
            
            # Create a mock chat module for compatibility
            class MockChatModule:
                def __init__(self, function_registry):
                    self.function_registry = function_registry
                
                def execute(self, function_name, *args):
                    return self.function_registry.execute_function(function_name, *args)
            
            mock_chat_module = MockChatModule(self)
            
            # Call the chart options menu
            chart_options_menu(mock_chat_module, available_months, categories)
            
            return "✅ Chart options menu completed"
            
        except Exception as e:
            return f"❌ Error opening chart options menu: {e}"
    
    def get_functions_for_intent(self, intent: str) -> List[str]:
        """Get available functions for an intent"""
        return self.intent_mappings.get(intent, [])
    
    def get_function(self, function_name: str) -> Callable:
        """Get a specific function by name"""
        return self.functions.get(function_name)
    
    def list_all_functions(self) -> Dict[str, str]:
        """List all registered functions with descriptions"""
        descriptions = {
            # Table functions
            'display_monthly_sheet': 'Display monthly sheet with rich formatting',
            'display_annual_summary': 'Display annual budget summary',
            'show_monthly_table': 'Show monthly transactions in rich table',
            'show_category_breakdown': 'Show category spending breakdown',
            'show_category_table': 'Show category spending breakdown (alias)',
            'show_comparison_table': 'Show month-to-month comparison table',
            'show_yearly_summary': 'Show yearly summary table',
            'show_yearly_table': 'Show yearly summary table (alias)',
            'show_trend_table': 'Show trend analysis table',
            
            # Terminal graphs
            'plot_monthly_bar': 'Monthly spending bar chart (terminal)',
            'plot_category_horizontal_bar': 'Category breakdown horizontal bar (terminal)',
            'plot_trend_line': 'Category trend line chart (terminal)',
            'plot_comparison_bars': 'Month comparison bar chart (terminal)',
            'plot_stacked_trend': 'Stacked trend chart (terminal)',
            
            # GUI graphs
            'plot_pie_chart': 'Category breakdown pie chart (GUI)',
            'plot_donut_chart': 'Summary donut chart (GUI)'
        }
        
        return {name: descriptions.get(name, 'No description') 
                for name in self.functions.keys()}
    
    def execute_function(self, function_name: str, *args, **kwargs) -> Any:
        """Execute a function with given parameters"""
        func = self.get_function(function_name)
        if not func:
            raise ValueError(f"Function '{function_name}' not found")
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"
