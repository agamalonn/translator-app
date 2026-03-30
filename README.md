# 📚 English-to-Hebrew Clipboard Translator

A smart Python-based automation tool that listens to your clipboard, detects English text, provides instant Hebrew translations, and reads them out loud.

## ✨ Key Features
- **Real-time Monitoring:** Instantly detects when you copy English text.
- **Smart Detection:** Only processes English content to avoid unnecessary translations.
- **Voice Synthesis (TTS):** Pronounces words/sentences using gTTS for better learning.
- **Vocabulary Builder:** Saves single translated words to `new_words.txt` automatically.
- **System Notifications:** Displays the translation as a macOS system notification.

## 🚀 Getting Started
1. Install dependencies:
   ```bash
   pip install pyperclip gtts httpx
   ```
2. Run the script:
   ```bash
   python3 translator_script.py
   ```
3. Copy any English text and watch the magic happen!

## 🛠 Requirements
- Python 3.x
- `terminal-notifier` (for macOS notifications)
- Internet connection (for Google Translate API)
