from nlp.diabete_dict import DIABETES_SYMPTOMS

def predict_prediabetes(labs, symptoms):
    # Initialize variables to track test values
    glucose_values = []
    hba1c_values = []
    cholesterol_values = []
    triglycerides_values = []
    creatinine_values = []
    bun_values = []
    egfr_values = []
    sodium_values = []
    potassium_values = []
    
    # Collect test values
    for timestamp, tests in labs.items():
        for test_key, test_data in tests.items():
            test_name = test_data["name"]
            value = float(test_data["value"]) if test_data.get("value") else None
            if value is not None:  # Ensure only valid test values are considered
                if test_name == "Blood Glucose":
                    glucose_values.append((timestamp, value))
                elif test_name == "Hemoglobin A1c":
                    hba1c_values.append((timestamp, value))
                elif test_name == "Total Cholesterol":
                    cholesterol_values.append((timestamp, value))
                elif test_name == "Triglycerides":
                    triglycerides_values.append((timestamp, value))
                elif test_name == "Serum Creatinine":
                    creatinine_values.append((timestamp, value))
                elif test_name == "Blood Urea Nitrogen (BUN)":
                    bun_values.append((timestamp, value))
                elif test_name == "Estimated Glomerular Filtration Rate (eGFR)":
                    egfr_values.append((timestamp, value))
                elif test_name == "Sodium":
                    sodium_values.append((timestamp, value))
                elif test_name == "Potassium":
                    potassium_values.append((timestamp, value))
    
    # Define cutoff values for prediabetes
    glucose_cutoff = 100
    hba1c_cutoff = 5.7
    cholesterol_cutoff = 200
    triglycerides_cutoff = 150
    creatinine_cutoff = 1.2
    bun_cutoff = 20
    egfr_cutoff = 60
    sodium_cutoff = 140
    potassium_cutoff = 5
    
    # Check the most recent test values and predict prediabetes
    recent_tests = [
        ("Glucose", glucose_values),
        ("Hemoglobin A1c", hba1c_values),
        ("Total Cholesterol", cholesterol_values),
        ("Triglycerides", triglycerides_values),
        ("Serum Creatinine", creatinine_values),
        ("Blood Urea Nitrogen (BUN)", bun_values),
        ("Estimated Glomerular Filtration Rate (eGFR)", egfr_values),
        ("Sodium", sodium_values),
        ("Potassium", potassium_values)
    ]
    
    predictions = []
    total_valid_tests = 0
    for test_name, test_values in recent_tests:
        if test_values:
            total_valid_tests += 1
            latest_value = max(test_values, key=lambda x: x[0])[1]
            if latest_value:
                if test_name == "Glucose" and latest_value > glucose_cutoff:
                    predictions.append((test_name, "Prediabetes"))
                elif test_name == "Hemoglobin A1c" and latest_value > hba1c_cutoff:
                    predictions.append((test_name, "Prediabetes"))
                elif test_name == "Total Cholesterol" and latest_value > cholesterol_cutoff:
                    predictions.append((test_name, "Prediabetes"))
                elif test_name == "Triglycerides" and latest_value > triglycerides_cutoff:
                    predictions.append((test_name, "Prediabetes"))
                elif test_name == "Serum Creatinine" and latest_value > creatinine_cutoff:
                    predictions.append((test_name, "Prediabetes"))
                elif test_name == "Blood Urea Nitrogen (BUN)" and latest_value > bun_cutoff:
                    predictions.append((test_name, "Prediabetes"))
                elif test_name == "Estimated Glomerular Filtration Rate (eGFR)" and latest_value < egfr_cutoff:
                    predictions.append((test_name, "Prediabetes"))
                elif test_name == "Sodium" and latest_value < sodium_cutoff:
                    predictions.append((test_name, "Prediabetes"))
                elif test_name == "Potassium" and latest_value > potassium_cutoff:
                    predictions.append((test_name, "Prediabetes"))
    
    # Check for the presence of symptoms related to diabetes
    symptom_check = any(symptom in DIABETES_SYMPTOMS for symptom in symptoms)
    if symptom_check:
        predictions.append(("Symptoms", "Prediabetes"))

    total_tests = len(recent_tests)
    prediabetes_tests = len(predictions)
    prediabetes_percentage = (prediabetes_tests / (total_tests + 1)) * 100 if total_tests > 0 else 0  
    
    return predictions, prediabetes_percentage