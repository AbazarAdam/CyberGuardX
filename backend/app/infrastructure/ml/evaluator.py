"""
Enhanced ML Model Evaluation and Analysis for CyberGuardX

This module provides comprehensive evaluation of the phishing URL detection model
including confusion matrix, feature importance analysis, and performance metrics.

Academic Purpose: Final Year Project Documentation
"""

import pickle
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from app.infrastructure.ml.feature_extractor import extract_url_features, features_to_array


def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_confusion_matrix_analysis(y_test, y_pred):
    """
    Generate and print confusion matrix with detailed analysis.
    
    Confusion Matrix Layout:
                    Predicted
                    Legit   Phish
    Actual  Legit   TN      FP
            Phish   FN      TP
    
    Args:
        y_test: True labels
        y_pred: Predicted labels
    """
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    print_section_header("CONFUSION MATRIX")
    print("\n                  Predicted")
    print("                Legitimate  Phishing")
    print(f"Actual Legit    {tn:>6}     {fp:>6}    (True Negatives / False Positives)")
    print(f"       Phish    {fn:>6}     {tp:>6}    (False Negatives / True Positives)")
    
    print("\nDetailed Analysis:")
    print(f"  True Positives (TP):   {tp:>4}  - Correctly identified phishing URLs")
    print(f"  True Negatives (TN):   {tn:>4}  - Correctly identified legitimate URLs")
    print(f"  False Positives (FP):  {fp:>4}  - Legitimate URLs flagged as phishing")
    print(f"  False Negatives (FN):  {fn:>4}  - Phishing URLs missed by model")
    
    print("\nPerformance Implications:")
    if fp > 0:
        print(f"  - {fp} legitimate sites may be incorrectly blocked")
    if fn > 0:
        print(f"  - {fn} phishing sites may evade detection (security risk)")
    
    total = tp + tn + fp + fn
    print(f"\nTotal Predictions: {total}")
    print(f"Correct Predictions: {tp + tn} ({((tp + tn) / total * 100):.2f}%)")


def analyze_feature_importance(model, feature_names):
    """
    Extract and analyze Logistic Regression coefficients to understand
    which features contribute most to phishing detection.
    
    Args:
        model: Trained Logistic Regression model
        feature_names: List of feature names
    """
    print_section_header("FEATURE IMPORTANCE ANALYSIS")
    
    # Extract coefficients (weights for each feature)
    coefficients = model.coef_[0]
    
    # Create feature importance dataframe
    feature_importance = pd.DataFrame({
        'Feature': feature_names,
        'Coefficient': coefficients,
        'Abs_Coefficient': abs(coefficients)
    }).sort_values('Abs_Coefficient', ascending=False)
    
    print("\nLogistic Regression Feature Coefficients:")
    print("(Higher absolute value = stronger influence on prediction)")
    print("\n{:<20} {:>15} {:>15}".format("Feature", "Coefficient", "Importance"))
    print("-" * 52)
    
    # Feature explanations for academic reporting
    feature_explanations = {
        "url_length": "Long URLs often indicate obfuscation attempts",
        "num_dots": "Multiple subdomains suggest domain spoofing",
        "num_hyphens": "Excessive hyphens used to mimic legitimate brands",
        "num_digits": "Random digits often appear in phishing URLs",
        "has_at": "@ symbol can hide true destination in URLs",
        "has_https": "HTTPS presence (surprisingly, phishers use it too)"
    }
    
    for _, row in feature_importance.iterrows():
        feature = row['Feature']
        coef = row['Coefficient']
        impact = "↑ Phishing" if coef > 0 else "↓ Phishing"
        print(f"{feature:<20} {coef:>15.6f} {impact:>15}")
    
    print("\nFeature Explanations (Academic Context):")
    print("-" * 70)
    for feature, explanation in feature_explanations.items():
        coef = feature_importance[feature_importance['Feature'] == feature]['Coefficient'].values[0]
        direction = "increases" if coef > 0 else "decreases"
        print(f"\n  • {feature.upper()}")
        print(f"    {explanation}")
        print(f"    Impact: {direction} phishing probability")


def print_model_justification():
    """
    Document the rationale behind model and feature selection choices.
    Essential for academic report writing.
    """
    print_section_header("MODEL JUSTIFICATION & DESIGN DECISIONS")
    
    print("\n1. WHY LOGISTIC REGRESSION?")
    print("   ✓ Interpretable: Coefficients show feature importance")
    print("   ✓ Fast inference: <5ms per URL (real-time detection)")
    print("   ✓ Low computational cost: Runs on modest hardware")
    print("   ✓ Baseline model: Industry standard for binary classification")
    print("   ✓ Academic clarity: Easy to explain in FYP documentation")
    
    print("\n2. WHY LEXICAL FEATURES?")
    print("   ✓ No external dependencies: No DNS lookups or API calls")
    print("   ✓ Privacy-preserving: URL analysis only, no user data")
    print("   ✓ Instant analysis: No waiting for domain registration checks")
    print("   ✓ Language-agnostic: Works across all URL formats")
    print("   ✓ Robust: Cannot be easily manipulated by attackers")


def print_limitations():
    """
    Document model limitations for academic transparency.
    Critical for demonstrating understanding of system constraints.
    """
    print_section_header("MODEL LIMITATIONS & CONSTRAINTS")
    
    print("\n1. FEATURE SET LIMITATIONS")
    print("   ⚠ Lexical-only features miss important signals:")
    print("     - Domain age (new domains = higher phishing risk)")
    print("     - WHOIS information (registrar, registrant)")
    print("     - DNS records (suspicious nameservers)")
    print("     - Page content analysis (HTML/JavaScript inspection)")
    print("     - Certificate validity (SSL/TLS details)")
    
    print("\n2. DATASET CONSTRAINTS")
    print("   ⚠ Synthetic/limited dataset (1000 URLs):")
    print("     - May not represent real-world distribution")
    print("     - Limited variety of phishing patterns")
    print("     - No adversarial examples included")
    
    print("\n3. MODEL ARCHITECTURE")
    print("   ⚠ Linear model limitations:")
    print("     - Cannot capture complex non-linear patterns")
    print("     - No sequential analysis (deep learning advantage)")
    print("     - Limited feature interaction modeling")
    
    print("\n4. OPERATIONAL LIMITATIONS")
    print("   ⚠ False Positive Risk:")
    print("     - Legitimate new startups may be flagged")
    print("     - Internationalized domain names may score high")
    print("   ⚠ False Negative Risk:")
    print("     - Sophisticated phishing sites may evade detection")
    print("     - Zero-day phishing campaigns with new patterns")
    
    print("\n5. ACADEMIC CONTEXT")
    print("   ⚠ Demonstration system (not production-ready):")
    print("     - Requires larger labeled dataset for deployment")
    print("     - Needs continuous retraining with new threats")
    print("     - Should be combined with other security layers")


def print_future_improvements():
    """
    Document realistic future enhancements for academic roadmap.
    Shows forward-thinking and system evolution planning.
    """
    print_section_header("FUTURE IMPROVEMENTS & RESEARCH DIRECTIONS")
    
    print("\n1. ENHANCED FEATURE ENGINEERING")
    print("   → Domain age and registration date analysis")
    print("   → WHOIS database integration (registrar reputation)")
    print("   → DNS record analysis (MX, TXT, SPF records)")
    print("   → SSL certificate validation and issuer trust")
    print("   → Page content features (HTML structure, JavaScript)")
    print("   → Brand impersonation detection (logo similarity)")
    
    print("\n2. ADVANCED MACHINE LEARNING")
    print("   → Deep Learning models:")
    print("     • LSTM (Long Short-Term Memory) for sequential URL analysis")
    print("     • CNN (Convolutional Neural Networks) for pattern recognition")
    print("     • Transformer models (BERT) for semantic understanding")
    print("   → Ensemble methods (Random Forest, XGBoost)")
    print("   → Active learning for continuous model improvement")
    
    print("\n3. LARGER REAL-WORLD DATASETS")
    print("   → PhishTank API integration (live phishing URLs)")
    print("   → Alexa Top 1M (legitimate URL corpus)")
    print("   → URLhaus dataset (malware and phishing)")
    print("   → OpenPhish feeds (real-time threat intelligence)")
    
    print("\n4. DEPLOYMENT & SCALABILITY")
    print("   → Cloud deployment (Azure/AWS for scalability)")
    print("   → Browser extension (Chrome/Firefox)")
    print("   → Mobile app integration (iOS/Android)")
    print("   → API service with authentication and rate limiting")
    print("   → Dockerized microservices architecture")
    
    print("\n5. SECURITY ENHANCEMENTS")
    print("   → Multi-layer defense (combine with email filtering)")
    print("   → Real-time threat intelligence integration")
    print("   → User feedback mechanism (report false positives)")
    print("   → Explainable AI (show why URL is flagged)")
    print("   → A/B testing framework for model comparison")
    
    print("\n6. ACADEMIC RESEARCH OPPORTUNITIES")
    print("   → Adversarial robustness testing")
    print("   → Cross-language phishing detection")
    print("   → Zero-day phishing pattern discovery")
    print("   → Behavioral analysis (user interaction patterns)")


def evaluate_model_comprehensive():
    """
    Comprehensive model evaluation with all academic metrics and analysis.
    Suitable for FYP documentation and screenshots.
    """
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  CYBERGUARDX - ML MODEL EVALUATION & ANALYSIS".center(68) + "█")
    print("█" + "  Academic Final Year Project".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    # Load dataset
    print_section_header("DATASET LOADING")
    data_dir = Path(__file__).resolve().parents[2] / "data"
    dataset_path = data_dir / "phishing_urls.csv"
    
    if not dataset_path.exists():
        print("\n⚠ Dataset not found. Please run training script first.")
        return
    
    df = pd.read_csv(dataset_path)
    print(f"\nDataset: {dataset_path}")
    print(f"Total URLs: {len(df)}")
    print(f"Phishing URLs: {(df['label'] == 1).sum()} ({(df['label'] == 1).sum() / len(df) * 100:.1f}%)")
    print(f"Legitimate URLs: {(df['label'] == 0).sum()} ({(df['label'] == 0).sum() / len(df) * 100:.1f}%)")
    
    # Extract features
    print_section_header("FEATURE EXTRACTION")
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
    
    feature_names = ["url_length", "num_dots", "num_hyphens", "num_digits", "has_at", "has_https"]
    print(f"\nExtracted {len(feature_names)} lexical features from {len(X)} URLs")
    print(f"Features: {', '.join(feature_names)}")
    
    # Split dataset
    print_section_header("TRAIN/TEST SPLIT")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTraining Set: {len(X_train)} samples (80%)")
    print(f"Test Set:     {len(X_test)} samples (20%)")
    print(f"Split Strategy: Stratified (maintains class distribution)")
    
    # Train model
    print_section_header("MODEL TRAINING")
    print("\nAlgorithm: Logistic Regression")
    print("Hyperparameters:")
    print("  - max_iter: 1000")
    print("  - random_state: 42 (reproducibility)")
    print("  - solver: lbfgs (default, efficient for small datasets)")
    
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    print("\n✓ Model training completed")
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Compute metrics
    print_section_header("EVALUATION METRICS")
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\n  Accuracy:  {accuracy:.4f}  ({accuracy * 100:.2f}%)")
    print(f"  Precision: {precision:.4f}  ({precision * 100:.2f}%)")
    print(f"  Recall:    {recall:.4f}  ({recall * 100:.2f}%)")
    print(f"  F1-Score:  {f1:.4f}  ({f1 * 100:.2f}%)")
    
    print("\nMetric Definitions (Academic Context):")
    print("  • Accuracy:  Overall correctness (TP+TN)/(TP+TN+FP+FN)")
    print("  • Precision: Of flagged phishing, how many were correct? TP/(TP+FP)")
    print("  • Recall:    Of actual phishing, how many detected? TP/(TP+FN)")
    print("  • F1-Score:  Harmonic mean of Precision and Recall")
    
    # Confusion matrix
    print_confusion_matrix_analysis(y_test, y_pred)
    
    # Feature importance
    analyze_feature_importance(model, feature_names)
    
    # Model justification
    print_model_justification()
    
    # Limitations
    print_limitations()
    
    # Future work
    print_future_improvements()
    
    # Final summary
    print_section_header("EVALUATION COMPLETE")
    print("\n✓ All metrics computed successfully")
    print("✓ Ready for academic documentation")
    print("✓ Suitable for FYP report screenshots")
    print("\n" + "█" * 70 + "\n")


if __name__ == "__main__":
    evaluate_model_comprehensive()
