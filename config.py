"""
Configuration file for pyAnkiHanzi
"""

# Anki model configuration
ANKI_CONFIG = {
    'model_id': 1607392319,
    'model_name': 'Hanzi Stroke Order Online JS',
    'hanzi_writer_version': '2.2',
}

# HanziWriter configuration
HANZI_WRITER_CONFIG = {
    'quiz': {
        'character_width': 250,
        'character_height': 250,
        'show_character': False,
        'show_outline': False,
        'show_hint_after_misses': 1,
        'highlight_on_complete': False,
        'padding': 5
    },
    'animation': {
        'character_width': 70,
        'character_height': 70,
        'padding': 5,
        'show_outline': True,
        'stroke_animation_speed': 1,
        'delay_between_strokes': 150,
        'radical_color': '#337ab7'
    }
}

# TTS configuration
TTS_CONFIG = {
    'default_language': 'zh',
    'supported_languages': ['zh', 'zh-cn', 'zh-tw'],
    'retry_attempts': 3,
    'timeout': 10
}

# General configuration
GENERAL_CONFIG = {
    'log_file': 'pyankihanzi.log',
    'temp_dir_prefix': 'pyankihanzi_',
    'supported_formats': ['.csv'],
    'csv_delimiter': '\t',
    'encoding': 'utf-8'
}

# Validation configuration
VALIDATION_CONFIG = {
    'min_header_columns': 2,
    'required_row_columns': 2,
    'max_file_size_mb': 100,
    'max_cards_per_deck': 10000
}
