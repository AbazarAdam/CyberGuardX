import pickle
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
import numpy as np

from app.infrastructure.ml.feature_extractor import extract_url_features, features_to_array, get_feature_names


def load_dataset() -> pd.DataFrame:
    """
    Load phishing URL dataset.
    Downloads from public source if not present locally.
    
    Returns:
        DataFrame with 'url' and 'label' columns
    """
    data_dir = Path(__file__).resolve().parents[2] / "data"
    data_dir.mkdir(exist_ok=True)
    
    dataset_path = data_dir / "phishing_urls.csv"
    
    if not dataset_path.exists():
        print("Downloading phishing URL dataset...")
        
        try:
            url = "https://raw.githubusercontent.com/faizann24/Using-machine-learning-to-detect-malicious-URLs/master/data/data.csv"
            df = pd.read_csv(url)
            
            if "url" in df.columns and "label" in df.columns:
                df = df[["url", "label"]].dropna()
            else:
                raise ValueError("Dataset missing required columns")
                
        except Exception as e:
            print(f"Could not download from GitHub: {e}")
            print("Creating synthetic dataset for demonstration...")
            
            phishing_urls = [
                "http://paypal-verify-account-login.com",
                "https://secure-updates-microsoft.net/update",
                "http://amazon-account-suspended.info",
                "http://faceb00k-security-check.com",
                "http://apple-icloud-support.net/verify",
                "https://bank-of-america-alert.com",
                "http://google-security-update.info",
                "http://netflix-payment-update.net",
                "https://ups-tracking-delivery.info",
                "http://fedex-package-delivery.org",
            ] * 50
            
            legitimate_urls = [
                "https://www.google.com",
                "https://www.github.com",
                "https://www.stackoverflow.com",
                "https://www.wikipedia.org",
                "https://www.python.org",
                "https://www.microsoft.com",
                "https://www.amazon.com",
                "https://www.facebook.com",
                "https://www.twitter.com",
                "https://www.linkedin.com",
            ] * 50
            
            df = pd.DataFrame({
                "url": phishing_urls + legitimate_urls,
                "label": [1] * len(phishing_urls) + [0] * len(legitimate_urls)
            })
        
        df.to_csv(dataset_path, index=False)
        print(f"Dataset saved to {dataset_path}")
    else:
        print(f"Loading existing dataset from {dataset_path}")
        df = pd.read_csv(dataset_path)
    
    return df


def extract_features_from_dataframe(df: pd.DataFrame) -> tuple:
    """
    Extract features from all URLs in dataframe.
    
    Args:
        df: DataFrame with 'url' and 'label' columns
        
    Returns:
        Tuple of (X, y) where X is feature matrix and y is labels
    """
    print("Extracting features from URLs...")
    
    X = []
    y = []
    
    for idx, row in df.iterrows():
        try:
            features = extract_url_features(row["url"])
            feature_array = features_to_array(features)
            X.append(feature_array)
            y.append(row["label"])
        except Exception:
            continue
    
    print(f"Extracted features from {len(X)} URLs")
    return X, y


def train_model():
    """
    Train phishing URL detection model and save to disk.
    """
    print("=" * 60)
    print("PHISHING URL DETECTION MODEL TRAINING")
    print("=" * 60)
    
    df = load_dataset()
    print(f"\nDataset size: {len(df)} URLs")
    print(f"Phishing: {(df['label'] == 1).sum()}")
    print(f"Legitimate: {(df['label'] == 0).sum()}")
    
    X, y = extract_features_from_dataframe(df)
    
    print("\nSplitting dataset (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train both models for comparison
    print("\n" + "="*60)
    print("TRAINING LOGISTIC REGRESSION")
    print("="*60)
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    
    y_pred_lr = lr_model.predict(X_test)
    lr_metrics = {
        "accuracy": accuracy_score(y_test, y_pred_lr),
        "precision": precision_score(y_test, y_pred_lr),
        "recall": recall_score(y_test, y_pred_lr),
        "f1_score": f1_score(y_test, y_pred_lr)
    }
    
    print(f"Accuracy:  {lr_metrics['accuracy']:.4f}")
    print(f"Precision: {lr_metrics['precision']:.4f}")
    print(f"Recall:    {lr_metrics['recall']:.4f}")
    print(f"F1-Score:  {lr_metrics['f1_score']:.4f}")
    
    print("\n" + "="*60)
    print("TRAINING RANDOM FOREST")
    print("="*60)
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    rf_model.fit(X_train, y_train)
    
    y_pred_rf = rf_model.predict(X_test)
    rf_metrics = {
        "accuracy": accuracy_score(y_test, y_pred_rf),
        "precision": precision_score(y_test, y_pred_rf),
        "recall": recall_score(y_test, y_pred_rf),
        "f1_score": f1_score(y_test, y_pred_rf)
    }
    
    print(f"Accuracy:  {rf_metrics['accuracy']:.4f}")
    print(f"Precision: {rf_metrics['precision']:.4f}")
    print(f"Recall:    {rf_metrics['recall']:.4f}")
    print(f"F1-Score:  {rf_metrics['f1_score']:.4f}")
    
    # Choose best model
    best_model = rf_model if rf_metrics['f1_score'] > lr_metrics['f1_score'] else lr_model
    best_model_name = "Random Forest" if rf_metrics['f1_score'] > lr_metrics['f1_score'] else "Logistic Regression"
    best_metrics = rf_metrics if rf_metrics['f1_score'] > lr_metrics['f1_score'] else lr_metrics
    
    print("\n" + "="*60)
    print(f"BEST MODEL: {best_model_name}")
    print("="*60)
    
    # Extract feature importance
    feature_names = get_feature_names()
    if hasattr(best_model, 'feature_importances_'):
        feature_importance = dict(zip(feature_names, best_model.feature_importances_))
    else:
        # For logistic regression, use absolute coefficients
        coef = np.abs(best_model.coef_[0])
        coef_normalized = coef / coef.sum()
        feature_importance = dict(zip(feature_names, coef_normalized))
    
    # Sort by importance
    feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
    
    print("\nFEATURE IMPORTANCE:")
    for feature, importance in feature_importance.items():
        print(f"  {feature:25s}: {importance:.4f}")
    
    print("="*60)
    
    models_dir = Path(__file__).resolve().parents[2] / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Save best model
    model_path = models_dir / "phishing_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(best_model, f)
    
    # Save model metadata
    metadata = {
        "model_name": best_model_name,
        "model_version": "2.0",
        "trained_at": datetime.utcnow().isoformat(),
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "num_features": len(feature_names),
        "feature_names": feature_names,
        "feature_importance": feature_importance,
        "metrics": best_metrics,
        "lr_metrics": lr_metrics,
        "rf_metrics": rf_metrics
    }
    
    metadata_path = models_dir / "phishing_model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nModel saved to: {model_path}")
    print(f"Metadata saved to: {metadata_path}")
    print("\nTraining complete!")


if __name__ == "__main__":
    train_model()
