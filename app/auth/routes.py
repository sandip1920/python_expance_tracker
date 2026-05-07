from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from app import models, schemas
from app.database import SessionLocal
from app.auth.utils import hash_password, verify_password, create_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()

    if existing:
        raise HTTPException(400, "Email already exists")

    new_user = models.User(
        id=str(uuid.uuid4()),
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created successfully"}

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        raise HTTPException(404, "User not found")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(401, "Wrong password entered")

    token = create_token({"user_id": db_user.id})

    return {"access_token": token}