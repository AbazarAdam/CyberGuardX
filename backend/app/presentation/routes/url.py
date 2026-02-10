"""
Route — Phishing URL Checker
==============================
``POST /check-url`` — ML-powered phishing URL classification with
feature-level explainability.
"""

import json
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import PHISHING_MODEL_PATH, PHISHING_METADATA_PATH
from app.presentation.schemas import (
    URLCheckRequest,
    URLCheckResponse,
    ModelInfo,
    FeatureAnalysis,
)
from app.presentation.dependencies import get_db
from app.domain.risk_engine import calculate_risk_level
from app.infrastructure.database.models import ScanHistory
from app.infrastructure.ml.feature_extractor import (
    extract_url_features,
    features_to_array,
    explain_features,
    get_feature_names,
)

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────
# Model loader (cached — loaded once, reused across requests)
# ──────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_phishing_model() -> Tuple:
    """
    Load the trained phishing detection model and its metadata.

    Returns:
        ``(model, metadata_dict)``

    Raises:
        FileNotFoundError: if the ``.pkl`` file doesn't exist.
    """
    if not PHISHING_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {PHISHING_MODEL_PATH}. "
            "Train first:  python -m app.infrastructure.ml.trainer"
        )
    with open(PHISHING_MODEL_PATH, "rb") as fh:
        model = pickle.load(fh)

    metadata = {}
    if PHISHING_METADATA_PATH.exists():
        with open(PHISHING_METADATA_PATH, "r") as fh:
            metadata = json.load(fh)

    return model, metadata


# ──────────────────────────────────────────────────────────────────────────
# Endpoint
# ──────────────────────────────────────────────────────────────────────────

@router.post("/check-url", response_model=URLCheckResponse)
def check_url(payload: URLCheckRequest, db: Session = Depends(get_db)):
    """Analyse a URL for phishing indicators using the ML model."""

    # 1. Load model
    try:
        model, metadata = load_phishing_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # 2. Extract features
    try:
        features = extract_url_features(payload.url)
        feature_array = [features_to_array(features)]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid URL: {exc}") from exc

    # 3. Predict
    try:
        probabilities = model.predict_proba(feature_array)[0]
        phishing_probability = probabilities[1]
        is_phishing = phishing_probability >= 0.5
        confidence = abs(phishing_probability - 0.5) * 2      # scale to 0–1
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Model prediction failed") from exc

    # 4. Explainability
    feature_importance = metadata.get("feature_importance", {})
    feature_names = get_feature_names()
    feature_explanations = explain_features(features)

    feature_analysis = []
    for name in feature_names:
        if name in feature_explanations:
            exp = feature_explanations[name]
            impact = feature_importance.get(name, 0)
            feature_analysis.append(
                FeatureAnalysis(
                    feature=name,
                    value=features[name],
                    impact=float(impact),
                    risk=exp["risk"],
                    explanation=exp["explanation"],
                )
            )
    feature_analysis.sort(key=lambda x: x.impact, reverse=True)

    # 5. Recommendations
    recommendations = []
    if is_phishing:
        recommendations.append("⚠️ This URL shows multiple phishing indicators — do not click or enter credentials")
        if features.get("has_https") == 0:
            recommendations.append("Missing HTTPS encryption — legitimate sites use HTTPS")
        if features.get("domain_age") == 0:
            recommendations.append("New or unknown domain — verify legitimacy before visiting")
        if features.get("has_at") == 1:
            recommendations.append("Contains @ symbol — often used to disguise real destination")
        if features.get("num_hyphens", 0) >= 2:
            recommendations.append("Multiple hyphens in domain — possible brand impersonation")
        recommendations += [
            "Verify the URL matches the official website",
            "Check for spelling errors in the domain name",
        ]
    else:
        recommendations += [
            "✅ URL appears legitimate based on analysis",
            "Always verify sender before clicking links in emails",
            "Look for HTTPS and valid SSL certificates",
        ]

    # 6. Model info
    model_info = None
    if metadata.get("metrics"):
        m = metadata["metrics"]
        model_info = ModelInfo(
            name=metadata.get("model_name", "Unknown"),
            version=metadata.get("model_version", "1.0"),
            accuracy=m.get("accuracy", 0),
            precision=m.get("precision", 0),
            recall=m.get("recall", 0),
            f1_score=m.get("f1_score", 0),
        )

    risk_level = calculate_risk_level(email_breached=False, phishing_score=phishing_probability)

    # 7. Persist (best-effort)
    scan = ScanHistory(
        email="URL_SCAN",
        email_breached=False,
        phishing_score=float(phishing_probability),
        risk_level=risk_level,
    )
    try:
        db.add(scan)
        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"Warning: failed to save URL scan record: {exc}")

    # 8. Response
    if is_phishing:
        message = f"⚠️ High phishing probability ({phishing_probability:.1%}), confidence {confidence:.1%}"
    else:
        message = f"✅ Appears legitimate (phishing probability: {phishing_probability:.1%}, confidence: {confidence:.1%})"

    return URLCheckResponse(
        url=payload.url,
        is_phishing=is_phishing,
        phishing_score=float(phishing_probability),
        confidence=float(confidence),
        risk_level=risk_level,
        message=message,
        model_info=model_info,
        feature_importance=feature_importance,
        feature_analysis=feature_analysis[:5],
        recommendations=recommendations,
    )
