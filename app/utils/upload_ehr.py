import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename
from models.models import EhrUpload
import logging
import uuid

def upload_document(db_session: sessionmaker, file_obj, uid):
    logger = logging.getLogger(__name__)

    # Check if file is uploaded
    if not file_obj:
        return {"error": "No file uploaded."}

    # Validate file format (ensure .txt only)
    filename = secure_filename(file_obj.filename)
    if not filename.endswith(".txt"):
        return {"error": "Only .txt files are allowed."}

    # Location of uploaded ehr documents data/ehr
    data_dir = os.path.join("data", "ehr")

    # Generate UUID for both filename and id
    upload_id = uuid.uuid4()  # Generate UUID

    try:
        # Create a new upload record with the same UUID as id
        upload_record = EhrUpload(id=upload_id, uid=uid, doc_format=".txt", doc_url=os.path.join(data_dir, f"{upload_id}.txt"))
        db_session.add(upload_record)

        # Save file to data directory
        filepath = os.path.join(data_dir, f"{upload_id}.txt")
        with open(filepath, "wb") as f:
            f.write(file_obj.file.read())
        
        db_session.commit()
        logger.info("Upload record saved successfully.")
        return {"message": f"SUCCESS: {filename}"}
    except IntegrityError as e:
        db_session.rollback()  # Rollback the transaction to maintain integrity
        logger.error(f"IntegrityError: {str(e)}")
        return {"error": "Failed to save upload record in database due to duplicate data or constraint violation."}
    except Exception as e:
        db_session.rollback()  # Rollback the transaction in case of other errors
        logger.error(f"Error saving file: {str(e)}")
        return {"error": f"Error saving file: {str(e)}"}
