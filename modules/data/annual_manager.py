"""
Annual Manager - Handle annual budget file creation
"""

import os
import shutil
from datetime import datetime
from openpyxl import load_workbook, Workbook
from core.base_module import BaseModule

class AnnualManager(BaseModule):
    """Manage annual budget file lifecycle"""
    
    def _setup(self):
        """Initialize annual manager"""
        self.onedrive_path = self.config.get('onedrive_path', '')
        self.template_file = self.config.get('template_file', 'TEMPLATE_年開銷表.xlsx')
        self.auto_create = self.config.get('auto_create', True)
        print("  📅 Annual Manager initialized")
    
    def execute(self, year: int = None):
        """
        Check and create annual budget file if needed
        Returns: (file_path, created)
        """
        if year is None:
            year = datetime.now().year
        
        budget_file = self.get_budget_file_path(year)
        
        if os.path.exists(budget_file):
            return budget_file, False  # Already exists
        
        if self.auto_create:
            print(f"\n🆕 Creating budget file for {year}...")
            self.create_annual_budget(year)
            return budget_file, True
        
        return None, False
    
    def get_budget_file_path(self, year: int) -> str:
        """Get path for year's budget file"""
        filename = f"{year}年開銷表（NT）.xlsx"
        
        if self.onedrive_path:
            return os.path.join(self.onedrive_path, filename)
        else:
            return filename
    
    def get_active_budget_file(self) -> str:
        """Get current year's budget file, create if needed"""
        current_year = datetime.now().year
        budget_file, created = self.execute(current_year)
        
        if created:
            print(f"  ✅ Created new budget file for {current_year}")
        
        return budget_file
    
    def create_annual_budget(self, year: int):
        """
        Create new annual budget file
        Priority: Template > Clone previous > Create new
        """
        target_file = self.get_budget_file_path(year)
        
        # Option 1: Use template if exists
        if os.path.exists(self.template_file):
            print(f"  📋 Using template: {self.template_file}")
            shutil.copy2(self.template_file, target_file)
            print(f"  ✅ Created from template: {target_file}")
            return target_file
        
        # Option 2: Clone previous year
        prev_year_file = self.get_budget_file_path(year - 1)
        if os.path.exists(prev_year_file):
            print(f"  📋 Cloning structure from {year - 1}")
            self.clone_and_clear(prev_year_file, target_file)
            print(f"  ✅ Created from {year - 1}: {target_file}")
            return target_file
        
        # Option 3: Create from scratch
        print(f"  📋 Creating new structure from scratch")
        self.create_from_scratch(target_file)
        print(f"  ✅ Created new file: {target_file}")
        return target_file
    
    def clone_and_clear(self, source_file: str, target_file: str):
        """
        Clone structure from previous year but clear all data
        Keeps formulas, formatting, structure
        """
        wb = load_workbook(source_file)
        
        # For each sheet (month)
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            # Clear data cells (rows 3 onwards, but keep structure)
            # Keep row 1-2 (headers)
            # Clear rows 3-48 (daily entries area)
            for row in range(3, 49):
                for col in range(1, 12):
                    cell = ws.cell(row, col)
                    
                    # Keep if it's a label/structure cell
                    cell_val = str(cell.value or '')
                    if any(keyword in cell_val for keyword in ['週總額', '周總額', '單項總額', '年度明細', '星期']):
                        continue  # Keep structure
                    
                    # Clear data
                    if cell.value is not None:
                        # Keep formula if exists, otherwise clear
                        if not str(cell.value).startswith('='):
                            cell.value = None
            
            # Clear monthly summary rows (49-62)
            for row in range(49, 63):
                for col in range(3, 10):  # Clear amount columns only
                    cell = ws.cell(row, col)
                    if cell.value is not None and not str(cell.value).startswith('='):
                        cell.value = None
        
        wb.save(target_file)
    
    def create_from_scratch(self, target_file: str):
        """
        Create basic annual budget structure from scratch
        """
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        # Create 12 month sheets
        months = ['一月', '二月', '三月', '四月', '五月', '六月', 
                 '七月', '八月', '九月', '十月', '十一月', '十二月']
        
        for month in months:
            ws = wb.create_sheet(month)
            
            # Create headers
            ws.cell(1, 1, '日期：')
            ws.cell(1, 2, '星期:')
            ws.cell(1, 4, '交通费：')
            ws.cell(1, 5, '伙食费：')
            ws.cell(1, 6, '休闲/娱乐：')
            ws.cell(1, 7, '家务：')
            ws.cell(1, 8, '阿幫：')
            ws.cell(1, 9, '其它：')
            ws.cell(1, 11, '每日總額')
            
            # Add day of week labels
            days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期天']
            for i, day in enumerate(days, start=2):
                ws.cell(i, 2, day)
        
        wb.save(target_file)
    
    def archive_old_year(self, year: int):
        """Move old year's budget to archive"""
        archive_dir = self.config.get('archive_path', 'archive')
        
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        
        old_file = self.get_budget_file_path(year)
        if os.path.exists(old_file):
            archive_file = os.path.join(archive_dir, os.path.basename(old_file))
            shutil.move(old_file, archive_file)
            print(f"  📦 Archived {year} budget to {archive_file}")

