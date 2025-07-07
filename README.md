# pyAnkiHanzi 🈲

An improved Python tool for creating Anki cards for Chinese characters with interactive stroke order animations.

## Features ✨

- **Robust Error Handling**: Comprehensive validation and meaningful error messages
- **Interactive Stroke Order**: Uses HanziWriter to learn correct stroke sequences
- **Audio Support**: Automatic generation of pronunciation files (TTS)
- **Pinyin Integration**: Automatic conversion to Pinyin with tones
- **Progress Display**: Visual progress indication during card creation
- **Duplicate Detection**: Warns about duplicate entries
- **Configurable Options**: Flexible customization via command-line parameters
- **Logging**: Detailed logging for debugging
- **Context Manager**: Automatic cleanup of temporary files

## HSK Vocabulary Integration 🎯

### HSK to Anki Deck Generator

This repository now includes `hsk_anki_generator.py`, a powerful script that automatically creates Anki decks for all HSK levels using the complete HSK vocabulary dataset.

#### Features

- **Complete HSK Coverage**: Generates decks for HSK levels 1-9 (both new and old systems)
- **Automatic Data Download**: Fetches the latest HSK vocabulary from GitHub
- **Smart Level Detection**: Handles both "new-X" and "old-X" level formats
- **Rich Card Content**: Includes English meanings, Pinyin, and optional audio
- **Batch Processing**: Create all levels at once or individual levels

#### Quick Start

```bash
# Generate unified HSK deck with all levels (1-9)
python hsk_anki_generator.py

# Generate without audio (faster, no rate limits)
python hsk_anki_generator.py --no-audio

# Generate specific level only
python hsk_anki_generator.py --level 3

# Analyze HSK data structure first
python hsk_anki_generator.py --analyze-only

# Check audio cache statistics
python hsk_anki_generator.py --cache-stats
```

#### Audio Caching System

The HSK generator includes an intelligent audio caching system to handle TTS rate limits:

- **Automatic Caching**: Audio files are cached in `./audio_cache/` directory
- **Resume Support**: Re-running the script will only process missing audio files
- **Rate Limit Handling**: Automatically handles 429 (Too Many Requests) errors
- **Failure Tracking**: Failed requests are marked to avoid repeated attempts
- **Cache Management**: Tools to clear failed markers and retry audio generation

#### Handling Rate Limits

When you encounter TTS rate limits:

```bash
# 1. Check what failed
python hsk_anki_generator.py --cache-stats

# 2. Wait and retry (uses cached audio, only retries new/failed)
python hsk_anki_generator.py

# 3. Clear failed markers and retry everything that failed
python hsk_anki_generator.py --clear-failed
python hsk_anki_generator.py
```

#### Output Structure

The script creates a single unified deck file:
- `HSK_Complete.apkg` - One deck containing all HSK levels as subdecks:
  - `HSK Complete Vocabulary::HSK 1` - Basic Vocabulary (~150 words)
  - `HSK Complete Vocabulary::HSK 2` - Elementary Vocabulary (~300 words)
  - `HSK Complete Vocabulary::HSK 3` - Intermediate Vocabulary (~600 words)
  - `HSK Complete Vocabulary::HSK 4` - Upper Intermediate Vocabulary (~1200 words)
  - `HSK Complete Vocabulary::HSK 5` - Advanced Vocabulary (~2500 words)
  - `HSK Complete Vocabulary::HSK 6` - Superior Vocabulary (~5000+ words)
  - `HSK Complete Vocabulary::HSK 7` - Proficient Level I
  - `HSK Complete Vocabulary::HSK 8` - Proficient Level II  
  - `HSK Complete Vocabulary::HSK 9` - Proficient Level III

This structure allows you to study each level separately within Anki while keeping everything organized in a single deck file.

#### Card Format

Each card contains:
- **Front**: English meaning(s) with Pinyin pronunciation
- **Back**: Chinese characters with stroke order animation, Pinyin, and optional audio
- **Interactive Practice**: Click-through stroke order learning

#### Command Line Options

```bash
python hsk_anki_generator.py [OPTIONS]

Options:
  --unified             Generate one unified deck with subdecks (default)
  --separate            Generate separate deck files for each level
  --level LEVEL         Generate deck for specific HSK level (1-9)
  --no-audio            Do not include audio files (faster generation)
  --language LANG       TTS language: zh, zh-cn, zh-tw (default: zh)
  --output FILE         Output file name (default: HSK_Complete.apkg)
  --cache-dir DIR       Directory for audio cache (default: ./audio_cache)
  --clear-failed        Clear failure markers to retry failed TTS requests
  --cache-stats         Show audio cache statistics
  --analyze-only        Only analyze JSON data without creating decks
  --verbose, -v         Verbose output for debugging
```

#### Audio Cache Management

```bash
# Check cache status
python hsk_anki_generator.py --cache-stats

# Clear failed audio attempts for retry
python hsk_anki_generator.py --clear-failed

# Use custom cache directory
python hsk_anki_generator.py --cache-dir /path/to/cache

# Generate separate files instead of unified deck
python hsk_anki_generator.py --separate
```

#### Interactive Mode

Run without arguments for interactive mode:

```bash
python hsk_anki_generator.py
```

The script will automatically generate a unified HSK deck with all levels. No interactive menu is needed as the unified approach is now the default.

#### Prerequisites

Install additional dependency for HSK script:

```bash
pip install requests
```

All other dependencies are shared with the main pyAnkiHanzi tool.

## Installation 📦

1. **Clone repository or download files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install requests  # Additional dependency for HSK script
   ```

### System Requirements

- Python 3.7+
- Internet connection (for HanziWriter CDN and TTS)

## Usage 🚀

### Basic Usage

```bash
python pyAnkiHanzi.py input.csv
```

### With Options

```bash
# Without audio files
python pyAnkiHanzi.py input.csv --no-audio

# With specific language
python pyAnkiHanzi.py input.csv --language zh-cn

# With custom output file
python pyAnkiHanzi.py input.csv --output my_deck.apkg

# Verbose output
python pyAnkiHanzi.py input.csv --verbose
```

### CSV Format 📄

The input CSV file must have the following format:

```
DECK_ID	DECK_NAME
TRANSLATION1	HANZI1
TRANSLATION2	HANZI2
...
```

**Example:**
```
123456	Chinese Basic Vocabulary
Hello	你好
Thank you	谢谢
Goodbye	再见
```

### Create Sample CSV

```bash
# Creates a sample CSV file
python test_pyankihanzi.py --create-sample
```

## Program Structure 🏗️

### Main Class: `AnkiHanziGenerator`

```python
with AnkiHanziGenerator(language='zh', include_audio=True) as generator:
    output_file = generator.create_deck('input.csv')
    print(f"Deck created: {output_file}")
```

### Important Methods

- `validate_csv_format()`: Validates the input file
- `read_hanzi_words()`: Reads and parses the CSV file
- `check_duplicates()`: Detects duplicate entries
- `get_pinyin_with_tones()`: Converts to Pinyin
- `get_pronunciation_mp3()`: Creates audio files
- `create_deck()`: Generates the Anki deck

## Configuration ⚙️

### Available Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--language` | TTS language (zh, zh-cn, zh-tw) | zh |
| `--no-audio` | Disable audio generation | False |
| `--output` | Output file | input.apkg |
| `--verbose` | Verbose output | False |

### Advanced Configuration

The `config.py` file contains detailed settings for:
- HanziWriter parameters
- TTS configuration
- Validation rules
- Anki model settings

## Running Tests 🧪

```bash
# Run all tests
python test_pyankihanzi.py --run-tests

# Or with pytest
pytest test_pyankihanzi.py -v
```

### Test Suites

```bash
# Basic functionality tests
python test_pyankihanzi.py --run-tests --test-suite basic

# Integration tests
python test_pyankihanzi.py --run-tests --test-suite integration

# Error handling tests
python test_pyankihanzi.py --run-tests --test-suite error

# Performance tests
python test_pyankihanzi.py --run-tests --test-suite performance

# Environment diagnosis
python test_pyankihanzi.py --diagnose
```

## Logging 📋

The tool automatically creates a log file `pyankihanzi.log` with:
- Information about processing progress
- Warnings for issues
- Error details for debugging

## Troubleshooting 🔧

### Common Issues

1. **"File not found"**
   - Check the file path
   - Make sure the file has a .csv extension

2. **"Invalid CSV format"**
   - Header must have at least 2 columns
   - Use tab separation
   - First line: `DECK_ID<TAB>DECK_NAME`

3. **TTS errors / Rate limits**
   - Use `--no-audio` for faster generation without audio
   - Run `python hsk_anki_generator.py --cache-stats` to check progress
   - Re-run the script later - it will resume where it left off
   - Use `--clear-failed` to retry failed audio generations

4. **Encoding problems**
   - CSV file must be UTF-8 encoded
   - In Excel: "Save as" → "CSV UTF-8"

5. **Memory issues with large HSK dataset**
   - Use `--no-audio` to reduce memory usage
   - Close other applications
   - Generate individual levels with `--level X`

### Debug Mode

```bash
python pyAnkiHanzi.py input.csv --verbose
```

## Advanced Features 🎯

### Batch Processing

```python
from pyAnkiHanzi import AnkiHanziGenerator

files = ['deck1.csv', 'deck2.csv', 'deck3.csv']

with AnkiHanziGenerator() as generator:
    for file in files:
        try:
            output = generator.create_deck(file)
            print(f"✅ {file} → {output}")
        except Exception as e:
            print(f"❌ {file}: {e}")
```

### Custom Card Template

The HTML templates in the `create_model()` method can be customized for:
- Different font sizes
- Color schemes
- Additional fields
- Layout changes

## Contributing 🤝

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License 📄

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments 🙏

- [HanziWriter](https://hanziwriter.org/) for stroke order animations
- [genanki](https://github.com/kerrickstaley/genanki) for Anki package generation
- [gTTS](https://github.com/pndurette/gTTS) for text-to-speech functionality
- [pypinyin](https://github.com/mozillazg/python-pinyin) for Pinyin conversion
- [Complete HSK Vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) by [@drkameleon](https://github.com/drkameleon) for the comprehensive HSK vocabulary dataset covering all levels (1-9) in both new and old systems

## Changelog 📅

### Version 2.0.0
- ✨ Complete architectural overhaul with classes
- ✨ Robust error handling and validation
- ✨ Progress bars and better user experience
- ✨ Comprehensive logging
- ✨ Context manager for resource management
- ✨ Duplicate detection
- ✨ Configurable options
- ✨ Comprehensive test suite
- 🐛 Fixed encoding issues
- 🐛 Improved cleanup of temporary files

### Version 2.1.0
- ✨ Added HSK vocabulary integration with `hsk_anki_generator.py`
- ✨ Unified deck structure with subdecks for each HSK level
- ✨ Complete HSK levels 1-9 support (both new and old systems)
- ✨ Automatic vocabulary download from GitHub repository
- ✨ Smart level detection and parsing
- ✨ Audio caching system with rate limit handling
- ✨ Resume capability for interrupted audio generation
- ✨ Cache management tools for failed TTS requests
- ✨ Intelligent retry logic for TTS failures

## Usage Examples 📖

### Basic Card Creation

```bash
# Create a basic deck from your own CSV
python pyAnkiHanzi.py my_vocabulary.csv
```

### HSK Vocabulary Decks

```bash
# Generate complete unified HSK deck (default)
python hsk_anki_generator.py

# Generate without audio (much faster, no rate limits)
python hsk_anki_generator.py --no-audio

# Generate only HSK Level 3
python hsk_anki_generator.py --level 3

# Generate separate files for each level
python hsk_anki_generator.py --separate

# Resume after TTS rate limits (uses cached audio)
python hsk_anki_generator.py --cache-stats
python hsk_anki_generator.py  # Will skip already cached audio

# Retry failed audio generation
python hsk_anki_generator.py --clear-failed
python hsk_anki_generator.py
```

### Advanced Usage

```bash
# Create deck without audio for faster processing
python pyAnkiHanzi.py large_vocabulary.csv --no-audio

# Use Traditional Chinese TTS
python pyAnkiHanzi.py traditional_vocab.csv --language zh-tw

# Verbose mode for troubleshooting
python pyAnkiHanzi.py problematic_file.csv --verbose
```

### Environment Check

```bash
# Check if all dependencies are installed
python test_pyankihanzi.py --diagnose

# Analyze HSK data before generating decks
python hsk_anki_generator.py --analyze-only
```

---

**Happy Chinese learning! 🇨🇳**
