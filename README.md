# pyAnkiHanzi 🈲

Ein verbessertes Python-Tool zur Erstellung von Anki-Karten für chinesische Zeichen mit interaktiven Strichfolgen-Animationen.

## Features ✨

- **Robuste Fehlerbehandlung**: Umfassende Validierung und aussagekräftige Fehlermeldungen
- **Interaktive Strichfolgen**: Nutzt HanziWriter für das Lernen der korrekten Strichfolge
- **Audio-Unterstützung**: Automatische Generierung von Aussprache-Dateien (TTS)
- **Pinyin-Integration**: Automatische Konvertierung zu Pinyin mit Tönen
- **Progress-Anzeige**: Visualisierung des Fortschritts bei der Kartenerstellung
- **Duplikat-Erkennung**: Warnt vor doppelten Einträgen
- **Konfigurierbare Optionen**: Flexible Anpassung über Kommandozeilenparameter
- **Logging**: Detaillierte Protokollierung für Debugging
- **Context Manager**: Automatische Bereinigung temporärer Dateien

## Installation 📦

1. **Repository klonen oder Dateien herunterladen**
2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

### Systemvoraussetzungen

- Python 3.7+
- Internetverbindung (für HanziWriter CDN und TTS)

## Nutzung 🚀

### Grundlegende Nutzung

```bash
python pyAnkiHanzi.py input.csv
```

### Mit Optionen

```bash
# Ohne Audio-Dateien
python pyAnkiHanzi.py input.csv --no-audio

# Mit spezifischer Sprache
python pyAnkiHanzi.py input.csv --language zh-cn

# Mit benutzerdefinierter Ausgabedatei
python pyAnkiHanzi.py input.csv --output mein_deck.apkg

# Ausführliche Ausgabe
python pyAnkiHanzi.py input.csv --verbose
```

### CSV-Format 📄

Die Eingabe-CSV-Datei muss folgendes Format haben:

```
DECK_ID	DECK_NAME
ÜBERSETZUNG1	HANZI1
ÜBERSETZUNG2	HANZI2
...
```

**Beispiel:**
```
123456	Chinesisch Grundwortschatz
Hallo	你好
Danke	谢谢
Auf Wiedersehen	再见
```

### Beispiel-CSV erstellen

```bash
# Erstellt eine Beispiel-CSV-Datei
python test_pyankihanzi.py --create-sample
```

## Programmstruktur 🏗️

### Hauptklasse: `AnkiHanziGenerator`

```python
with AnkiHanziGenerator(language='zh', include_audio=True) as generator:
    output_file = generator.create_deck('input.csv')
    print(f"Deck erstellt: {output_file}")
```

### Wichtige Methoden

- `validate_csv_format()`: Validiert die Eingabedatei
- `read_hanzi_words()`: Liest und parst die CSV-Datei
- `check_duplicates()`: Erkennt doppelte Einträge
- `get_pinyin_with_tones()`: Konvertiert zu Pinyin
- `get_pronunciation_mp3()`: Erstellt Audio-Dateien
- `create_deck()`: Generiert das Anki-Deck

## Konfiguration ⚙️

### Verfügbare Parameter

| Parameter | Beschreibung | Standard |
|-----------|--------------|----------|
| `--language` | TTS-Sprache (zh, zh-cn, zh-tw) | zh |
| `--no-audio` | Deaktiviert Audio-Generierung | False |
| `--output` | Ausgabedatei | input.apkg |
| `--verbose` | Ausführliche Ausgabe | False |

### Erweiterte Konfiguration

Die Datei `config.py` enthält detaillierte Einstellungen für:
- HanziWriter-Parameter
- TTS-Konfiguration
- Validierungsregeln
- Anki-Modell-Einstellungen

## Tests ausführen 🧪

```bash
# Alle Tests ausführen
python test_pyankihanzi.py --run-tests

# Oder mit pytest
pytest test_pyankihanzi.py -v
```

## Logging 📋

Das Tool erstellt automatisch eine Log-Datei `pyankihanzi.log` mit:
- Informationen über den Verarbeitungsfortschritt
- Warnungen bei Problemen
- Fehlerdetails für Debugging

## Fehlerbehebung 🔧

### Häufige Probleme

1. **"Datei nicht gefunden"**
   - Prüfen Sie den Dateipfad
   - Stellen Sie sicher, dass die Datei eine .csv-Endung hat

2. **"Ungültiges CSV-Format"**
   - Header muss mindestens 2 Spalten haben
   - Verwenden Sie Tab-Trennung
   - Erste Zeile: `DECK_ID<TAB>DECK_NAME`

3. **TTS-Fehler**
   - Internetverbindung prüfen
   - Mit `--no-audio` ohne Audio erstellen

4. **Encoding-Probleme**
   - CSV-Datei muss UTF-8 kodiert sein
   - In Excel: "Speichern unter" → "CSV UTF-8"

### Debug-Modus

```bash
python pyAnkiHanzi.py input.csv --verbose
```

## Erweiterte Features 🎯

### Batch-Verarbeitung

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

### Anpassung der Kartenvorlage

Die HTML-Templates in der `create_model()`-Methode können angepasst werden für:
- Unterschiedliche Schriftgrößen
- Farbschemata
- Zusätzliche Felder
- Layout-Änderungen

## Beitragen 🤝

1. Fork des Repositories
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request öffnen

## Lizenz 📄

Dieses Projekt steht unter der MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

## Danksagungen 🙏

- [HanziWriter](https://hanziwriter.org/) für die Strichfolgen-Animationen
- [genanki](https://github.com/kerrickstaley/genanki) für die Anki-Package-Generierung
- [gTTS](https://github.com/pndurette/gTTS) für die Text-zu-Sprache-Funktionalität
- [pypinyin](https://github.com/mozillazg/python-pinyin) für die Pinyin-Konvertierung

## Changelog 📅

### Version 2.0.0
- ✨ Komplett überarbeitete Architektur mit Klassen
- ✨ Robuste Fehlerbehandlung und Validierung
- ✨ Progress-Bars und bessere Benutzerfreundlichkeit
- ✨ Umfassendes Logging
- ✨ Context Manager für Ressourcenverwaltung
- ✨ Duplikat-Erkennung
- ✨ Konfigurierbare Optionen
- ✨ Umfassende Tests
- 🐛 Behebung von Encoding-Problemen
- 🐛 Verbesserte Bereinigung temporärer Dateien

---

**Viel Erfolg beim Chinesisch lernen! 🇨🇳**
