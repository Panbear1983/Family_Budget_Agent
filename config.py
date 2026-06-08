#!/usr/bin/env python3
"""
Family Budget Agent v2.0 - Configuration
All system settings in one place
"""

import os
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# 🤖 LLM CONFIGURATION (Change these 2 variables to swap models!)
# ═══════════════════════════════════════════════════════════

STRUCTURED_LLM = "qwen3:8b"      # Fast, structured tasks (parsing, categorization, data extraction)
REASONING_LLM = "gpt-oss:20b"    # Use GPT-OSS for reasoning/insight tasks
                                 # Qwen handles structured tasks, GPT-OSS handles reasoning

# Alternative models (uncomment to use):
# REASONING_LLM = "qwen3:8b"       # Use Qwen for both (faster but less insightful)
# STRUCTURED_LLM = "gpt-oss:20b"   # Larger GPT-OSS model
# REASONING_LLM = "gpt-oss:20b"    # Use GPT-OSS for both structured and reasoning tasks
# REASONING_LLM = "llama3:70b"     # Larger reasoning model

LLM_CONFIG = {
    "structured": {
        "model": STRUCTURED_LLM,
        "timeout": 60,  # 1 minute for structured tasks
        "temperature": 0.1  # Deterministic for structured tasks
    },
"reasoning": {
    "model": REASONING_LLM,
    "timeout": 180,  # GPT-OSS gives richer reasoning; allow more time
    "temperature": 0.7  # Restore expressive setting for GPT-OSS
}
}

# ═══════════════════════════════════════════════════════════
# 📁 FILE PATHS
# ═══════════════════════════════════════════════════════════

# OneDrive base path
ONEDRIVE_PATH = "/Users/peter/Library/CloudStorage/OneDrive-Personal/Documents"

# Current year (auto-detected)
CURRENT_YEAR = datetime.now().year

# Main budget file (auto-determined by year)
# Keep in sync with AnnualManager.get_budget_file_path()
BUDGET_FILE = f"{CURRENT_YEAR}年開銷表（NT）.xlsx"
BUDGET_PATH = os.path.join(ONEDRIVE_PATH, BUDGET_FILE)

# Category mapping
CATEGORY_MAPPING_FILE = "category_mapping.json"

# ═══════════════════════════════════════════════════════════
# 📥 MONTHLY MERGE SETTINGS
# ═══════════════════════════════════════════════════════════

MERGE_CONFIG = {
    "your_export_pattern": "peter_*.xlsx",
    "wife_export_pattern": "wife_*.xlsx",
    "auto_detect_month": True,       # Detect from filename or data
    "require_preview": True,         # Show preview before applying
    "auto_backup": True,             # Always backup before update
    "duplicate_strategy": "llm_assisted",  # Use LLM for fuzzy matching
    "same_person_dedup_tolerance": 0  # NT$ tolerance for same-person exact dedup (0 = exact match only)
}

# ═══════════════════════════════════════════════════════════
# 📅 ANNUAL MANAGEMENT
# ═══════════════════════════════════════════════════════════

ANNUAL_CONFIG = {
    "auto_create": True,             # Auto-create budget file for new year
    "template_file": "20XX年開銷表（NT）.xlsx",
    "naming_pattern": "{year}年開銷表（NT）.xlsx",
    "archive_old_years": True,       # Move old years to archive/
    "archive_path": "archive/",
    "years_to_keep_active": 2        # Current + previous year
}

# ═══════════════════════════════════════════════════════════
# 🔧 SYSTEM SETTINGS
# ═══════════════════════════════════════════════════════════

# Module discovery
MODULE_PATHS = ['modules']

# Logging
DEBUG_MODE = False
LOG_FILE = "budget_agent.log"

# Performance
CACHE_ENABLED = True
MAX_LLM_RETRIES = 3

# ═══════════════════════════════════════════════════════════
# 🌍 LANGUAGE CONFIGURATION (AI Chat)
# ═══════════════════════════════════════════════════════════

LANGUAGE_CONFIG = {
    "default_language": "auto",  # auto | zh | en
    "supported_languages": ["zh", "en"],
    "auto_detect": True,         # Detect from user input
    "allow_mixed": True,         # Allow bilingual responses
    "data_language": "zh"        # Budget data is in Chinese
}

# Language detection patterns
LANGUAGE_PATTERNS = {
    "zh": {
        "name": "中文",
        "indicators": ['的', '是', '嗎', '為什麼', '怎麼', '多少', '請', '幫我'],
        "response_style": "natural_chinese"
    },
    "en": {
        "name": "English", 
        "indicators": ['the', 'is', 'are', 'what', 'how', 'why', 'please', 'show me'],
        "response_style": "natural_english"
    }
}

# ═══════════════════════════════════════════════════════════
# 🎯 AI CHAT CONFIGURATION (Confidence & Behavior)
# ═══════════════════════════════════════════════════════════

AI_CHAT_CONFIG = {
    "show_confidence": True,        # Display confidence scores
    "confidence_threshold": 0.6,    # Warn if confidence below this
    "verbose_uncertainty": True,    # Show detailed breakdown for low confidence
    "show_uncertainty_warning": True,  # Show warning messages for uncertain answers
    "min_confidence_for_action": 0.7,   # Minimum confidence for action recommendations
    "use_dual_pipeline": True,      # Use Qwen→GPT-OSS pipeline for all complex questions (best quality)
    "dual_pipeline_mode": "smart",   # "always" | "smart" | "never" 
                                    # smart = use for insight/advice/optimize only
                                    # always = use for all questions (slower but more insightful)
    # Budget Advisor Personality Configuration
    "personality": {
        "enabled": True,            # Enable personality mode
        "style": "humorous_casual",  # "formal" | "humorous_casual" | "professional"
        "allow_swear_words": True,   # Allow occasional swear words (fuck, shit, damn, etc.)
        "swear_frequency": "sparing", # "never" | "sparing" | "moderate" | "frequent"
        "use_humor": True,           # Use humor in responses
        "bilingual": True,           # Use both Chinese and English naturally
        "short_paragraphs": True,    # Keep spending feedback short (2-3 sentences)
        "data_citation": True        # Always cite specific months/categories from Excel
    },
    # Budget Topic Filtering
    "topic_filter": {
        "enabled": True,             # Only answer budget-related questions
        "strict_mode": True,         # Strictly enforce budget-only responses
        "decline_message": "Hey, I'm your budget consultant, not your everything consultant. Stick to money, spending, and budget questions, okay? 😏"
    }
}

# ═══════════════════════════════════════════════════════════
# 📊 EXCEL STRUCTURE (Your Budget File)
# ═══════════════════════════════════════════════════════════

EXCEL_STRUCTURE = {
    "month_sheets": ["一月", "二月", "三月", "四月", "五月", "六月", 
                     "七月", "八月", "九月", "十月", "十一月", "十二月"],
    
    "columns": {
        "date": 1,           # Column A
        "day_of_week": 2,    # Column B
        "empty": 3,          # Column C (spacing)
        "交通費": 4,          # Column D
        "伙食費": 5,          # Column E
        "休閒/娛樂": 6,       # Column F
        "家務": 7,            # Column G
        "阿幫": 8,            # Column H
        "其它": 9,            # Column I
        "notes": 10,         # Column J (optional)
        "daily_total": 11    # Column K
    },
    
    "row_patterns": {
        "header_row": 1,
        "daily_entry_start": 3,
        "daily_entry_end": 40,
        "weekly_total_marker": "周總額",
        "monthly_summary_marker": "單項總額"
    }
}

