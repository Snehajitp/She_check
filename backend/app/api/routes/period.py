from fastapi import APIRouter, Depends
from app.schemas.period import PeriodLogRequest, PeriodPredictionResponse
from app.core.security import get_current_user
from app.services.period_service import predict_next_period, get_period_log

router = APIRouter()


@router.post("/log", response_model=PeriodPredictionResponse)
async def log_period(
    payload: PeriodLogRequest,
    current_user: dict = Depends(get_current_user),
):
    return await predict_next_period(payload, current_user["user_id"])


@router.get("/log")
async def fetch_period_log(current_user: dict = Depends(get_current_user)):
    return await get_period_log(current_user["user_id"])
