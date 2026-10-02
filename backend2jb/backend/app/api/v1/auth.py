from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.db.database import get_db
from backend.app.db.models import User, UserRole
from backend.app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.services.age_service import AgeVerificationService

router = APIRouter()

def seed_demo_users(db: Session):
    """Ensures demo accounts (brand_demo, admin_demo) are present in the DB."""
    try:
        brand = db.query(User).filter(User.username == "brand_demo").first()
        if not brand:
            brand = User(
                username="brand_demo",
                email="brand_demo@safead.ai",
                password_hash=hash_password("brand123"),
                date_of_birth=datetime(1990, 1, 1),
                role=UserRole.BRAND_OWNER
            )
            db.add(brand)
            
        admin = db.query(User).filter(User.username == "admin_demo").first()
        if not admin:
            admin = User(
                username="admin_demo",
                email="admin_demo@safead.ai",
                password_hash=hash_password("admin123"),
                date_of_birth=datetime(1985, 1, 1),
                role=UserRole.ADMIN
            )
            db.add(admin)
        db.commit()
    except Exception:
        db.rollback()

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    try:
        dob = datetime.strptime(user_in.date_of_birth, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
    # Perform initial age check based on DOB
    age_res = AgeVerificationService.verify_user_age(dob, face_image=None)
    
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        date_of_birth=dob,
        age_verification_status=age_res["status"],
        verified_age_group=age_res["verified_age_group"],
        chronological_age=age_res["chronological_age"],
        estimated_age=age_res["estimated_age"],
        role=UserRole.BRAND_OWNER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    seed_demo_users(db)
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    access_token = create_access_token(data={"sub": user.username, "role": role_str})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": role_str,
        "verified_age_group": user.verified_age_group.value if (hasattr(user, "verified_age_group") and user.verified_age_group and hasattr(user.verified_age_group, "value")) else "AGE_18_PLUS"
    }
