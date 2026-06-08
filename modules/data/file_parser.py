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
        Parse MonnyReport Excel file using dynamic header detection.
        Finds the 'Details' section header row automatically — works regardless
        of which MonnyReport version or how many metadata rows precede the data.

        Args:
            filepath: Path to Excel file
            person: 'peter' or 'wife' (for category mapping later)

        Returns:
            DataFrame with columns: date, category, amount, person, description
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        print(f"\n📂 Parsing: {os.path.basename(filepath)}")

        # Dynamically find the header row containing Date/Category/Amount
        header_row = self._find_header_row(filepath)
        print(f"  ℹ️  Data header found at row {header_row + 1} (reading data from row {header_row + 2})")

        # Read the full file from the header row, let pandas use it as column names
        df_raw = pd.read_excel(filepath, header=header_row)

        print(f"  🔍 Raw rows read: {len(df_raw)}")
        print(f"  🔍 Columns found: {list(df_raw.columns)}")

        # Normalise column names — find date, category, amount, description flexibly
        col_map = self._map_columns(df_raw.columns.tolist())

        if not all(k in col_map for k in ('date', 'category', 'amount')):
            raise ValueError(
                f"Could not find required columns (Date/Category/Amount) in {filepath}. "
                f"Columns present: {list(df_raw.columns)}"
            )

        # Build standardised DataFrame
        df = pd.DataFrame()
        df['date'] = df_raw[col_map['date']]
        df['category'] = df_raw[col_map['category']]
        df['amount'] = df_raw[col_map['amount']]
        df['description'] = df_raw[col_map['description']].astype(str).str.strip() \
            if 'description' in col_map else ''
        # Blank out placeholder values like '.' or 'nan'
        df['description'] = df['description'].apply(
            lambda x: '' if x in ('.', 'nan', 'None', '') else x
        )

        # Clean data
        df = self._clean_data(df)

        print(f"  🔍 After cleaning: {len(df)} rows")

        # Warn about same-day same-amount same-category rows
        duplicate_mask = df.duplicated(subset=['date', 'category', 'amount'], keep=False)
        if duplicate_mask.any():
            print(f"  ⚠️  {duplicate_mask.sum()} row(s) share date+category+amount — review in preview")

        # Add metadata
        df['person'] = person
        df['source_file'] = os.path.basename(filepath)

        print(f"  ✅ Parsed {len(df)} transactions")
        return df

    def _find_header_row(self, filepath: str) -> int:
        """
        Locate the 0-based row index of the transaction data header using 3 strategies
        in order, so the parser stays robust across MonnyReport versions and languages.

        Strategy 1 — Keyword exact match (fastest):
            Look for a row where any cell exactly matches a known Date keyword AND
            any cell exactly matches a known Category keyword.

        Strategy 2 — Keyword substring match (handles renamed columns):
            Same logic but using 'in' on the lowercased cell value, so headers like
            "Transaction Date" or "交易類別" still match.

        Strategy 3 — Data-row proximity (language-agnostic):
            Find the last row in the file whose column-0 value is NOT a valid date,
            immediately before a run of rows that ARE valid dates. Works regardless
            of what the header is actually called.

        Falls back to row 29 (row 30 in 1-based) only if all three fail.
        """
        df_scan = pd.read_excel(filepath, header=None, nrows=60)

        # Keyword sets — extend these if MonnyReport adds new languages
        DATE_EXACT   = {'date', '日期', 'transaction date', '交易日期'}
        CAT_EXACT    = {'category', '類別', '分類', '科目'}
        DATE_SUBSTR  = ('date', '日期', '交易')
        CAT_SUBSTR   = ('category', '類別', '分類', '科目', 'type')
        AMT_SUBSTR   = ('amount', '金額', '數額', 'sum')

        def cell_vals(row):
            return [str(v).strip() for v in row if pd.notna(v) and str(v).strip()]

        # ── Strategy 1: exact match ──────────────────────────────────────────
        for i, row in df_scan.iterrows():
            vals_lower = [v.lower() for v in cell_vals(row)]
            if (any(v in DATE_EXACT for v in vals_lower) and
                    any(v in CAT_EXACT for v in vals_lower)):
                print(f"  🔍 Header detected via exact match at row {i + 1}")
                return i

        # ── Strategy 2: substring match ──────────────────────────────────────
        for i, row in df_scan.iterrows():
            vals_lower = [v.lower() for v in cell_vals(row)]
            has_date = any(any(kw in v for kw in DATE_SUBSTR) for v in vals_lower)
            has_cat  = any(any(kw in v for kw in CAT_SUBSTR)  for v in vals_lower)
            has_amt  = any(any(kw in v for kw in AMT_SUBSTR)  for v in vals_lower)
            if has_date and has_cat and has_amt:
                print(f"  🔍 Header detected via substring match at row {i + 1}")
                return i

        # ── Strategy 3: data-row proximity (find where dates start) ──────────
        # Build a boolean series: True where col-0 looks like a real date
        def looks_like_date(val):
            if pd.isna(val):
                return False
            if isinstance(val, (pd.Timestamp, datetime)):
                return True
            try:
                pd.to_datetime(str(val), errors='raise')
                return True
            except Exception:
                return False

        date_flags = [looks_like_date(df_scan.iloc[i, 0]) for i in range(len(df_scan))]

        # Find first index where dates appear consistently (3+ in next 5 rows)
        for i in range(len(date_flags) - 4):
            if sum(date_flags[i:i + 5]) >= 3:
                # The header row is one row above
                header_idx = max(0, i - 1)
                print(f"  🔍 Header detected via data-proximity at row {header_idx + 1}")
                return header_idx

        # ── Fallback ──────────────────────────────────────────────────────────
        print(f"  ⚠️  All header detection strategies failed — falling back to row 30")
        return 29

    def _map_columns(self, columns: list) -> dict:
        """
        Map raw column names to standard keys: date, category, amount, description.
        Uses three-pass matching (exact → substring → positional) so renamed or
        translated column headers still resolve correctly.
        """
        DATE_EXACT  = {'date', '日期', 'transaction date', '交易日期'}
        CAT_EXACT   = {'category', '類別', '分類', '科目'}
        AMT_EXACT   = {'amount', '金額', '數額', 'expense', 'income'}
        DESC_EXACT  = {'description', '備註', '描述', '說明', 'note', 'notes',
                       'memo', '摘要', 'remarks'}

        DATE_SUB  = ('date', '日期')
        CAT_SUB   = ('category', '類別', '分類', '科目')
        AMT_SUB   = ('amount', '金額', '費用', 'expense')
        DESC_SUB  = ('description', '備註', 'note', 'memo', '摘要')

        mapping = {}

        # Pass 1 — exact match (case-insensitive)
        for col in columns:
            c = str(col).strip().lower()
            if c in DATE_EXACT  and 'date'        not in mapping: mapping['date']        = col
            if c in CAT_EXACT   and 'category'    not in mapping: mapping['category']    = col
            if c in AMT_EXACT   and 'amount'      not in mapping: mapping['amount']      = col
            if c in DESC_EXACT  and 'description' not in mapping: mapping['description'] = col

        # Pass 2 — substring match for anything still unmapped
        for col in columns:
            c = str(col).strip().lower()
            if 'date'        not in mapping and any(kw in c for kw in DATE_SUB):  mapping['date']        = col
            if 'category'    not in mapping and any(kw in c for kw in CAT_SUB):   mapping['category']    = col
            if 'amount'      not in mapping and any(kw in c for kw in AMT_SUB):   mapping['amount']      = col
            if 'description' not in mapping and any(kw in c for kw in DESC_SUB):  mapping['description'] = col

        # Pass 3 — positional fallback (MonnyReport always has Date/Cat/Amt in cols 0/1/2)
        named = [c for c in columns if not str(c).startswith('Unnamed')]
        if 'date'     not in mapping and len(named) > 0: mapping['date']     = named[0]
        if 'category' not in mapping and len(named) > 1: mapping['category'] = named[1]
        if 'amount'   not in mapping and len(named) > 2: mapping['amount']   = named[2]
        if 'description' not in mapping:
            # Take the last named column if it's not already mapped (often col E)
            last = named[-1] if named else None
            if last and last not in mapping.values():
                mapping['description'] = last

        return mapping
    
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
        # 🛡️ FIX: Remove currency symbols, commas, and handle negative signs before conversion
        if df['amount'].dtype == object:
            # Remove whitespace
            df['amount'] = df['amount'].astype(str).str.strip()
            # Remove currency symbols ($, NT$, NT, etc.) and commas
            df['amount'] = df['amount'].str.replace(r'[^\d.-]', '', regex=True)
            
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df.dropna(subset=['amount'])
        
        # Convert negative amounts to positive (expenses shown as negative in MonnyReport)
        df['amount'] = df['amount'].abs()
        
        # Clean categories (convert to string, strip whitespace)
        df['category'] = df['category'].astype(str).str.strip()
        
        # Remove rows with 0 amount
        df = df[df['amount'] > 0]
        
        # 🛡️ FINAL STEP: Warn about rows that look identical (date + category + amount)
        # We do NOT auto-remove them — with only 3 columns we can't distinguish a MonnyReport
        # export bug from two legitimate same-day same-amount transactions (e.g. two NT$150 lunches).
        # The user will see these in the preview and can decide.
        duplicate_mask = df.duplicated(subset=['date', 'category', 'amount'], keep=False)
        if duplicate_mask.any():
            dup_count = duplicate_mask.sum()
            print(f"  ⚠️  {dup_count} row(s) share the same date+category+amount — review in preview")
        
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

