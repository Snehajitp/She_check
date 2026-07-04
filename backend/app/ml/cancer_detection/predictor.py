"""
Predictor — loads trained models once at startup and exposes
predict_parameters() and predict_image() functions.
"""
import io
import joblib
import numpy as np
from pathlib import Path
from typing import Tuple
import torch
MODELS_DIR = Path(__file__).parent / "models"

_params_model  = None
_scaler        = None
_feature_names = None
_image_model   = None
_img_transform = None

LABELS = {0: "Malignant", 1: "Benign"}

# All 30 Wisconsin dataset features in the correct order
FEATURE_ORDER = [
    "mean radius", "mean texture", "mean perimeter", "mean area",
    "mean smoothness", "mean compactness", "mean concavity",
    "mean concave points", "mean symmetry", "mean fractal dimension",
    "radius error", "texture error", "perimeter error", "area error",
    "smoothness error", "compactness error", "concavity error",
    "concave points error", "symmetry error", "fractal dimension error",
    "worst radius", "worst texture", "worst perimeter", "worst area",
    "worst smoothness", "worst compactness", "worst concavity",
    "worst concave points", "worst symmetry", "worst fractal dimension",
]

# Map our API field names → dataset feature names
API_TO_FEATURE = {
    "radius_mean":              "mean radius",
    "texture_mean":             "mean texture",
    "perimeter_mean":           "mean perimeter",
    "area_mean":                "mean area",
    "smoothness_mean":          "mean smoothness",
    "compactness_mean":         "mean compactness",
    "concavity_mean":           "mean concavity",
    "concave_points_mean":      "mean concave points",
    "symmetry_mean":            "mean symmetry",
    "fractal_dimension_mean":   "mean fractal dimension",
}

# Median values from Wisconsin dataset — used to fill the 20 unrequired features
FEATURE_MEDIANS = {
    "mean radius": 13.37, "mean texture": 18.84, "mean perimeter": 86.24,
    "mean area": 551.1, "mean smoothness": 0.0959, "mean compactness": 0.1045,
    "mean concavity": 0.0888, "mean concave points": 0.0489,
    "mean symmetry": 0.1792, "mean fractal dimension": 0.0616,
    "radius error": 0.3242, "texture error": 1.108, "perimeter error": 2.287,
    "area error": 24.53, "smoothness error": 0.00638, "compactness error": 0.02045,
    "concavity error": 0.02589, "concave points error": 0.01093,
    "symmetry error": 0.01587, "fractal dimension error": 0.003695,
    "worst radius": 14.97, "worst texture": 25.41, "worst perimeter": 97.66,
    "worst area": 686.5, "worst smoothness": 0.1323, "worst compactness": 0.2119,
    "worst concavity": 0.2267, "worst concave points": 0.09993,
    "worst symmetry": 0.2822, "worst fractal dimension": 0.08004,
}


def _load_params_model():
    global _params_model, _scaler, _feature_names
    if _params_model is None:
        model_path = MODELS_DIR / "parameters_model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(
                "Parameters model not found. Run:\n"
                "  python -m app.ml.cancer_detection.train_parameters_model"
            )
        _params_model  = joblib.load(MODELS_DIR / "parameters_model.pkl")
        _scaler        = joblib.load(MODELS_DIR / "scaler.pkl")
        _feature_names = joblib.load(MODELS_DIR / "feature_names.pkl")
        print(f"[Cancer] Parameters model loaded. Features: {_feature_names[:3]}...")
    return _params_model, _scaler, _feature_names


def predict_parameters(api_input: dict) -> Tuple[str, float]:
    """
    Accepts our 10-field API input, fills remaining 20 features with
    dataset medians, then runs the trained 30-feature model.
    """
    model, scaler, feature_names = _load_params_model()

    # Build full feature vector in correct order
    feature_values = {}
    for api_key, feat_name in API_TO_FEATURE.items():
        feature_values[feat_name] = api_input.get(api_key, FEATURE_MEDIANS[feat_name])

    # Fill remaining features with medians
    for feat in FEATURE_ORDER:
        if feat not in feature_values:
            feature_values[feat] = FEATURE_MEDIANS[feat]

    # Build array in the exact order the model was trained on
    vector = np.array([[feature_values[f] for f in feature_names]])

    scaled     = scaler.transform(vector)
    pred_idx   = int(model.predict(scaled)[0])
    confidence = float(model.predict_proba(scaled)[0][pred_idx])
    label      = LABELS[pred_idx]

    print(f"[Cancer] Prediction: {label}, Confidence: {confidence:.4f}")
    return label, round(confidence, 4)


def _load_image_model():
    global _image_model, _img_transform
    if _image_model is None:
        try:
            import torch
            from torchvision import models, transforms
        except ImportError:
            raise ImportError("Install PyTorch: pip install torch torchvision Pillow")

        model_path = MODELS_DIR / "image_model.pth"
        if not model_path.exists():
            raise FileNotFoundError(
                "Image model not found. Run:\n"
                "  python -m app.ml.cancer_detection.train_image_model"
            )

        checkpoint  = torch.load(model_path, map_location="cpu", weights_only=False)
        img_size    = checkpoint.get("img_size", 224)

        import torch.nn as nn
        net = models.efficientnet_b0(weights=None)
        in_features = net.classifier[1].in_features
        net.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 2),
        )
        net.load_state_dict(checkpoint["model_state_dict"])
        net.eval()
        _image_model = net

        _img_transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        print("[Cancer] Image model loaded.")
    return _image_model, _img_transform


def predict_image(image_bytes: bytes) -> Tuple[str, float]:
    # import torch
    from PIL import Image

    model, transform = _load_image_model()
    img    = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        logits = model(tensor)
        probs  = torch.softmax(logits, dim=1)[0]

    pred_idx   = int(probs.argmax().item())
    confidence = float(probs[pred_idx].item())
    label      = LABELS[pred_idx]

    print(f"[Cancer] Image prediction: {label}, Confidence: {confidence:.4f}")
    return label, round(confidence, 4)