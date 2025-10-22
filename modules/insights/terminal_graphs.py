"""
Terminal Graph Generator - ASCII charts using plotext
"""

import plotext as plt
from typing import Dict, List

class TerminalGraphGenerator:
    """Generates terminal-based charts"""
    
    # Category translations (same as GUI)
    CATEGORY_TRANSLATION = {
        '交通費': 'Transportation',
        '伙食費': 'Food & Dining',
        '休閒/娛樂': 'Entertainment',
        '家務': 'Household',
        '阿幫': 'A-Bang',
        '其它': 'Others'
    }
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
    
    def translate_category(self, category: str) -> str:
        """Translate Chinese category to English"""
        return self.CATEGORY_TRANSLATION.get(category, category)
    
    def plot_monthly_bar(self, summary: Dict) -> None:
        """Bar chart of monthly spending"""
        monthly = summary['monthly_trend']
        
        # Month translations
        month_trans = {
            '一月': 'Jan', '二月': 'Feb', '三月': 'Mar', '四月': 'Apr',
            '五月': 'May', '六月': 'Jun', '七月': 'Jul', '八月': 'Aug',
            '九月': 'Sep', '十月': 'Oct', '十一月': 'Nov', '十二月': 'Dec'
        }
        
        months = [month_trans.get(m, m) for m in monthly.keys()]
        amounts = [monthly[m] / 1000 for m in list(monthly.keys())]  # Convert to thousands
        
        plt.clear_figure()
        plt.bar(months, amounts, color='cyan')
        plt.title("📊 Monthly Spending Trend (in 1000s)")
        plt.xlabel("Month")
        plt.ylabel("Amount (NT$ 1000)")
        plt.theme('dark')
        plt.plotsize(100, 20)
        plt.show()
    
    def plot_category_horizontal_bar(self, insights: Dict) -> None:
        """Horizontal bar chart for category breakdown"""
        # Handle error case
        if 'error' in insights:
            print(f"\n❌ {insights['error']}\n")
            return
        
        categories = sorted(
            insights['categories'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Translate to English
        labels = [self.translate_category(cat) for cat, _ in categories]
        values = [amount / 1000 for _, amount in categories]
        
        # Month translation
        month_trans = {
            '一月': 'Jan', '二月': 'Feb', '三月': 'Mar', '四月': 'Apr',
            '五月': 'May', '六月': 'Jun', '七月': 'Jul', '八月': 'Aug',
            '九月': 'Sep', '十月': 'Oct', '十一月': 'Nov', '十二月': 'Dec'
        }
        month_en = month_trans.get(insights['month'], insights['month'])
        
        plt.clear_figure()
        plt.bar(labels, values, orientation='h', color='green')
        plt.title(f"📂 {month_en} Category Spending (in 1000s)")
        plt.xlabel("Amount (NT$ 1000)")
        plt.theme('dark')
        plt.plotsize(100, 15)
        plt.show()
    
    def plot_trend_line(self, trend_data: List[Dict], category: str) -> None:
        """Line chart of category trend"""
        if not trend_data:
            print("❌ No trend data available")
            return
        
        # Month translations
        month_trans = {
            '一月': 'Jan', '二月': 'Feb', '三月': 'Mar', '四月': 'Apr',
            '五月': 'May', '六月': 'Jun', '七月': 'Jul', '八月': 'Aug',
            '九月': 'Sep', '十月': 'Oct', '十一月': 'Nov', '十二月': 'Dec'
        }
        
        months = [month_trans.get(d['month'], d['month']) for d in trend_data]
        amounts = [d['amount'] / 1000 for d in trend_data]
        category_en = self.translate_category(category)
        
        plt.clear_figure()
        
        # Use numeric x-axis (plotext doesn't handle string labels well in plot())
        x_values = list(range(1, len(months) + 1))
        
        plt.plot(x_values, amounts, marker='braille', color='magenta')
        plt.xticks(x_values, months)  # Set custom labels
        plt.title(f"📈 {category_en} Trend (in 1000s)")
        plt.xlabel("Month")
        plt.ylabel("Amount (NT$ 1000)")
        plt.theme('dark')
        plt.plotsize(100, 20)
        plt.show()
    
    def plot_comparison_bars(self, comparison: Dict) -> None:
        """Side-by-side comparison chart"""
        # Handle error case
        if 'error' in comparison:
            print(f"\n❌ {comparison['error']}\n")
            return
        
        categories = list(comparison['category_changes'].keys())
        
        # Translate to English
        categories_en = [self.translate_category(cat) for cat in categories]
        
        month1_data = [comparison['category_changes'][c]['month1'] / 1000 
                       for c in categories]
        month2_data = [comparison['category_changes'][c]['month2'] / 1000 
                       for c in categories]
        
        # Month translations
        month_trans = {
            '一月': 'Jan', '二月': 'Feb', '三月': 'Mar', '四月': 'Apr',
            '五月': 'May', '六月': 'Jun', '七月': 'Jul', '八月': 'Aug',
            '九月': 'Sep', '十月': 'Oct', '十一月': 'Nov', '十二月': 'Dec'
        }
        month1_label = month_trans.get(comparison['month1'], comparison['month1'])
        month2_label = month_trans.get(comparison['month2'], comparison['month2'])
        
        plt.clear_figure()
        
        # Use simple_multiple_bar (plotext doesn't support 'colors' parameter)
        plt.simple_multiple_bar(
            categories_en,
            [month1_data, month2_data],
            labels=[month1_label, month2_label]
        )
        
        plt.title(f"⚖️  {month1_label} vs {month2_label} Comparison (in 1000s)")
        plt.xlabel("Category")
        plt.ylabel("Amount (NT$ 1000)")
        plt.theme('dark')
        plt.plotsize(100, 20)
        plt.show()
    
    def plot_stacked_trend(self, summary: Dict) -> None:
        """Stacked bar chart showing category composition by month"""
        monthly_data = summary['monthly_trend']
        months = list(monthly_data.keys())
        
        # Get all categories
        all_data = self.data_loader.load_all_data()
        categories = set()
        for df in all_data.values():
            if 'category' in df.columns:
                categories.update(df['category'].unique())
        
        categories = sorted(list(categories))
        
        # Build data for each category
        category_data = {cat: [] for cat in categories}
        
        for month in months:
            if month in all_data:
                df = all_data[month]
                if 'category' in df.columns and 'amount' in df.columns:
                    month_cats = df.groupby('category')['amount'].sum() / 1000
                    for cat in categories:
                        category_data[cat].append(month_cats.get(cat, 0))
                else:
                    for cat in categories:
                        category_data[cat].append(0)
            else:
                for cat in categories:
                    category_data[cat].append(0)
        
        plt.clear_figure()
        plt.stacked_bar(
            months,
            list(category_data.values()),
            labels=categories
        )
        plt.title("📊 月度分類支出堆疊圖 (單位: 千元)")
        plt.xlabel("月份")
        plt.ylabel("金額 (NT$ 1000)")
        plt.theme('dark')
        plt.plotsize(100, 25)
        plt.show()

