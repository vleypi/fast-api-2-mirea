from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Header, HTTPException, Request, Response
from config import ACCEPT_LANGUAGE_RE
from models import CommonHeaders

router = APIRouter(tags=["5.4/5.5 Headers"])

@router.get("/headers", summary="5.4 User-Agent и Accept-Language")
def get_headers(request: Request):
    user_agent = request.headers.get("user-agent")
    accept_language = request.headers.get("accept-language")

    if not user_agent:
        raise HTTPException(status_code=400, detail="Missing User-Agent header")
    if not accept_language:
        raise HTTPException(status_code=400, detail="Missing Accept-Language header")
    if not ACCEPT_LANGUAGE_RE.match(accept_language):
        raise HTTPException(status_code=400, detail="Invalid Accept-Language format")

    return {"User-Agent": user_agent, "Accept-Language": accept_language}


@router.get("/info", summary="5.5 CommonHeaders + X-Server-Time")
def get_info(
    response: Response,
    user_agent: Annotated[Optional[str], Header()] = None,
    accept_language: Annotated[Optional[str], Header()] = None,
):
    if not user_agent:
        raise HTTPException(status_code=400, detail="Missing User-Agent header")
    if not accept_language:
        raise HTTPException(status_code=400, detail="Missing Accept-Language header")
    if not ACCEPT_LANGUAGE_RE.match(accept_language):
        raise HTTPException(status_code=400, detail="Invalid Accept-Language format")

    response.headers["X-Server-Time"] = datetime.now().isoformat(timespec="seconds")
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {"User-Agent": user_agent, "Accept-Language": accept_language},
    }
