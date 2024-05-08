
import datetime
import re


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
    "GLYCOSYLATED HEMOGLOBIN": "Glycosylated Hemoglobin"  # Include alternate names
}

def extract_results(text):
    chunks = split_text_by_time(text)
    results = {}

    for time, chunk in chunks.items():
        test_results = {}
        test_count = 1
        for word in chunk.split():
            for test, full_name in DIABETES_TESTS.items():
                if test.upper() in word.upper():
                    value_match = re.search(rf"\b{re.escape(test)}(\d+)\b", word)
                    if value_match:
                        test_value = value_match.group(1)
                        test_results[f"test{test_count}"] = {
                            "name": full_name,
                            "value": test_value
                        }
                        test_count += 1
        results[time] = test_results

    return results




def split_text_by_time(text):
    times = extract_time(text)
    chunks = {}

    for i in range(len(times)):
        if i == len(times) - 1:
            # Last time occurrence, take the substring from this time to the end
            chunks[times[i]] = text[text.index(times[i]) + len(times[i]):].strip()
        else:
            # Substring between two time occurrences
            start_index = text.index(times[i]) + len(times[i])
            end_index = text.index(times[i + 1])
            chunks[times[i]] = text[start_index:end_index].strip()

    return chunks