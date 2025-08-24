from typing import Dict, Union

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies.db import get_db

router = APIRouter()


@router.get("", summary="ヘルスチェック")
async def health_check(
    db: Session = Depends(get_db),
) -> Dict[str, Union[str, Dict[str, str]]]:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "detail": str(e)}
