import datetime
from sqlalchemy import Column, Date, DateTime, String, Text, TIMESTAMP, JSON, ForeignKey, ARRAY, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()




class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now)
    email = Column(String(128), nullable=False, unique=True)
    phone = Column(String(128), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(128), nullable=True)
    address = Column(String(256), nullable=True)
    full_name = Column(String(256), nullable=True)
    date_of_birth = Column(Date)
    gender = Column(String(20), nullable=True)
    country = Column(String(256), nullable=True)
    role = Column(String(10), nullable=False, default="user")

class TokenTable(Base):
    __tablename__ = "token"
    uid = Column(String(36))
    access_token = Column(String(450), primary_key=True)
    refresh_token = Column(String(450),nullable=False)
    role = Column(String(10), nullable=False, default="user")
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)

class EhrUpload(Base):
    __tablename__ = "ehr_uploads"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    timestamp = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now)
    doc_url = Column(String, nullable=True)
    uid = Column(String(36), nullable=False)
    doc_format = Column(String, nullable=False)

    # Relationship with ProcessedEhr table (one-to-many)
    processed_ehr = relationship("ProcessedEhr", backref="ehr_upload")

    # Relationship with Symptoms table (one-to-many)
    symptoms = relationship("Symptom", backref="ehr_upload")

    # Relationship with FamilyHistory table (one-to-many)
    family_history = relationship("FamilyHistory", backref="ehr_upload")

    # Relationship with LabResult table (one-to-many)
    lab_results = relationship("LabResult", backref="ehr_upload")

    # Relationship with Medications table (one-to-many)
    medications = relationship("Medication", backref="ehr_upload")

    # Relationship with Results table (one-to-many)
    results = relationship("Result", backref="ehr_upload")


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String, primary_key=True)
    category_value = Column(Text, nullable=False)
    additional_values = Column(ARRAY(String), nullable=True)


class ProcessedEhr(Base):
    __tablename__ = "processed_ehr"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    hpi = Column(Text)
    family_history = Column(Text)
    medications = Column(Text)
    lab_tests = Column(Text)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    symptom = Column(String, nullable=False)
    ill_diagnosed = Column(String(128), nullable=False)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)
    def to_dict(self):
        return {
            "symptom": self.symptom,
        }


class FamilyHistory(Base):
    __tablename__ = "family_history"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    condition_name = Column(String(256), nullable=False)
    ill_diagnosed = Column(String(128), nullable=False)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)



class LabResult(Base):
    __tablename__ = "lab_result"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    test_name = Column(String(128), nullable=False)
    value = Column(Text, nullable=False)
    date_time = Column(DateTime, nullable=False)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)
    ill_diagnosed = Column(String(128), nullable=False)
    def to_dict(self):
        return {
            "test_name": self.test_name,
            "value": self.value,
            "date_time": self.date_time.isoformat(),
        }


class Medication(Base):
    __tablename__ = "medications"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    medication = Column(String, nullable=False)
    medication_family = Column(String)
    dosage = Column(Text)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)
    ill_diagnosed = Column(String(128), nullable=False)


class Result(Base):
    __tablename__ = "results"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    timestamp = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)
    ill_results = Column(JSON, nullable=False)

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "doc_id": self.doc_id,
            "ill_results": self.ill_results
        }