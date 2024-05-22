from app.models.models import Category
from sqlalchemy.orm import sessionmaker

def add_categories(db_session: sessionmaker, categories):
    try:
        for category, category_value in categories.items():
            new_category = Category(category_id=category, category_values=category_value)
            db_session.add(new_category)

        db_session.commit()
        print("Categories added successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")
        # Rollback the session in case of error
        db_session.rollback()
