from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from .database import SessionLocal
from .models import User
from .security import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Extracts user info from the JWT token and returns the user object.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def require_admin(current_user: User = Depends(get_current_user)):
    """
    Allows only admins or owner.
    """
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_owner(current_user: User = Depends(get_current_user)):
    """
    Allows only owner user role.
    """
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Owner access required")
    return current_user
