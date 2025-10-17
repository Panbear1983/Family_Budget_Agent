"""
FileParser - Parse MonnyReport Excel exports
Handles Peter & Dolly's monthly expense files with dynamic header detection
"""

import pandas as pd
import os
from datetime import datetime
from core.base_module import BaseModule

class FileParser(BaseModule):
    """Parse MonnyReport Excel files into standardized format"""
    
    def _setup(self):
        """Initialize parser"""
        print("  📄 File Parser initialized")
    
    def execute(self, filepath: str, person: str = 'peter') -> pd.DataFrame:
        """
        Parse MonnyReport Excel file starting from row 30
        
        Args:
            filepath: Path to Excel file
            person: 'peter' or 'wife' (for category mapping later)
        
        Returns:
            DataFrame with columns: date, category, amount, person, description
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        print(f"\n📂 Parsing: {os.path.basename(filepath)}")
        print(f"  ℹ️  Reading data from row 30 onwards")
        
        # Always start reading from row 30 (0-indexed = 29)
        skip_rows = 29
        
        # Read data
        df = pd.read_excel(
            filepath,
            skiprows=skip_rows,
            usecols=[0, 1, 2],  # Columns A, B, C
            header=None,
            names=['date', 'category', 'amount']
        )
        
        print(f"  🔍 Raw rows read: {len(df)}")
        
        # Step 3: Clean data
        df = self._clean_data(df)
        
        print(f"  🔍 After cleaning: {len(df)} rows")
        
        # 🔍 DEBUG: Check for duplicate dates
        if len(df) > 0:
            duplicate_dates = df[df.duplicated(subset=['date'], keep=False)]
            if len(duplicate_dates) > 0:
                print(f"  ⚠️  Found {len(duplicate_dates)} rows with duplicate dates:")
                date_counts = df['date'].value_counts()
                for date, count in date_counts.head(5).items():
                    if count > 1:
                        print(f"    {date.date()}: appears {count} times")
                        # Show the duplicate transactions
                        dupes = df[df['date'] == date]
                        for idx, row in dupes.iterrows():
                            print(f"      - {row['category'][:30]:30s} | NT${row['amount']:>6.0f}")
        
        # Step 4: Add metadata
        df['person'] = person
        df['description'] = df['category']  # Use category as description
        df['source_file'] = os.path.basename(filepath)
        
        print(f"  ✅ Parsed {len(df)} transactions")
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data"""
        
        # 🛡️ STEP 1: Find where data ends (detect summary/total rows)
        # Look for common terminator patterns in the date column
        end_markers = ['總', '总', 'Total', 'Summary', '合計', '彙總', '統計']
        end_idx = len(df)
        
        for idx, row in df.iterrows():
            date_val = str(row['date']).strip()
            # If the date cell contains summary keywords, stop here
            if any(marker in date_val for marker in end_markers):
                print(f"  🛑 Found end marker '{date_val}' at row {idx}, stopping data read")
                end_idx = idx
                break
        
        # Truncate dataframe at the end marker
        if end_idx < len(df):
            df = df.iloc[:end_idx].copy()
        
        # Remove rows where date is empty/invalid
        df = df.dropna(subset=['date'])
        
        # Remove rows where date is not date-like
        df = df[df['date'].apply(self._is_valid_date)]
        
        # Parse dates (handle M/D/YYYY format)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        # Clean amounts (convert to positive values, handle negative)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df.dropna(subset=['amount'])
        
        # Convert negative amounts to positive (expenses shown as negative in MonnyReport)
        df['amount'] = df['amount'].abs()
        
        # Clean categories (convert to string, strip whitespace)
        df['category'] = df['category'].astype(str).str.strip()
        
        # Remove rows with 0 amount
        df = df[df['amount'] > 0]
        
        # 🛡️ FINAL STEP: Remove any duplicate transactions from source file
        # (same date, category, and amount = likely duplicate)
        before_dedup = len(df)
        df = df.drop_duplicates(subset=['date', 'category', 'amount'], keep='first')
        after_dedup = len(df)
        
        if before_dedup != after_dedup:
            removed = before_dedup - after_dedup
            print(f"  🛡️  Removed {removed} duplicate(s) from source file")
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _is_valid_date(self, val) -> bool:
        """Check if value looks like a date"""
        if pd.isna(val):
            return False
        
        # If already datetime
        if isinstance(val, (pd.Timestamp, datetime)):
            return True
        
        # If string that looks like date
        if isinstance(val, str):
            # Check for date patterns
            if '/' in val or '-' in val:
                try:
                    pd.to_datetime(val)
                    return True
                except:
                    return False
        
        # If numeric (Excel date serial)
        if isinstance(val, (int, float)):
            try:
                pd.to_datetime(val, unit='D', origin='1899-12-30')
                return True
            except:
                return False
        
        return False
    
    def parse_multiple(self, filepaths: list, persons: list) -> pd.DataFrame:
        """
        Parse multiple files and combine
        
        Args:
            filepaths: List of file paths
            persons: List of person identifiers (same length as filepaths)
        
        Returns:
            Combined DataFrame
        """
        dfs = []
        
        for filepath, person in zip(filepaths, persons):
            df = self.execute(filepath, person)
            dfs.append(df)
        
        # Combine all dataframes
        combined = pd.concat(dfs, ignore_index=True)
        
        print(f"\n  ✅ Combined total: {len(combined)} transactions")
        
        return combined

