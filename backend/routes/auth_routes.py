from fastapi import APIRouter, HTTPException, status, Depends
from backend.models import UserRegister, UserLogin, UserResponse, Token
from backend.database import get_db
from backend.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):
    username = user_data.username.strip().lower()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
        
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Username already registered. Please choose another or login.")
            
        hashed_pw = hash_password(user_data.password)
        cursor.execute(
            "INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)",
            (username, hashed_pw, user_data.full_name or username)
        )
        
    token = create_access_token(data={"sub": username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": username,
            "full_name": user_data.full_name or username,
            "created_at": None
        }
    }

@router.post("/login", response_model=Token)
def login(credentials: UserLogin):
    username = credentials.username.strip().lower()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, full_name, created_at FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
            
        stored_password = user["password"]
        if not verify_password(credentials.password, stored_password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
            
        # Seamless migration: if legacy password wasn't PBKDF2 hashed, upgrade it now!
        if not stored_password.startswith("pbkdf2:sha256:"):
            new_hash = hash_password(credentials.password)
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_hash, username))

    token = create_access_token(data={"sub": username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "full_name": user["full_name"] or user["username"],
            "created_at": user["created_at"]
        }
    }

@router.get("/me", response_model=UserResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "full_name": current_user["full_name"] or current_user["username"],
        "created_at": current_user.get("created_at")
    }
