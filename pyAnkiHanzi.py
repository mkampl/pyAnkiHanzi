#!/usr/bin/env python3
"""
pyAnkiHanzi - Creates Anki cards for Chinese characters with stroke order animations
"""

import genanki
from gtts import gTTS
from pypinyin import pinyin, Style
import os
import csv
import sys
import argparse
import logging
import tempfile
import shutil
from typing import List, Tuple, Optional
from tqdm import tqdm

# Configuration
DEFAULT_CONFIG = {
    'model_id': 1607392319,
    'hanzi_writer_version': '2.2',
    'stroke_animation_speed': 1,
    'delay_between_strokes': 150,
    'character_width': 250,
    'character_height': 250,
    'template_file': 'hanzi_template.json'
}

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pyankihanzi.log')
    ]
)
logger = logging.getLogger(__name__)


class AnkiHanziGenerator:
    """Main class for creating Anki cards for Chinese characters"""
    
    def __init__(self, language: str = 'zh', include_audio: bool = True, template_file: str = None):
        self.language = language
        self.include_audio = include_audio
        self.template_file = template_file or DEFAULT_CONFIG['template_file']
        self.temp_dir = tempfile.mkdtemp(prefix='pyankihanzi_')
        self.media_files = []
        logger.info(f"Initialized with language: {language}, audio: {include_audio}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def cleanup(self):
        """Cleans up temporary files and directories"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Could not clean up temporary directory: {e}")
    
    def load_template(self) -> Tuple[str, str]:
        """
        Loads HTML template from file and extracts question and answer formats.
        
        Returns:
            Tuple of (question_format, answer_format)
        """
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                import json
                template_data = json.load(f)
            
            # Replace placeholders with actual values in both qfmt and afmt
            qfmt = template_data['qfmt']
            afmt = template_data['afmt']
            
            # Replace placeholders
            replacements = {
                '__HANZI_WRITER_VERSION__': DEFAULT_CONFIG['hanzi_writer_version'],
                '__STROKE_ANIMATION_SPEED__': str(DEFAULT_CONFIG['stroke_animation_speed']),
                '__DELAY_BETWEEN_STROKES__': str(DEFAULT_CONFIG['delay_between_strokes']),
                '__CHARACTER_WIDTH__': str(DEFAULT_CONFIG['character_width']),
                '__CHARACTER_HEIGHT__': str(DEFAULT_CONFIG['character_height'])
            }
            
            for placeholder, value in replacements.items():
                qfmt = qfmt.replace(placeholder, value)
                afmt = afmt.replace(placeholder, value)
            
            return qfmt, afmt
            
        except FileNotFoundError:
            logger.error(f"Template file {self.template_file} not found")
            raise
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            raise
    
    def validate_csv_format(self, csv_filename: str) -> bool:
        """Validates CSV format before processing"""
        if not csv_filename.endswith('.csv'):
            logger.error("File must be a .csv file")
            return False
        
        if not os.path.exists(csv_filename):
            logger.error(f"File {csv_filename} does not exist")
            return False
        
        if os.path.getsize(csv_filename) == 0:
            logger.error(f"File {csv_filename} is empty")
            return False
        
        return True
    
    def read_hanzi_words(self, csv_filename: str) -> Tuple[int, str, List[List[str]]]:
        """
        Reads Chinese words from a CSV file.
        
        Args:
            csv_filename: Path to CSV file
            
        Returns:
            Tuple of (deck number, deck name, list of words)
            
        Raises:
            ValueError: For invalid CSV format
            FileNotFoundError: When file is not found
        """
        try:
            hanzi_words = []
            with open(csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                try:
                    header = next(reader)
                    if len(header) < 2:
                        raise ValueError("Header must have at least 2 columns")
                    deck_number = int(header[0])
                    deck_name = header[1]
                    logger.info(f"Found deck: {deck_name} (ID: {deck_number})")
                except (ValueError, StopIteration) as e:
                    logger.error(f"Error reading header: {e}")
                    raise ValueError(f"Invalid CSV format: {e}")
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) >= 2:
                        # Remove whitespace and check for empty values
                        translation = row[0].strip()
                        hanzi = row[1].strip()
                        if translation and hanzi:
                            hanzi_words.append([translation, hanzi])
                        else:
                            logger.warning(f"Row {row_num} skipped (empty values)")
                    else:
                        logger.warning(f"Row {row_num} skipped (incomplete)")
            
            if not hanzi_words:
                raise ValueError("No valid words found in CSV file")
            
            logger.info(f"{len(hanzi_words)} words successfully read")
            return deck_number, deck_name, hanzi_words
        
        except FileNotFoundError:
            logger.error(f"File {csv_filename} not found")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def check_duplicates(self, hanzi_words: List[List[str]]) -> List[Tuple[int, str, str]]:
        """Checks for duplicate entries"""
        seen = set()
        duplicates = []
        for i, (translation, hanzi) in enumerate(hanzi_words):
            key = (translation.lower(), hanzi)
            if key in seen:
                duplicates.append((i+1, translation, hanzi))
                logger.warning(f"Duplicate found: {translation} - {hanzi}")
            seen.add(key)
        return duplicates
    
    def get_pronunciation_mp3(self, word: str) -> Optional[str]:
        """
        Creates an MP3 file for the pronunciation of a Chinese word.
        
        Args:
            word: Chinese word
            
        Returns:
            Path to MP3 file or None on errors
        """
        if not self.include_audio:
            return None
        
        try:
            unicode_ids = "_".join(str(ord(char)) for char in word)
            mp3_filename = os.path.join(self.temp_dir, f"{unicode_ids}_pronunciation.mp3")
            
            tts = gTTS(word, lang=self.language)
            tts.save(mp3_filename)
            
            self.media_files.append(mp3_filename)
            return mp3_filename
        except Exception as e:
            logger.warning(f"Could not create audio for '{word}': {e}")
            return None
    
    def get_pinyin_with_tones(self, word: str) -> str:
        """
        Converts Chinese characters to Pinyin with tones.
        
        Args:
            word: Chinese characters as string
            
        Returns:
            Pinyin string with tones, separated by spaces
            
        Example:
            >>> get_pinyin_with_tones("你好")
            'nǐ hǎo'
        """
        try:
            pinyin_with_tone = pinyin(word, style=Style.TONE)
            return ' '.join([item[0] for item in pinyin_with_tone])
        except Exception as e:
            logger.warning(f"Could not create Pinyin for '{word}': {e}")
            return word  # Fallback to original word
    
    def create_model(self) -> genanki.Model:
        """Creates the Anki model for the cards"""
        qfmt, afmt = self.load_template()
        
        return genanki.Model(
            DEFAULT_CONFIG['model_id'],
            'Hanzi Stroke Order Online JS',
            fields=[
                {'name': 'Translation'},
                {'name': 'Hanzi'},
                {'name': 'Pinyin'},
                {'name': 'Mp3'},
            ],
            templates=[
                {
                    'name': 'Hanzi Card',
                    'qfmt': qfmt,
                    'afmt': afmt,
                },
            ],
        )
    
    def create_deck(self, csv_filename: str, output_file: Optional[str] = None) -> str:
        """
        Creates an Anki deck from a CSV file.
        
        Args:
            csv_filename: Path to CSV input file
            output_file: Path to output file (optional)
            
        Returns:
            Path to created .apkg file
        """
        # Validation
        if not self.validate_csv_format(csv_filename):
            raise ValueError("Invalid CSV format")
        
        # Read data
        deck_number, deck_name, hanzi_words = self.read_hanzi_words(csv_filename)
        
        # Check duplicates
        duplicates = self.check_duplicates(hanzi_words)
        if duplicates:
            logger.warning(f"{len(duplicates)} duplicates found")
        
        # Create model and deck
        model = self.create_model()
        deck = genanki.Deck(deck_number, deck_name)
        
        # Create cards
        logger.info("Creating Anki cards...")
        for translation, hanzi in tqdm(hanzi_words, desc="Creating cards"):
            try:
                pinyin_str = self.get_pinyin_with_tones(hanzi)
                mp3_path = self.get_pronunciation_mp3(hanzi)
                
                mp3_field = f'[sound:{os.path.basename(mp3_path)}]' if mp3_path else ''
                
                note = genanki.Note(
                    model=model,
                    fields=[translation, hanzi, pinyin_str, mp3_field]
                )
                deck.add_note(note)
            except Exception as e:
                logger.error(f"Error creating card for '{hanzi}': {e}")
                continue
        
        # Create package
        package = genanki.Package(deck)
        if self.media_files:
            package.media_files = self.media_files
        
        # Determine output file
        if not output_file:
            output_file = csv_filename.replace('.csv', '.apkg')
        
        # Write file
        try:
            package.write_to_file(output_file)
            logger.info(f"Deck successfully created: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            raise


def parse_arguments():
    """Parses command line arguments"""
    parser = argparse.ArgumentParser(
        description='Creates Anki cards for Chinese characters with stroke order animations'
    )
    parser.add_argument('input_file', help='CSV input file')
    parser.add_argument('--no-audio', action='store_true', 
                       help='Do not create audio files')
    parser.add_argument('--language', default='zh', 
                       choices=['zh', 'zh-cn', 'zh-tw'], 
                       help='Language for TTS (default: zh)')
    parser.add_argument('--output', 
                       help='Output file (default: based on input file)')
    parser.add_argument('--template', 
                       help='HTML template file (default: hanzi_template.html)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()
    
    # Adjust logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        with AnkiHanziGenerator(
            language=args.language,
            include_audio=not args.no_audio,
            template_file=args.template
        ) as generator:
            output_file = generator.create_deck(args.input_file, args.output)
            print(f"✅ Deck successfully created: {output_file}")
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
