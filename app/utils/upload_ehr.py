import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename
from models.models import EhrUpload
import uuid

def upload_document(db_session: sessionmaker, file_obj, uid):

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
    upload_id = str(uuid.uuid4())  # Generate UUID
    print(type(upload_id))
    

    upload_record = EhrUpload(id=upload_id, uid=uid, doc_format=".txt", doc_url=os.path.join(data_dir, f"{upload_id}.txt"))
    db_session.add(upload_record)

    # Save file to data directory
    filepath = os.path.join(data_dir, f"{upload_id}.txt")
    with open(filepath, "wb") as f:
        f.write(file_obj.file.read())
    
    db_session.commit()
    return upload_record.id
