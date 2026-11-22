from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from poc_studio.config import Settings, get_settings
from poc_studio.db.session import get_session
from poc_studio.routes.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(get_settings), session: Session = Depends(get_session)
) -> HealthResponse:
    session.execute(text("SELECT 1"))
    return HealthResponse(
        status="ok", llm_provider=settings.llm_provider, github_mode=settings.github_mode, db="ok"
    )
