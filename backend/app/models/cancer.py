from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class CancerResultDocument(BaseModel):
    user_id: str
    input_type: Literal["image", "parameters", "both"]
    parameters: Optional[dict] = None
    image_filename: Optional[str] = None
    prediction: Literal["Malignant", "Benign"]
    confidence: float                          # 0.0 – 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
