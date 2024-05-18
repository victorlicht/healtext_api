from fastapi import Depends, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import configs.db as db
import utils.upload_ehr as upload
import tasks.sections as sections
import nlp.preprocess as preprocess
import nlp.symptoms_extractions as sy
import nlp.lab_results_extractions as lab

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)
@router.post("/upload")
async def upload_ehr(file: UploadFile = File(...), uid: str = Form(...), session: Session = Depends(db.get_session)):
    try:
        uploaded = upload.upload_document(session, file, uid)
        extracted_sections = sections.sections_extraction(session, uploaded)
        inserted_sections = sections.insert_processed_ehr(session, uploaded, extracted_sections)
        processed_sections = preprocess.preprocess_text(session, uploaded)
        labs_text = preprocess.preprocess_lab_tests_text(session, uploaded)
        detected_diabetes_symptoms = sy.detect_symptoms_diabetes(processed_sections, sy.DIABETES_SYMPTOMS)
        sy.insert_symptoms(session, detected_diabetes_symptoms, uploaded)
        print(type(labs_text), type(processed_sections), type(detected_diabetes_symptoms))


    except Exception as e:
        session.rollback()
        logger.error(f"Error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "can't upload file, try later."},
            media_type="application/json"
        )
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Document uploaded successfully",
            "id": uploaded,
            "symptoms": detected_diabetes_symptoms,
            "labs": labs_text
        },
        media_type="application/json"
    )
