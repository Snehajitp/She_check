"""
Train XGBoost / Random Forest model on Wisconsin Breast Cancer Dataset.

Dataset: sklearn's built-in load_breast_cancer()
         OR download from Kaggle: "Breast Cancer Wisconsin (Diagnostic) Data Set"

Run from the backend/ directory:
    python -m app.ml.cancer_detection.train_parameters_model

Outputs saved to app/ml/cancer_detection/models/:
    - parameters_model.pkl
    - scaler.pkl
    - label_encoder.pkl
    - feature_names.pkl
    - training_report.txt
"""

import os
import json
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, accuracy_score
)

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("XGBoost not installed — using GradientBoostingClassifier instead.")

MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


def load_data():
    """Load Wisconsin Breast Cancer dataset."""
    data = load_breast_cancer()
    X, y = data.data, data.target
    feature_names = list(data.feature_names)
    # sklearn uses 0=malignant, 1=benign — we keep that convention
    class_names = list(data.target_names)   # ['malignant', 'benign']
    print(f"Dataset loaded: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"Classes: {class_names}")
    print(f"Malignant: {sum(y==0)}, Benign: {sum(y==1)}")
    return X, y, feature_names, class_names


def preprocess(X_train, X_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, scaler


def build_candidates():
    candidates = {
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=None,
            min_samples_split=2, random_state=42, n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.05,
            max_depth=4, random_state=42
        ),
        "LogisticRegression": LogisticRegression(
            C=1.0, max_iter=1000, random_state=42
        ),
    }
    if HAS_XGBOOST:
        candidates["XGBoost"] = XGBClassifier(
            n_estimators=200, learning_rate=0.05,
            max_depth=4, use_label_encoder=False,
            eval_metric="logloss", random_state=42
        )
    return candidates


def evaluate(name, model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc  = accuracy_score(y_test, y_pred)
    auc  = roc_auc_score(y_test, y_prob)
    cv   = cross_val_score(model, X_train, y_train, cv=5, scoring="roc_auc")

    print(f"\n── {name} ──")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  ROC-AUC  : {auc:.4f}")
    print(f"  CV AUC   : {cv.mean():.4f} ± {cv.std():.4f}")
    print(classification_report(y_test, y_pred, target_names=["Malignant", "Benign"]))

    return {"name": name, "model": model, "acc": acc, "auc": auc, "cv_mean": cv.mean()}


def train():
    print("=" * 55)
    print("  She Check — Cancer Parameters Model Training")
    print("=" * 55)

    X, y, feature_names, class_names = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    X_train_s, X_test_s, scaler = preprocess(X_train, X_test)

    results = []
    for name, model in build_candidates().items():
        res = evaluate(name, model, X_train_s, y_train, X_test_s, y_test)
        results.append(res)

    # Pick best by ROC-AUC
    best = max(results, key=lambda r: r["auc"])
    print(f"\n✅ Best model: {best['name']} (AUC={best['auc']:.4f})")

    # Save artefacts
    joblib.dump(best["model"], MODELS_DIR / "parameters_model.pkl")
    joblib.dump(scaler,        MODELS_DIR / "scaler.pkl")
    joblib.dump(feature_names, MODELS_DIR / "feature_names.pkl")

    le = LabelEncoder()
    le.fit(["Malignant", "Benign"])
    joblib.dump(le, MODELS_DIR / "label_encoder.pkl")

    # Save report
    report = {
        "trained_at": datetime.utcnow().isoformat(),
        "best_model": best["name"],
        "accuracy": round(best["acc"], 4),
        "roc_auc": round(best["auc"], 4),
        "cv_auc_mean": round(best["cv_mean"], 4),
        "features": feature_names,
        "classes": class_names,
    }
    with open(MODELS_DIR / "training_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nModels saved to: {MODELS_DIR}")
    print("Training complete!")
    return report


if __name__ == "__main__":
    train()
