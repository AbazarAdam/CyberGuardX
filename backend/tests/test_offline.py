"""
Quick test of the offline breach checker with SQLite database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.services.breach_checker import get_breach_checker
from app.application.services.breach_checker import hash_email


def test_breach_checker():
    """Test the breach checker service."""
    print("\n" + "="*70)
    print("🧪 TESTING OFFLINE BREACH CHECKER")
    print("="*70)
    
    checker = get_breach_checker()
    
    # Get database stats
    print("\n📊 Database Statistics:")
    stats = checker.get_database_stats()
    for key, value in stats.items():
        print(f"  • {key}: {value}")
    
    # Test emails from database
    test_emails = [
        ("test@example.com", 3),
        ("user@gmail.com", 2),
        ("admin@yahoo.com", 4),
        ("pwned@hotmail.com", 5),
        ("safe@cyberguardx.com", 0),
        ("notindb@example.com", 0)  # Should not be in DB
    ]
    
    print("\n🔍 Testing Required Emails:")
    print("-"*70)
    
    all_passed = True
    
    for email, expected_breaches in test_emails:
        result = checker.check_email_breach(email)
        
        breached = result["breached"]
        count = result["total_breaches"]
        risk = result["risk_level"]
        source = result["breach_source"]
        
        # Check if result matches expectation
        passed = (count == expected_breaches)
        status = "✅ PASS" if passed else "❌ FAIL"
        
        if not passed:
            all_passed = False
        
        print(f"\n{status} {email}")
        print(f"  Expected: {expected_breaches} breaches")
        print(f"  Got: {count} breaches")
        print(f"  Risk Level: {risk}")
        print(f"  Source: {source}")
        
        if count > 0 and len(result.get("breaches", [])) > 0:
            print(f"  Breaches found: {', '.join(b['name'] for b in result['breaches'][:3])}")
            if len(result.get("recommendations", [])) > 0:
                print(f"  First recommendation: {result['recommendations'][0]}")
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = test_breach_checker()
    sys.exit(0 if success else 1)
