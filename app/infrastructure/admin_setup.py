from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.infrastructure.database.models import User
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user(db: Session):
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@cbt.com")
    
    existing_admin = db.query(User).filter(User.username == admin_username).first()
    if not existing_admin:
        hashed_password = pwd_context.hash(admin_password)
        admin_user = User(
            username=admin_username,
            email=admin_email,
            hashed_password=hashed_password,
            full_name="System Administrator",
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin user created: {admin_username}")
    else:
        print("Admin user already exists")