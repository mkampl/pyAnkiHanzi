# pyAnkiHanzi

A Python tool for creating Anki flashcards for Chinese characters with interactive stroke order animations and subdeck support.

## Features

- **Interactive Stroke Order**: Uses HanziWriter for correct stroke sequence learning
- **Audio Support**: Automatic TTS pronunciation with intelligent caching
- **Pinyin Integration**: Automatic conversion with tone marks
- **Subdeck Support**: Organize cards into hierarchical subdecks
- **Template System**: Customizable modern card templates
- **Error Handling**: Comprehensive validation and meaningful error messages
- **Progress Display**: Visual progress indication during card creation

## Quick Start

### Generate HSK Vocabulary Decks

```bash
# 1. Generate CSV from HSK JSON data
python hsk_csv_generator.py

# 2. Create Anki deck with subdecks for all HSK levels
python pyAnkiHanzi.py hsk_complete.csv
```

This creates a single Anki deck with subdecks:
- HSK Complete Vocabulary::HSK 1
- HSK Complete Vocabulary::HSK 2
- HSK Complete Vocabulary::HSK 3
- ...up to HSK 9

### Create Custom Decks

```bash
# Basic usage
python pyAnkiHanzi.py my_vocabulary.csv

# Without audio (faster)
python pyAnkiHanzi.py my_vocabulary.csv --no-audio

# With custom template
python pyAnkiHanzi.py my_vocabulary.csv --template my_template.json
```

## Installation

```bash
# Install dependencies
pip install genanki gtts pypinyin tqdm requests

# Clone or download the repository
git clone <repository-url>
cd pyAnkiHanzi
```

## CSV Format

### Basic Format
```
#<deck_id>	<deck_name>
<translation>	<hanzi>
<translation>	<hanzi>
```

### With Subdecks
```
#<deck_id>	<deck_name>
##<subdeck_name>
<translation>	<hanzi>
<translation>	<hanzi>
##<another_subdeck>
<translation>	<hanzi>
```

### Example
```
#2059400110	Chinese Basic Vocabulary
##Greetings
Hello (nǐ hǎo)	你好
Thank you (xiè xiè)	谢谢
##Food
Water (shuǐ)	水
Rice (mǐ fàn)	米饭
```

## Audio Caching

The tool includes intelligent audio caching to avoid TTS rate limits:

- Audio files are cached in `./audio_cache/`
- Re-running uses cached files automatically
- Failed requests are tracked to avoid retries
- Compatible with HSK generator cache

## Templates

The default template (`hanzi_template.json`) provides:
- Modern gradient design with glassmorphism effects
- Interactive stroke order practice on front
- Stroke order animation on back
- Responsive layout for mobile devices

### Custom Templates

Create your own JSON template with `qfmt` and `afmt` fields:

```json
{
  "qfmt": "<div>Front side HTML with {{Translation}} and {{Hanzi}}</div>",
  "afmt": "<div>Back side HTML with {{Translation}}, {{Hanzi}}, {{Pinyin}}, {{Mp3}}</div>"
}
```

Use placeholders like `__HANZI_WRITER_VERSION__` for configuration values.

## Command Line Options

### pyAnkiHanzi.py
```bash
python pyAnkiHanzi.py input.csv [options]

Options:
  --no-audio          Skip audio generation
  --language LANG     TTS language: zh, zh-cn, zh-tw (default: zh)
  --output FILE       Output filename (default: based on input)
  --template FILE     Custom template file (default: hanzi_template.json)
  --verbose, -v       Verbose output
```

### hsk_csv_generator.py
```bash
python hsk_csv_generator.py

# Downloads HSK JSON data and creates hsk_complete.csv
# Ready for use with pyAnkiHanzi.py
```

## Testing

Run the test suite to verify everything works correctly:

```bash
# Run all tests
python test_pyankihanzi.py --run-tests

# Run basic functionality tests only
python test_pyankihanzi.py --run-tests --test-suite basic

# Check if all dependencies are installed
python test_pyankihanzi.py --diagnose

# Create a sample CSV file for testing
python test_pyankihanzi.py --create-sample
```

The test suite includes:
- CSV format validation
- Subdeck functionality
- Audio caching
- Pinyin conversion
- Template loading
- Error handling

## File Structure

```
pyAnkiHanzi/
├── pyAnkiHanzi.py           # Main Anki deck generator
├── hsk_csv_generator.py     # HSK vocabulary CSV generator
├── test_pyankihanzi.py      # Test suite
├── hanzi_template.json      # Default modern template
├── elegant_card_template.json # Alternative elegant template
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Card Format

Each Anki card contains:
- **Front**: Translation with interactive stroke order practice
- **Back**: Chinese characters, Pinyin, audio, and stroke animation
- **Fields**: Translation, Hanzi, Pinyin, Mp3

## Troubleshooting

**CSV Format Errors**
- Ensure UTF-8 encoding
- Use tab separation
- Header format: `#<number><TAB><name>`

**Audio Issues**
- Use `--no-audio` to skip TTS
- Check internet connection
- Audio cache will resume on retry

**Template Errors**
- Verify JSON syntax
- Check placeholder names
- Use default template for testing

## HSK Vocabulary

The HSK CSV generator downloads vocabulary from the complete HSK repository covering:
- HSK 1-6 (Traditional levels)
- HSK 7-9 (New advanced levels)
- Both old and new HSK systems
- English meanings and Pinyin included

Data source: [Complete HSK Vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary)

## Dependencies

- **genanki**: Anki package generation
- **gtts**: Text-to-speech audio
- **pypinyin**: Chinese to Pinyin conversion
- **tqdm**: Progress bars
- **requests**: Downloads HSK data from [drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary)

## License

MIT License - see LICENSE file for details.
