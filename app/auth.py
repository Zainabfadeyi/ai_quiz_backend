from fastapi import APIRouter, HTTPException, Depends
from jose import JWTError, jwt
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import models, database
import os
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret")
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_user(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = get_user(db, username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"username": user.username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

@router.post("/register")
def register(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    if get_user(db, form.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_pw = bcrypt.hash(form.password)
    user = models.User(username=form.username, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered"}

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = get_user(db, form.username)
    if not user or not bcrypt.verify(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
