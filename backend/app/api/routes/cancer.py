from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi import status as http_status

from app.schemas.cancer import CancerParametersInput, CancerPredictionResponse
from app.core.security import get_current_user
from app.services.cancer_service import predict_from_parameters, predict_from_image

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png"}
MAX_SIZE_MB   = 10


@router.post("/predict/parameters", response_model=CancerPredictionResponse)
async def predict_cancer_parameters(
    payload: CancerParametersInput,
    current_user: dict = Depends(get_current_user),
):
    """Predict malignant/benign from 10 clinical parameters."""
    try:
        return await predict_from_parameters(payload, current_user["user_id"])
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/predict/image", response_model=CancerPredictionResponse)
async def predict_cancer_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Predict malignant/benign from a mammogram image (JPEG/PNG, max 10 MB)."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Upload JPEG or PNG."
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_SIZE_MB} MB limit.")

    try:
        return await predict_from_image(image_bytes, file.filename, current_user["user_id"])
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not process image: {str(e)}")


@router.get("/history")
async def get_cancer_history(current_user: dict = Depends(get_current_user)):
    """Fetch last 20 predictions for the logged-in user."""
    from app.db.mongodb import get_cancer_results_collection
    col = get_cancer_results_collection()
    results = await col.find(
        {"user_id": current_user["user_id"]}
    ).sort("created_at", -1).to_list(20)
    for r in results:
        r["_id"] = str(r["_id"])
        r["created_at"] = r["created_at"].isoformat()
    return results


@router.get("/model-info")
async def model_info():
    """Returns info about currently loaded models."""
    import json
    from pathlib import Path
    MODELS_DIR = Path("app/ml/cancer_detection/models")
    info = {}
    for report in ("training_report.json", "image_training_report.json"):
        p = MODELS_DIR / report
        if p.exists():
            info[report.replace("_report.json", "")] = json.loads(p.read_text())
    return info or {"message": "No trained models found yet. Run the training scripts first."}
