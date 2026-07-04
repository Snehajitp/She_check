"""
Cancer detection service.
- predict_from_parameters : trained scikit-learn model (local)
- predict_from_image      : Gemini Vision API (free, no training needed)
"""
import base64
from datetime import datetime, timezone

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.cancer import CancerParametersInput, CancerPredictionResponse
from app.db.mongodb import get_cancer_results_collection
from app.ml.cancer_detection.predictor import predict_parameters


MAMMOGRAM_PROMPT = """You are an AI assistant helping with breast cancer screening analysis.

Analyze this mammogram or breast tissue image and provide:
1. A prediction: MALIGNANT or BENIGN
2. A confidence percentage (0-100)
3. Key visual findings that support your assessment (mass characteristics, calcifications, density, etc.)

Respond in this EXACT format:
PREDICTION: [MALIGNANT or BENIGN]
CONFIDENCE: [number between 0 and 100]
FINDINGS: [2-3 sentences describing what you observe]

IMPORTANT: This is for educational/screening assistance only. Always recommend professional medical evaluation.
If the image is not a mammogram or medical image, respond with:
PREDICTION: UNKNOWN
CONFIDENCE: 0
FINDINGS: The uploaded image does not appear to be a mammogram or medical image."""


def _parse_gemini_response(text: str) -> tuple[str, float, str]:
    """Parse structured response from Gemini into (prediction, confidence, findings)."""
    prediction = "Benign"
    confidence = 0.5
    findings   = ""

    for line in text.strip().splitlines():
        line = line.strip()
        if line.startswith("PREDICTION:"):
            val = line.replace("PREDICTION:", "").strip().upper()
            if "MALIGNANT" in val:
                prediction = "Malignant"
            elif "BENIGN" in val:
                prediction = "Benign"
        elif line.startswith("CONFIDENCE:"):
            try:
                num = float(line.replace("CONFIDENCE:", "").strip().rstrip("%"))
                confidence = round(num / 100, 4)   # convert % → 0-1
            except ValueError:
                pass
        elif line.startswith("FINDINGS:"):
            findings = line.replace("FINDINGS:", "").strip()

    return prediction, confidence, findings


def _build_message(prediction: str, confidence: float, findings: str, input_type: str) -> str:
    pct = f"{confidence * 100:.1f}%"
    source = "mammogram image" if input_type == "image" else "clinical parameters"
    base = (
        f"Based on the provided {source}, the analysis indicates a "
        f"{prediction} result with {pct} confidence."
    )
    if findings:
        base += f" Key findings: {findings}"
    if prediction == "Malignant":
        base += " Please consult an oncologist or radiologist immediately for further evaluation."
    else:
        base += " Regular screening is still recommended. Consult your doctor if you have concerns."
    return base


async def _save(user_id, input_type, parameters, image_filename, prediction, confidence):
    col = get_cancer_results_collection()
    await col.insert_one({
        "user_id":        user_id,
        "input_type":     input_type,
        "parameters":     parameters,
        "image_filename": image_filename,
        "prediction":     prediction,
        "confidence":     confidence,
        "created_at":     datetime.now(timezone.utc),
    })


async def predict_from_parameters(
    payload: CancerParametersInput, user_id: str
) -> CancerPredictionResponse:
    prediction, confidence = predict_parameters(payload.dict())
    await _save(user_id, "parameters", payload.dict(), None, prediction, confidence)
    return CancerPredictionResponse(
        prediction=prediction,
        confidence=confidence,
        message=_build_message(prediction, confidence, "", "parameters"),
    )


async def predict_from_image(
    image_bytes: bytes, filename: str, user_id: str
) -> CancerPredictionResponse:
    # Detect MIME type
    mime_type = "image/jpeg"
    if filename.lower().endswith(".png"):
        mime_type = "image/png"

    # Send to Gemini Vision
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            types.Part.from_text(text=MAMMOGRAM_PROMPT),
        ],
    )

    prediction, confidence, findings = _parse_gemini_response(response.text)

    await _save(user_id, "image", None, filename, prediction, confidence)

    return CancerPredictionResponse(
        prediction=prediction,
        confidence=confidence,
        message=_build_message(prediction, confidence, findings, "image"),
    )