from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field


class PeriodLogDocument(BaseModel):
    user_id: str
    cycle_entries: List[dict] = []   # [{start_date, end_date, symptoms: []}]
    avg_cycle_length: Optional[float] = None
    predicted_next_date: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
