import os

from models.database import DATABASE_NAME, create_db

from models.user import User


if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if not db_is_created:
        create_db()
