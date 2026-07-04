from pydantic import BaseModel
from typing import List, Optional


class CycleEntry(BaseModel):
    start_date: str          # "YYYY-MM-DD"
    end_date: Optional[str] = None
    symptoms: List[str] = []


class PeriodLogRequest(BaseModel):
    cycle_entries: List[CycleEntry]


class PeriodPredictionResponse(BaseModel):
    predicted_next_date: str
    avg_cycle_length: float
    current_phase: str
    ovulation_window: dict     # {start, end}
    advisories: List[str]
    phase_description: str
