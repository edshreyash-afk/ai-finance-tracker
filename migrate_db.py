from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text("ALTER TABLE transactions MODIFY date DATETIME;"))
        conn.commit()
        print("Database schema updated successfully.")
