import hashlib
import hmac
import time
import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Cookie, HTTPException, Response
from config import FAKE_USERS, SECRET_KEY, SESSION_RENEW_AFTER, SESSION_TTL
from models import LoginData

router = APIRouter(tags=["5.1/5.2/5.3 — Auth"])

simple_sessions: dict[str, str] = {}
signed_user_map: dict[str, str] = {}
ts_user_map: dict[str, str] = {}

def _sign(user_id: str) -> str:
    return hmac.new(SECRET_KEY.encode(), user_id.encode(), hashlib.sha256).hexdigest()

def _verify_signed_token(token: str) -> Optional[str]:
    try:
        user_id, sig = token.rsplit(".", 1)
        if hmac.compare_digest(_sign(user_id), sig):
            uuid.UUID(user_id)
            return user_id
    except Exception:
        pass
    return None

def _sign_ts(user_id: str, timestamp: int) -> str:
    msg = f"{user_id}.{timestamp}"
    return hmac.new(SECRET_KEY.encode(), msg.encode(), hashlib.sha256).hexdigest()


def _make_ts_token(user_id: str, timestamp: int) -> str:
    return f"{user_id}.{timestamp}.{_sign_ts(user_id, timestamp)}"


def _verify_ts_token(token: str):
    try:
        segments = token.rsplit(".", 2)
        if len(segments) != 3:
            return None, None
        user_id, ts_str, sig = segments
        timestamp = int(ts_str)
        if hmac.compare_digest(_sign_ts(user_id, timestamp), sig):
            uuid.UUID(user_id)
            return user_id, timestamp
    except Exception:
        pass
    return None, None


@router.post("/login", summary="5.1 — Логин (простая cookie)")
def login(data: LoginData, response: Response):
    user = FAKE_USERS.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = str(uuid.uuid4())
    simple_sessions[token] = data.username
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=300)
    return {"message": "Login successful"}


@router.get("/user", summary="5.1 — Профиль (простая cookie)")
def get_user(response: Response, session_token: Annotated[Optional[str], Cookie()] = None):
    if not session_token or session_token not in simple_sessions:
        response.status_code = 401
        return {"message": "Unauthorized"}
    username = simple_sessions[session_token]
    user = FAKE_USERS[username]
    return {"username": username, "name": user["name"], "email": user["email"]}


@router.post("/login/signed", summary="5.2 Логин (подписанная cookie)")
def login_signed(data: LoginData, response: Response):
    user = FAKE_USERS.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id = str(uuid.uuid4())
    signed_user_map[user_id] = data.username
    token = f"{user_id}.{_sign(user_id)}"
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=300)
    return {"message": "Login successful (signed cookie)"}


@router.get("/profile", summary="5.2 Профиль (подписанная cookie)")
def get_profile(response: Response, session_token: Annotated[Optional[str], Cookie()] = None):
    if not session_token:
        response.status_code = 401
        return {"message": "Unauthorized"}
    user_id = _verify_signed_token(session_token)
    if not user_id or user_id not in signed_user_map:
        response.status_code = 401
        return {"message": "Unauthorized"}
    username = signed_user_map[user_id]
    user = FAKE_USERS[username]
    return {"user_id": user_id, "username": username, "name": user["name"], "email": user["email"]}


@router.post("/login/session", summary="5.3 Логин (динамический TTL)")
def login_session(data: LoginData, response: Response):
    user = FAKE_USERS.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id = str(uuid.uuid4())
    ts_user_map[user_id] = data.username
    token = _make_ts_token(user_id, int(time.time()))
    response.set_cookie(key="session_token", value=token, httponly=True, secure=False, max_age=SESSION_TTL)
    return {"message": "Login successful (dynamic TTL session)"}


@router.get("/session/profile", summary="5.3 Профиль (динамический TTL)")
def session_profile(response: Response, session_token: Annotated[Optional[str], Cookie()] = None):
    if not session_token:
        response.status_code = 401
        return {"message": "Session expired"}

    user_id, last_active = _verify_ts_token(session_token)
    if not user_id:
        response.status_code = 401
        return {"message": "Invalid session"}

    elapsed = int(time.time()) - last_active

    if elapsed >= SESSION_TTL:
        response.status_code = 401
        return {"message": "Session expired"}

    if SESSION_RENEW_AFTER <= elapsed < SESSION_TTL:
        new_token = _make_ts_token(user_id, int(time.time()))
        response.set_cookie(key="session_token", value=new_token, httponly=True, secure=False, max_age=SESSION_TTL)

    username = ts_user_map.get(user_id, "unknown")
    user = FAKE_USERS.get(username, {})
    return {
        "user_id": user_id,
        "username": username,
        "name": user.get("name"),
        "elapsed_seconds": elapsed,
        "session_renewed": SESSION_RENEW_AFTER <= elapsed < SESSION_TTL,
    }
