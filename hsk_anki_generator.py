#!/usr/bin/env python3
"""
HSK to Anki Deck Generator
Converts HSK vocabulary from JSON to Anki decks using pyAnkiHanzi
"""

import json
import requests
import os
import sys
import csv
import tempfile
import genanki
import time
from typing import Dict, List, Any
import logging
from pathlib import Path
from tqdm import tqdm

# Import your pyAnkiHanzi module
try:
    from pyAnkiHanzi import AnkiHanziGenerator
except ImportError:
    print("❌ Error: pyAnkiHanzi module not found!")
    print("Make sure pyAnkiHanzi.py is in the same directory as this script.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('hsk_anki_generator.log')
    ]
)
logger = logging.getLogger(__name__)

class HSKAnkiGenerator:
    """Generates Anki decks from HSK vocabulary JSON data"""
    
    def __init__(self, json_url: str = None, include_audio: bool = True, language: str = 'zh', cache_dir: str = None):
        """
        Initialize the HSK Anki Generator
        
        Args:
            json_url: URL to the HSK JSON data
            include_audio: Whether to include audio in the cards
            language: Language for TTS (zh, zh-cn, zh-tw)
            cache_dir: Directory to cache audio files (default: ./audio_cache)
        """
        self.json_url = json_url or "https://raw.githubusercontent.com/drkameleon/complete-hsk-vocabulary/refs/heads/main/complete.json"
        self.include_audio = include_audio
        self.language = language
        self.hsk_data = None
        self.temp_files = []
        self.media_files = []
        
        # Audio caching setup
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), "audio_cache")
        if self.include_audio:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Audio cache directory: {self.cache_dir}")
        
        # Track TTS requests to avoid rate limiting
        self.tts_success_count = 0
        self.tts_fail_count = 0
    
    def download_hsk_data(self) -> Dict[str, Any]:
        """Download HSK vocabulary data from JSON URL"""
        logger.info(f"Downloading HSK data from: {self.json_url}")
        
        try:
            response = requests.get(self.json_url, timeout=30)
            response.raise_for_status()
            
            self.hsk_data = response.json()
            logger.info(f"Successfully downloaded HSK data with {len(self.hsk_data)} entries")
            return self.hsk_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to download HSK data: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON data: {e}")
            raise
    
    def analyze_hsk_data(self) -> Dict[int, int]:
        """Analyze the HSK data to understand structure and count entries per level"""
        if not self.hsk_data:
            self.download_hsk_data()
        
        level_counts = {}
        sample_entries = {}
        
        logger.info("Analyzing HSK data structure...")
        
        for entry in self.hsk_data[:5]:  # Show first 5 entries for structure analysis
            logger.info(f"Sample entry: {entry}")
        
        # Count entries per HSK level - data uses 'level' field with values like ['new-2', 'old-3']
        for entry in self.hsk_data:
            if isinstance(entry, dict) and 'level' in entry:
                levels = entry.get('level', [])
                if levels and isinstance(levels, list):
                    for level_str in levels:
                        # Parse level strings like 'new-2', 'old-3', 'new-7+', etc.
                        hsk_level = self._parse_hsk_level(level_str)
                        if hsk_level:
                            level_counts[hsk_level] = level_counts.get(hsk_level, 0) + 1
                            if hsk_level not in sample_entries:
                                sample_entries[hsk_level] = entry
        
        logger.info("HSK Level Distribution:")
        for level in sorted(level_counts.keys()):
            logger.info(f"  HSK {level}: {level_counts[level]} words")
            logger.info(f"  Sample: {sample_entries[level]}")
        
        return level_counts
    
    def _parse_hsk_level(self, level_str: str) -> int:
        """Parse HSK level from strings like 'new-2', 'old-3', 'new-7+', etc."""
        try:
            if not isinstance(level_str, str):
                return None
            
            # Handle formats like 'new-2', 'old-3', 'new-7+', etc.
            if '-' in level_str:
                parts = level_str.split('-')
                if len(parts) >= 2:
                    level_part = parts[1].replace('+', '')  # Remove '+' if present
                    return int(level_part)
            
            return None
        except (ValueError, TypeError, IndexError):
            return None
    
    def create_csv_for_level(self, hsk_level: int) -> str:
        """Create a CSV file for a specific HSK level"""
        if not self.hsk_data:
            self.download_hsk_data()
        
        # Filter entries for this HSK level
        level_entries = []
        for entry in self.hsk_data:
            if isinstance(entry, dict) and 'level' in entry:
                levels = entry.get('level', [])
                if levels and isinstance(levels, list):
                    for level_str in levels:
                        if self._parse_hsk_level(level_str) == hsk_level:
                            level_entries.append(entry)
                            break  # Don't add the same entry multiple times
        
        if not level_entries:
            logger.warning(f"No entries found for HSK level {hsk_level}")
            return None
        
        # Create temporary CSV file
        csv_filename = f"hsk_{hsk_level}_temp.csv"
        
        # Configuration for this level
        config = {
            "deck_id": 2059400100 + hsk_level * 10,
            "name": f"HSK {hsk_level} - Vocabulary"
        }
        
        logger.info(f"Creating CSV for HSK {hsk_level} with {len(level_entries)} words")
        
        with open(csv_filename, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t')
            
            # Write header
            writer.writerow([config["deck_id"], config["name"]])
            
            # Write vocabulary entries
            for entry in level_entries:
                try:
                    # Extract fields from JSON entry
                    simplified = entry.get('simplified', '').strip()
                    forms = entry.get('forms', [])
                    
                    if simplified and forms:
                        # Get the first form for primary data
                        primary_form = forms[0]
                        
                        # Extract meanings and pinyin
                        meanings = primary_form.get('meanings', [])
                        transcriptions = primary_form.get('transcriptions', {})
                        pinyin = transcriptions.get('pinyin', '').strip()
                        
                        if meanings:
                            # Create translation field
                            english = ', '.join(meanings[:3])  # Use first 3 meanings
                            
                            # Combine English and Pinyin for the translation field
                            translation = english
                            if pinyin:
                                translation += f" ({pinyin})"
                            
                            writer.writerow([translation, simplified])
                        else:
                            logger.warning(f"Skipping entry without meanings: {entry}")
                    else:
                        logger.warning(f"Skipping incomplete entry: {entry}")
                        
                except Exception as e:
                    logger.warning(f"Error processing entry {entry}: {e}")
                    continue
        
        self.temp_files.append(csv_filename)
        logger.info(f"Created CSV file: {csv_filename}")
        return csv_filename
    
    def generate_unified_hsk_deck(self, output_file: str = "HSK_Complete.apkg") -> str:
        """Generate a single Anki deck with subdecks for all HSK levels"""
        
        # Analyze data first
        level_counts = self.analyze_hsk_data()
        
        if not level_counts:
            logger.error("No HSK data found!")
            return None
        
        logger.info(f"Creating unified HSK deck with subdecks for {len(level_counts)} levels...")
        
        # Create the main model (shared by all subdecks)
        model = self._create_hsk_model()
        
        # Create main deck and subdecks
        main_deck_id = 2059400000  # Main HSK deck ID
        main_deck = genanki.Deck(main_deck_id, "HSK Complete Vocabulary")
        
        # Dictionary to store subdecks
        subdecks = {}
        
        # Create subdecks for each HSK level
        for hsk_level in sorted(level_counts.keys()):
            subdeck_id = main_deck_id + hsk_level * 100  # e.g., 2059400100, 2059400200, etc.
            subdeck_name = f"HSK Complete Vocabulary::HSK {hsk_level}"
            subdecks[hsk_level] = genanki.Deck(subdeck_id, subdeck_name)
            logger.info(f"Created subdeck: {subdeck_name}")
        
        # Process all entries and add to appropriate subdecks
        total_cards = 0
        for entry in tqdm(self.hsk_data, desc="Processing HSK vocabulary"):
            try:
                if not isinstance(entry, dict) or 'level' not in entry:
                    continue
                
                levels = entry.get('level', [])
                if not levels or not isinstance(levels, list):
                    continue
                
                # Extract card data
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
                english = ', '.join(meanings[:3])  # Use first 3 meanings
                translation = english
                if pinyin:
                    translation += f" ({pinyin})"
                
                # Create audio file if enabled - FIXED: proper Anki format
                mp3_field = ''
                if self.include_audio:
                    mp3_path = self.get_pronunciation_mp3(simplified)
                    if mp3_path:
                        # Use proper Anki sound format: [sound:filename.mp3]
                        mp3_filename = os.path.basename(mp3_path)
                        mp3_field = f'[sound:{mp3_filename}]'
                
                # Add card to all relevant HSK level subdecks
                for level_str in levels:
                    hsk_level = self._parse_hsk_level(level_str)
                    if hsk_level and hsk_level in subdecks:
                        note = genanki.Note(
                            model=model,
                            fields=[translation, simplified, pinyin, mp3_field]
                        )
                        subdecks[hsk_level].add_note(note)
                        total_cards += 1
                
            except Exception as e:
                logger.warning(f"Error processing entry {entry}: {e}")
                continue
        
        # Create package with all subdecks
        all_decks = [main_deck] + list(subdecks.values())
        package = genanki.Package(all_decks)
        
        # Add media files if any
        if self.media_files:
            package.media_files = self.media_files
            logger.info(f"Adding {len(self.media_files)} media files to package")
            # Debug: Log all media files being included
            for media_file in self.media_files:
                logger.debug(f"Including media file: {media_file}")
                # Verify file exists and has content
                if os.path.exists(media_file):
                    file_size = os.path.getsize(media_file)
                    logger.debug(f"  - Size: {file_size} bytes")
                    if file_size == 0:
                        logger.warning(f"  - Warning: Empty file detected: {media_file}")
                else:
                    logger.error(f"  - Error: File not found: {media_file}")

        
        # Write the unified deck file
        try:
            package.write_to_file(output_file)
            logger.info(f"✅ Unified HSK deck created: {output_file}")
            logger.info(f"📊 Total cards: {total_cards}")
            logger.info(f"📁 Subdecks: {len(subdecks)}")
            for level in sorted(subdecks.keys()):
                card_count = len(subdecks[level].notes)
                logger.info(f"   HSK {level}: {card_count} cards")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error writing unified deck: {e}")
            raise
    
    def _create_hsk_model(self) -> genanki.Model:
        """Creates the Anki model for HSK cards (same as pyAnkiHanzi)"""
        from pyAnkiHanzi import DEFAULT_CONFIG
        
        return genanki.Model(
            DEFAULT_CONFIG['model_id'],
            'HSK Hanzi Stroke Order',
            fields=[
                {'name': 'Translation'},
                {'name': 'Hanzi'},
                {'name': 'Pinyin'},
                {'name': 'Mp3'},
            ],
            templates=[
                {
                    'name': 'HSK Hanzi Card',
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
                        <div id="word">{{{{Translation}}}} - {{{{Hanzi}}}} {{{{Pinyin}}}}<br>{{{{Mp3}}}}<br></div>
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
    
    def get_pronunciation_mp3(self, word: str) -> str:
        """Creates an MP3 file for pronunciation with caching and retry logic"""
        if not self.include_audio:
            return None
        
        try:
            # Create cache filename
            safe_word = "".join(c for c in word if c.isalnum() or c in "._-")
            unicode_ids = "_".join(str(ord(char)) for char in word)
            cache_filename = f"{safe_word}_{unicode_ids}_{self.language}.mp3"
            cache_path = os.path.join(self.cache_dir, cache_filename)
            
            # FIXED: Use working directory instead of temp directory for AnkiDroid compatibility
            deck_filename = f"hsk_{unicode_ids}.mp3"
            media_path = os.path.join(os.getcwd(), deck_filename)
            
            # Check if file already exists in cache
            if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
                logger.debug(f"Using cached audio for '{word}': {cache_path}")
                
                import shutil
                shutil.copy2(cache_path, media_path)
                self.media_files.append(media_path)
                self.temp_files.append(media_path)
                logger.debug(f"Copied cached audio to media path: {media_path}")
                return media_path
            
            # Check if we should skip due to previous failures
            fail_marker = cache_path + ".failed"
            if os.path.exists(fail_marker):
                logger.debug(f"Skipping '{word}' due to previous TTS failure")
                return None
            
            # Import here to avoid circular imports
            from gtts import gTTS
            import time
            
            # Add delay to respect rate limits
            if self.tts_success_count > 0 and self.tts_success_count % 10 == 0:
                logger.info(f"TTS progress: {self.tts_success_count} successful, {self.tts_fail_count} failed. Adding delay...")
                time.sleep(2)  # 2 second delay every 10 requests
            
            # Create TTS audio
            logger.debug(f"Creating TTS audio for '{word}'...")
            tts = gTTS(word, lang=self.language)
            tts.save(cache_path)
            
            # Verify the file was created successfully
            if not os.path.exists(cache_path) or os.path.getsize(cache_path) == 0:
                raise Exception("TTS file creation failed")
            
            # FIXED: Copy to working directory for proper Anki media inclusion
            import shutil
            shutil.copy2(cache_path, media_path)
            
            self.media_files.append(media_path)
            self.temp_files.append(media_path)
            self.tts_success_count += 1
            
            logger.debug(f"Successfully created and cached audio for '{word}' at: {media_path}")
            return media_path
            
        except Exception as e:
            self.tts_fail_count += 1
            
            # Create a failure marker to avoid retrying the same word
            try:
                fail_marker = cache_path + ".failed"
                with open(fail_marker, 'w') as f:
                    f.write(f"Failed: {str(e)}\n")
            except:
                pass  # Don't fail if we can't write the marker
            
            # Check if it's a rate limit error
            if "429" in str(e) or "Too Many Requests" in str(e):
                logger.warning(f"Rate limited for '{word}': {e}")
                logger.info("Consider running with --no-audio or trying again later")
            else:
                logger.warning(f"Could not create audio for '{word}': {e}")
            
            return None
    
    def generate_single_deck(self, hsk_level: int, output_file: str = None) -> str:
        """Generate an Anki deck for a single HSK level (compatibility method)"""
        logger.info(f"Generating deck for HSK Level {hsk_level}")
        
        # Create CSV file
        csv_file = self.create_csv_for_level(hsk_level)
        if not csv_file:
            raise ValueError(f"No data found for HSK level {hsk_level}")
        
        # Determine output file
        if not output_file:
            output_file = f"HSK_{hsk_level}.apkg"
        
        # Generate deck using pyAnkiHanzi
        with AnkiHanziGenerator(
            language=self.language,
            include_audio=self.include_audio
        ) as generator:
            deck_file = generator.create_deck(csv_file, output_file)
            logger.info(f"✅ Created deck: {deck_file}")
            return deck_file
    
    def generate_separate_decks(self, output_dir: str = "./decks") -> List[str]:
        """Generate separate Anki deck files for each HSK level (old behavior)"""
        os.makedirs(output_dir, exist_ok=True)
        
        level_counts = self.analyze_hsk_data()
        if not level_counts:
            logger.error("No HSK data found!")
            return []
        
        created_decks = []
        
        for hsk_level in sorted(level_counts.keys()):
            try:
                csv_file = self.create_csv_for_level(hsk_level)
                if not csv_file:
                    continue
                
                output_file = os.path.join(output_dir, f"HSK_{hsk_level}.apkg")
                
                with AnkiHanziGenerator(
                    language=self.language,
                    include_audio=self.include_audio
                ) as generator:
                    deck_file = generator.create_deck(csv_file, output_file)
                    created_decks.append(deck_file)
                    logger.info(f"✅ Created deck: {deck_file}")
                
            except Exception as e:
                logger.error(f"❌ Failed to create deck for HSK {hsk_level}: {e}")
                continue
        
        return created_decks
    
    def cleanup(self):
        """Clean up temporary files (but preserve cache)"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Removed temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Could not remove {temp_file}: {e}")
        
        # Report TTS statistics
        if self.include_audio:
            logger.info(f"TTS Statistics: {self.tts_success_count} successful, {self.tts_fail_count} failed")
            if self.tts_fail_count > 0:
                logger.info(f"Failed audio files can be retried by running the script again")
                logger.info(f"Cache directory: {self.cache_dir}")
    
    def clear_failed_markers(self):
        """Clear all failure markers to retry failed TTS requests"""
        if not os.path.exists(self.cache_dir):
            return
        
        failed_count = 0
        for file in os.listdir(self.cache_dir):
            if file.endswith('.failed'):
                try:
                    os.remove(os.path.join(self.cache_dir, file))
                    failed_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove failure marker {file}: {e}")
        
        if failed_count > 0:
            logger.info(f"Cleared {failed_count} failure markers. Failed TTS requests will be retried.")
    
    def test_tts_connection(self, test_word: str = "你好") -> Dict[str, Any]:
        """Test TTS connection and rate limit status"""
        logger.info(f"Testing TTS connection with word: '{test_word}'")
        
        result = {
            "word": test_word,
            "success": False,
            "error": None,
            "response_time": None,
            "file_size": None,
            "rate_limited": False,
            "timestamp": None
        }
        
        try:
            import time
            from gtts import gTTS
            
            start_time = time.time()
            result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a temporary file for testing
            temp_file = os.path.join(tempfile.gettempdir(), f"tts_test_{int(time.time())}.mp3")
            
            # Attempt TTS request
            tts = gTTS(test_word, lang=self.language)
            tts.save(temp_file)
            
            end_time = time.time()
            result["response_time"] = end_time - start_time
            
            # Check if file was created successfully
            if os.path.exists(temp_file):
                result["file_size"] = os.path.getsize(temp_file)
                result["success"] = True
                logger.info(f"✅ TTS test successful: {result['response_time']:.2f}s, {result['file_size']} bytes")
                os.remove(temp_file)  # Clean up
            else:
                result["error"] = "File not created"
                logger.error("❌ TTS test failed: File not created")
                
        except Exception as e:
            error_str = str(e)
            result["error"] = error_str
            
            # Check for different types of errors
            if "429" in error_str or "Too Many Requests" in error_str:
                result["rate_limited"] = True
                logger.error(f"❌ TTS Rate Limited: {error_str}")
            elif "403" in error_str or "Forbidden" in error_str:
                logger.error(f"❌ TTS Forbidden: {error_str}")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                logger.error(f"❌ TTS Network Error: {error_str}")
            else:
                logger.error(f"❌ TTS Unknown Error: {error_str}")
        
        return result
    
    def run_tts_stress_test(self, num_tests: int = 5, delay: float = 1.0) -> List[Dict[str, Any]]:
        """Run multiple TTS tests to understand rate limiting behavior"""
        test_words = ["你好", "谢谢", "再见", "学习", "汉字"]
        results = []
        
        logger.info(f"Running TTS stress test with {num_tests} requests, {delay}s delay")
        
        for i in range(num_tests):
            if i > 0:
                time.sleep(delay)
            
            word = test_words[i % len(test_words)]
            result = self.test_tts_connection(word)
            results.append(result)
            
            logger.info(f"Test {i+1}/{num_tests}: {'✅' if result['success'] else '❌'} {word}")
            
            # Stop if we hit rate limit
            if result["rate_limited"]:
                logger.warning(f"Rate limit hit on test {i+1}, stopping stress test")
                break
        
        return results
    
    def analyze_rate_limit_pattern(self) -> Dict[str, Any]:
        """Analyze rate limiting patterns and suggest solutions"""
        logger.info("Analyzing rate limit patterns...")
        
        # Test with different delays
        test_results = []
        delays = [0.1, 0.5, 1.0, 2.0, 5.0]
        
        for delay in delays:
            if delay > 0:
                logger.info(f"Testing with {delay}s delay...")
                results = self.run_tts_stress_test(num_tests=3, delay=delay)
                success_rate = sum(1 for r in results if r["success"]) / len(results)
                test_results.append({
                    "delay": delay,
                    "success_rate": success_rate,
                    "results": results
                })
                
                if success_rate == 1.0:
                    logger.info(f"✅ Found working delay: {delay}s")
                    break
            else:
                # Test without delay
                results = self.run_tts_stress_test(num_tests=3, delay=0)
                success_rate = sum(1 for r in results if r["success"]) / len(results)
                test_results.append({
                    "delay": delay,
                    "success_rate": success_rate,
                    "results": results
                })
        
        # Analysis
        analysis = {
            "test_results": test_results,
            "recommendations": [],
            "working_delay": None,
            "total_blocked": True
        }
        
        # Find working delay
        for test in test_results:
            if test["success_rate"] > 0:
                analysis["total_blocked"] = False
                if test["success_rate"] == 1.0:
                    analysis["working_delay"] = test["delay"]
                    break
        
        # Generate recommendations
        if analysis["total_blocked"]:
            analysis["recommendations"].extend([
                "TTS service appears to be completely blocked",
                "Try again in a few hours or tomorrow",
                "Consider using --no-audio for now",
                "Check if your IP is blocked",
                "Try using a VPN or different network"
            ])
        elif analysis["working_delay"] is not None:
            analysis["recommendations"].extend([
                f"Use a delay of {analysis['working_delay']}s between requests",
                "Consider running with smaller batches",
                "The rate limit appears to be strict but not permanent"
            ])
        else:
            analysis["recommendations"].extend([
                "Partial blocking detected",
                "Try longer delays (10-30 seconds)",
                "Consider running overnight with very slow requests",
                "Use --no-audio for immediate results"
            ])
        
        return analysis
    
    def get_cache_stats(self):
        """Get statistics about the audio cache"""
        if not os.path.exists(self.cache_dir):
            return {"cached": 0, "failed": 0, "total_size": 0}
        
        cached_count = 0
        failed_count = 0
        total_size = 0
        
        for file in os.listdir(self.cache_dir):
            if file.endswith('.mp3'):
                cached_count += 1
                file_path = os.path.join(self.cache_dir, file)
                total_size += os.path.getsize(file_path)
            elif file.endswith('.failed'):
                failed_count += 1
        
        return {
            "cached": cached_count,
            "failed": failed_count,
            "total_size": total_size,
            "size_mb": total_size / (1024 * 1024)
        }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate Anki decks from HSK vocabulary JSON data'
    )
    parser.add_argument('--unified', action='store_true', default=True,
                       help='Generate one unified deck with subdecks (default)')
    parser.add_argument('--separate', action='store_true',
                       help='Generate separate deck files for each level')
    parser.add_argument('--level', type=int, choices=range(1, 10),
                       help='Generate deck for specific HSK level (1-9)')
    parser.add_argument('--no-audio', action='store_true',
                       help='Do not include audio files')
    parser.add_argument('--language', default='zh',
                       choices=['zh', 'zh-cn', 'zh-tw'],
                       help='Language for TTS (default: zh)')
    parser.add_argument('--output', default='HSK_Complete.apkg',
                       help='Output file name (default: HSK_Complete.apkg)')
    parser.add_argument('--cache-dir', default='./audio_cache',
                       help='Directory for audio cache (default: ./audio_cache)')
    parser.add_argument('--clear-failed', action='store_true',
                       help='Clear failure markers to retry failed TTS requests')
    parser.add_argument('--test-tts', action='store_true',
                       help='Test TTS connection and rate limit status')
    parser.add_argument('--stress-test', type=int, metavar='N',
                       help='Run N TTS stress tests to analyze rate limits')
    parser.add_argument('--analyze-limits', action='store_true',
                       help='Analyze rate limiting patterns and suggest solutions')
    parser.add_argument('--test-word', default='你好',
                       help='Word to use for TTS testing (default: 你好)')
    parser.add_argument('--cache-stats', action='store_true',
                       help='Show audio cache statistics')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze the JSON data without creating decks')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Adjust logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        with HSKAnkiGenerator(
            include_audio=not args.no_audio,
            language=args.language,
            cache_dir=args.cache_dir
        ) as generator:
            
            if args.test_tts:
                result = generator.test_tts_connection(args.test_word)
                print(f"🔍 TTS Test Results:")
                print(f"  Word: {result['word']}")
                print(f"  Success: {'✅' if result['success'] else '❌'}")
                print(f"  Response Time: {result['response_time']:.2f}s" if result['response_time'] else "  Response Time: N/A")
                print(f"  File Size: {result['file_size']} bytes" if result['file_size'] else "  File Size: N/A")
                print(f"  Rate Limited: {'⚠️  Yes' if result['rate_limited'] else '✅ No'}")
                print(f"  Timestamp: {result['timestamp']}")
                if result['error']:
                    print(f"  Error: {result['error']}")
                return
            
            if args.stress_test:
                results = generator.run_tts_stress_test(args.stress_test, delay=1.0)
                success_count = sum(1 for r in results if r["success"])
                print(f"🧪 Stress Test Results:")
                print(f"  Tests: {len(results)}")
                print(f"  Success: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
                print(f"  Rate Limited: {sum(1 for r in results if r['rate_limited'])}")
                return
            
            if args.analyze_limits:
                analysis = generator.analyze_rate_limit_pattern()
                print(f"📊 Rate Limit Analysis:")
                print(f"  Total Blocked: {'❌ Yes' if analysis['total_blocked'] else '✅ No'}")
                print(f"  Working Delay: {analysis['working_delay']}s" if analysis['working_delay'] else "  Working Delay: None found")
                print(f"📋 Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"  • {rec}")
                return
            
            if args.cache_stats:
                stats = generator.get_cache_stats()
                print(f"📊 Audio Cache Statistics:")
                print(f"  Cached files: {stats['cached']}")
                print(f"  Failed markers: {stats['failed']}")
                print(f"  Total size: {stats['size_mb']:.1f} MB")
                print(f"  Cache directory: {generator.cache_dir}")
                return
            
            if args.clear_failed:
                generator.clear_failed_markers()
                return
            
            if args.analyze_only:
                logger.info("Analyzing HSK data...")
                generator.analyze_hsk_data()
                return
            
            if args.level:
                # Generate single level (using old method for compatibility)
                output_file = f"HSK_{args.level}.apkg"
                generator.generate_single_deck(args.level, output_file)
                print(f"✅ Successfully created HSK {args.level} deck: {output_file}")
                
            elif args.separate:
                # Generate separate decks for each level
                created_decks = generator.generate_separate_decks()
                print(f"✅ Successfully created {len(created_decks)} separate HSK decks:")
                for deck in created_decks:
                    print(f"  - {deck}")
                    
            else:
                # Default: Generate unified deck with subdecks
                unified_deck = generator.generate_unified_hsk_deck(args.output)
                if unified_deck:
                    print(f"✅ Successfully created unified HSK deck: {unified_deck}")
                    print("📁 Contains subdecks for all HSK levels (1-9)")
                    
                    # Show cache statistics
                    stats = generator.get_cache_stats()
                    print(f"📊 Audio: {stats['cached']} cached, {generator.tts_fail_count} failed")
                else:
                    print("❌ Failed to create unified HSK deck")
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
