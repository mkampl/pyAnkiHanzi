import genanki
from gtts import gTTS
from pypinyin import pinyin, Style
import os

def get_pronunciation_mp3(word, language='zh'):
    unicode_ids = "_".join(str(ord(char)) for char in word)
    mp3_filename = f"{unicode_ids}_pronunciation.mp3"
    tts = gTTS(word, lang=language)
    tts.save(mp3_filename)
    return mp3_filename

def get_pinyin_with_tones(word):
    pinyin_with_tone = pinyin(word, style=Style.TONE)
    return ' '.join([item[0] for item in pinyin_with_tone])

model = genanki.Model(
    1607392319,
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
            'qfmt': '''
              <div id="translation">{{Translation}}</div>
<div id="target-quiz"></div>
<script type="text/javascript">
  var characters = "{{Hanzi}}".split("");
  var js = document.createElement("script");
  js.type = "text/javascript";
  js.src = "https://cdn.jsdelivr.net/npm/hanzi-writer@2.2/dist/hanzi-writer.min.js";
  js.onload = function() {
    for (let x of characters) {
      // Create a container for each character
      var characterContainer = document.createElement('div');
      characterContainer.style.display = 'inline-block';  // Ensure characters are inline
      characterContainer.style.border = '2px solid black';  // Border around the character
      characterContainer.style.margin = '2px';  // Margin between characters

      // Create HanziWriter instance inside the container
      var writer = HanziWriter.create(characterContainer, x, {
        width: 150,
        height: 150,
        showCharacter: false,
        showOutline: false,
        showHintAfterMisses: 1,
        highlightOnComplete: false,
        padding: 5
      });

      // Initialize the quiz functionality
      writer.quiz({
        onMistake: function() { console.log("Mistake!"); },
        onComplete: function() { console.log("Completed!"); }
      });

      // Append the character container to the target container
      document.getElementById('target-quiz').appendChild(characterContainer);
    }
  };
  document.body.appendChild(js);
</script>


            ''',
            'afmt': '''
                <div id="word">{{Translation}} - {{Hanzi}} {{Pinyin}} <br>{{Mp3}}<br></div>
                <hr id="answer">
                <div id="target-animation"></div>
                <script type="text/javascript">
                  var characters = "{{Hanzi}}".split("");
                  var js = document.createElement("script");
                  js.type = "text/javascript";
                  js.src = "https://cdn.jsdelivr.net/npm/hanzi-writer@2.2/dist/hanzi-writer.min.js";
                  js.onload = function() {
                    for (let x of characters) {
                      var writer = HanziWriter.create('target-animation', x, {
                        width: 70,
                        height: 70,
                        padding: 5,   
                        showOutline: true,
                        strokeAnimationSpeed: 1, 
                        delayBetweenStrokes: 150,
                        radicalColor: '#337ab7'
                      });
                      writer.loopCharacterAnimation();
                    }
                  };
                  document.body.appendChild(js);
                </script>
            ''',
        },
    ],
)

deck = genanki.Deck(2059400110, 'Hanzi Stroke Order with Online JS')

hanzi_words = [['Hello', '你好'], ['learn', '学习'], ['chinese character', '汉字'], ['china', '中国']]
media_files = []

for word in hanzi_words:
    pinyin_str = get_pinyin_with_tones(word[1])
    mp3 = get_pronunciation_mp3(word[1])
    media_files.append(mp3)
    note = genanki.Note(
        model=model,
        fields=[word[0], word[1], pinyin_str, '[sound:'+mp3+']']
    )
    deck.add_note(note)

package = genanki.Package(deck)
package.media_files = media_files

output_file = 'Hanzi_Stroke_Order_Online_JS.apkg'
package.write_to_file(output_file)

# Clean up MP3 files
for file in media_files:
    os.remove(file)

print(f"Deck created successfully: {output_file}")
