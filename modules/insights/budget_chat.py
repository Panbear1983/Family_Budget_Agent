"""
Budget Chat - Main chat module integrating all insights components
"""

from typing import Dict, Any
import re
from core.base_module import BaseModule
from .data_loader import DataLoader
from .visual_report_generator import VisualReportGenerator
from .terminal_graphs import TerminalGraphGenerator
from .gui_graphs import GUIGraphGenerator
from .insight_generator import InsightGenerator
from .trend_analyzer import TrendAnalyzer
import config

class BudgetChat(BaseModule):
    """Main Budget Chat module - integrates all insight components"""
    
    def _setup(self):
        """Initialize all sub-components"""
        # Support both budget_file and data_loader parameters
        budget_file = self.config.get('budget_file')
        data_loader = self.config.get('data_loader')
        
        if data_loader:
            # Use provided data loader (e.g., MultiYearDataLoader)
            self.data_loader = data_loader
        elif budget_file:
            # Fallback to creating DataLoader from budget_file
            self.data_loader = DataLoader(budget_file)
        else:
            raise ValueError("Either 'budget_file' or 'data_loader' required in config")
        
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
            'show_full_monthly_view': self.show_full_monthly_view,
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
    
    def _detect_response_language(self, question: str) -> str:
        """Detect the desired response language (English or Traditional Chinese)."""
        if re.search(r'[\u4e00-\u9fff]', question):
            return 'zh-traditional'
        return 'en'
    
    def _extract_month_mentions(self, question: str, month_order: list) -> list:
        """Extract month keys referenced in the user's question."""
        if not month_order:
            return []
        
        chinese_months = ['一月', '二月', '三月', '四月', '五月', '六月',
                          '七月', '八月', '九月', '十月', '十一月', '十二月']
        english_months = ['january', 'february', 'march', 'april', 'may', 'june',
                          'july', 'august', 'september', 'october', 'november', 'december']
        
        mentions = []
        lower_question = question.lower()
        
        for key in month_order:
            month_name = key.split('-', 1)[1] if '-' in key else key
            # Direct Chinese month name match
            if month_name in question:
                mentions.append(key)
                continue
            # Numeric month reference in Chinese (e.g., 8月)
            if month_name in chinese_months:
                idx = chinese_months.index(month_name) + 1
                if f'{idx}月' in question or f'{idx} 月' in question:
                    mentions.append(key)
                    continue
            # English month references
            for en_idx, en_month in enumerate(english_months):
                if en_month in lower_question and en_idx < len(chinese_months):
                    if month_name == chinese_months[en_idx]:
                        mentions.append(key)
                        break
        # Deduplicate while preserving order
        seen = set()
        result = []
        for key in mentions:
            if key not in seen:
                seen.add(key)
                result.append(key)
        return result
    
    def _format_currency(self, amount: float) -> str:
        try:
            return f"{amount:,.0f}"
        except Exception:
            return str(amount)
    
    def _format_month_summary(self, key: str, data: dict, language: str) -> str:
        """Create a short textual summary for a single month."""
        month_name = key.split('-', 1)[1] if '-' in key else key
        total = float(data.get('total', 0.0))
        transaction_count = data.get('transaction_count', 0)
        categories = data.get('categories', {}) or {}
        has_data = data.get('has_data', False)
        top_categories = sorted(categories.items(), key=lambda item: item[1], reverse=True)[:3]
        
        if language == 'zh-traditional':
            if not has_data:
                return f"{month_name}尚未紀錄任何交易。"
            parts = [f"{month_name}總支出 NT${self._format_currency(total)}，共 {transaction_count} 筆交易。"]
            if top_categories:
                cat_parts = [f"{cat} NT${self._format_currency(amount)}" for cat, amount in top_categories]
                parts.append("主要支出類別：" + "、".join(cat_parts) + "。")
            else:
                parts.append("目前沒有分類明細。")
            return " ".join(parts)
        else:
            if not has_data:
                return f"{month_name} has no recorded transactions yet."
            parts = [f"{month_name}: total spend NT${self._format_currency(total)} across {transaction_count} transactions."]
            if top_categories:
                cat_parts = [f"{cat} NT${self._format_currency(amount)}" for cat, amount in top_categories]
                parts.append("Top categories: " + ", ".join(cat_parts) + ".")
            else:
                parts.append("Category breakdown is currently unavailable.")
            return " ".join(parts)
    
    def _format_comparison_summary(self, comparison: dict, language: str) -> str:
        """Create a short textual summary comparing two months."""
        if not comparison:
            return ""
        month1 = comparison.get('month1', '')
        month2 = comparison.get('month2', '')
        total1 = comparison.get('total1', 0)
        total2 = comparison.get('total2', 0)
        change = comparison.get('total_change', 0)
        change_str = self._format_currency(change)
        total1_str = self._format_currency(total1)
        total2_str = self._format_currency(total2)
        
        if language == 'zh-traditional':
            direction = "增加" if change >= 0 else "減少"
            return (f"{month1}總額 NT${total1_str}，{month2}總額 NT${total2_str}，"
                    f"{month2}較{month1}{direction} NT${change_str}。")
        else:
            direction = "up" if change >= 0 else "down"
            return (f"{month1} total NT${total1_str}; {month2} total NT${total2_str} "
                    f"({direction} NT${change_str} from {month1}).")
    
    def chat(self, question: str) -> str:
        """Main chat interface"""
        # Load fresh data with rolling 12-month window (force reload to get latest Excel data)
        all_data = self.data_loader.load_all_data(force_reload=True, use_rolling_window=True)
        stats = self.data_loader.get_summary_stats()

        # Build structured month rollup for GPT to reference
        monthly_rollup = {}
        recent_months = []
        consultant_flags = {}
        comparison_summary = {}
        months_with_data = []
        months_without_data = []
        month_order = []
        latest_month_with_data = None
        previous_month_with_data = None

        rollup = {}

        response_language = self._detect_response_language(question)

        if hasattr(self.data_loader, 'build_monthly_rollup'):
            try:
                rollup = self.data_loader.build_monthly_rollup(limit_months=12)
                monthly_rollup = rollup.get('by_month', {})
                month_order = rollup.get('month_order', []) or list(monthly_rollup.keys())
                rolling_totals = rollup.get('rolling_totals', {})
                months_with_data = rollup.get('months_with_data', [])
                months_without_data = rollup.get('months_without_data', [])

                # Keep the most recent 6 months (even if empty) to control prompt size
                if month_order:
                    recent_months = month_order[-6:]

                category_averages = rolling_totals.get('category_averages', {})
                average_total = rolling_totals.get('average_total', 0)

                if months_with_data:
                    latest_month_with_data = months_with_data[-1]
                    previous_month_with_data = months_with_data[-2] if len(months_with_data) > 1 else None

                if latest_month_with_data:
                    latest_data = monthly_rollup.get(latest_month_with_data, {})
                    previous_data = monthly_rollup.get(previous_month_with_data, {}) if previous_month_with_data else {}

                    latest_total = float(latest_data.get('total', 0))
                    previous_total = float(previous_data.get('total', 0)) if previous_data else 0.0
                    total_delta = latest_total - previous_total

                    comparison_summary = {
                        'latest_month_key': latest_month_with_data,
                        'previous_month_key': previous_month_with_data,
                        'latest_total': latest_total,
                        'previous_total': previous_total,
                        'delta_total': total_delta,
                        'rolling_average_total': average_total
                    }

                    alerts = []
                    latest_categories = latest_data.get('categories', {})
                    previous_categories = previous_data.get('categories', {}) if previous_data else {}

                    for category, latest_amount in latest_categories.items():
                        latest_amount = float(latest_amount)
                        rolling_avg = float(category_averages.get(category, 0)) if category_averages else 0.0
                        prev_amount = float(previous_categories.get(category, 0)) if previous_categories else 0.0

                        delta_vs_prev = latest_amount - prev_amount
                        delta_vs_avg = (latest_amount - rolling_avg) if rolling_avg else None

                        percent_vs_prev = (delta_vs_prev / prev_amount) if prev_amount else None
                        percent_vs_avg = (delta_vs_avg / rolling_avg) if (rolling_avg and delta_vs_avg is not None) else None

                        status = None
                        trigger_reason = None

                        if percent_vs_avg is not None and percent_vs_avg >= 0.2:
                            status = 'above_average'
                            trigger_reason = 'above rolling average'
                        elif percent_vs_avg is not None and percent_vs_avg <= -0.25:
                            status = 'below_average'
                            trigger_reason = 'below rolling average'
                        elif percent_vs_prev is not None and percent_vs_prev >= 0.2:
                            status = 'spike_vs_previous'
                            trigger_reason = 'spike vs previous month'
                        elif percent_vs_prev is not None and percent_vs_prev <= -0.25:
                            status = 'drop_vs_previous'
                            trigger_reason = 'drop vs previous month'

                        if status:
                            alerts.append({
                                'category': category,
                                'status': status,
                                'reason': trigger_reason,
                                'latest_amount': latest_amount,
                                'previous_amount': prev_amount,
                                'rolling_average_amount': rolling_avg,
                                'delta_vs_previous': delta_vs_prev,
                                'delta_vs_average': delta_vs_avg,
                                'percent_vs_previous': percent_vs_prev,
                                'percent_vs_average': percent_vs_avg
                            })

                    consultant_flags = {
                        'latest_month_key': latest_month_with_data,
                        'alerts': alerts,
                        'rolling_average_total': average_total,
                        'previous_month_key': previous_month_with_data
                    }
                else:
                    consultant_flags = {
                        'latest_month_key': None,
                        'alerts': [],
                        'rolling_average_total': rolling_totals.get('average_total', 0),
                        'note': 'No months with transactions yet.'
                    }
            except Exception as exc:
                consultant_flags = {
                    'error': f'Failed to build monthly rollup: {exc}'
                }
        
        months_of_interest = self._extract_month_mentions(question, month_order)
        if not months_of_interest and latest_month_with_data:
            months_of_interest = [latest_month_with_data]
        if not months_of_interest and month_order:
            months_of_interest = month_order[-1:]
        
        precomputed_views = {}
        if monthly_rollup:
            summary_lines = []
            for key in months_of_interest:
                month_data = monthly_rollup.get(key, {})
                summary_lines.append(self._format_month_summary(key, month_data, response_language))
            precomputed_views['monthly_keys'] = months_of_interest
            precomputed_views['monthly_summaries'] = "\n".join(summary_lines)
        
        if months_of_interest and len(months_of_interest) >= 2:
            comparison_data = self.insight_generator.generate_comparison(months_of_interest[0], months_of_interest[1])
            comparison_summary = comparison_data
            precomputed_views['comparison'] = comparison_data
            precomputed_views['comparison_summary'] = self._format_comparison_summary(comparison_data, response_language)
        elif comparison_summary:
            precomputed_views['comparison'] = comparison_summary
            precomputed_views['comparison_summary'] = self._format_comparison_summary(comparison_summary, response_language)
        else:
            precomputed_views['comparison_summary'] = ""

        if months_of_interest:
            daily_category_summaries = {}
            for key in months_of_interest:
                daily_category_summaries[key] = self.insight_generator.generate_daily_category_summary(key)
            precomputed_views['daily_category_summaries'] = daily_category_summaries
        
        # Build enriched data for LLM with proper labeling to prevent hallucination
        # Preserves keyword structure for data access (months, categories, etc.)
        enriched_data = {
            'stats': stats,  # Statistics from Excel file
            'available_months': list(all_data.keys()),  # List of months with data (format: "2025-七月", "2025-八月", etc.)
            'data_source': 'Annual Excel Budget File',  # Explicit source label
            'data_summary': f"Data from {len(all_data)} months in Excel file",  # Summary label
            # Add category labels for easy reference (preserves Chinese category names)
            'categories': ['交通费', '伙食费', '休闲/娱乐', '家务', '其它'] if stats else [],
            # Add month names for easy reference (preserves Chinese month names)
            'month_names': ['一月', '二月', '三月', '四月', '五月', '六月', 
                           '七月', '八月', '九月', '十月', '十一月', '十二月'],
            'response_language': response_language,
            'requested_months': months_of_interest
        }
        
        if monthly_rollup:
            enriched_data['monthly_rollup'] = monthly_rollup
        if recent_months:
            enriched_data['recent_months'] = recent_months

        if rollup:
            enriched_data['rolling_totals'] = rollup.get('rolling_totals', {})

        if consultant_flags:
            enriched_data['consultant_flags'] = consultant_flags

        if comparison_summary:
            enriched_data['comparison_summary'] = comparison_summary

        if month_order:
            enriched_data['month_order'] = month_order
        if months_with_data is not None:
            enriched_data['months_with_data'] = months_with_data
        if months_without_data is not None:
            enriched_data['months_without_data'] = months_without_data
        if latest_month_with_data is not None:
            enriched_data['latest_month_with_data'] = latest_month_with_data
        if previous_month_with_data is not None:
            enriched_data['previous_month_with_data'] = previous_month_with_data
        if precomputed_views:
            enriched_data['precomputed_views'] = precomputed_views

        # Add category breakdown if available in stats
        if stats and 'by_category' in stats:
            enriched_data['by_category'] = stats['by_category']  # Spending breakdown by category
        
        # Add monthly totals if available
        if stats and 'monthly_totals' in stats:
            enriched_data['monthly_totals'] = stats['monthly_totals']  # Total spending per month
        
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
        # Try to load with full key first (for MultiYearDataLoader), then fallback to month name
        df = None
        if hasattr(self.data_loader, 'load_all_data'):
            all_data = self.data_loader.load_all_data()
            # Try full key first
            if month in all_data:
                df = all_data[month]
            # Fallback to month name
            elif month_name in all_data:
                df = all_data[month_name]
        if df is None:
            df = self.data_loader.load_month(month_name)
        self.visual_report.show_monthly_table(month, df)
    
    def show_full_monthly_view(self, month: str) -> None:
        """Show full Excel monthly view (like View Budget module)"""
        # Extract month name from format like "2025-九月" -> "九月"
        month_name = month.split('-')[1] if '-' in month else month
        
        # Get the file path from the data loader
        file_path = None
        if hasattr(self.data_loader, 'budget_files') and self.data_loader.budget_files:
            # MultiYearDataLoader - find the file that contains this month
            # Extract year from month key if available (e.g., "2025-九月" -> 2025)
            if '-' in month:
                year_str = month.split('-')[0]
                try:
                    year = int(year_str)
                    # Find the file that matches this year
                    for file in self.data_loader.budget_files:
                        import os
                        filename = os.path.basename(file)
                        if filename.startswith(str(year)):
                            file_path = file
                            break
                except ValueError:
                    pass
            
            # If not found by year, use the first file
            if not file_path and self.data_loader.budget_files:
                file_path = self.data_loader.budget_files[0]
        elif hasattr(self.data_loader, 'budget_file'):
            # Single DataLoader
            file_path = self.data_loader.budget_file
        else:
            # Fallback to config
            file_path = config.BUDGET_PATH
        
        # Display the full monthly sheet view
        if file_path:
            try:
                from utils.view_sheets import display_monthly_sheet_from_file
                display_monthly_sheet_from_file(file_path, month_name)
            except Exception as e:
                print(f"❌ 無法顯示完整視圖: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to simple table view
                self.show_monthly_table(month)
        else:
            print("❌ 無法找到預算檔案")
            # Fallback to simple table view
            self.show_monthly_table(month)
    
    def show_category_table(self, month: str) -> None:
        """Show category breakdown table"""
        # Extract month name from format like "2025-九月" -> "九月"
        month_name = month.split('-')[1] if '-' in month else month
        # For MultiYearDataLoader, use the full key if available
        month_key = month if '-' in month else month_name
        insights = self.insight_generator.generate_monthly_insights(month_key)
        self.visual_report.show_category_breakdown_table(insights)
    
    def show_comparison_table(self, month1: str, month2: str) -> str:
        """Show comparison table"""
        # Extract month names from keys (e.g., "2025-二月" -> "二月")
        month1_name = month1.split('-')[1] if '-' in month1 else month1
        month2_name = month2.split('-')[1] if '-' in month2 else month2
        
        try:
            # Try to load with full key first (for MultiYearDataLoader), then fallback to month name
            df1 = None
            df2 = None
            
            if hasattr(self.data_loader, 'load_all_data'):
                all_data = self.data_loader.load_all_data()
                # Try full key first
                if month1 in all_data:
                    df1 = all_data[month1]
                elif month1_name in all_data:
                    df1 = all_data[month1_name]
                if month2 in all_data:
                    df2 = all_data[month2]
                elif month2_name in all_data:
                    df2 = all_data[month2_name]
            
            # Fallback to load_month if not found
            if df1 is None:
                df1 = self.data_loader.load_month(month1_name)
            if df2 is None:
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
            # Pass full month keys to generate_comparison (handles both "2025-二月" and "二月" formats)
            comparison = self.insight_generator.generate_comparison(month1, month2)
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
            # Pass full month keys to generate_comparison (handles both "2025-二月" and "二月" formats)
            comparison = self.insight_generator.generate_comparison(month1, month2)
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

