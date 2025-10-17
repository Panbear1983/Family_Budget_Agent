"""
Report Generator - Formats insights into readable reports
"""

from typing import Dict
from rich.console import Console
from rich.table import Table

class ReportGenerator:
    """Generates formatted reports"""
    
    def __init__(self):
        self.console = Console()
    
    def format_monthly_report(self, insights: Dict) -> str:
        """Format monthly insights as report"""
        if 'error' in insights:
            return f"❌ {insights['error']}"
        
        report = f"\n{'='*80}\n"
        report += f"📊 {insights['month']} 月度報告\n"
        report += f"{'='*80}\n\n"
        
        report += f"💰 總支出: NT${insights['total_spending']:,.0f}\n"
        report += f"📝 交易數: {insights['transaction_count']}\n"
        report += f"📊 平均每筆: NT${insights['avg_transaction']:,.0f}\n\n"
        
        if insights['categories']:
            report += "📂 分類支出:\n"
            for cat, amount in sorted(insights['categories'].items(), key=lambda x: x[1], reverse=True):
                pct = (amount / insights['total_spending'] * 100) if insights['total_spending'] > 0 else 0
                report += f"   {cat:12s}: NT${amount:8,.0f} ({pct:5.1f}%)\n"
            report += "\n"
        
        if insights['top_expenses']:
            report += "🔝 前五大支出:\n"
            for i, exp in enumerate(insights['top_expenses'], 1):
                report += f"   {i}. NT${exp['amount']:,.0f} - {exp['description']} ({exp['category']})\n"
            report += "\n"
        
        if insights['warnings']:
            report += "⚠️  注意事項:\n"
            for warning in insights['warnings']:
                report += f"   • {warning}\n"
        
        return report
    
    def format_comparison(self, comparison: Dict) -> str:
        """Format month comparison"""
        if 'error' in comparison:
            return f"❌ {comparison['error']}"
        
        report = f"\n{'='*80}\n"
        report += f"📊 對比分析: {comparison['month1']} vs {comparison['month2']}\n"
        report += f"{'='*80}\n\n"
        
        report += f"{comparison['month1']:6s}: NT${comparison['total1']:,.0f}\n"
        report += f"{comparison['month2']:6s}: NT${comparison['total2']:,.0f}\n"
        report += f"變化: NT${comparison['change']:+,.0f} ({comparison['change_percent']:+.1f}%)\n\n"
        
        if comparison['category_changes']:
            report += "📂 分類變化:\n"
            for cat, change in comparison['category_changes'].items():
                diff = change['change']
                report += f"   {cat:12s}: NT${diff:+8,.0f}\n"
        
        return report
    
    def format_summary(self, summary: Dict) -> str:
        """Format yearly summary"""
        report = f"\n{'='*80}\n"
        report += "📊 年度總覽\n"
        report += f"{'='*80}\n\n"
        
        report += f"💰 總支出: NT${summary['total_spending']:,.0f}\n"
        report += f"📊 月平均: NT${summary['avg_monthly_spending']:,.0f}\n"
        report += f"📝 交易數: {summary['total_transactions']}\n"
        report += f"📅 資料月份: {summary['months_with_data']}\n\n"
        
        report += f"📈 最高月份: {summary['highest_month']['month']} (NT${summary['highest_month']['amount']:,.0f})\n"
        report += f"📉 最低月份: {summary['lowest_month']['month']} (NT${summary['lowest_month']['amount']:,.0f})\n\n"
        
        if summary['category_breakdown']:
            report += "📂 分類總計:\n"
            for cat, amount in sorted(summary['category_breakdown'].items(), key=lambda x: x[1], reverse=True):
                pct = (amount / summary['total_spending'] * 100) if summary['total_spending'] > 0 else 0
                report += f"   {cat:12s}: NT${amount:10,.0f} ({pct:5.1f}%)\n"
        
        return report

