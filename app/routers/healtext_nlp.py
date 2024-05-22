from fastapi import Depends, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from schemas import schemas
from models import models
from jose import jwt
from configs.config import SECRET_KEY, ALGORITHM
from auth.bearer import JWTBearer
import configs.db as db
from predictions.results import process_medical_document
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
@router.post("/diabetes-prediction")
async def upload_ehr(dependencies=Depends(JWTBearer()), file: UploadFile = File(...), session: Session = Depends(db.get_session)):
    try:
        token = dependencies
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id = payload['sub']
        existing_token = session.query(models.TokenTable).filter(
            models.TokenTable.uid == user_id,
            models.TokenTable.access_token == token
        ).first()
        if existing_token: 
            return process_medical_document(session, file, user_id, "diabetes")
        else:
            return {"message": "Invalid or expired token"}
    

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
