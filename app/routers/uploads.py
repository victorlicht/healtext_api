from fastapi import Depends, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import configs.db as db
import utils.upload_ehr as upload
import tasks.sections as s
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)
@router.post("/upload")
async def upload_ehr(file: UploadFile = File(...),
                    uid: str = Form(...),
                    session: Session = Depends(db.get_session)):
    """
    Uploads a document and stores it in the database and data/ehr directory.

    Args:
        file (werkzeug.datastructures.FileStorage): Uploaded document file object.
        uid (str): Unique identifier for the user uploading the document.
        session (sqlalchemy.orm.Session): Database session object (injected by dependency).

    Returns:
        dict: Dictionary containing information about the uploaded document or an error message.
    """
    
    try:
        uploaded = upload.upload_document(session, file, uid)
        se = s.sections_extraction(session, uploaded)
        ehr = s.insert_processed_ehr(session, uploaded, se)
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
            "sections": se,
            "processed_ehr": ehr
        },
        media_type="application/json"
    )
