"""
GUI Graph Generator - Professional charts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # macOS compatible
import numpy as np
from typing import Dict, List
import pandas as pd
import warnings
import logging

# Suppress matplotlib font warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

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
    
    def _force_chinese_font(self):
        """Force Chinese font configuration for each plot"""
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        
        # Get available Chinese fonts
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        chinese_fonts = [f for f in available_fonts if any(keyword in f for keyword in ['PingFang', 'Heiti', 'Arial Unicode', 'Hiragino', 'SimHei', 'STHeiti', 'LiGothic', 'LiSung'])]
        
        if chinese_fonts:
            selected_font = chinese_fonts[0]
            plt.rcParams['font.sans-serif'] = [selected_font]
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
    
    def setup_style(self):
        """Configure matplotlib style and Chinese font"""
        import matplotlib.font_manager as fm
        import matplotlib.pyplot as plt
        import os
        
        # Suppress font warnings completely
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Force Chinese font support with direct font file approach
            try:
                # Find available Chinese fonts
                available_fonts = [f.name for f in fm.fontManager.ttflist]
                chinese_fonts = []
                
                # Check for specific Chinese fonts (optimized to 1 most reliable font)
                chinese_font_candidates = [
                    'STHeiti'  # Fast, lightweight Chinese font (~4MB)
                ]
                
                for font_name in chinese_font_candidates:
                    if font_name in available_fonts:
                        chinese_fonts.append(font_name)
                
                # Debug: Print available Chinese fonts
                print(f"🔍 Available Chinese fonts: {chinese_fonts}")
                
                if chinese_fonts:
                    # Use the first available Chinese font
                    selected_font = chinese_fonts[0]
                    # Force the Chinese font to be used first - ONLY the Chinese font
                    plt.rcParams['font.sans-serif'] = [selected_font]
                    plt.rcParams['font.family'] = 'sans-serif'
                    # Clear font cache to force reload
                    try:
                        fm.fontManager.__init__()
                    except:
                        pass
                    print(f"✅ Using Chinese font: {selected_font}")
                else:
                    # Fallback: use fonts that support Unicode (NO DejaVu!)
                    plt.rcParams['font.sans-serif'] = ['STHeiti', 'Hiragino Sans', 'PingFang SC', 'Arial']
                    print("⚠️ Using fallback fonts for Chinese characters")
                
                plt.rcParams['axes.unicode_minus'] = False
                plt.rcParams['font.size'] = 12
                
                # Suppress font manager warnings
                plt.rcParams['font.fallback'] = ['DejaVu Sans']
                
            except Exception:
                # Final fallback - silent
                plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
                plt.rcParams['font.family'] = 'sans-serif'
        
        # Use a clean style
        try:
            plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
        except:
            pass
    
    def plot_pie_chart(self, insights: Dict) -> None:
        """Beautiful pie chart for category breakdown"""
        # Handle error case
        if 'error' in insights:
            print(f"\n❌ {insights['error']}\n")
            return
        
        # Force Chinese font configuration
        self._force_chinese_font()
        
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plt.tight_layout()
        plt.show()
    
    def plot_monthly_bar(self, summary: Dict) -> None:
        """Bar chart of monthly spending"""
        # Force Chinese font configuration
        self._force_chinese_font()
        
        monthly = summary['monthly_trend']
        
        # Use English month labels to avoid font issues
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plt.tight_layout()
        plt.show()
    
    def plot_comparison_grouped_bars(self, comparison: Dict) -> None:
        """Grouped bar chart for month comparison"""
        # Handle error case
        if 'error' in comparison:
            print(f"\n❌ {comparison['error']}\n")
            return
        
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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
        
        # Use English labels to avoid font issues
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plt.tight_layout()
        plt.show()
    
    def plot_donut_chart(self, summary: Dict) -> None:
        """Donut chart for yearly category breakdown"""
        categories = sorted(
            summary['category_breakdown'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Use English category labels to avoid font issues
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
        ax.text(0, 0, f'Total\nNT${total/1000:.0f}k', 
               ha='center', va='center', fontsize=16, weight='bold')
        
        # Enhance text
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        ax.set_title('Annual Category Distribution', fontsize=18, weight='bold', pad=20)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plt.tight_layout()
        plt.show()
    
    def self_test_chinese_fonts(self) -> None:
        """Self-test Chinese font configuration and display"""
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        
        print("🔍 Self-testing Chinese font configuration...")
        
        # Test 1: Check available fonts
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        chinese_fonts = [f for f in available_fonts if any(keyword in f for keyword in ['PingFang', 'Heiti', 'Arial Unicode', 'Hiragino', 'SimHei', 'STHeiti', 'LiGothic', 'LiSung'])]
        
        print(f"📋 Available Chinese fonts: {chinese_fonts}")
        
        if not chinese_fonts:
            print("❌ No Chinese fonts found!")
            return False
        
        # Test 2: Configure font
        selected_font = chinese_fonts[0]
        plt.rcParams['font.sans-serif'] = [selected_font]
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
        
        print(f"🎯 Using font: {selected_font}")
        
        # Test 3: Create test plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Test different Chinese text
        test_texts = [
            "中文測試：一月、二月、三月",
            "分類：交通費、伙食費、休閒娛樂",
            "月份：四月、五月、六月",
            "測試：家務、阿幫、其它"
        ]
        
        y_positions = [0.8, 0.6, 0.4, 0.2]
        
        for i, (text, y_pos) in enumerate(zip(test_texts, y_positions)):
            ax.text(0.5, y_pos, text, fontsize=14, ha='center', va='center', 
                   transform=ax.transAxes, color=f'C{i}')
        
        ax.set_title("Chinese Font Self-Test", fontsize=20, weight='bold')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add font info
        ax.text(0.5, 0.05, f"Font: {selected_font}", fontsize=10, ha='center', 
               transform=ax.transAxes, style='italic')
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Chinese font self-test completed successfully!")
        return True

