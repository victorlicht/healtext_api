from app.nlp.preprocess import preprocess_lab_tests_text, preprocess_text
from app.utils.upload_ehr import upload_document
from app.tasks.sections import sections_extraction, insert_processed_ehr
from app.nlp.symptoms_extractions import detect_symptoms_diabetes, insert_symptoms
from app.predictions.diabetes import predict_prediabetes
from app.nlp.diabete_dict import DIABETES_SYMPTOMS
from app.models.models import Result

def process_medical_document(session, file, user_id, ill):
    doc_id = upload_document(session, file, user_id)
    extracted_sections = sections_extraction(session, doc_id)
    inserted_sections = insert_processed_ehr(session, doc_id, extracted_sections)
    processed_sections = preprocess_text(session, doc_id)
    
    if ill == "diabetes":
        labs_text = preprocess_lab_tests_text(session, doc_id, "Diabetes")
        detected_diabetes_symptoms = detect_symptoms_diabetes(processed_sections, DIABETES_SYMPTOMS)
        insert_symptoms(session, detected_diabetes_symptoms, doc_id)
        predictions, prediabetes_percentage = predict_prediabetes(labs_text, detected_diabetes_symptoms)
        result = Result(
            doc_id=doc_id,
            ill_results={"prediabetes_percentage": prediabetes_percentage}
        )
        session.add(result)
        session.commit()
        
        return prediabetes_percentage
    
