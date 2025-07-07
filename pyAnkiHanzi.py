#!/usr/bin/env python3
"""
pyAnkiHanzi - Erstellt Anki-Karten für chinesische Zeichen mit Strichfolgen-Animation
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

# Konfiguration
DEFAULT_CONFIG = {
    'model_id': 1607392319,
    'hanzi_writer_version': '2.2',
    'stroke_animation_speed': 1,
    'delay_between_strokes': 150,
    'character_width': 250,
    'character_height': 250
}

# Logging-Konfiguration
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
    """Hauptklasse für die Erstellung von Anki-Karten für chinesische Zeichen"""
    
    def __init__(self, language: str = 'zh', include_audio: bool = True):
        self.language = language
        self.include_audio = include_audio
        self.temp_dir = tempfile.mkdtemp(prefix='pyankihanzi_')
        self.media_files = []
        logger.info(f"Initialisiert mit Sprache: {language}, Audio: {include_audio}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def cleanup(self):
        """Räumt temporäre Dateien und Verzeichnisse auf"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Temporäres Verzeichnis {self.temp_dir} aufgeräumt")
        except Exception as e:
            logger.warning(f"Konnte temporäres Verzeichnis nicht aufräumen: {e}")
    
    def validate_csv_format(self, csv_filename: str) -> bool:
        """Validiert das CSV-Format vor der Verarbeitung"""
        if not csv_filename.endswith('.csv'):
            logger.error("Datei muss eine .csv-Datei sein")
            return False
        
        if not os.path.exists(csv_filename):
            logger.error(f"Datei {csv_filename} existiert nicht")
            return False
        
        if os.path.getsize(csv_filename) == 0:
            logger.error(f"Datei {csv_filename} ist leer")
            return False
        
        return True
    
    def read_hanzi_words(self, csv_filename: str) -> Tuple[int, str, List[List[str]]]:
        """
        Liest chinesische Wörter aus einer CSV-Datei.
        
        Args:
            csv_filename: Pfad zur CSV-Datei
            
        Returns:
            Tupel aus (Deck-Nummer, Deck-Name, Liste der Wörter)
            
        Raises:
            ValueError: Bei ungültigem CSV-Format
            FileNotFoundError: Wenn Datei nicht gefunden wird
        """
        try:
            hanzi_words = []
            with open(csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                try:
                    header = next(reader)
                    if len(header) < 2:
                        raise ValueError("Header muss mindestens 2 Spalten haben")
                    deck_number = int(header[0])
                    deck_name = header[1]
                    logger.info(f"Deck gefunden: {deck_name} (ID: {deck_number})")
                except (ValueError, StopIteration) as e:
                    logger.error(f"Fehler beim Lesen der Header: {e}")
                    raise ValueError(f"Ungültiges CSV-Format: {e}")
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) >= 2:
                        # Entferne Leerzeichen und prüfe auf leere Werte
                        translation = row[0].strip()
                        hanzi = row[1].strip()
                        if translation and hanzi:
                            hanzi_words.append([translation, hanzi])
                        else:
                            logger.warning(f"Zeile {row_num} übersprungen (leere Werte)")
                    else:
                        logger.warning(f"Zeile {row_num} übersprungen (unvollständig)")
            
            if not hanzi_words:
                raise ValueError("Keine gültigen Wörter in der CSV-Datei gefunden")
            
            logger.info(f"{len(hanzi_words)} Wörter erfolgreich gelesen")
            return deck_number, deck_name, hanzi_words
        
        except FileNotFoundError:
            logger.error(f"Datei {csv_filename} nicht gefunden")
            raise
        except Exception as e:
            logger.error(f"Fehler beim Lesen der CSV-Datei: {e}")
            raise
    
    def check_duplicates(self, hanzi_words: List[List[str]]) -> List[Tuple[int, str, str]]:
        """Prüft auf doppelte Einträge"""
        seen = set()
        duplicates = []
        for i, (translation, hanzi) in enumerate(hanzi_words):
            key = (translation.lower(), hanzi)
            if key in seen:
                duplicates.append((i+1, translation, hanzi))
                logger.warning(f"Duplikat gefunden: {translation} - {hanzi}")
            seen.add(key)
        return duplicates
    
    def get_pronunciation_mp3(self, word: str) -> Optional[str]:
        """
        Erstellt eine MP3-Datei für die Aussprache eines chinesischen Wortes.
        
        Args:
            word: Chinesisches Wort
            
        Returns:
            Pfad zur MP3-Datei oder None bei Fehlern
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
            logger.warning(f"Konnte Audio für '{word}' nicht erstellen: {e}")
            return None
    
    def get_pinyin_with_tones(self, word: str) -> str:
        """
        Konvertiert chinesische Zeichen zu Pinyin mit Tönen.
        
        Args:
            word: Chinesische Zeichen als String
            
        Returns:
            Pinyin-String mit Tönen, durch Leerzeichen getrennt
            
        Example:
            >>> get_pinyin_with_tones("你好")
            'nǐ hǎo'
        """
        try:
            pinyin_with_tone = pinyin(word, style=Style.TONE)
            return ' '.join([item[0] for item in pinyin_with_tone])
        except Exception as e:
            logger.warning(f"Konnte Pinyin für '{word}' nicht erstellen: {e}")
            return word  # Fallback zum ursprünglichen Wort
    
    def create_model(self) -> genanki.Model:
        """Erstellt das Anki-Modell für die Karten"""
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
                    'qfmt': f'''
                        <div id="translation">{{{{Translation}}}}</div>
                        <div id="target-quiz"></div>
                        <script type="text/javascript">
                            var characters = "{{{{Hanzi}}}}".split("");
                            var js = document.createElement("script");
                            js.type = "text/javascript";
                            js.src = "https://cdn.jsdelivr.net/npm/hanzi-writer@{DEFAULT_CONFIG['hanzi_writer_version']}/dist/hanzi-writer.min.js";
                            js.onload = function() {{
                                for (let x of characters) {{
                                    var characterContainer = document.createElement('div');
                                    characterContainer.style.display = 'inline-block';
                                    characterContainer.style.border = '2px solid black';
                                    characterContainer.style.margin = '2px';

                                    var writer = HanziWriter.create(characterContainer, x, {{
                                        width: {DEFAULT_CONFIG['character_width']},
                                        height: {DEFAULT_CONFIG['character_height']},
                                        showCharacter: false,
                                        showOutline: false,
                                        showHintAfterMisses: 1,
                                        highlightOnComplete: false,
                                        padding: 5
                                    }});

                                    writer.quiz({{
                                        onMistake: function() {{ console.log("Mistake!"); }},
                                        onComplete: function() {{ console.log("Completed!"); }}
                                    }});

                                    document.getElementById('target-quiz').appendChild(characterContainer);
                                }}
                            }};
                            document.body.appendChild(js);
                        </script>
                    ''',
                    'afmt': f'''
                        <div id="word">{{{{Translation}}}} - {{{{Hanzi}}}} {{{{Pinyin}}}} <br>{{{{Mp3}}}}<br></div>
                        <hr id="answer">
                        <div id="target-animation"></div>
                        <script type="text/javascript">
                            var characters = "{{{{Hanzi}}}}".split("");
                            var js = document.createElement("script");
                            js.type = "text/javascript";
                            js.src = "https://cdn.jsdelivr.net/npm/hanzi-writer@{DEFAULT_CONFIG['hanzi_writer_version']}/dist/hanzi-writer.min.js";
                            js.onload = function() {{
                                for (let x of characters) {{
                                    var writer = HanziWriter.create('target-animation', x, {{
                                        width: 70,
                                        height: 70,
                                        padding: 5,   
                                        showOutline: true,
                                        strokeAnimationSpeed: {DEFAULT_CONFIG['stroke_animation_speed']}, 
                                        delayBetweenStrokes: {DEFAULT_CONFIG['delay_between_strokes']},
                                        radicalColor: '#337ab7'
                                    }});
                                    writer.loopCharacterAnimation();
                                }}
                            }};
                            document.body.appendChild(js);
                        </script>
                    ''',
                },
            ],
        )
    
    def create_deck(self, csv_filename: str, output_file: Optional[str] = None) -> str:
        """
        Erstellt ein Anki-Deck aus einer CSV-Datei.
        
        Args:
            csv_filename: Pfad zur CSV-Eingabedatei
            output_file: Pfad zur Ausgabedatei (optional)
            
        Returns:
            Pfad zur erstellten .apkg-Datei
        """
        # Validierung
        if not self.validate_csv_format(csv_filename):
            raise ValueError("Ungültiges CSV-Format")
        
        # Daten lesen
        deck_number, deck_name, hanzi_words = self.read_hanzi_words(csv_filename)
        
        # Duplikate prüfen
        duplicates = self.check_duplicates(hanzi_words)
        if duplicates:
            logger.warning(f"{len(duplicates)} Duplikate gefunden")
        
        # Modell und Deck erstellen
        model = self.create_model()
        deck = genanki.Deck(deck_number, deck_name)
        
        # Karten erstellen
        logger.info("Erstelle Anki-Karten...")
        for translation, hanzi in tqdm(hanzi_words, desc="Erstelle Karten"):
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
                logger.error(f"Fehler beim Erstellen der Karte für '{hanzi}': {e}")
                continue
        
        # Package erstellen
        package = genanki.Package(deck)
        if self.media_files:
            package.media_files = self.media_files
        
        # Ausgabedatei bestimmen
        if not output_file:
            output_file = csv_filename.replace('.csv', '.apkg')
        
        # Datei schreiben
        try:
            package.write_to_file(output_file)
            logger.info(f"Deck erfolgreich erstellt: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Fehler beim Schreiben der Ausgabedatei: {e}")
            raise


def parse_arguments():
    """Parst Kommandozeilenargumente"""
    parser = argparse.ArgumentParser(
        description='Erstellt Anki-Karten für chinesische Zeichen mit Strichfolgen-Animation'
    )
    parser.add_argument('input_file', help='CSV-Eingabedatei')
    parser.add_argument('--no-audio', action='store_true', 
                       help='Keine Audio-Dateien erstellen')
    parser.add_argument('--language', default='zh', 
                       choices=['zh', 'zh-cn', 'zh-tw'], 
                       help='Sprache für TTS (Standard: zh)')
    parser.add_argument('--output', 
                       help='Ausgabedatei (Standard: basierend auf Eingabedatei)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Ausführliche Ausgabe')
    return parser.parse_args()


def main():
    """Hauptfunktion"""
    args = parse_arguments()
    
    # Logging-Level anpassen
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        with AnkiHanziGenerator(
            language=args.language,
            include_audio=not args.no_audio
        ) as generator:
            output_file = generator.create_deck(args.input_file, args.output)
            print(f"✅ Deck erfolgreich erstellt: {output_file}")
    
    except KeyboardInterrupt:
        logger.info("Vorgang vom Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fehler: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
