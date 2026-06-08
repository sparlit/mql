# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Hardened RBAC Security Layer with JWT Refresh Tokens

import jwt
from datetime import datetime, timedelta, timezone
import json
import os
from typing import Optional, List
from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

# Load from Vault
VAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "vault.json")
with open(VAULT_PATH, "r") as f:
    vault = json.load(f)

SECRET_KEY = vault.get("JWT_SECRET")
if not SECRET_KEY or SECRET_KEY == "FALLBACK_SECRET":
    raise ValueError("CRITICAL: JWT_SECRET not properly configured in vault.json")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    roles: List[str]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        return payload
    except jwt.PyJWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    username: str = payload.get("sub")
    # In a full RBAC system, we would fetch roles from a DB.
    # For Sovereign V5.0.0, we derive them from the vault admin user.
    roles = ["admin", "trader", "auditor"] if username == vault["ADMIN_USERNAME"] else ["viewer"]

    return User(username=username, roles=roles)

def check_role(required_role: str):
    async def role_checker(user: User = Depends(get_current_user)):
        if required_role not in user.roles:
            raise HTTPException(status_code=403, detail=f"Role '{required_role}' required")
        return user
    return role_checker
