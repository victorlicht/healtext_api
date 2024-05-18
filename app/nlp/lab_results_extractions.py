from datetime import datetime
import re
from models.models import LabResult

def extract_time(text):
    #Extract Time from text
    time_pattern = r"\d{1,2}:\d{2}(?:\s*(AM|PM))?"  # Allow variations (optional)
    compiled_pattern = re.compile(time_pattern)

    all_times = []
    for time_match in compiled_pattern.finditer(text):  # Use finditer for all matches
        time_str = time_match.group(0)
        all_times.append(time_str)

    return all_times



# Example diabetes-related tests (modify as needed)
DIABETES_TESTS = {
    "GLUCOSE": "Blood Glucose",
    "SODIUM": "Sodium",
    "HEMOGLOBIN A1C": "Hemoglobin A1c",
    "FRUCTOSAMINE": "Fructosamine",
    "INSULIN": "Insulin",
    "C-PEPTIDE": "C-Peptide",
    "KETONES": "Ketones",
    "UREA N": "Blood Urea Nitrogen (BUN)",
    "PT": "Glycosylated Hemoglobin",
    "PH": "PH",
    "RBC": "Fructosamine",
    "Potassium ": "Potassium",
    "CO2": "Total CO2",
}


def extract_date_time(text):
    # Extract Date and Time from text
    date_time_pattern = r"(\d{4}-\d{1,2}-\d{1,2}) (\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)"
    compiled_pattern = re.compile(date_time_pattern)
    
    date_times = []
    for match in compiled_pattern.finditer(text):
        date_times.append((match.group(1), match.group(2)))
    
    return date_times

def split_text_by_date_time(text):
    date_times = extract_date_time(text)
    chunks = {}
    
    for i in range(len(date_times)):
        date, time = date_times[i]
        date_time_str = f"{date} {time}"
        if i == len(date_times) - 1:
            # Last date-time occurrence, take the substring from this date-time to the end
            chunks[date_time_str] = text[text.index(date_time_str) + len(date_time_str):].strip()
        else:
            # Substring between two date-time occurrences
            next_date, next_time = date_times[i + 1]
            next_date_time_str = f"{next_date} {next_time}"
            start_index = text.index(date_time_str) + len(date_time_str)
            end_index = text.index(next_date_time_str)
            chunks[date_time_str] = text[start_index:end_index].strip()
    
    return chunks

def extract_results(db_session, text, doc_id, ill_diagnosed):
    chunks = split_text_by_date_time(text)
    results = {}

    for date_time, chunk in chunks.items():
        test_results = {}
        test_count = 1
        for word in chunk.split():
            for test, full_name in DIABETES_TESTS.items():
                if test.upper() in word.upper().replace("-", " "):
                    value_match = re.search(rf"{re.escape(test)}-(\d+(?:\.\d+)?)\*?", word, re.IGNORECASE)
                    if value_match:
                        test_value = value_match.group(1)
                        test_results[f"test{test_count}"] = {
                            "name": full_name,
                            "value": test_value
                        }
                        test_count += 1
        results[date_time] = test_results

    parse_and_store_lab_results(db_session, results, doc_id, ill_diagnosed)
    return results

def parse_and_store_lab_results(db_session, results, doc_id, ill_diagnosed):

    for date_time_str, tests in results.items():
        date_str, time_str = date_time_str.split()
        combined_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M%p")

        for test_key, test_info in tests.items():
            lab_result = LabResult(
                test_name=test_info["name"],
                value=test_info["value"],
                date_time=combined_datetime,
                doc_id=doc_id,
                ill_diagnosed=ill_diagnosed
            )
            db_session.add(lab_result)

    db_session.commit()
