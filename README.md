# pyAnkiHanzi

`pyAnkiHanzi` ist ein Python-Skript, das eine CSV-Datei mit chinesischen Zeichen (Hanzi) oder Phrasen und deren
Übersetzungen einliest und daraus ein Anki-Karteikartendeck erstellt. Die generierten Karten enthalten:

- **Pinyin** mit Tönen zur Aussprachehilfe
- **Text-to-Speech (TTS)**-generierte Audio-Dateien zur Aussprache
- **Strichreihenfolge-Animationen** zur visuellen Unterstützung
- **Interaktive Schreibübungen** mit `hanzi-writer`

## Voraussetzungen

Bevor du das Skript verwendest, stelle sicher, dass die folgenden Abhängigkeiten installiert sind:

```bash
pip install genanki gtts pypinyin
```

## Verwendung

Das Skript wird mit einer CSV-Datei als Eingabe aufgerufen:

```bash
python3 pyAnkiHanzi.py <input.csv>
```

Die CSV-Datei muss im **tabulator-getrennten** Format sein und folgende Struktur haben:

```
<Deck-Nummer>\t<Deck-Name>
<Übersetzung>\t<Hanzi>
<Übersetzung>\t<Hanzi>
...
```

### Beispiel für `input.csv`:

```
123456\tDeck Name
Hello\t你好
Thank you\t谢谢
```

## Funktionen

### 1. **Pinyin-Erzeugung**

Das Skript verwendet `pypinyin`, um die Lautumschrift (Pinyin mit Tönen) automatisch zu generieren.

### 2. **Aussprache als MP3 (TTS)**

Mit `gTTS` (Google Text-to-Speech) wird zu jedem chinesischen Wort eine Audiodatei erzeugt.

### 3. **Strichreihenfolge-Animation**

Durch die Einbindung von `hanzi-writer` zeigt jede Karte eine interaktive Strichreihenfolge-Animation.

### 4. **Schreibquiz in Anki**

Das Skript fügt Anki-Karten eine interaktive Quizfunktion hinzu, bei der Nutzer die Zeichen nachzeichnen müssen.

## Ausgabe

Das Skript erzeugt eine `.apkg`-Datei, die direkt in Anki importiert werden kann.

## Beispiel-Deck

Ein Beispieldeck mit der offiziellen HSK 3.0 Wortliste ist im Repository enthalten.
