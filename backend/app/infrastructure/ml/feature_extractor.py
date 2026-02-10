"""
Infrastructure — ML Feature Extractor
=======================================
Extracts 10 lexical features from URLs for the phishing detection model.

Features:
    1. url_length         — Total character count
    2. num_dots           — Count of '.' characters
    3. num_hyphens        — Count of '-' characters
    4. num_digits         — Count of numeric digits
    5. has_at             — Presence of '@' symbol (binary)
    6. has_https          — URL uses HTTPS protocol (binary)
    7. domain_age         — Simulated trusted-domain check (binary)
    8. ssl_valid          — HTTPS + trusted domain combo (binary)
    9. path_length        — Length of URL path after domain
    10. special_char_ratio — Ratio of non-alphanumeric characters
"""

from urllib.parse import urlparse
import re


# Trusted old domains (simulated domain age check)
OLD_TRUSTED_DOMAINS = {
    'google.com', 'facebook.com', 'amazon.com', 'microsoft.com', 'apple.com',
    'wikipedia.org', 'github.com', 'stackoverflow.com', 'linkedin.com', 'twitter.com',
    'instagram.com', 'youtube.com', 'reddit.com', 'ebay.com', 'netflix.com',
    'paypal.com', 'adobe.com', 'dropbox.com', 'yahoo.com', 'bing.com'
}


def extract_url_features(url: str) -> dict:
    """
    Extract lexical features from URL for phishing detection.
    
    Enhanced Features (10 total):
        Original (6):
        - url_length: Total character count
        - num_dots: Count of '.' characters
        - num_hyphens: Count of '-' characters
        - num_digits: Count of numeric digits
        - has_at: Presence of '@' symbol (binary)
        - has_https: URL uses HTTPS protocol (binary)
        
        New (4):
        - domain_age: Simulated domain age check (1=old/trusted, 0=new/suspicious)
        - ssl_valid: HTTPS with valid-looking certificate (binary)
        - path_length: Length of URL path after domain
        - special_char_ratio: Percentage of non-alphanumeric characters
    
    Args:
        url: URL string to analyze
        
    Returns:
        Dictionary of extracted features
    """
    features = {}
    
    # Original features
    features["url_length"] = len(url)
    features["num_dots"] = url.count(".")
    features["num_hyphens"] = url.count("-")
    features["num_digits"] = sum(c.isdigit() for c in url)
    features["has_at"] = int("@" in url)
    
    try:
        parsed = urlparse(url)
        features["has_https"] = int(parsed.scheme == "https")
        
        # NEW FEATURE 1: Domain Age (simulated)
        domain = parsed.netloc.lower()
        # Remove www prefix if present
        domain = domain.replace('www.', '')
        features["domain_age"] = int(domain in OLD_TRUSTED_DOMAINS)
        
        # NEW FEATURE 2: SSL Valid (HTTPS + trusted domain combination)
        features["ssl_valid"] = int(features["has_https"] == 1 and features["domain_age"] == 1)
        
        # NEW FEATURE 3: Path Length
        path = parsed.path
        features["path_length"] = len(path)
        
        # NEW FEATURE 4: Special Character Ratio
        # Count non-alphanumeric characters (excluding common valid chars like /, ., -, _)
        special_chars = re.findall(r'[^a-zA-Z0-9/.\-_:]', url)
        features["special_char_ratio"] = len(special_chars) / len(url) if len(url) > 0 else 0
        
    except Exception:
        features["has_https"] = 0
        features["domain_age"] = 0
        features["ssl_valid"] = 0
        features["path_length"] = 0
        features["special_char_ratio"] = 0
    
    return features


def features_to_array(features: dict) -> list:
    """
    Convert feature dictionary to ordered array for model input.
    
    Args:
        features: Dictionary from extract_url_features
        
    Returns:
        List of feature values in consistent order (10 features)
    """
    return [
        features["url_length"],
        features["num_dots"],
        features["num_hyphens"],
        features["num_digits"],
        features["has_at"],
        features["has_https"],
        features["domain_age"],        # NEW
        features["ssl_valid"],         # NEW
        features["path_length"],       # NEW
        features["special_char_ratio"], # NEW
    ]


def get_feature_names() -> list:
    """Get ordered list of feature names."""
    return [
        "url_length",
        "num_dots",
        "num_hyphens",
        "num_digits",
        "has_at",
        "has_https",
        "domain_age",
        "ssl_valid",
        "path_length",
        "special_char_ratio"
    ]


def explain_features(features: dict) -> dict:
    """
    Provide human-readable explanations for features.
    
    Args:
        features: Feature dictionary
        
    Returns:
        Dictionary with feature explanations
    """
    explanations = {}
    
    # URL Length
    if features["url_length"] > 75:
        explanations["url_length"] = {
            "value": features["url_length"],
            "risk": "HIGH",
            "explanation": "Unusually long URL - common in phishing to hide malicious intent"
        }
    elif features["url_length"] > 54:
        explanations["url_length"] = {
            "value": features["url_length"],
            "risk": "MEDIUM",
            "explanation": "Longer than average URL - slightly suspicious"
        }
    else:
        explanations["url_length"] = {
            "value": features["url_length"],
            "risk": "LOW",
            "explanation": "Normal URL length"
        }
    
    # Hyphens
    if features["num_hyphens"] >= 3:
        explanations["num_hyphens"] = {
            "value": features["num_hyphens"],
            "risk": "HIGH",
            "explanation": "Multiple hyphens in domain - common phishing technique"
        }
    elif features["num_hyphens"] >= 1:
        explanations["num_hyphens"] = {
            "value": features["num_hyphens"],
            "risk": "MEDIUM",
            "explanation": "Hyphen present - monitor for brand impersonation"
        }
    
    # @ Symbol
    if features["has_at"] == 1:
        explanations["has_at"] = {
            "value": features["has_at"],
            "risk": "CRITICAL",
            "explanation": "Contains @ symbol - often used to trick users about actual domain"
        }
    
    # HTTPS
    if features["has_https"] == 0:
        explanations["has_https"] = {
            "value": features["has_https"],
            "risk": "HIGH",
            "explanation": "No HTTPS encryption - data transmitted insecurely"
        }
    
    # Domain Age
    if features["domain_age"] == 0:
        explanations["domain_age"] = {
            "value": features["domain_age"],
            "risk": "HIGH",
            "explanation": "New or unknown domain - not in trusted domains list"
        }
    else:
        explanations["domain_age"] = {
            "value": features["domain_age"],
            "risk": "LOW",
            "explanation": "Established trusted domain"
        }
    
    # SSL Valid
    if features["ssl_valid"] == 0:
        explanations["ssl_valid"] = {
            "value": features["ssl_valid"],
            "risk": "HIGH",
            "explanation": "No valid SSL certificate detected"
        }
    
    # Path Length
    if features["path_length"] > 100:
        explanations["path_length"] = {
            "value": features["path_length"],
            "risk": "MEDIUM",
            "explanation": "Unusually long URL path - may be attempting obfuscation"
        }
    
    # Special Characters
    if features["special_char_ratio"] > 0.15:
        explanations["special_char_ratio"] = {
            "value": features["special_char_ratio"],
            "risk": "HIGH",
            "explanation": f"High special character ratio ({features['special_char_ratio']:.1%}) - possible obfuscation"
        }
    
    return explanations
