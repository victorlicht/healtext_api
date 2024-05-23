from fastapi import Depends, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.models import models
from jose import jwt
from app.configs.config import SECRET_KEY, ALGORITHM
from app.auth.bearer import JWTBearer
from app.predictions.results import process_medical_document
from app.configs.db import get_session

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)
@router.post("/diabetes-prediction")
async def upload_ehr(dependencies=Depends(JWTBearer()), file: UploadFile = File(...), session: Session = Depends(get_session)):
    try:
        token = dependencies
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id = payload['sub']
        existing_token = session.query(models.TokenTable).filter(
            models.TokenTable.uid == user_id,
            models.TokenTable.access_token == token
        ).first()
        if existing_token:
            result = process_medical_document(session, file, user_id, "diabetes")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"result": result},
                media_type="application/json"
            )
        else:
            return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Token not valid"},
            media_type="application/json"
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={"error": "can't upload file, try later."},
            media_type="application/json"
        )

@router.get("/user-results")
async def get_user_results(dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    try:
        token = dependencies
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id = payload['sub']

        # Query to fetch all EHR uploads for the user
        documents = session.query(models.EhrUpload).filter(models.EhrUpload.uid == user_id).all()

        if not documents:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "No documents found for the user"},
                media_type="application/json"
            )

        results = []

        for doc in documents:
            # Get the results associated with each document
            result_details = session.query(models.Result).filter(models.Result.doc_id == doc.id).all()
            result_details_dicts = [result for result in result_details]

            # Get symptoms associated with each document
            symptoms = session.query(models.Symptom).filter(models.Symptom.doc_id == doc.id).all()
            symptoms_dicts = [symptom.to_dict() for symptom in symptoms]

            # Get lab results associated with each document
            lab_results = session.query(models.LabResult).filter(models.LabResult.doc_id == doc.id).all()
            lab_results_dicts = [lab_result.to_dict() for lab_result in lab_results]

            if result_details_dicts:
                doc_details = {
                    "timestamp": doc.timestamp,
                    "results": result_details_dicts,
                    "symptoms": symptoms_dicts,
                    "lab_results": lab_results_dicts
                }
                results.append(doc_details)

        return results

    except Exception as e:
        session.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)},
            media_type="application/json"
        )