"""
Visual Report Generator - Beautiful tables using Rich
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Dict, List
import pandas as pd

class VisualReportGenerator:
    """Generates beautiful visual reports with Rich tables"""
    
    def __init__(self):
        self.console = Console()
    
    def show_monthly_table(self, month: str, df: pd.DataFrame, limit: int = None) -> None:
        """Display monthly transactions as a rich table"""
        
        table = Table(
            title=f"📊 {month} 交易明細",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
            title_style="bold magenta"
        )
        
        table.add_column("日期", style="dim", width=20)
        table.add_column("分類", style="cyan", width=30)
        table.add_column("金額", justify="right", style="green", width=25)
        
        # Add rows (no truncation - show all data)
        rows_to_show = df if limit is None else df.head(limit)
        for idx, row in rows_to_show.iterrows():
            # Format date to show only date part (remove time)
            date_value = row.get('date', '')
            if hasattr(date_value, 'date'):
                formatted_date = date_value.date()
            else:
                formatted_date = str(date_value).split(' ')[0] if ' ' in str(date_value) else str(date_value)
            
            table.add_row(
                str(formatted_date),  # Date (without time)
                str(row.get('category', '')),  # Category
                f"NT$ {row.get('amount', 0):,.0f}"  # Amount
            )
        
        # No truncation summary - show all data
        self.console.print(table)
    
    def show_category_breakdown_table(self, insights: Dict) -> None:
        """Display category breakdown as a rich table"""
        
        # Handle error case
        if 'error' in insights:
            self.console.print(f"\n[red]❌ {insights['error']}[/red]\n")
            return
        
        table = Table(
            title=f"📂 {insights['month']} 分類支出統計",
            box=box.DOUBLE,
            show_header=True,
            header_style="bold yellow"
        )
        
        table.add_column("分類", style="cyan", width=20)
        table.add_column("金額", justify="right", style="green", width=18)
        table.add_column("占比", justify="right", style="magenta", width=12)
        table.add_column("視覺化", width=40)
        
        total = insights.get('total_spending', 0)
        # Handle both 'categories' and 'category_breakdown' keys for compatibility
        categories_dict = insights.get('categories', {}) or insights.get('category_breakdown', {})
        categories = sorted(
            categories_dict.items(),
            key=lambda x: x[1],
            reverse=True
        ) if categories_dict else []
        
        # If no categories, show a message
        if not categories:
            table.add_row(
                "[dim]無數據[/dim]",
                "[dim]NT$ 0[/dim]",
                "[dim]0%[/dim]",
                "[dim]（此月份尚未有支出記錄）[/dim]"
            )
        else:
            for cat, amount in categories:
                percentage = (amount / total * 100) if total > 0 else 0
                bar_length = int(percentage / 3)  # Scale to fit
                bar = "█" * bar_length
                
                table.add_row(
                    cat,
                    f"NT$ {amount:,.0f}",
                    f"{percentage:.1f}%",
                    f"[green]{bar}[/green]"
                )
        
        # Add total row
        table.add_section()
        table.add_row(
            "[bold]總計[/bold]",
            f"[bold]NT$ {total:,.0f}[/bold]",
            "[bold]100%[/bold]" if total > 0 else "[dim]0%[/dim]",
            ""
        )
        
        self.console.print(table)
    
    def show_monthly_comparison_table(self, comparison: Dict) -> None:
        """Display month-to-month comparison table"""
        
        # Handle error case
        if 'error' in comparison:
            console = Console()
            console.print(f"\n[red]❌ {comparison['error']}[/red]\n")
            return
        
        table = Table(
            title=f"⚖️  {comparison['month1']} vs {comparison['month2']} 對比",
            box=box.HEAVY,
            show_header=True,
            header_style="bold blue"
        )
        
        table.add_column("分類", style="cyan", width=18)
        table.add_column(comparison['month1'], justify="right", width=18)
        table.add_column(comparison['month2'], justify="right", width=18)
        table.add_column("變化", justify="right", width=18)
        table.add_column("趨勢", justify="center", width=10)
        
        for cat, change in sorted(
            comparison['category_changes'].items(),
            key=lambda x: abs(x[1]['change']),
            reverse=True
        ):
            val1 = change['month1']
            val2 = change['month2']
            diff = change['change']
            
            # Determine trend icon
            if diff > 0:
                trend = "📈"
                diff_style = "red"
            elif diff < 0:
                trend = "📉"
                diff_style = "green"
            else:
                trend = "➡️"
                diff_style = "white"
            
            table.add_row(
                cat,
                f"NT$ {val1:,.0f}",
                f"NT$ {val2:,.0f}",
                f"[{diff_style}]{diff:+,.0f}[/{diff_style}]",
                trend
            )
        
        # Summary row
        table.add_section()
        total_change = comparison['change']
        total_style = "red" if total_change > 0 else "green"
        
        table.add_row(
            "[bold]總計[/bold]",
            f"[bold]NT$ {comparison['total1']:,.0f}[/bold]",
            f"[bold]NT$ {comparison['total2']:,.0f}[/bold]",
            f"[bold {total_style}]{total_change:+,.0f}[/bold {total_style}]",
            "📊"
        )
        
        self.console.print(table)
    
    def show_yearly_summary_table(self, summary: Dict) -> None:
        """Display yearly summary with all months"""
        
        # Monthly spending table
        table = Table(
            title="📅 2025 年度月別支出 (僅2025年資料)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("月份", style="cyan", width=10)
        table.add_column("支出金額", justify="right", style="green", width=15)
        table.add_column("視覺化", width=45)
        table.add_column("狀態", justify="center", width=8)
        
        monthly = summary['monthly_trend']
        avg = summary['avg_monthly_spending']
        max_amount = max(monthly.values()) if monthly else 1
        
        # Create a mapping for Chinese month names to their chronological order
        chinese_month_order = {
            '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
            '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
        }
        
        # Sort months chronologically
        def get_month_number(month_key):
            # Extract month name from format like "2025-一月"
            month_name = month_key.split('-')[1] if '-' in month_key else month_key
            return chinese_month_order.get(month_name, 999)
        
        sorted_monthly = sorted(monthly.items(), key=lambda x: get_month_number(x[0]))
        
        for month, amount in sorted_monthly:
            # Scale bar to max spending
            bar_length = int((amount / max_amount) * 35)
            bar = "█" * bar_length
            
            # Status indicator
            if amount > avg * 1.2:
                status = "⚠️"
                style = "red"
            elif amount < avg * 0.8:
                status = "✅"
                style = "green"
            else:
                status = "➡️"
                style = "yellow"
            
            table.add_row(
                month,
                f"NT$ {amount:,.0f}",
                f"[{style}]{bar}[/{style}]",
                status
            )
        
        # Add average line
        table.add_section()
        avg_bar_length = int((avg / max_amount) * 35)
        avg_bar = "█" * avg_bar_length
        table.add_row(
            "[bold]月平均[/bold]",
            f"[bold]NT$ {avg:,.0f}[/bold]",
            f"[bold blue]{avg_bar}[/bold blue]",
            "📊"
        )
        
        self.console.print(table)
        
        # Category summary table
        self.console.print("\n")
        
        cat_table = Table(
            title="📂 年度分類統計",
            box=box.DOUBLE,
            show_header=True,
            header_style="bold yellow"
        )
        
        cat_table.add_column("分類", style="cyan", width=15)
        cat_table.add_column("總金額", justify="right", style="green", width=15)
        cat_table.add_column("占比", justify="right", style="magenta", width=10)
        cat_table.add_column("月均", justify="right", width=15)
        
        total = summary['total_spending']
        months_count = summary['months_with_data']
        
        for cat, amount in sorted(
            summary['category_breakdown'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            percentage = (amount / total * 100) if total > 0 else 0
            monthly_avg = amount / months_count if months_count > 0 else 0
            
            cat_table.add_row(
                cat,
                f"NT$ {amount:,.0f}",
                f"{percentage:.1f}%",
                f"NT$ {monthly_avg:,.0f}"
            )
        
        self.console.print(cat_table)
    
    def show_trend_table(self, trend_data: List[Dict], category: str) -> None:
        """Display trend data as a table"""
        
        table = Table(
            title=f"📈 {category} 趨勢分析",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("月份", style="cyan", width=10)
        table.add_column("金額", justify="right", style="green", width=15)
        table.add_column("趨勢圖", width=40)
        table.add_column("變化", justify="right", width=12)
        
        amounts = [d['amount'] for d in trend_data]
        max_amount = max(amounts) if amounts and max(amounts) > 0 else 1
        
        for i, item in enumerate(trend_data):
            amount = item['amount']
            bar_length = int((amount / max_amount) * 30) if max_amount > 0 else 0
            bar = "█" * bar_length
            
            # Calculate change from previous month
            if i > 0:
                prev_amount = trend_data[i-1]['amount']
                change = amount - prev_amount
                change_pct = (change / prev_amount * 100) if prev_amount > 0 else 0
                change_str = f"{change_pct:+.1f}%"
                change_style = "red" if change > 0 else "green"
            else:
                change_str = "-"
                change_style = "white"
            
            table.add_row(
                item['month'],
                f"NT$ {amount:,.0f}",
                f"[cyan]{bar}[/cyan]",
                f"[{change_style}]{change_str}[/{change_style}]"
            )
        
        self.console.print(table)

