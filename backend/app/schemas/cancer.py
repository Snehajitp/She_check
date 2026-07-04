from pydantic import BaseModel, Field
from typing import Optional, Literal


class CancerParametersInput(BaseModel):
    radius_mean: float
    texture_mean: float
    perimeter_mean: float
    area_mean: float
    smoothness_mean: float
    compactness_mean: float
    concavity_mean: float
    concave_points_mean: float
    symmetry_mean: float
    fractal_dimension_mean: float


class CancerPredictionResponse(BaseModel):
    prediction: Literal["Malignant", "Benign"]
    confidence: float
    message: str =""
    disclaimer: str = (
        "This is an AI-assisted screening tool and does not replace professional medical diagnosis. "
        "Please consult a qualified healthcare provider for any health concerns."
    )
