import pyperclip
import os
import time
import re
from httpx import Timeout  # Ensure this import works with the updated version
import subprocess  # For running googletrans in a separate environment
from gtts import gTTS  # Add gtts for TTS fallback
import tempfile  # For temporary audio files

last_text = ""
new_words = set()  # To track new words

def is_english_text(text):
    # Optimized to avoid creating unnecessary lists
    english_chars = sum(1 for char in text if char.isalpha() and char.isascii())
    return english_chars > 0 and english_chars / max(1, len(text)) > 0.6

def show_notification(title, subtitle, message):
    # Escaping for shell command
    message = message.replace('"', '\\"')
    subtitle = subtitle.replace('"', '\\"')
    os.system(
        f'''terminal-notifier -title "{title}" -message "{message}" -subtitle "{subtitle}" -timeout 2'''
    )

def split_text_into_chunks(text, max_length=500):
    # Splits text into chunks of a specified maximum length
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += len(word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def save_new_words_to_file(filepath="new_words.txt"):
    # Save the new words to a file
    with open(filepath, "w", encoding="utf-8") as file:
        for word in sorted(new_words):
            file.write(word + "\n")
    print(f"New words saved to {filepath}")

def stop_speech():
    # Stops any ongoing speech
    os.system("pkill -f 'say'")

def pronounce_text(text, voice="Karen", rate=180):
    # Pronounce the text with a specified voice and rate
    stop_speech()  # Stop any ongoing speech before starting new
    os.system(f'say -v {voice} -r {rate} "{text}"')

def pronounce_text_gtts(text, lang="en"):
    # Pronounce the text using gtts and the default system player
    if not text.strip():
        print("No text to pronounce.")
        return
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            temp_path = fp.name
        # Use the default system player (afplay for macOS, start for Windows, xdg-open for Linux)
        if os.name == "posix":
            os.system(f"afplay '{temp_path}'")
        elif os.name == "nt":
            os.system(f"start {temp_path}")
        else:
            os.system(f"xdg-open '{temp_path}'")
        os.remove(temp_path)
    except Exception as e:
        print(f"gTTS error: {e}")

def translate_with_googletrans(text, dest="he"):
    """
    Use a subprocess to call googletrans in a separate virtual environment.
    """
    try:
        result = subprocess.run(
            [
                "/Users/agamalon/Downloads/googletrans-env/bin/python",
                "-c",
                f"from googletrans import Translator; print(Translator().translate('{text}', dest='{dest}').text)"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error calling googletrans subprocess: {e}")
        return None

def process_text(text):
    # Only Google Translate logic, no ChatGPT
    if len(text.split()) == 1:  # Single word
        translation = translate_with_googletrans(text, dest='he')
        if translation:
            print("Translation:", translation)
            pyperclip.copy(translation)

            # Add to new words list
            new_words.add(text)

            # Show notification with both English and Hebrew
            show_notification("📘 Word Translation", f"{text} -> {translation}", f"{text} -> {translation}")

            # Pronounce the English word using gtts (force lang='en')
            pronounce_text_gtts(text, lang="en")
    else:  # Full paragraph
        # Split text into chunks and translate each
        chunks = split_text_into_chunks(text)
        translations = []
        for chunk in chunks:
            translation = translate_with_googletrans(chunk, dest='he')
            if translation:
                translations.append(translation)

        # Combine translations and copy to clipboard
        full_translation = " ".join(translations)
        print("Translation:", full_translation)
        pyperclip.copy(full_translation)

        # Show notification with a preview of the translation
        show_notification("📘 Paragraph Translation", f"of: {text[:50]}...", full_translation[:50] + "...")

        # Pronounce the English text using gtts (force lang='en')
        pronounce_text_gtts(text[:500], lang="en")

def main():
    global last_text
    print("📚 English-to-Hebrew Clipboard Translator is running...")
    max_text_length = 5000  # Set a maximum limit for clipboard text
    while True:
        try:
            text = pyperclip.paste().strip()
            if len(text) > max_text_length:
                print("Text is too long to process. Please copy smaller text.")
                time.sleep(1.5)
                continue

            # Only proceed if it's new, non-empty, and mostly English
            if (
                text and
                text != last_text and
                is_english_text(text)
            ):
                print("You copied:", text)
                last_text = text

                # Process the text with Google Translate logic only
                process_text(text)

                # Wait to avoid double notifications
                time.sleep(2.2)
            else:
                time.sleep(1.0)
        except KeyboardInterrupt:
            # On exit, save new words to a file and display them
            save_new_words_to_file()
            print("\nSession ended. Here are the new words you learned:")
            for word in sorted(new_words):
                print(word)
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1.5)

if __name__ == "__main__":
    main()