# Flashcard Generator

This project automatically generates flashcards for a your course syllabus using Google Gemini API and adds them to an Anki deck via AnkiConnect.

---

## Features

- Parses the course syllabus units and generates flashcards (Q&A pairs) for each unit.
- Uses Google Gemini API (`gemini-2.5-flash` model) to generate unique and relevant flashcards.
- Adds flashcards directly into an Anki deck using AnkiConnect.
- Keeps track of duplicates via a JSON log file to avoid repeating flashcards.
- Configurable Anki deck name and log file.
- Built-in delay to avoid API rate limits.

---

## Requirements

- Python 3.x
- `requests` library
- `google-genai` Python SDK (for Gemini API client)
- Running [AnkiConnect](https://ankiweb.net/shared/info/2055492159) on your local machine with Anki open.
- Google Gemini API key

---

## Setup

1. Clone this repo:
   ```bash
   git clone https://github.com/yourusername/pgdca-flashcard-generator.git
   cd pgdca-flashcard-generator
   ```

2. Install dependencies:
   ```bash
   pip install requests google-genai
   ```

3. Get your Google Gemini API key and set it in the script (`GEMINI_API_KEY` variable).

4. Make sure Anki is running with the AnkiConnect plugin enabled.

5. Run the script:
   ```bash
   python generate_flashcards.py
   ```

---

## Configuration

- **ANKI_DECK_NAME**: Set the name of the Anki deck where flashcards will be added.
- **LOG_FILE**: Path to the JSON file used to track already added flashcards and avoid duplicates.
- **COURSE_SYLLABUS**: The syllabus text used to generate flashcards.

---

## Notes

- Each run generates up to 20 flashcards per syllabus unit.
- There is a 15-second delay between adding cards to avoid API rate limits.
- Make sure AnkiConnect is running on `http://localhost:8765`.

---

## License

This project is open source and free to use.

---

## Author

Your Name (or GitHub username)

---

## Example


you can check the json output file for the sample

Feel free to open issues or contribute!
