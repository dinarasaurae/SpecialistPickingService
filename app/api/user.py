from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_jwt_token, decode_jwt_token
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdatePassword

router = APIRouter(prefix="/users", tags=["Users"])
security = HTTPBearer()

@router.post("/register", response_model=UserRead)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email уже используется")
    
    hashed_password = hash_password(user_data.password)
    new_user = User(**user_data.model_dump(exclude={"password"}), password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    token = create_jwt_token(user.id)
    print("Создан токен:", token)
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    user_id = decode_jwt_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

@router.get("/me", response_model=UserRead)
def get_me(user: User = Depends(get_current_user)):
    return user

@router.put("/change-password")
def change_password(password_data: UserUpdatePassword, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.password_hash = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Пароль изменён"}

@router.delete("/delete", response_model=dict)
def delete_user(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(user)
    db.commit()
    return {"message": "Пользователь удалён"}
