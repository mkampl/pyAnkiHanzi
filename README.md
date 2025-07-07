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

## Installation 📦

1. **Clone repository or download files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
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

3. **TTS errors**
   - Check internet connection
   - Create without audio using `--no-audio`

4. **Encoding problems**
   - CSV file must be UTF-8 encoded
   - In Excel: "Save as" → "CSV UTF-8"

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

## Usage Examples 📖

### Basic Card Creation

```bash
# Create a basic deck
python pyAnkiHanzi.py my_vocabulary.csv
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
```

---

**Happy Chinese learning! 🇨🇳**
