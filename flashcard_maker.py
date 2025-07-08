import os
import json
import requests
from google import genai
import time

GEMINI_API_KEY = 'your gemini_api key here'


# === Anki deck name where flashcards will be added ===
ANKI_DECK_NAME = "PCA105 - Digital System"

# === JSON log file path to track duplicates ===
LOG_FILE = "flashcard_log.json"

# === Initialize Google Gemini Client ===
client = genai.Client(api_key=GEMINI_API_KEY)

# === Course syllabus text ===
COURSE_SYLLABUS = """
Unit 1: Matrix and Determinant (14 Hrs)
Matrix and Determinant; Vector space (Introduction), dependent and independent vectors; Linear Transformation; System of Linear equations (Gauss Elimination method); Inverse of matrix (Gauss Jordan method); Rank of the matrix; Eigen values of matrix. Eigen vectors and its applications.

Unit 2: Derivatives (5 Hrs)
Definition of derivatives; Derivative Rules: Power, Sum, Product, Quotient, Chain rules; Derivatives of: Algebraic functions, Trigonometric functions, Exponential functions, Logarithmic functions, Inverse Trigonometric functions, Hyperbolic functions. Evaluation of limits; Using L'Hopital’s Rule.

Unit 3: Integral Calculus (10 Hrs)
Indefinite and Definite integrals; Integration Formulas, Substitutions, Trigonometric Substitutions, Integration by parts; Standard Integrals, Use of partial fractions, Evaluation of integrals using standard formulas; Definite Integral and its evaluation; Applications in calculating length, surface area, volume and average value. (Common curves only); Evaluation of Improper integrals.

Unit 4: Laplace Transform (10 Hrs)
Introduction; Laplace transform of some elementary functions; Properties of Laplace transform; Inverse Laplace transforms; Application to differential equations.

Unit 5: Fourier series (6 Hrs)
Periodic function; Trigonometric Series; Fourier series; Determination of Fourier coefficients Euler Formula (-π, π); Fourier Series in the intervals (0, 2π) and (-ℓ, ℓ); Even and Odd functions and their Fourier Series: Fourier cosine and Sine Series; Half range function; Parseval’s formula; Fourier series in complex form (Introduction).
"""

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"flashcards": []}

def save_log(log_data):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2)

def is_duplicate(front, log_data):
    return any(card["front"] == front for card in log_data["flashcards"])

def call_gemini_api(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text

def parse_qa_pairs(text):
    qa_pairs = []
    lines = text.split('\n')
    q = None
    a = None
    for line in lines:
        line = line.strip()
        if line.startswith('Q:'):
            if q and a:
                qa_pairs.append((q, a))
            q = line[2:].strip()
            a = None
        elif line.startswith('A:'):
            a = line[2:].strip()
    if q and a:
        qa_pairs.append((q, a))
    return qa_pairs

def add_anki_card(front, back, deck=ANKI_DECK_NAME):
    note = {
        "deckName": deck,
        "modelName": "Basic",
        "fields": {
            "Front": front,
            "Back": back
        },
        "options": {
            "allowDuplicate": False
        }
    }
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": note
        }
    }
    try:
        response = requests.post("http://localhost:8765", json=payload).json()
        return response
    except Exception as e:
        print("AnkiConnect request failed:", e)
        return None

def generate_flashcards_for_unit(unit_text, unit_number):
    prompt = f"""
You are a helpful assistant creating flashcards for a PGDCA course.
Based on the following unit syllabus text, generate 20 unique flashcards per unit (question and answer) in this format:

Q: [Question]
A: [Answer]

Avoid repeating any previously generated question. Make questions clear, concise, and relevant to the unit content.

Unit {unit_number} syllabus:
\"\"\"
{unit_text}
\"\"\"
"""
    output = call_gemini_api(prompt)
    if not output:
        return []
    return parse_qa_pairs(output)

def main():
    log_data = load_log()
    units = COURSE_SYLLABUS.strip().split('Unit ')[1:]  # Split syllabus by 'Unit '
    for unit in units:
        lines = unit.strip().split('\n')
        if not lines:
            continue
        try:
            unit_number = int(lines[0].split(':')[0])
        except:
            unit_number = 0
        unit_text = '\n'.join(lines[1:]).strip()

        print(f"\nGenerating flashcards for Unit {unit_number} ...")
        qa_pairs = generate_flashcards_for_unit(unit_text, unit_number)

        for front, back in qa_pairs:
            if is_duplicate(front, log_data):
                print(f"Skipping duplicate question: {front}")
                continue

            print(f"Adding card:\n Q: {front}\n A: {back}\n")
            response = add_anki_card(front, back)

            # Fixed success detection logic
            if response and response.get('result') is not None and response.get('error') is None:
                print(f"✅ Added card successfully with note ID: {response.get('result')}")
                log_data["flashcards"].append({"front": front, "back": back, "unit": unit_number})
                save_log(log_data)
            else:
                error_msg = response.get('error') if response else "No response from AnkiConnect"
                print(f"❌ Failed to add card: {error_msg}")
                print(f"Full response: {response}")

            time.sleep(15)  # Delay to avoid API rate limits # Delay to avoid API rate limits

if __name__ == "__main__":
    main()