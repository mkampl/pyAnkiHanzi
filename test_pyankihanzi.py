#!/usr/bin/env python3
"""
Test-Script für pyAnkiHanzi
"""

import unittest
import tempfile
import os
import sys
import shutil
from unittest.mock import patch, MagicMock

# Füge das Hauptmodul zum Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from pyAnkiHanzi import AnkiHanziGenerator
except ImportError:
    print("Warnung: pyAnkiHanzi konnte nicht importiert werden. Stelle sicher, dass die Datei im gleichen Verzeichnis liegt.")
    sys.exit(1)


class TestAnkiHanziGenerator(unittest.TestCase):
    """Tests für die AnkiHanziGenerator-Klasse"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.generator = AnkiHanziGenerator()
        self.test_csv = self.create_test_csv()
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        if os.path.exists(self.test_csv):
            os.unlink(self.test_csv)
        self.generator.cleanup()
    
    def create_test_csv(self):
        """Erstellt eine Test-CSV-Datei"""
        content = "123456\tTest Deck\n你好\tHallo\n谢谢\tDanke\n再见\tAuf Wiedersehen\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def create_invalid_csv(self):
        """Erstellt eine ungültige CSV-Datei"""
        content = "invalid\n你好\n"  # Fehlende zweite Spalte im Header
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def create_empty_csv(self):
        """Erstellt eine leere CSV-Datei"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("")
            return f.name
    
    def test_validate_csv_format_valid(self):
        """Test für gültige CSV-Validierung"""
        self.assertTrue(self.generator.validate_csv_format(self.test_csv))
    
    def test_validate_csv_format_invalid_extension(self):
        """Test für ungültige Dateiendung"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test")
            txt_file = f.name
        
        self.assertFalse(self.generator.validate_csv_format(txt_file))
        os.unlink(txt_file)
    
    def test_validate_csv_format_nonexistent(self):
        """Test für nicht existierende Datei"""
        self.assertFalse(self.generator.validate_csv_format("nonexistent.csv"))
    
    def test_validate_csv_format_empty(self):
        """Test für leere Datei"""
        empty_csv = self.create_empty_csv()
        self.assertFalse(self.generator.validate_csv_format(empty_csv))
        os.unlink(empty_csv)
    
    def test_read_hanzi_words_valid(self):
        """Test für gültiges Lesen von Hanzi-Wörtern"""
        deck_number, deck_name, words = self.generator.read_hanzi_words(self.test_csv)
        
        self.assertEqual(deck_number, 123456)
        self.assertEqual(deck_name, "Test Deck")
        self.assertEqual(len(words), 3)
        self.assertEqual(words[0], ["你好", "Hallo"])
        self.assertEqual(words[1], ["谢谢", "Danke"])
        self.assertEqual(words[2], ["再见", "Auf Wiedersehen"])
    
    def test_read_hanzi_words_invalid_header(self):
        """Test für ungültigen Header"""
        invalid_csv = self.create_invalid_csv()
        
        with self.assertRaises(ValueError):
            self.generator.read_hanzi_words(invalid_csv)
        
        os.unlink(invalid_csv)
    
    def test_read_hanzi_words_nonexistent_file(self):
        """Test für nicht existierende Datei"""
        with self.assertRaises(FileNotFoundError):
            self.generator.read_hanzi_words("nonexistent.csv")
    
    def test_check_duplicates_no_duplicates(self):
        """Test für keine Duplikate"""
        words = [["你好", "Hallo"], ["谢谢", "Danke"]]
        duplicates = self.generator.check_duplicates(words)
        self.assertEqual(len(duplicates), 0)
    
    def test_check_duplicates_with_duplicates(self):
        """Test für Duplikate"""
        words = [["你好", "Hallo"], ["谢谢", "Danke"], ["你好", "Hallo"]]
        duplicates = self.generator.check_duplicates(words)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0], (3, "你好", "Hallo"))
    
    def test_get_pinyin_with_tones(self):
        """Test für Pinyin-Konvertierung"""
        pinyin = self.generator.get_pinyin_with_tones("你好")
        self.assertIn("nǐ", pinyin)
        self.assertIn("hǎo", pinyin)
    
    def test_get_pinyin_with_tones_invalid(self):
        """Test für ungültige Zeichen"""
        pinyin = self.generator.get_pinyin_with_tones("abc")
        self.assertIsInstance(pinyin, str)
    
    @patch('pyAnkiHanzi.gTTS')
    def test_get_pronunciation_mp3_success(self, mock_gtts):
        """Test für erfolgreiche MP3-Erstellung"""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts
        
        result = self.generator.get_pronunciation_mp3("你好")
        
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith('.mp3'))
        mock_gtts.assert_called_once_with("你好", lang='zh')
        mock_tts.save.assert_called_once()
    
    @patch('pyAnkiHanzi.gTTS')
    def test_get_pronunciation_mp3_no_audio(self, mock_gtts):
        """Test für deaktivierte Audio-Erstellung"""
        generator = AnkiHanziGenerator(include_audio=False)
        result = generator.get_pronunciation_mp3("你好")
        self.assertIsNone(result)
        mock_gtts.assert_not_called()
        generator.cleanup()
    
    @patch('pyAnkiHanzi.gTTS')
    def test_get_pronunciation_mp3_error(self, mock_gtts):
        """Test für Fehler bei MP3-Erstellung"""
        mock_gtts.side_effect = Exception("TTS Error")
        
        result = self.generator.get_pronunciation_mp3("你好")
        self.assertIsNone(result)
    
    def test_create_model(self):
        """Test für Modell-Erstellung"""
        model = self.generator.create_model()
        self.assertIsNotNone(model)
        self.assertEqual(len(model.fields), 4)
        self.assertEqual(len(model.templates), 1)
    
    @patch('pyAnkiHanzi.genanki.Package')
    @patch('pyAnkiHanzi.gTTS')
    def test_create_deck_success(self, mock_gtts, mock_package):
        """Test für erfolgreiche Deck-Erstellung"""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts
        
        mock_pkg = MagicMock()
        mock_package.return_value = mock_pkg
        
        output_file = self.generator.create_deck(self.test_csv)
        
        self.assertTrue(output_file.endswith('.apkg'))
        mock_pkg.write_to_file.assert_called_once()
    
    def test_create_deck_invalid_csv(self):
        """Test für ungültige CSV bei Deck-Erstellung"""
        with self.assertRaises(ValueError):
            self.generator.create_deck("nonexistent.csv")
    
    def test_context_manager(self):
        """Test für Context Manager"""
        with AnkiHanziGenerator() as generator:
            self.assertIsNotNone(generator)
            temp_dir = generator.temp_dir
            self.assertTrue(os.path.exists(temp_dir))
        
        # Nach dem Verlassen sollte das temp_dir aufgeräumt sein
        self.assertFalse(os.path.exists(temp_dir))


class TestUtilityFunctions(unittest.TestCase):
    """Tests für Utility-Funktionen"""
    
    def test_parse_arguments_basic(self):
        """Test für grundlegende Argument-Parsing"""
        try:
            from pyAnkiHanzi import parse_arguments
        except ImportError:
            self.skipTest("parse_arguments nicht verfügbar")
        
        test_args = ['pyAnkiHanzi.py', 'test.csv']
        with patch('sys.argv', test_args):
            args = parse_arguments()
            self.assertEqual(args.input_file, 'test.csv')
            self.assertEqual(args.language, 'zh')
            self.assertFalse(args.no_audio)
    
    def test_parse_arguments_with_options(self):
        """Test für Argument-Parsing mit Optionen"""
        try:
            from pyAnkiHanzi import parse_arguments
        except ImportError:
            self.skipTest("parse_arguments nicht verfügbar")
        
        test_args = ['pyAnkiHanzi.py', 'test.csv', '--no-audio', '--language', 'zh-cn', '--output', 'output.apkg', '--verbose']
        with patch('sys.argv', test_args):
            args = parse_arguments()
            self.assertEqual(args.input_file, 'test.csv')
            self.assertEqual(args.language, 'zh-cn')
            self.assertTrue(args.no_audio)
            self.assertEqual(args.output, 'output.apkg')
            self.assertTrue(args.verbose)


class TestIntegrationTests(unittest.TestCase):
    """Integrationstests für das gesamte System"""
    
    def setUp(self):
        """Setup für Integrationstests"""
        self.test_dir = tempfile.mkdtemp()
        self.test_csv = os.path.join(self.test_dir, 'test.csv')
        self.create_comprehensive_test_csv()
    
    def tearDown(self):
        """Cleanup nach Integrationstests"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_comprehensive_test_csv(self):
        """Erstellt eine umfassende Test-CSV mit verschiedenen Szenarien"""
        content = """999999	Integrationstest Deck
你好	Hallo
谢谢	Danke
再见	Auf Wiedersehen
中国	China
北京	Peking
上海	Shanghai
学习	Lernen
汉字	Hanzi
拼音	Pinyin
发音	Aussprache
"""
        with open(self.test_csv, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @patch('pyAnkiHanzi.gTTS')
    @patch('pyAnkiHanzi.genanki.Package')
    def test_full_deck_creation_with_audio(self, mock_package, mock_gtts):
        """Test für vollständige Deck-Erstellung mit Audio"""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts
        
        # Mock das Package zum Vermeiden von Dateischreibfehlern
        mock_pkg = MagicMock()
        mock_package.return_value = mock_pkg
        
        with AnkiHanziGenerator(include_audio=True) as generator:
            output_file = generator.create_deck(self.test_csv)
            
            self.assertTrue(output_file.endswith('.apkg'))
            # Prüfe, dass TTS für alle 10 Wörter aufgerufen wurde
            self.assertEqual(mock_gtts.call_count, 10)
            # Prüfe, dass Package geschrieben wurde
            mock_pkg.write_to_file.assert_called_once_with(output_file)
    
    def test_full_deck_creation_without_audio(self):
        """Test für vollständige Deck-Erstellung ohne Audio"""
        with AnkiHanziGenerator(include_audio=False) as generator:
            output_file = generator.create_deck(self.test_csv)
            
            self.assertTrue(output_file.endswith('.apkg'))
            self.assertTrue(os.path.exists(output_file))
            self.assertEqual(len(generator.media_files), 0)
            
    @patch('pyAnkiHanzi.gTTS')
    @patch('pyAnkiHanzi.genanki.Package')
    def test_full_deck_creation_with_audio_debug(self, mock_package, mock_gtts):
        """Debug-Test für Audio-Deck-Erstellung mit detaillierter Fehlerausgabe"""
        try:
            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts
            
            mock_pkg = MagicMock()
            mock_package.return_value = mock_pkg
            
            with AnkiHanziGenerator(include_audio=True) as generator:
                # Debug: Prüfe CSV-Inhalt
                deck_number, deck_name, words = generator.read_hanzi_words(self.test_csv)
                print(f"Debug: Deck {deck_number} - {deck_name}, {len(words)} Wörter")
                
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
    
    def test_different_languages(self):
        """Test für verschiedene Sprachen"""
        languages = ['zh', 'zh-cn', 'zh-tw']
        
        for lang in languages:
            with AnkiHanziGenerator(language=lang, include_audio=False) as generator:
                output_file = generator.create_deck(self.test_csv)
                self.assertTrue(os.path.exists(output_file))
                
                if os.path.exists(output_file):
                    os.remove(output_file)
    
    def test_large_dataset(self):
        """Test für große Datensätze"""
        large_csv = os.path.join(self.test_dir, 'large_test.csv')
        with open(large_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tGroßer Test\n")
            for i in range(100):
                f.write(f"Wort{i}\t汉字{i}\n")
        
        with AnkiHanziGenerator(include_audio=False) as generator:
            output_file = generator.create_deck(large_csv)
            self.assertTrue(os.path.exists(output_file))
            
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_special_characters(self):
        """Test für Sonderzeichen und komplexe Zeichen"""
        special_csv = os.path.join(self.test_dir, 'special.csv')
        content = """555555	Sonderzeichen Test
Hello World	你好世界
Zahlen	一二三四五
Radikale	氵木火土金
Komplexe Zeichen	龍鳳麟龜
Interpunktion	？！。，
"""
        with open(special_csv, 'w', encoding='utf-8') as f:
            f.write(content)
        
        with AnkiHanziGenerator(include_audio=False) as generator:
            output_file = generator.create_deck(special_csv)
            self.assertTrue(os.path.exists(output_file))
            
            if os.path.exists(output_file):
                os.remove(output_file)


class TestErrorHandling(unittest.TestCase):
    """Tests für Fehlerbehandlung"""
    
    def setUp(self):
        """Setup für Fehlerbehandlungstests"""
        self.test_dir = tempfile.mkdtemp()
        self.generator = AnkiHanziGenerator()
    
    def tearDown(self):
        """Cleanup nach Fehlerbehandlungstests"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        self.generator.cleanup()
    
    def test_corrupted_csv(self):
        """Test für beschädigte CSV-Dateien"""
        corrupted_csv = os.path.join(self.test_dir, 'corrupted.csv')
        
        with open(corrupted_csv, 'wb') as f:
            f.write(b'\xff\xfe\x00\x00invalid\x00data')
        
        with self.assertRaises(Exception):
            self.generator.read_hanzi_words(corrupted_csv)
    
    def test_missing_header(self):
        """Test für fehlenden Header"""
        no_header_csv = os.path.join(self.test_dir, 'no_header.csv')
        with open(no_header_csv, 'w', encoding='utf-8') as f:
            f.write("你好\tHallo\n")
        
        with self.assertRaises(ValueError):
            self.generator.read_hanzi_words(no_header_csv)
    
    def test_invalid_deck_number(self):
        """Test für ungültige Deck-Nummer"""
        invalid_deck_csv = os.path.join(self.test_dir, 'invalid_deck.csv')
        with open(invalid_deck_csv, 'w', encoding='utf-8') as f:
            f.write("nicht_numerisch\tTest Deck\n你好\tHallo\n")
        
        with self.assertRaises(ValueError):
            self.generator.read_hanzi_words(invalid_deck_csv)
    
    def test_empty_rows(self):
        """Test für leere Zeilen"""
        empty_rows_csv = os.path.join(self.test_dir, 'empty_rows.csv')
        with open(empty_rows_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tTest Deck\n")
            f.write("你好\tHallo\n")
            f.write("\t\n")
            f.write("谢谢\tDanke\n")
            f.write("\n")
        
        deck_number, deck_name, words = self.generator.read_hanzi_words(empty_rows_csv)
        self.assertEqual(len(words), 2)
    
    def test_network_error_simulation(self):
        """Test für Netzwerkfehler bei TTS"""
        with patch('pyAnkiHanzi.gTTS') as mock_gtts:
            mock_gtts.side_effect = Exception("Network error")
            
            result = self.generator.get_pronunciation_mp3("你好")
            self.assertIsNone(result)
    
    def test_file_permission_error(self):
        """Test für Dateiberechtigungsfehler"""
        if os.name == 'nt':
            self.skipTest("Dateiberechtigungstests auf Windows übersprungen")
        
        readonly_csv = os.path.join(self.test_dir, 'readonly.csv')
        with open(readonly_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tTest\n你好\tHallo\n")
        
        os.chmod(readonly_csv, 0o444)
        
        try:
            deck_number, deck_name, words = self.generator.read_hanzi_words(readonly_csv)
            self.assertEqual(len(words), 1)
        finally:
            os.chmod(readonly_csv, 0o644)


class TestPerformance(unittest.TestCase):
    """Performance-Tests"""
    
    def setUp(self):
        """Setup für Performance-Tests"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup nach Performance-Tests"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_memory_usage(self):
        """Test für Speicherverbrauch bei großen Dateien"""
        try:
            import psutil
        except ImportError:
            self.skipTest("psutil nicht verfügbar für Memory-Tests")
        
        large_csv = os.path.join(self.test_dir, 'memory_test.csv')
        with open(large_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tMemory Test\n")
            for i in range(1000):
                f.write(f"Wort{i}\t汉字{i}\n")
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        with AnkiHanziGenerator(include_audio=False) as generator:
            generator.create_deck(large_csv)
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        self.assertLess(memory_increase, 100 * 1024 * 1024)
    
    def test_processing_time(self):
        """Test für Verarbeitungszeit"""
        import time
        
        medium_csv = os.path.join(self.test_dir, 'time_test.csv')
        with open(medium_csv, 'w', encoding='utf-8') as f:
            f.write("123456\tTime Test\n")
            for i in range(100):
                f.write(f"Wort{i}\t汉字{i}\n")
        
        start_time = time.time()
        
        with AnkiHanziGenerator(include_audio=False) as generator:
            generator.create_deck(medium_csv)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        self.assertLess(processing_time, 30)


def diagnose_environment():
    """Diagnostiziert die Test-Umgebung"""
    print("🔍 Umgebungsdiagnose")
    print("=" * 50)
    
    # Python Version
    print(f"Python Version: {sys.version}")
    
    # Abhängigkeiten prüfen
    required_modules = ['genanki', 'gtts', 'pypinyin', 'tqdm']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: verfügbar")
        except ImportError:
            print(f"❌ {module}: FEHLT")
    
    # Optional modules
    optional_modules = ['psutil']
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module}: verfügbar (optional)")
        except ImportError:
            print(f"⚠️  {module}: nicht verfügbar (optional)")
    
    # pyAnkiHanzi importieren
    try:
        from pyAnkiHanzi import AnkiHanziGenerator
        print("✅ pyAnkiHanzi: importiert")
        
        # Test-Generator erstellen
        with AnkiHanziGenerator() as gen:
            print(f"✅ Generator erstellt, temp_dir: {gen.temp_dir}")
            
    except Exception as e:
        print(f"❌ pyAnkiHanzi Import-Fehler: {e}")
    
    print("=" * 50)
    """Erstellt eine umfassende Beispiel-CSV-Datei für manuelle Tests"""
    content = """123456	Chinesisch Grundwortschatz
你好	Hallo
谢谢	Danke
再见	Auf Wiedersehen
请	Bitte
对不起	Entschuldigung
没关系	Macht nichts
是	Sein/Ja
不是	Nicht sein/Nein
我	Ich
你	Du
他	Er
她	Sie
我们	Wir
你们	Ihr
他们	Sie (Plural)
水	Wasser
茶	Tee
咖啡	Kaffee
米饭	Reis
面条	Nudeln
苹果	Apfel
香蕉	Banane
橙子	Orange
牛奶	Milch
面包	Brot
鸡蛋	Ei
鱼	Fisch
肉	Fleisch
蔬菜	Gemüse
水果	Obst
红色	Rot
蓝色	Blau
绿色	Grün
黄色	Gelb
白色	Weiß
黑色	Schwarz
大	Groß
小	Klein
高	Hoch
矮	Niedrig
新	Neu
旧	Alt
快	Schnell
慢	Langsam
好	Gut
坏	Schlecht
热	Heiß
冷	Kalt
今天	Heute
昨天	Gestern
明天	Morgen
现在	Jetzt
时间	Zeit
年	Jahr
月	Monat
日	Tag
小时	Stunde
分钟	Minute
学校	Schule
老师	Lehrer
学生	Student
朋友	Freund
家	Haus/Zuhause
工作	Arbeit
钱	Geld
书	Buch
电脑	Computer
手机	Handy
汽车	Auto
飞机	Flugzeug
火车	Zug
医院	Krankenhaus
银行	Bank
饭店	Restaurant
商店	Geschäft
公园	Park
动物园	Zoo
图书馆	Bibliothek
电影院	Kino
音乐	Musik
电影	Film
运动	Sport
游戏	Spiel
旅游	Reisen
照片	Foto
生日	Geburtstag
礼物	Geschenk
爱	Liebe
开心	Glücklich
难过	Traurig
生气	Wütend
累	Müde
饿	Hungrig
渴	Durstig
睡觉	Schlafen
起床	Aufstehen
吃	Essen
喝	Trinken
看	Schauen
听	Hören
说	Sprechen
写	Schreiben
读	Lesen
走	Gehen
跑	Rennen
坐	Sitzen
站	Stehen
买	Kaufen
卖	Verkaufen
开	Öffnen
关	Schließen
来	Kommen
去	Gehen
回	Zurückkehren
进	Hineingehen
出	Hinausgehen
上	Auf/Oben
下	Unter/Unten
左	Links
右	Rechts
前	Vorn
后	Hinten
里	Drinnen
外	Draußen
这	Dies
那	Das
什么	Was
谁	Wer
哪里	Wo
什么时候	Wann
怎么	Wie
为什么	Warum
多少	Wie viel
几	Wie viele
一	Eins
二	Zwei
三	Drei
四	Vier
五	Fünf
六	Sechs
七	Sieben
八	Acht
九	Neun
十	Zehn
百	Hundert
千	Tausend
万	Zehntausend"""
    
    with open('sample_chinese.csv', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Umfassende Beispiel-CSV erstellt: sample_chinese.csv")
    print(f"📊 Enthält {len(content.split(chr(10))[1:])} Wörter")


def run_test_suite(test_suite='all', verbosity=1):
    """Führt die gewählte Test-Suite aus"""
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
    print(f"Test-Ergebnisse für Suite: {test_suite}")
    print(f"{'='*50}")
    print(f"Tests ausgeführt: {result.testsRun}")
    print(f"Erfolgreich: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fehlgeschlagen: {len(result.failures)}")
    print(f"Fehler: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFehlgeschlagene Tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nTests mit Fehlern:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test pyAnkiHanzi')
    parser.add_argument('--create-sample', action='store_true', 
                       help='Erstelle eine umfassende Beispiel-CSV-Datei')
    parser.add_argument('--run-tests', action='store_true', 
                       help='Führe Tests aus')
    parser.add_argument('--diagnose', action='store_true',
                       help='Führe Umgebungsdiagnose aus')
    parser.add_argument('--test-suite', 
                       choices=['basic', 'integration', 'error', 'performance', 'utility', 'all'],
                       default='all', 
                       help='Wähle Test-Suite (Standard: all)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Ausführliche Test-Ausgabe')
    
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
        # Standardmäßig alle Tests ausführen
        print("Führe alle Tests aus...")
        success = run_test_suite('all', 2)
        sys.exit(0 if success else 1)
