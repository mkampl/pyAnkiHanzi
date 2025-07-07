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
        """Creates a test CSV file"""
        content = "123456\tTest Deck\nHello\t你好\nThank you\t谢谢\nGoodbye\t再见\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def create_invalid_csv(self):
        """Creates an invalid CSV file"""
        content = "invalid\n你好\n"  # Missing second column in header
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
        deck_number, deck_name, words = self.generator.read_hanzi_words(self.test_csv)
        
        self.assertEqual(deck_number, 123456)
        self.assertEqual(deck_name, "Test Deck")
        self.assertEqual(len(words), 3)
        self.assertEqual(words[0], ["Hello", "你好"])
        self.assertEqual(words[1], ["Thank you", "谢谢"])
        self.assertEqual(words[2], ["Goodbye", "再见"])
    
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
    
    def test_create_model(self):
        """Test for model creation"""
        model = self.generator.create_model()
        self.assertIsNotNone(model)
        self.assertEqual(len(model.fields), 4)
        self.assertEqual(len(model.templates), 1)
    
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


class TestUtilityFunctions(unittest.TestCase):
    """Tests for utility functions"""
    
    def test_parse_arguments_basic(self):
        """Test for basic argument parsing"""
        try:
            from pyAnkiHanzi import parse_arguments
        except ImportError:
            self.skipTest("parse_arguments not available")
        
        test_args = ['pyAnkiHanzi.py', 'test.csv']
        with patch('sys.argv', test_args):
            args = parse_arguments()
            self.assertEqual(args.input_file, 'test.csv')
            self.assertEqual(args.language, 'zh')
            self.assertFalse(args.no_audio)
    
    def test_parse_arguments_with_options(self):
        """Test for argument parsing with options"""
        try:
            from pyAnkiHanzi import parse_arguments
        except ImportError:
            self.skipTest("parse_arguments not available")
        
        test_args = ['pyAnkiHanzi.py', 'test.csv', '--no-audio', '--language', 'zh-cn', '--output', 'output.apkg', '--verbose']
        with patch('sys.argv', test_args):
            args = parse_arguments()
            self.assertEqual(args.input_file, 'test.csv')
            self.assertEqual(args.language, 'zh-cn')
            self.assertTrue(args.no_audio)
            self.assertEqual(args.output, 'output.apkg')
            self.assertTrue(args.verbose)


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
        content = """999999	Integration Test Deck
Hello	你好
Thank you	谢谢
Goodbye	再见
China	中国
Beijing	北京
Shanghai	上海
Learn	学习
Chinese characters	汉字
Pinyin	拼音
Pronunciation	发音
"""
        with open(self.test_csv, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @patch('pyAnkiHanzi.gTTS')
    @patch('pyAnkiHanzi.genanki.Package')
    def test_full_deck_creation_with_audio(self, mock_package, mock_gtts):
        """Test for complete deck creation with audio"""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts
        
        # Mock the package to avoid file writing errors
        mock_pkg = MagicMock()
        mock_package.return_value = mock_pkg
        
        with AnkiHanziGenerator(include_audio=True) as generator:
            output_file = generator.create_deck(self.test_csv)
            
            self.assertTrue(output_file.endswith('.apkg'))
            # Check that TTS was called for all 10 words
            self.assertEqual(mock_gtts.call_count, 10)
            # Check that package was written
            mock_pkg.write_to_file.assert_called_once_with(output_file)
    
    @patch('pyAnkiHanzi.gTTS')
    @patch('pyAnkiHanzi.genanki.Package')
    def test_full_deck_creation_with_audio_debug(self, mock_package, mock_gtts):
        """Debug test for audio deck creation with detailed error output"""
        try:
            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts
            
            mock_pkg = MagicMock()
            mock_package.return_value = mock_pkg
            
            with AnkiHanziGenerator(include_audio=True) as generator:
                # Debug: Check CSV content
                deck_number, deck_name, words = generator.read_hanzi_words(self.test_csv)
                print(f"Debug: Deck {deck_number} - {deck_name}, {len(words)} words")
                
                output_file = generator.create_deck(self.test_csv)
                
                print(f"Debug: Output file: {output_file}")
                print(f"Debug: TTS call count: {mock_gtts.call_count}")
                print(f"Debug: Media files: {len(generator.media_files)}")
                
                self.assertTrue(output_file.endswith('.apkg'))
                
        except Exception as e:
            print(f"Debug: Exception in test: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def test_full_deck_creation_without_audio(self):
        """Test for complete deck creation without audio"""
        with AnkiHanziGenerator(include_audio=False) as generator:
            output_file = generator.create_deck(self.test_csv)
            
            self.assertTrue(output_file.endswith('.apkg'))
            self.assertTrue(os.path.exists(output_file))
            self.assertEqual(len(generator.media_files), 0)
            
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_different_languages(self):
        """Test for different languages"""
        languages = ['zh', 'zh-cn', 'zh-tw']
        
        for lang in languages:
            with AnkiHanziGenerator(language=lang, include_audio=False) as generator:
                output_file = generator.create_deck(self.test_csv)
                self.assertTrue(os.path.exists(output_file))
                
                if os.path.exists(output_file):
                    os.remove(output_file)
    
    def test_large_dataset(self):
        """Test for large datasets"""
        large_csv = os.path.join(self.test_dir, 'large_test.csv')
        with open(large_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tLarge Test\n")
            for i in range(100):
                f.write(f"Word{i}\t汉字{i}\n")
        
        with AnkiHanziGenerator(include_audio=False) as generator:
            output_file = generator.create_deck(large_csv)
            self.assertTrue(os.path.exists(output_file))
            
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_special_characters(self):
        """Test for special characters and complex characters"""
        special_csv = os.path.join(self.test_dir, 'special.csv')
        content = """555555	Special Characters Test
Hello World	你好世界
Numbers	一二三四五
Radicals	氵木火土金
Complex Characters	龍鳳麟龜
Punctuation	？！。，
"""
        with open(special_csv, 'w', encoding='utf-8') as f:
            f.write(content)
        
        with AnkiHanziGenerator(include_audio=False) as generator:
            output_file = generator.create_deck(special_csv)
            self.assertTrue(os.path.exists(output_file))
            
            if os.path.exists(output_file):
                os.remove(output_file)


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling"""
    
    def setUp(self):
        """Setup for error handling tests"""
        self.test_dir = tempfile.mkdtemp()
        self.generator = AnkiHanziGenerator()
    
    def tearDown(self):
        """Cleanup after error handling tests"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        self.generator.cleanup()
    
    def test_corrupted_csv(self):
        """Test for corrupted CSV files"""
        corrupted_csv = os.path.join(self.test_dir, 'corrupted.csv')
        
        with open(corrupted_csv, 'wb') as f:
            f.write(b'\xff\xfe\x00\x00invalid\x00data')
        
        with self.assertRaises(Exception):
            self.generator.read_hanzi_words(corrupted_csv)
    
    def test_missing_header(self):
        """Test for missing header"""
        no_header_csv = os.path.join(self.test_dir, 'no_header.csv')
        with open(no_header_csv, 'w', encoding='utf-8') as f:
            f.write("你好\tHello\n")
        
        with self.assertRaises(ValueError):
            self.generator.read_hanzi_words(no_header_csv)
    
    def test_invalid_deck_number(self):
        """Test for invalid deck number"""
        invalid_deck_csv = os.path.join(self.test_dir, 'invalid_deck.csv')
        with open(invalid_deck_csv, 'w', encoding='utf-8') as f:
            f.write("not_numeric\tTest Deck\n你好\tHello\n")
        
        with self.assertRaises(ValueError):
            self.generator.read_hanzi_words(invalid_deck_csv)
    
    def test_empty_rows(self):
        """Test for empty rows"""
        empty_rows_csv = os.path.join(self.test_dir, 'empty_rows.csv')
        with open(empty_rows_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tTest Deck\n")
            f.write("你好\tHello\n")
            f.write("\t\n")  # Empty row
            f.write("谢谢\tThank you\n")
            f.write("\n")    # Completely empty row
        
        # Should not crash, but skip empty rows
        deck_number, deck_name, words = self.generator.read_hanzi_words(empty_rows_csv)
        self.assertEqual(len(words), 2)
    
    def test_network_error_simulation(self):
        """Test for network errors with TTS"""
        with patch('pyAnkiHanzi.gTTS') as mock_gtts:
            mock_gtts.side_effect = Exception("Network error")
            
            result = self.generator.get_pronunciation_mp3("你好")
            self.assertIsNone(result)
    
    def test_file_permission_error(self):
        """Test for file permission errors"""
        if os.name == 'nt':  # Windows
            self.skipTest("File permission tests skipped on Windows")
        
        readonly_csv = os.path.join(self.test_dir, 'readonly.csv')
        with open(readonly_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tTest\n你好\tHello\n")
        
        # Make file read-only
        os.chmod(readonly_csv, 0o444)
        
        try:
            # Should still be readable
            deck_number, deck_name, words = self.generator.read_hanzi_words(readonly_csv)
            self.assertEqual(len(words), 1)
        finally:
            # Reset permissions for cleanup
            os.chmod(readonly_csv, 0o644)


class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def setUp(self):
        """Setup for performance tests"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup after performance tests"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_memory_usage(self):
        """Test for memory usage with large files"""
        try:
            import psutil
        except ImportError:
            self.skipTest("psutil not available for memory tests")
        
        large_csv = os.path.join(self.test_dir, 'memory_test.csv')
        with open(large_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tMemory Test\n")
            for i in range(1000):
                f.write(f"Word{i}\t汉字{i}\n")
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        with AnkiHanziGenerator(include_audio=False) as generator:
            generator.create_deck(large_csv)
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Memory usage should stay under 100MB
        self.assertLess(memory_increase, 100 * 1024 * 1024)
    
    def test_processing_time(self):
        """Test for processing time"""
        import time
        
        medium_csv = os.path.join(self.test_dir, 'time_test.csv')
        with open(medium_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tTime Test\n")
            for i in range(100):
                f.write(f"Word{i}\t汉字{i}\n")
        
        start_time = time.time()
        
        with AnkiHanziGenerator(include_audio=False) as generator:
            generator.create_deck(medium_csv)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Processing should take less than 30 seconds
        self.assertLess(processing_time, 30)


def diagnose_environment():
    """Diagnoses the test environment"""
    print("🔍 Environment Diagnosis")
    print("=" * 50)
    
    # Python version
    print(f"Python Version: {sys.version}")
    
    # Check dependencies
    required_modules = ['genanki', 'gtts', 'pypinyin', 'tqdm']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: available")
        except ImportError:
            print(f"❌ {module}: MISSING")
    
    # Optional modules
    optional_modules = ['psutil']
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module}: available (optional)")
        except ImportError:
            print(f"⚠️  {module}: not available (optional)")
    
    # Import pyAnkiHanzi
    try:
        from pyAnkiHanzi import AnkiHanziGenerator
        print("✅ pyAnkiHanzi: imported")
        
        # Create test generator
        with AnkiHanziGenerator() as gen:
            print(f"✅ Generator created, temp_dir: {gen.temp_dir}")
            
    except Exception as e:
        print(f"❌ pyAnkiHanzi import error: {e}")
    
    print("=" * 50)


def create_sample_csv():
    """Creates a comprehensive sample CSV file for manual testing"""
    content = """123456	Chinese Basic Vocabulary
Hello	你好
Thank you	谢谢
Goodbye	再见
Please	请
Sorry	对不起
It's okay	没关系
Yes/To be	是
No/Not to be	不是
I	我
You	你
He	他
She	她
We	我们
You (plural)	你们
They	他们
Water	水
Tea	茶
Coffee	咖啡
Rice	米饭
Noodles	面条
Apple	苹果
Banana	香蕉
Orange	橙子
Milk	牛奶
Bread	面包
Egg	鸡蛋
Fish	鱼
Meat	肉
Vegetables	蔬菜
Fruit	水果
Red	红色
Blue	蓝色
Green	绿色
Yellow	黄色
White	白色
Black	黑色
Big	大
Small	小
High	高
Low	矮
New	新
Old	旧
Fast	快
Slow	慢
Good	好
Bad	坏
Hot	热
Cold	冷
Today	今天
Yesterday	昨天
Tomorrow	明天
Now	现在
Time	时间
Year	年
Month	月
Day	日
Hour	小时
Minute	分钟
School	学校
Teacher	老师
Student	学生
Friend	朋友
Home	家
Work	工作
Money	钱
Book	书
Computer	电脑
Phone	手机
Car	汽车
Airplane	飞机
Train	火车
Hospital	医院
Bank	银行
Restaurant	饭店
Store	商店
Park	公园
Zoo	动物园
Library	图书馆
Cinema	电影院
Music	音乐
Movie	电影
Sports	运动
Game	游戏
Travel	旅游
Photo	照片
Birthday	生日
Gift	礼物
Love	爱
Happy	开心
Sad	难过
Angry	生气
Tired	累
Hungry	饿
Thirsty	渴
Sleep	睡觉
Wake up	起床
Eat	吃
Drink	喝
Look	看
Listen	听
Speak	说
Write	写
Read	读
Walk	走
Run	跑
Sit	坐
Stand	站
Buy	买
Sell	卖
Open	开
Close	关
Come	来
Go	去
Return	回
Enter	进
Exit	出
Up/On	上
Down/Under	下
Left	左
Right	右
Front	前
Back	后
Inside	里
Outside	外
This	这
That	那
What	什么
Who	谁
Where	哪里
When	什么时候
How	怎么
Why	为什么
How much	多少
How many	几
One	一
Two	二
Three	三
Four	四
Five	五
Six	六
Seven	七
Eight	八
Nine	九
Ten	十
Hundred	百
Thousand	千
Ten thousand	万"""
    
    with open('sample_chinese.csv', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Comprehensive sample CSV created: sample_chinese.csv")
    print(f"📊 Contains {len(content.split(chr(10))[1:])} words")


def run_test_suite(test_suite='all', verbosity=1):
    """Runs the selected test suite"""
    if test_suite == 'basic':
        suite = unittest.TestLoader().loadTestsFromTestCase(TestAnkiHanziGenerator)
    elif test_suite == 'integration':
        suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegrationTests)
    elif test_suite == 'error':
        suite = unittest.TestLoader().loadTestsFromTestCase(TestErrorHandling)
    elif test_suite == 'performance':
        suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformance)
    elif test_suite == 'utility':
        suite = unittest.TestLoader().loadTestsFromTestCase(TestUtilityFunctions)
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
                       help='Create a comprehensive sample CSV file')
    parser.add_argument('--run-tests', action='store_true', 
                       help='Run tests')
    parser.add_argument('--diagnose', action='store_true',
                       help='Run environment diagnosis')
    parser.add_argument('--test-suite', 
                       choices=['basic', 'integration', 'error', 'performance', 'utility', 'all'],
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
