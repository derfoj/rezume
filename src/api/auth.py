from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import jwt, JWTError
from src.core.database import get_db
from src.models.user import User
from src.core.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM

router = APIRouter()

# oauth2_scheme handles the 'Authorization: Bearer <token>' header automatically
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

async def get_current_user(request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. If no token in Authorization header, check cookies (fallback)
    if not token:
        token = request.cookies.get("access_token")
        if token and token.startswith("Bearer "):
            token = token.replace("Bearer ", "", 1)

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = None
    title: str = "Étudiant"

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token)
def register(response: Response, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    # Using specific keyword arguments to ensure strict DB compatibility
    new_user = User(
        email=user.email, 
        hashed_password=hashed_password, 
        full_name=user.full_name, 
        title=user.title or "Étudiant",
        role="user" # Default role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    
    # Determine cookie security based on environment
    from os import getenv
    is_prod = getenv("ENV_STATE", "dev") == "prod"
    
    # Set cookie for traditional session support
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800, 
        expires=1800,
        samesite="none" if is_prod else "lax",
        secure=is_prod
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(response: Response, user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": db_user.email})
    
    # Determine cookie security based on environment
    from os import getenv
    is_prod = getenv("ENV_STATE", "dev") == "prod"
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        expires=1800,
        samesite="none" if is_prod else "lax",
        secure=is_prod
    )
    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer", "role": db_user.role}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.get("/users", dependencies=[Depends(get_admin_user)])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role} for u in users]
