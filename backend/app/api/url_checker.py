import pickle
import json
from functools import lru_cache
from pathlib import Path
from typing import Tuple, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import URLCheckRequest, URLCheckResponse, ModelInfo, FeatureAnalysis
from app.core.risk_engine import calculate_risk_level
from app.db.database import SessionLocal
from app.db.models import ScanHistory
from app.ml.feature_extractor import extract_url_features, features_to_array, explain_features, get_feature_names
import numpy as np

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache(maxsize=1)
def load_phishing_model() -> Tuple:
    """
    Load trained phishing detection model and metadata.
    Cached to avoid reloading on every request.
    
    Returns:
        Tuple of (model, metadata_dict)
        
    Raises:
        FileNotFoundError: If model file doesn't exist
    """
    models_dir = Path(__file__).resolve().parents[2] / "models"
    model_path = models_dir / "phishing_model.pkl"
    metadata_path = models_dir / "phishing_model_metadata.json"
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            "Run training script first: python -m app.ml.train_phishing_model"
        )
    
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    
    return model, metadata


@router.post("/check-url", response_model=URLCheckResponse)
def check_url(payload: URLCheckRequest, db: Session = Depends(get_db)):
    """
    Analyze URL for phishing indicators using ML model.
    
    Args:
        payload: URLCheckRequest with url field
        db: Database session
        
    Returns:
        URLCheckResponse with prediction results
        
    Raises:
        HTTPException: If model not found or URL processing fails
    """
    try:
        model, metadata = load_phishing_model()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Phishing detection model not available. Please train the model first.",
        ) from exc
    
    try:
        features = extract_url_features(payload.url)
        feature_array = [features_to_array(features)]
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid URL format: {str(exc)}",
        ) from exc
    
    try:
        probabilities = model.predict_proba(feature_array)[0]
        phishing_probability = probabilities[1]
        is_phishing = phishing_probability >= 0.5
        
        # Calculate confidence (distance from decision boundary)
        confidence = abs(phishing_probability - 0.5) * 2  # Scale to 0-1
        
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Model prediction failed",
        ) from exc
    
    # Get feature importance and explanations
    feature_importance = metadata.get('feature_importance', {})
    feature_names = get_feature_names()
    feature_explanations = explain_features(features)
    
    # Calculate feature impacts (approximate)
    feature_analysis = []
    for feat_name in feature_names:
        if feat_name in feature_explanations:
            exp = feature_explanations[feat_name]
            impact = feature_importance.get(feat_name, 0)
            feature_analysis.append(FeatureAnalysis(
                feature=feat_name,
                value=features[feat_name],
                impact=float(impact),
                risk=exp['risk'],
                explanation=exp['explanation']
            ))
    
    # Sort by impact
    feature_analysis.sort(key=lambda x: x.impact, reverse=True)
    
    # Generate recommendations
    recommendations = []
    if is_phishing:
        recommendations.append("⚠️ This URL shows multiple phishing indicators - do not click or enter credentials")
        
        # Add specific recommendations based on features
        if features.get('has_https') == 0:
            recommendations.append("Missing HTTPS encryption - legitimate sites use HTTPS")
        if features.get('domain_age') == 0:
            recommendations.append("New or unknown domain - verify legitimacy before visiting")
        if features.get('has_at') == 1:
            recommendations.append("Contains @ symbol - often used to disguise real destination")
        if features.get('num_hyphens', 0) >= 2:
            recommendations.append("Multiple hyphens in domain - possible brand impersonation")
        
        recommendations.append("Verify the URL matches the official website")
        recommendations.append("Check for spelling errors in the domain name")
    else:
        recommendations.append("✅ URL appears legitimate based on analysis")
        recommendations.append("Always verify sender before clicking links in emails")
        recommendations.append("Look for HTTPS and valid SSL certificates")
    
    # Create model info
    model_info = None
    if metadata.get('metrics'):
        metrics = metadata['metrics']
        model_info = ModelInfo(
            name=metadata.get('model_name', 'Unknown'),
            version=metadata.get('model_version', '1.0'),
            accuracy=metrics.get('accuracy', 0),
            precision=metrics.get('precision', 0),
            recall=metrics.get('recall', 0),
            f1_score=metrics.get('f1_score', 0)
        )
    
    risk_level = calculate_risk_level(
        email_breached=False,
        phishing_score=phishing_probability,
    )
    
    scan = ScanHistory(
        email="URL_SCAN",
        email_breached=False,
        phishing_score=float(phishing_probability),
        risk_level=risk_level,
    )
    
    # Try to save but don't fail the request if it doesn't work
    try:
        db.add(scan)
        db.commit()
        db.refresh(scan)
    except Exception as exc:
        db.rollback()
        # Log the error but continue - ML results are more important
        print(f"Warning: Failed to save scan record: {exc}")
    
    if is_phishing:
        message = f"⚠️ High phishing probability detected ({phishing_probability:.1%}) with {confidence:.1%} confidence"
    else:
        message = f"✅ URL appears legitimate (phishing probability: {phishing_probability:.1%}, confidence: {confidence:.1%})"
    
    return URLCheckResponse(
        url=payload.url,
        is_phishing=is_phishing,
        phishing_score=float(phishing_probability),
        confidence=float(confidence),
        risk_level=risk_level,
        message=message,
        model_info=model_info,
        feature_importance=feature_importance,
        feature_analysis=feature_analysis[:5],  # Top 5 features
        recommendations=recommendations
    )
