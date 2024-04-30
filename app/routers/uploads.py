from fastapi import Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
import configs.db as db
import utils.upload_ehr as upload
from fastapi import APIRouter

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
    upload_result = upload.upload_document(session, file, uid)
    return upload_result
