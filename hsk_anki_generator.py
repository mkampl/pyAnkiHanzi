#!/usr/bin/env python3
"""
HSK CSV Generator - Minimal script to create CSV from HSK JSON for pyAnkiHanzi
"""

import json
import requests
import os
import sys
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

JSON_URL = "https://raw.githubusercontent.com/drkameleon/complete-hsk-vocabulary/refs/heads/main/complete.json"
JSON_FILE = "hsk_complete.json"
CSV_FILE = "hsk_complete.csv"

def download_json_if_needed():
    """Download JSON file if not present in folder"""
    if os.path.exists(JSON_FILE):
        logger.info(f"Using existing JSON file: {JSON_FILE}")
        return
    
    logger.info(f"Downloading HSK data from: {JSON_URL}")
    try:
        response = requests.get(JSON_URL, timeout=30)
        response.raise_for_status()
        
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Downloaded and saved: {JSON_FILE}")
    except Exception as e:
        logger.error(f"Failed to download JSON: {e}")
        sys.exit(1)

def parse_hsk_level(level_str: str) -> int:
    """Parse HSK level from strings like 'new-2', 'old-3', etc."""
    try:
        if not isinstance(level_str, str) or '-' not in level_str:
            return None
        parts = level_str.split('-')
        if len(parts) >= 2:
            level_part = parts[1].replace('+', '')
            return int(level_part)
        return None
    except (ValueError, TypeError, IndexError):
        return None

def create_csv_from_json():
    """Create CSV with subdecks from HSK JSON data"""
    logger.info(f"Reading JSON file: {JSON_FILE}")
    
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            hsk_data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON file: {e}")
        sys.exit(1)
    
    logger.info(f"Loaded {len(hsk_data)} HSK entries")
    
    # Organize words by HSK level
    hsk_levels = {}
    
    for entry in hsk_data:
        if not isinstance(entry, dict) or 'level' not in entry:
            continue
        
        levels = entry.get('level', [])
        if not levels or not isinstance(levels, list):
            continue
        
        # Extract word data
        simplified = entry.get('simplified', '').strip()
        forms = entry.get('forms', [])
        
        if not simplified or not forms:
            continue
        
        primary_form = forms[0]
        meanings = primary_form.get('meanings', [])
        transcriptions = primary_form.get('transcriptions', {})
        pinyin = transcriptions.get('pinyin', '').strip()
        
        if not meanings:
            continue
        
        # Create translation field
        english = ', '.join(meanings[:2])  # Use first 3 meanings
        translation = english
        #if pinyin:
        #    translation += f" ({pinyin})"
        
        # Add to all relevant HSK levels
        for level_str in levels:
            hsk_level = parse_hsk_level(level_str)
            if hsk_level:
                if hsk_level not in hsk_levels:
                    hsk_levels[hsk_level] = []
                hsk_levels[hsk_level].append([translation, simplified])
    
    # Write CSV file
    logger.info(f"Creating CSV file: {CSV_FILE}")
    
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        # Write deck header
        f.write("#2059400000\tHSK Complete Vocabulary\n")
        
        # Write each HSK level as subdeck
        for level in sorted(hsk_levels.keys()):
            words = hsk_levels[level]
            logger.info(f"HSK {level}: {len(words)} words")
            
            # Write subdeck header
            f.write(f"##HSK {level}\n")
            
            # Write words for this level
            for translation, hanzi in words:
                f.write(f"{translation}\t{hanzi}\n")
    
    total_words = sum(len(words) for words in hsk_levels.values())
    logger.info(f"✅ Created {CSV_FILE} with {len(hsk_levels)} subdecks and {total_words} total words")
    
    # Show statistics
    for level in sorted(hsk_levels.keys()):
        logger.info(f"  HSK {level}: {len(hsk_levels[level])} words")

def main():
    """Main function"""
    logger.info("HSK CSV Generator - Creating CSV for pyAnkiHanzi")
    
    # Download JSON if needed
    download_json_if_needed()
    
    # Create CSV from JSON
    create_csv_from_json()
    
    logger.info(f"✅ Done! Now run: python pyAnkiHanzi.py {CSV_FILE}")

if __name__ == '__main__':
    main()
