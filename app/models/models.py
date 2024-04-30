import datetime
from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


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

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    category = Column(String, nullable=False)
    category_values = Column(Text, nullable=False)


class ProcessedEhr(Base):
    __tablename__ = "processed_ehr"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    hpi = Column(Text)
    family_history = Column(Text)
    medications = Column(Text)
    lab_tests = Column(Text)
    category_id = Column(String(36), ForeignKey("categories.id"))
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    symptom = Column(String, nullable=False)
    is_found = Column(Boolean, nullable=False)
    ill_diagnosed = Column(Boolean, nullable=False)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)


class FamilyHistory(Base):
    __tablename__ = "family_history"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    condition_name = Column(String, nullable=False)
    is_found = Column(Boolean, nullable=False)
    ill_diagnosed = Column(Boolean, nullable=False)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)


class LabResult(Base):
    __tablename__ = "lab_result"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    test_name = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)
    ill_diagnosed = Column(Boolean, nullable=False)


class Medication(Base):
    __tablename__ = "medications"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    medication = Column(String, nullable=False)
    medication_family = Column(String)
    dosage = Column(Text)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)
    ill_diagnosed = Column(Boolean, nullable=False)


class Result(Base):
    __tablename__ = "results"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    timestamp = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now)
    doc_id = Column(String(36), ForeignKey("ehr_uploads.id"), nullable=False)
    ill_results = Column(JSON, nullable=False)

