import difflib
import re
from sqlalchemy.orm import sessionmaker
from models.models import Symptom



DIABETES_SYMPTOMS = ['blurred vision', 'thirst', 'frequent urination', 'increased hunger', 'fatigue', 'slow healing', 'numbness', 'weight loss']
NEGATION_PHRASES = ['deny', 'denies', 'no', 'not', 'without', 'never', 'none', 'neither', 'nor', 'nowhere', 'n\'t']

NEGATION_PATTERNS = [
    r'(cannot|can\'t|ca?n\'?t)',  # can't, cannot, can not
    r'(won\'t|will\snot)',
    r'(didn\'t|did\snot)',
    r'(doesn\'t|does\snot)',
    r'(haven\'t|has\snot|have\snot)',
    r'(wasn\'t|were\snot|was\snot)',
    r'(wouldn\'t|would\snot)',
    r'(couldn\'t|could\snot)',
    r'(shouldn\'t|should\snot)',
    r'(mightn\'t|might\snot)',
    r'(mustn\'t|must\snot)',
    r'(needn\'t|need\snot)',
    r'(daren\'t|dare\snot)',
    r'(shan\'t|shall\snot)',
    r'(aren\'t|are\snot|is\snot)',
    r'(n\'t)',  # Handles contractions like "isn't", "wasn't", etc.
]

def insert_symptom(db_session: sessionmaker, symptom, ill_diagnosed, doc_id):
    insert_symptoms = Symptom(symptom=symptom, ill_diagnosed=ill_diagnosed, doc_id=doc_id)
    db_session.add(insert_symptoms)
    db_session.commit()

def detect_negation(sentence):
    for phrase in NEGATION_PHRASES:
        if phrase in sentence:
            return True
    for pattern in NEGATION_PATTERNS:
        if re.search(pattern, sentence, re.IGNORECASE):
            return True
    return False


def detect_symptoms_diabetes(lemmatized_text, diabetes_symptoms):
    detected_symptoms = []

    for sentence in lemmatized_text:
        found_symptoms = set()
        is_negative = detect_negation(' '.join(sentence))  # Check negation for the entire sentence

        for symptom in diabetes_symptoms:
            if not is_negative:  # Only consider symptoms if negation isn't present
                all_words_found = True
                for word in symptom.split():
                    found_match = False
                    if word in sentence:  # Check for exact match
                        found_match = True
                    else:
                        close_matches = difflib.get_close_matches(word, sentence, n=1, cutoff=0.7)
                        if close_matches:  # Check for similar word
                            found_match = True
                            word = close_matches[0]
                    if not found_match:
                        all_words_found = False
                        break  # Stop searching for words in this symptom if any is missing

                if all_words_found:
                    found_symptoms.add(symptom)

        detected_symptoms.extend(found_symptoms)

    return detected_symptoms

def insert_symptoms(db_session: sessionmaker, detected_symptoms, doc_id):
    for detected_symptom in detected_symptoms:
            insert_symptom(db_session, detected_symptom, "Diabetes", doc_id)


