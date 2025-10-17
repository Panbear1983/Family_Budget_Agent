"""
GUI Graph Generator - Professional charts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # macOS compatible
import numpy as np
from typing import Dict, List
import pandas as pd

class GUIGraphGenerator:
    """Generates professional GUI charts"""
    
    # Category translations (Chinese to English)
    CATEGORY_TRANSLATION = {
        '交通費': 'Transportation',
        '伙食費': 'Food & Dining',
        '休閒/娛樂': 'Entertainment',
        '家務': 'Household',
        '阿幫': 'Pet',
        '其它': 'Others'
    }
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.setup_style()
    
    def translate_category(self, category: str) -> str:
        """Translate Chinese category to English"""
        return self.CATEGORY_TRANSLATION.get(category, category)
    
    def setup_style(self):
        """Configure matplotlib style and Chinese font"""
        import matplotlib.font_manager as fm
        
        # macOS Chinese fonts (in order of preference)
        preferred_fonts = [
            'PingFang TC',        # macOS default Chinese (Traditional)
            'PingFang SC',        # macOS default Chinese (Simplified)
            'Arial Unicode MS',   # macOS fallback with Chinese support
            'Heiti TC',          # macOS traditional
            'STHeiti',           # System Heiti
            'SimHei',            # Windows/Linux fallback
            'Microsoft YaHei'    # Windows fallback
        ]
        
        # Get all available font names
        available_fonts = set(f.name for f in fm.fontManager.ttflist)
        
        # Find first available font
        selected_font = None
        for font in preferred_fonts:
            if font in available_fonts:
                selected_font = font
                break
        
        if selected_font:
            plt.rcParams['font.sans-serif'] = [selected_font]
            print(f"✅ Using Chinese font: {selected_font}")
        else:
            # Fallback - try to find any font with Chinese characters
            plt.rcParams['font.sans-serif'] = preferred_fonts
            print("⚠️  Using fallback font list")
        
        plt.rcParams['axes.unicode_minus'] = False
        
        # Use a clean style
        try:
            plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
        except:
            pass
    
    def plot_pie_chart(self, insights: Dict) -> None:
        """Beautiful pie chart for category breakdown"""
        categories = sorted(
            insights['categories'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Translate labels to English
        labels = [self.translate_category(cat) for cat, _ in categories]
        values = [amount for _, amount in categories]
        colors = plt.cm.Set3(range(len(labels)))
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=[0.05] * len(labels),
            shadow=True
        )
        
        # Enhance text
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        # Month translation
        month_trans = {
            '一月': 'January', '二月': 'February', '三月': 'March', '四月': 'April',
            '五月': 'May', '六月': 'June', '七月': 'July', '八月': 'August',
            '九月': 'September', '十月': 'October', '十一月': 'November', '十二月': 'December'
        }
        month_en = month_trans.get(insights['month'], insights['month'])
        
        ax.set_title(f"{month_en} Spending Distribution", fontsize=16, weight='bold', pad=20)
        plt.tight_layout()
        plt.show()
    
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
        amounts = list(monthly.values())
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        bars = ax.bar(months, amounts, color='steelblue', alpha=0.8, edgecolor='navy', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., height,
                f'NT${height/1000:.1f}k',
                ha='center', va='bottom', fontsize=9, weight='bold'
            )
        
        ax.set_title('2025 Monthly Spending', fontsize=18, weight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=13, weight='bold')
        ax.set_ylabel('Amount (NT$)', fontsize=13, weight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    def plot_comparison_grouped_bars(self, comparison: Dict) -> None:
        """Grouped bar chart for month comparison"""
        categories = list(comparison['category_changes'].keys())
        
        # Translate categories to English
        categories_en = [self.translate_category(cat) for cat in categories]
        
        month1_data = [comparison['category_changes'][c]['month1'] for c in categories]
        month2_data = [comparison['category_changes'][c]['month2'] for c in categories]
        
        x = np.arange(len(categories))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Month translations
        month_trans = {
            '一月': 'Jan', '二月': 'Feb', '三月': 'Mar', '四月': 'Apr',
            '五月': 'May', '六月': 'Jun', '七月': 'Jul', '八月': 'Aug',
            '九月': 'Sep', '十月': 'Oct', '十一月': 'Nov', '十二月': 'Dec'
        }
        
        month1_label = month_trans.get(comparison['month1'], comparison['month1'])
        month2_label = month_trans.get(comparison['month2'], comparison['month2'])
        
        bars1 = ax.bar(x - width/2, month1_data, width, label=month1_label, 
                       color='skyblue', edgecolor='navy', alpha=0.8)
        bars2 = ax.bar(x + width/2, month2_data, width, label=month2_label, 
                       color='lightcoral', edgecolor='darkred', alpha=0.8)
        
        ax.set_title(f"{month1_label} vs {month2_label} Comparison", 
                     fontsize=18, weight='bold', pad=20)
        ax.set_xlabel('Category', fontsize=13, weight='bold')
        ax.set_ylabel('Amount (NT$)', fontsize=13, weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories_en, rotation=45, ha='right')
        ax.legend(fontsize=12)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
    
    def plot_trend_line(self, trend_data: List[Dict], category: str) -> None:
        """Line chart with markers for category trend"""
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
        amounts = [d['amount'] for d in trend_data]
        category_en = self.translate_category(category)
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        ax.plot(months, amounts, marker='o', linewidth=3, markersize=10, 
                color='steelblue', markerfacecolor='lightblue', 
                markeredgecolor='navy', markeredgewidth=2)
        
        # Add value labels
        for i, (month, amount) in enumerate(zip(months, amounts)):
            ax.text(i, amount, f'NT${amount/1000:.1f}k', 
                   ha='center', va='bottom', fontsize=9)
        
        ax.set_title(f'{category_en} Trend Analysis', fontsize=18, weight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=13, weight='bold')
        ax.set_ylabel('Amount (NT$)', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    def plot_stacked_area(self, summary: Dict) -> None:
        """Stacked area chart showing category composition over time"""
        all_data = self.data_loader.load_all_data()
        months = list(summary['monthly_trend'].keys())
        
        # Get all categories
        categories = set()
        for df in all_data.values():
            if 'category' in df.columns:
                categories.update(df['category'].unique())
        
        categories = sorted(list(categories))
        
        # Build data matrix
        data_matrix = []
        for cat in categories:
            cat_data = []
            for month in months:
                if month in all_data:
                    df = all_data[month]
                    if 'category' in df.columns and 'amount' in df.columns:
                        amount = df[df['category'] == cat]['amount'].sum()
                        cat_data.append(amount)
                    else:
                        cat_data.append(0)
                else:
                    cat_data.append(0)
            data_matrix.append(cat_data)
        
        # Translate categories and months FIRST
        categories_en = [self.translate_category(cat) for cat in categories]
        
        month_trans = {
            '一月': 'Jan', '二月': 'Feb', '三月': 'Mar', '四月': 'Apr',
            '五月': 'May', '六月': 'Jun', '七月': 'Jul', '八月': 'Aug',
            '九月': 'Sep', '十月': 'Oct', '十一月': 'Nov', '十二月': 'Dec'
        }
        months_en = [month_trans.get(m, m) for m in months]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = plt.cm.Set3(range(len(categories)))
        ax.stackplot(range(len(months)), *data_matrix, labels=categories_en, colors=colors, alpha=0.8)
        
        ax.set_title('Annual Category Spending Trend', fontsize=18, weight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=13, weight='bold')
        ax.set_ylabel('Amount (NT$)', fontsize=13, weight='bold')
        ax.set_xticks(range(len(months_en)))
        ax.set_xticklabels(months_en, rotation=45, ha='right')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
    
    def plot_donut_chart(self, summary: Dict) -> None:
        """Donut chart for yearly category breakdown"""
        categories = sorted(
            summary['category_breakdown'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Translate labels to English
        labels = [self.translate_category(cat) for cat, _ in categories]
        values = [amount for _, amount in categories]
        colors = plt.cm.Pastel1(range(len(labels)))
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            pctdistance=0.85
        )
        
        # Create donut hole
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax.add_artist(centre_circle)
        
        # Add total in center
        total = sum(values)
        ax.text(0, 0, f'總計\nNT${total/1000:.0f}k', 
               ha='center', va='center', fontsize=16, weight='bold')
        
        # Enhance text
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        ax.set_title('Annual Category Distribution', fontsize=18, weight='bold', pad=20)
        plt.tight_layout()
        plt.show()

