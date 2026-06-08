"""
Simple Categorizer - Dictionary-first approach
95% handled by dictionary, 5% by LLM fallback
"""

import json
import os
import re
from typing import Tuple
from core.base_module import BaseModule

class SimpleCategorizer(BaseModule):
    """Fast categorization using dictionary lookup with LLM fallback"""
    
    def _setup(self):
        """Load category mapping dictionary"""
        mapping_file = self.config.get('mapping_file', 'category_mapping.json')
        
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r', encoding='utf-8') as f:
                self.mapping = json.load(f)
            print(f"  📖 Loaded category mappings from {mapping_file}")
        else:
            print(f"  ⚠️  Mapping file not found: {mapping_file}")
            self.mapping = self._default_mapping()
        
        self.llm_engine = None  # Will be set by orchestrator if needed
    
    def set_llm_fallback(self, llm_engine):
        """Set LLM engine for fallback"""
        self.llm_engine = llm_engine
    
    def execute(self, transaction: dict, person: str = 'peter') -> Tuple[str, float]:
        """
        Categorize a transaction
        Returns: (category, confidence)
        """
        category = transaction.get('category', '')
        description = transaction.get('description', '')
        cat, conf, _ = self.categorize(category, description, person)
        return cat, conf
    
    def categorize(self, category: str, description: str, person: str = 'peter') -> Tuple[str, float, str]:
        """
        Multi-stage categorization:
        1. Exact person-specific mapping (instant, 100% confidence)
        2. Description keyword matching (fast, 90% confidence)
        3. LLM fallback (smart, 85% confidence)
        4. Default (其它, 50% confidence)
        Returns: (category, confidence, method)
        """

        # Stage 1: Person-specific exact mapping
        person_map = self.mapping.get('person_specific_mappings', {}).get(person, {})
        if category in person_map:
            return person_map[category], 1.0, 'dictionary'

        # Stage 2: Description keyword matching
        desc_lower = description.lower()

        # Check description rules
        desc_rules = self.mapping.get('description_rules', {}).get('if_contains', {})
        for pattern, main_cat in desc_rules.items():
            if re.search(pattern, desc_lower, re.IGNORECASE):
                return main_cat, 0.9, 'keyword'

        # Check main category keywords
        for main_cat, cat_data in self.mapping.get('main_categories', {}).items():
            keywords = cat_data.get('description_keywords', [])
            if any(kw.lower() in desc_lower for kw in keywords):
                return main_cat, 0.85, 'keyword'

            english_names = cat_data.get('english', [])
            chinese_names = cat_data.get('chinese', [])
            if any(name.lower() in category.lower() for name in english_names + chinese_names):
                return main_cat, 0.85, 'keyword'

        # Stage 3: LLM fallback (if configured)
        llm_config = self.mapping.get('llm_fallback', {})
        if llm_config.get('enabled', True) and self.llm_engine:
            print(f"    🤖 LLM fallback for: {description[:30]}")
            cat, conf = self.llm_engine.execute('categorize',
                {'category': category, 'description': description})
            return cat, conf, 'llm'

        # Stage 4: Default fallback — warn so user can add missing category to JSON
        print(f"  ⚠️  UNMAPPED CATEGORY: '{category}' (person={person}) → defaulting to 其它")
        print(f"       Add it to category_mapping.json > person_specific_mappings > {person}")
        return '其它', 0.5, 'default'
    
    def batch_categorize(self, transactions: list, person: str = 'peter') -> list:
        """
        Efficiently categorize multiple transactions
        """
        results = []
        dict_matched = 0
        llm_needed = 0
        
        total = len(transactions)
        if total == 0:
            return []

        for tx in transactions:
            cat, conf, method = self.categorize(
                tx.get('category', ''),
                tx.get('description', ''),
                person
            )

            if method in ('dictionary', 'keyword'):
                dict_matched += 1
            elif method == 'llm':
                llm_needed += 1

            results.append({
                **tx,
                'main_category': cat,
                'confidence': conf,
                'method': method
            })

        print(f"  ✅ Dictionary/Keyword: {dict_matched}/{total} ({dict_matched/total*100:.0f}%)")
        if llm_needed > 0:
            print(f"  🤖 LLM: {llm_needed}/{total} ({llm_needed/total*100:.0f}%)")
        
        return results
    
    def _default_mapping(self):
        """Minimal default mapping if file not found"""
        return {
            'person_specific_mappings': {
                'peter': {},
                'wife': {}
            },
            'main_categories': {
                '伙食費': {'english': ['food'], 'chinese': ['伙食'], 'description_keywords': []},
                '交通費': {'english': ['transport'], 'chinese': ['交通'], 'description_keywords': []},
                '休閒/娛樂': {'english': ['entertainment'], 'chinese': ['娛樂'], 'description_keywords': []},
                '家務': {'english': ['household'], 'chinese': ['家務'], 'description_keywords': []},
                '阿幫': {'english': ['pet'], 'chinese': ['寵物'], 'description_keywords': []},
                '其它': {'english': ['other'], 'chinese': ['其他'], 'description_keywords': []}
            },
            'description_rules': {'if_contains': {}},
            'llm_fallback': {'enabled': True, 'confidence_threshold': 0.8}
        }

