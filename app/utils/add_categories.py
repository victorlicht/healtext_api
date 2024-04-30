import uuid
from models.models import Category
from sqlalchemy.orm import sessionmaker

def add_categories(db_session: sessionmaker, categories):
    try:
        # Iterate over the categories dictionary
        for category, category_value in categories.items():
            # Create a new Category instance
            new_category = Category(category_id=category, category_values=category_value)
            # Add the new category to the session
            db_session.add(new_category)

        # Commit the session to save changes
        db_session.commit()
        print("Categories added successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")
        # Rollback the session in case of error
        db_session.rollback()

# Example usage

