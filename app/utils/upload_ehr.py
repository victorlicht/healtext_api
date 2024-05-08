import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename
from models.models import EhrUpload
import uuid

def upload_document(db_session: sessionmaker, file_obj, uid):
    filename = secure_filename(file_obj.filename)
    # Location of uploaded ehr documents data/ehr
    data_dir = os.path.join("data", "ehr")
    upload_id = str(uuid.uuid4())  # Generate UUID    
    upload_record = EhrUpload(id=upload_id, uid=uid, doc_format=".txt", doc_url=os.path.join(data_dir, f"{upload_id}.txt"))
    db_session.add(upload_record)
    filepath = os.path.join(data_dir, f"{upload_id}.txt")
    with open(filepath, "wb") as f:
        f.write(file_obj.file.read())  
    db_session.commit()
    return upload_record.id
