#!/usr/bin/env python3
"""
Test script for pyAnkiHanzi
"""

import unittest
import tempfile
import os
import sys
import shutil
from unittest.mock import patch, MagicMock

# Add main module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from pyAnkiHanzi import AnkiHanziGenerator
except ImportError:
    print("Warning: pyAnkiHanzi could not be imported. Make sure the file is in the same directory.")
    sys.exit(1)


class TestAnkiHanziGenerator(unittest.TestCase):
    """Tests for the AnkiHanziGenerator class"""
    
    def setUp(self):
        """Setup for each test"""
        self.generator = AnkiHanziGenerator()
        self.test_csv = self.create_test_csv()
    
    def tearDown(self):
        """Cleanup after each test"""
        if os.path.exists(self.test_csv):
            os.unlink(self.test_csv)
        self.generator.cleanup()
    
    def create_test_csv(self):
        """Creates a test CSV file with new format"""
        content = "#123456\tTest Deck\nHello\t你好\nThank you\t谢谢\nGoodbye\t再见\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def create_subdeck_csv(self):
        """Creates a test CSV file with subdecks"""
        content = "#123456\tTest Deck\n##Level 1\nHello\t你好\nThank you\t谢谢\n##Level 2\nGoodbye\t再见\nWater\t水\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def create_invalid_csv(self):
        """Creates an invalid CSV file"""
        content = "#invalid\n你好\n"  # Missing deck name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def create_empty_csv(self):
        """Creates an empty CSV file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("")
            return f.name
    
    def test_validate_csv_format_valid(self):
        """Test for valid CSV validation"""
        self.assertTrue(self.generator.validate_csv_format(self.test_csv))
    
    def test_validate_csv_format_invalid_extension(self):
        """Test for invalid file extension"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test")
            txt_file = f.name
        
        self.assertFalse(self.generator.validate_csv_format(txt_file))
        os.unlink(txt_file)
    
    def test_validate_csv_format_nonexistent(self):
        """Test for non-existent file"""
        self.assertFalse(self.generator.validate_csv_format("nonexistent.csv"))
    
    def test_validate_csv_format_empty(self):
        """Test for empty file"""
        empty_csv = self.create_empty_csv()
        self.assertFalse(self.generator.validate_csv_format(empty_csv))
        os.unlink(empty_csv)
    
    def test_read_hanzi_words_valid(self):
        """Test for valid reading of Hanzi words"""
        deck_number, deck_name, subdecks = self.generator.read_hanzi_words(self.test_csv)
        
        self.assertEqual(deck_number, 123456)
        self.assertEqual(deck_name, "Test Deck")
        self.assertEqual(len(subdecks), 1)
        subdeck_name, words = subdecks[0]
        self.assertIsNone(subdeck_name)  # No subdeck used
        self.assertEqual(len(words), 3)
        self.assertEqual(words[0], ["Hello", "你好"])
        self.assertEqual(words[1], ["Thank you", "谢谢"])
        self.assertEqual(words[2], ["Goodbye", "再见"])
    
    def test_read_hanzi_words_with_subdecks(self):
        """Test for reading CSV with subdecks"""
        subdeck_csv = self.create_subdeck_csv()
        deck_number, deck_name, subdecks = self.generator.read_hanzi_words(subdeck_csv)
        
        self.assertEqual(deck_number, 123456)
        self.assertEqual(deck_name, "Test Deck")
        self.assertEqual(len(subdecks), 2)
        
        # Check Level 1 subdeck
        subdeck_name, words = subdecks[0]
        self.assertEqual(subdeck_name, "Level 1")
        self.assertEqual(len(words), 2)
        self.assertEqual(words[0], ["Hello", "你好"])
        
        # Check Level 2 subdeck
        subdeck_name, words = subdecks[1]
        self.assertEqual(subdeck_name, "Level 2")
        self.assertEqual(len(words), 2)
        self.assertEqual(words[0], ["Goodbye", "再见"])
        
        os.unlink(subdeck_csv)
    
    def test_read_hanzi_words_invalid_header(self):
        """Test for invalid header"""
        invalid_csv = self.create_invalid_csv()
        
        with self.assertRaises(ValueError):
            self.generator.read_hanzi_words(invalid_csv)
        
        os.unlink(invalid_csv)
    
    def test_read_hanzi_words_nonexistent_file(self):
        """Test for non-existent file"""
        with self.assertRaises(FileNotFoundError):
            self.generator.read_hanzi_words("nonexistent.csv")
    
    def test_check_duplicates_no_duplicates(self):
        """Test for no duplicates"""
        words = [["Hello", "你好"], ["Thank you", "谢谢"]]
        duplicates = self.generator.check_duplicates(words)
        self.assertEqual(len(duplicates), 0)
    
    def test_check_duplicates_with_duplicates(self):
        """Test for duplicates"""
        words = [["Hello", "你好"], ["Thank you", "谢谢"], ["Hello", "你好"]]
        duplicates = self.generator.check_duplicates(words)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0], (3, "Hello", "你好"))
    
    def test_get_pinyin_with_tones(self):
        """Test for Pinyin conversion"""
        pinyin = self.generator.get_pinyin_with_tones("你好")
        self.assertIn("nǐ", pinyin)
        self.assertIn("hǎo", pinyin)
    
    def test_get_pinyin_with_tones_invalid(self):
        """Test for invalid characters"""
        pinyin = self.generator.get_pinyin_with_tones("abc")
        self.assertIsInstance(pinyin, str)
    
    @patch('pyAnkiHanzi.gTTS')
    def test_get_pronunciation_mp3_success(self, mock_gtts):
        """Test for successful MP3 creation"""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts
        
        result = self.generator.get_pronunciation_mp3("你好")
        
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith('.mp3'))
        mock_gtts.assert_called_once_with("你好", lang='zh')
        mock_tts.save.assert_called_once()
    
    @patch('pyAnkiHanzi.gTTS')
    def test_get_pronunciation_mp3_no_audio(self, mock_gtts):
        """Test for disabled audio creation"""
        generator = AnkiHanziGenerator(include_audio=False)
        result = generator.get_pronunciation_mp3("你好")
        self.assertIsNone(result)
        mock_gtts.assert_not_called()
        generator.cleanup()
    
    @patch('pyAnkiHanzi.gTTS')
    def test_get_pronunciation_mp3_error(self, mock_gtts):
        """Test for MP3 creation error"""
        mock_gtts.side_effect = Exception("TTS Error")
        
        result = self.generator.get_pronunciation_mp3("你好")
        self.assertIsNone(result)
    
    @patch('pyAnkiHanzi.AnkiHanziGenerator.load_template')
    def test_create_model(self, mock_load_template):
        """Test for model creation"""
        mock_load_template.return_value = ("<div>{{Translation}}</div>", "<div>{{Hanzi}}</div>")
        
        model = self.generator.create_model()
        self.assertIsNotNone(model)
        self.assertEqual(len(model.fields), 4)
        self.assertEqual(len(model.templates), 1)
    
    def test_audio_cache_functionality(self):
        """Test for audio cache functionality"""
        # Create a mock cache directory
        cache_dir = os.path.join(self.generator.temp_dir, 'test_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a mock cached file
        cache_file = os.path.join(cache_dir, "你好_20320_22909_zh.mp3")
        with open(cache_file, 'w') as f:
            f.write("mock audio data")
        
        # Temporarily modify the cache directory
        from pyAnkiHanzi import DEFAULT_CONFIG
        original_cache = DEFAULT_CONFIG['audio_cache_dir']
        DEFAULT_CONFIG['audio_cache_dir'] = cache_dir
        
        try:
            result = self.generator.get_pronunciation_mp3("你好")
            self.assertIsNotNone(result)
            self.assertTrue(os.path.exists(result))
        finally:
            DEFAULT_CONFIG['audio_cache_dir'] = original_cache
    
    @patch('pyAnkiHanzi.genanki.Package')
    @patch('pyAnkiHanzi.gTTS')
    def test_create_deck_success(self, mock_gtts, mock_package):
        """Test for successful deck creation"""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts
        
        mock_pkg = MagicMock()
        mock_package.return_value = mock_pkg
        
        output_file = self.generator.create_deck(self.test_csv)
        
        self.assertTrue(output_file.endswith('.apkg'))
        mock_pkg.write_to_file.assert_called_once()
    
    def test_create_deck_invalid_csv(self):
        """Test for invalid CSV in deck creation"""
        with self.assertRaises(ValueError):
            self.generator.create_deck("nonexistent.csv")
    
    def test_context_manager(self):
        """Test for context manager"""
        with AnkiHanziGenerator() as generator:
            self.assertIsNotNone(generator)
            temp_dir = generator.temp_dir
            self.assertTrue(os.path.exists(temp_dir))
        
        # After exiting, temp_dir should be cleaned up
        self.assertFalse(os.path.exists(temp_dir))


class TestIntegrationTests(unittest.TestCase):
    """Integration tests for the entire system"""
    
    def setUp(self):
        """Setup for integration tests"""
        self.test_dir = tempfile.mkdtemp()
        self.test_csv = os.path.join(self.test_dir, 'test.csv')
        self.create_comprehensive_test_csv()
    
    def tearDown(self):
        """Cleanup after integration tests"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_comprehensive_test_csv(self):
        """Creates a comprehensive test CSV with various scenarios"""
        content = """#999999\tIntegration Test Deck
##Basic Words
Hello\t你好
Thank you\t谢谢
Goodbye\t再见
##Countries
China\t中国
America\t美国
##Cities
Beijing\t北京
Shanghai\t上海
##Learning
Learn\t学习
Chinese characters\t汉字
Pinyin\t拼音
Pronunciation\t发音
"""
        with open(self.test_csv, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @patch('pyAnkiHanzi.gTTS')
    @patch('pyAnkiHanzi.genanki.Package')
    def test_full_deck_creation_with_subdecks(self, mock_package, mock_gtts):
        """Test for complete deck creation with subdecks"""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts
        
        mock_pkg = MagicMock()
        mock_package.return_value = mock_pkg
        
        with AnkiHanziGenerator(include_audio=True) as generator:
            output_file = generator.create_deck(self.test_csv)
            
            self.assertTrue(output_file.endswith('.apkg'))
            # Should create multiple decks for subdecks
            self.assertGreater(mock_gtts.call_count, 0)
            mock_pkg.write_to_file.assert_called_once_with(output_file)
    
    def test_full_deck_creation_without_audio(self):
        """Test for complete deck creation without audio"""
        with AnkiHanziGenerator(include_audio=False) as generator:
            output_file = generator.create_deck(self.test_csv)
            
            self.assertTrue(output_file.endswith('.apkg'))
            self.assertTrue(os.path.exists(output_file))
            self.assertEqual(len(generator.media_files), 0)
            
            if os.path.exists(output_file):
                os.remove(output_file)


def diagnose_environment():
    """Diagnoses the test environment"""
    print("Environment Diagnosis")
    print("=" * 50)
    
    # Python version
    print(f"Python Version: {sys.version}")
    
    # Check dependencies
    required_modules = ['genanki', 'gtts', 'pypinyin', 'tqdm', 'requests']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: available")
        except ImportError:
            print(f"❌ {module}: MISSING")
    
    # Import pyAnkiHanzi
    try:
        from pyAnkiHanzi import AnkiHanziGenerator
        print("✅ pyAnkiHanzi: imported")
        
        # Create test generator
        with AnkiHanziGenerator() as gen:
            print(f"✅ Generator created, temp_dir: {gen.temp_dir}")
            
    except Exception as e:
        print(f"❌ pyAnkiHanzi import error: {e}")
    
    # Check template file
    if os.path.exists('hanzi_template.json'):
        print("✅ hanzi_template.json: found")
    else:
        print("⚠️  hanzi_template.json: not found (will use fallback)")
    
    print("=" * 50)


def create_sample_csv():
    """Creates a sample CSV file for manual testing"""
    content = """#123456\tChinese Basic Vocabulary
##Greetings
Hello (nǐ hǎo)\t你好
Thank you (xiè xiè)\t谢谢
Goodbye (zài jiàn)\t再见
##Colors
Red (hóng sè)\t红色
Blue (lán sè)\t蓝色
Green (lǜ sè)\t绿色
##Numbers
One (yī)\t一
Two (èr)\t二
Three (sān)\t三
##Food
Water (shuǐ)\t水
Rice (mǐ fàn)\t米饭
Tea (chá)\t茶
"""
    
    with open('sample_chinese.csv', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Sample CSV created: sample_chinese.csv")
    print("📊 Contains subdecks: Greetings, Colors, Numbers, Food")


def run_test_suite(test_suite='all', verbosity=1):
    """Runs the selected test suite"""
    if test_suite == 'basic':
        suite = unittest.TestLoader().loadTestsFromTestCase(TestAnkiHanziGenerator)
    elif test_suite == 'integration':
        suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegrationTests)
    else:  # all
        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    print(f"\n{'='*50}")
    print(f"Test Results for Suite: {test_suite}")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFailed Tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nTests with Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test pyAnkiHanzi')
    parser.add_argument('--create-sample', action='store_true', 
                       help='Create a sample CSV file with subdecks')
    parser.add_argument('--run-tests', action='store_true', 
                       help='Run tests')
    parser.add_argument('--diagnose', action='store_true',
                       help='Run environment diagnosis')
    parser.add_argument('--test-suite', 
                       choices=['basic', 'integration', 'all'],
                       default='all', 
                       help='Select test suite (default: all)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose test output')
    
    args = parser.parse_args()
    
    if args.diagnose:
        diagnose_environment()
    elif args.create_sample:
        create_sample_csv()
    elif args.run_tests:
        verbosity = 2 if args.verbose else 1
        success = run_test_suite(args.test_suite, verbosity)
        sys.exit(0 if success else 1)
    else:
        # Run all tests by default
        print("Running all tests...")
        success = run_test_suite('all', 2)
        sys.exit(0 if success else 1)
