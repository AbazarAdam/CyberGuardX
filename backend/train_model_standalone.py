import pickle
import sys
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ml.feature_extractor import extract_url_features, features_to_array


def create_synthetic_dataset():
    """Create synthetic phishing URL dataset for demonstration."""
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
    
    return pd.DataFrame({
        "url": phishing_urls + legitimate_urls,
        "label": [1] * len(phishing_urls) + [0] * len(legitimate_urls)
    })


def main():
    print("=" * 60)
    print("PHISHING URL DETECTION MODEL TRAINING")
    print("=" * 60)
    
    backend_dir = Path(__file__).resolve().parent.parent
    data_dir = backend_dir / "data"
    models_dir = backend_dir / "models"
    
    data_dir.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    
    dataset_path = data_dir / "phishing_urls.csv"
    
    if not dataset_path.exists():
        print("\nCreating synthetic dataset for demonstration...")
        df = create_synthetic_dataset()
        df.to_csv(dataset_path, index=False)
        print(f"Dataset saved to {dataset_path}")
    else:
        print(f"\nLoading dataset from {dataset_path}")
        df = pd.read_csv(dataset_path)
    
    print(f"\nDataset size: {len(df)} URLs")
    print(f"Phishing: {(df['label'] == 1).sum()}")
    print(f"Legitimate: {(df['label'] == 0).sum()}")
    
    print("\nExtracting features from URLs...")
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
    
    print("\nSplitting dataset (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    print("\nTraining Logistic Regression model...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    print("\nEvaluating model...")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print("\n" + "=" * 60)
    print("MODEL EVALUATION METRICS")
    print("=" * 60)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print("=" * 60)
    
    model_path = models_dir / "phishing_model.pkl"
    
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    
    print(f"\nModel saved to: {model_path}")
    print("\nTraining complete!")


if __name__ == "__main__":
    main()
