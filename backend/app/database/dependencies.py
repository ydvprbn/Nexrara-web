from app.database.connection import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        print("get_db: Database session created")  # Debugging
        yield db
    finally:
        print("get_db: Database session closed")  # Debugging
        db.close()
