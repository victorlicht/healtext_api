import string
import nltk
import medialpy
import re
from sqlalchemy.orm import sessionmaker
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from models.models import ProcessedEhr
from nlp.lab_results_extractions import extract_results, parse_and_store_lab_results
# from .symptoms_extractions import detect_symptoms, NEGATION_PHRASES, DIABETES_SYMPTOMS
NEGATION_PHRASES = ['deny', 'denies', 'no', 'not', 'without', 'never', 'none', 'neither', 'nor', 'nowhere', 'n\'t']

def get_hpi(db_session: sessionmaker, doc_id):
    processed_ehr = db_session.query(ProcessedEhr).filter_by(doc_id=doc_id).first()
    if processed_ehr:
        return processed_ehr.hpi
    else:
        return None

def get_medications(db_session: sessionmaker, doc_id):
    processed_ehr = db_session.query(ProcessedEhr).filter_by(doc_id=doc_id).first()
    if processed_ehr:
        return processed_ehr.medications
    else:
        return None

def get_lab_tests(db_session: sessionmaker, doc_id):
    processed_ehr = db_session.query(ProcessedEhr).filter_by(doc_id=doc_id).first()
    if processed_ehr:
        return processed_ehr.lab_tests
    else:
        return None

def get_family_history(db_session: sessionmaker, doc_id):
    processed_ehr = db_session.query(ProcessedEhr).filter_by(doc_id=doc_id).first()
    if processed_ehr:
        return processed_ehr.family_history
    else:
        return None

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # Default to noun if unknown

# Function to lemmatize words with POS tagging
def lemmatize_words(words):
    pos_tags = nltk.tag.pos_tag(words)  # Use nltk.tag.pos_tag directly
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = []
    for word, pos_tag in pos_tags:
        wordnet_pos = get_wordnet_pos(pos_tag)
        lemmatized_word = lemmatizer.lemmatize(word, pos=wordnet_pos)
        lemmatized_words.append(lemmatized_word)
    return lemmatized_words

# Function to expand medical abbreviations
def expand_medical_abbreviations(words):
    expanded_words = []
    for word in words:
        term = medialpy.find(word)
        if term is not None:
            expanded_words.append(term.meaning[0])  # Select the first option
        else:
            expanded_words.append(word)
    return expanded_words

def split_sentence_into_phrases(sentence):
  conjunctions = ["and", "but", "so", "yet", "for"]
  pronouns = ["i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"]
  identified_phrases = []
  current_phrase = []

  # Split the sentence into individual sentences using full stop (.)
  sentences = sentence.split('.')

  for sentence in sentences:
    for word in sentence.split():
        if word.lower() in conjunctions:
            if current_phrase:
                identified_phrases.append(' '.join(current_phrase))
                current_phrase = []
        elif word.lower() in pronouns:
            if current_phrase:
                identified_phrases.append(' '.join(current_phrase))
                current_phrase = [word]
            else:
                current_phrase.append(word)
        else:
            current_phrase.append(word)
    if current_phrase:
        identified_phrases.append(' '.join(current_phrase))
        current_phrase = []

  return identified_phrases


def filter_noise(text):
  filtered_text = []
  for word in text.split():
    # Remove punctuation and special characters except for alphanumeric and space
    filtered_word = ''.join(c for c in word if c in string.ascii_letters + string.digits + " " + "'" + ":" + "." + "-")
    if filtered_word:  # Add only non-empty filtered words
        filtered_text.append(filtered_word)
  return ' '.join(filtered_text)


def preprocess_text(db_session: sessionmaker, doc_id):
    hpi_text = get_hpi(db_session, doc_id)
    phrases = split_sentence_into_phrases(hpi_text)
    filtered_phrases = [filter_noise(phrase) for phrase in phrases]
    words = [word_tokenize(phrase) for phrase in filtered_phrases]
    expanded_words = [expand_medical_abbreviations(word) for word in words]

    stop_words = set(stopwords.words('english'))
    filtered_words = [
        [word for word in phrase if 
        (word.lower() not in stop_words) 
        or 
        (word in NEGATION_PHRASES)] 
        for phrase in expanded_words
        ]
    lemmatized_words = [lemmatize_words(phrase) for phrase in filtered_words]

    # Return both lemmatized text and detected symptoms
    return lemmatized_words

def preprocess_medications_text(db_session: sessionmaker, doc_id):
    return None

def preprocess_lab_tests_text(db_session: sessionmaker, doc_id, ill_diagnosed):
    filtered_text = filter_noise(get_lab_tests(db_session, doc_id))
    return extract_results(db_session, filtered_text, doc_id, ill_diagnosed)
    
