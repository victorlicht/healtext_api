import os
import re
import uuid
from sqlalchemy.orm import sessionmaker
from models.models import Category, ProcessedEhr


def create_path(folder, id):
    path = os.path.join("data", folder, f"{id}.txt")
    return path


def get_category_data(db_session: sessionmaker):
    categories = db_session.query(Category).all()
    category_data = []
    for category in categories:
        category_data.append(get_category_dict(category))
    return category_data

def get_category_dict(category_object):
    return {
        "category_id": category_object.category_id,
        "category_value": category_object.category_value,
        "additional_values": category_object.additional_values or [],
    }


def sections_extraction(db_session: sessionmaker, doc_id):
    doc_path = create_path("ehr", doc_id)
    targete_section = False
    sections = {}
    current_section_title = None
    section_title_pattern = re.compile(r'^([^:\n]+):$')

    with open(doc_path, 'r') as file:
        for line in file:
            line = line.strip()
            match = section_title_pattern.match(line)
            if match:
                current_section_title = match.group(1).strip().lower()
                category_id = _matches_category_or_additional_values(current_section_title, db_session)[1]
                category = _matches_category_or_additional_values(current_section_title, db_session)[0]
                if not category:
                    targete_section = False
                else:
                    targete_section = True
                    sections[current_section_title] = {'category_id': category_id, 'category': current_section_title, 'content': []}
            elif current_section_title:
                if targete_section:
                    sections[current_section_title]['content'].append(line)
    return sections


def _matches_category_or_additional_values(section_title, db_session):
    lowercase_section_title = section_title.lower()
    categories = get_category_data(db_session)
    for category in categories:
        if lowercase_section_title == category["category_value"].lower():
            return True, category["category_id"]
        elif any(value.lower() == lowercase_section_title for value in category["additional_values"]):
            return True, category["category_id"]
    return False, None


def insert_processed_ehr(db_session, doc_id, sections):
    processed_ehr_id = str(uuid.uuid4())
    processed_data = {}

    for category_id, content in sections.items():
        category_id = content.get('category_id')
        real_content = content.get('content')
        if real_content is not None:  # Check if content is not None
            # Check if real_content is a list
            if isinstance(real_content, list):
                # Join the list elements and strip each element individually
                real_content = " ".join([line.strip() for line in real_content])
            if category_id in processed_data:
                processed_data[category_id]['content'] += (" " + real_content.strip()) 
            else:
                processed_data[category_id] = {'content': real_content.strip(), 'doc_id': doc_id}

    inserted_data = {}
    
    for category_id, data in processed_data.items():
        if category_id == "hpi":
            inserted_data["hpi"] = data["content"]
        elif category_id == "fh":
            inserted_data["family_history"] = data["content"]
        elif category_id == "me":
            inserted_data["medications"] = data["content"]
        elif category_id == "lab":
            inserted_data["lab_tests"] = data["content"]

    processed_ehr = ProcessedEhr(id = processed_ehr_id, **inserted_data, doc_id=doc_id)
    db_session.add(processed_ehr)
    db_session.commit()
    db_session.rollback()
    return inserted_data
