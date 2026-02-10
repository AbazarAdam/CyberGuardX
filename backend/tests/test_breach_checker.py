"""
Test script for Enhanced Email Breach Detection
Tests all components of the hybrid breach checking system
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from app.services.breach_checker import get_breach_checker
from app.utils.hashing import hash_email
from app.utils.hibp_client import get_hibp_client

def test_breach_generator():
    """Test that breach dataset exists and is valid."""
    print("\n" + "="*60)
    print("TEST 1: Breach Dataset Validation")
    print("="*60)
    
    dataset_path = Path("data/breach_emails_enhanced.csv")
    if not dataset_path.exists():
        print("❌ FAIL: Breach dataset not found!")
        return False
    
    import pandas as pd
    df = pd.read_csv(dataset_path)
    
    print(f"✅ Dataset found: {len(df)} records")
    print(f"✅ Columns: {list(df.columns)}")
    
    required_columns = ['email_hash', 'pwned_count', 'breach_names', 'breach_dates']
    for col in required_columns:
        if col in df.columns:
            print(f"✅ Column '{col}' present")
        else:
            print(f"❌ Column '{col}' missing")
            return False
    
    return True


def test_hashing_utility():
    """Test email hashing."""
    print("\n" + "="*60)
    print("TEST 2: Email Hashing Utility")
    print("="*60)
    
    test_email = "test@example.com"
    # Get the actual hash to verify consistency
    result = hash_email(test_email)
    
    # Verify it's a valid SHA-1 hash (40 hexadecimal characters)
    if len(result) == 40 and all(c in '0123456789abcdef' for c in result):
        print(f"✅ Hash format correct: {result}")
        
        # Test consistency - same input should give same output
        result2 = hash_email(test_email)
        if result == result2:
            print(f"✅ Hash is consistent across calls")
            return True
        else:
            print(f"❌ Hash inconsistency detected")
            return False
    else:
        print(f"❌ Hash format invalid: {result}")
        return False


def test_breach_checker_service():
    """Test breach checker service with local dataset."""
    print("\n" + "="*60)
    print("TEST 3: Breach Checker Service (Local Dataset)")
    print("="*60)
    
    checker = get_breach_checker()
    
    # Test with known breached email
    test_cases = [
        ("test@example.com", True, 3),
        ("demo@cyberguardx.com", True, 5),
        ("user@test.com", True, 2),
        ("safe-email-12345@nonexistent.com", False, 0)
    ]
    
    all_passed = True
    for email, should_be_breached, expected_count in test_cases:
        result = checker.check_email_breach(email)
        
        if result["breached"] == should_be_breached:
            print(f"✅ {email}: {'BREACHED' if should_be_breached else 'SAFE'}")
            
            if should_be_breached:
                if result["pwned_count"] == expected_count:
                    print(f"   ✅ Count correct: {expected_count}")
                    print(f"   ✅ Breaches found: {len(result['breaches'])}")
                    print(f"   ✅ Risk level: {result['risk_level']}")
                    print(f"   ✅ Recommendations: {len(result['recommendations'])}")
                else:
                    print(f"   ❌ Count incorrect: expected {expected_count}, got {result['pwned_count']}")
                    all_passed = False
        else:
            print(f"❌ {email}: Expected {'breached' if should_be_breached else 'safe'}, got {'breached' if result['breached'] else 'safe'}")
            all_passed = False
    
    return all_passed


def test_hibp_client():
    """Test HIBP API client (may fail if offline - that's OK)."""
    print("\n" + "="*60)
    print("TEST 4: HIBP API Client (Optional)")
    print("="*60)
    
    client = get_hibp_client()
    
    # Test with a common breached password
    test_email = "test@example.com"
    
    try:
        result = client.check_email_pwned(test_email)
        
        print(f"✅ HIBP client functional")
        print(f"   Source: {result['source']}")
        print(f"   Pwned: {result.get('pwned', 'N/A')}")
        
        if result.get('error'):
            print(f"   ⚠️  Note: {result['error']}")
            print(f"   ℹ️  This is normal - system falls back to local dataset")
        
        return True
    except Exception as e:
        print(f"⚠️  HIBP API test failed: {e}")
        print(f"ℹ️  This is acceptable - system uses local fallback")
        return True  # Don't fail on API unavailability


def test_response_structure():
    """Test that response includes all required fields."""
    print("\n" + "="*60)
    print("TEST 5: Response Structure Validation")
    print("="*60)
    
    checker = get_breach_checker()
    result = checker.check_email_breach("test@example.com")
    
    required_fields = [
        "breached", "pwned_count", "breaches", "risk_level",
        "recommendations", "breach_source", "last_checked", "message"
    ]
    
    all_present = True
    for field in required_fields:
        if field in result:
            print(f"✅ Field '{field}' present")
        else:
            print(f"❌ Field '{field}' missing")
            all_present = False
    
    # Check breach structure
    if result["breaches"] and len(result["breaches"]) > 0:
        breach = result["breaches"][0]
        breach_fields = ["name", "date", "accounts", "data_classes"]
        
        print("\n   Breach structure validation:")
        for bfield in breach_fields:
            if bfield in breach:
                print(f"   ✅ Breach field '{bfield}' present")
            else:
                print(f"   ❌ Breach field '{bfield}' missing")
                all_present = False
    
    return all_present


def test_risk_levels():
    """Test risk level calculation."""
    print("\n" + "="*60)
    print("TEST 6: Risk Level Calculation")
    print("="*60)
    
    checker = get_breach_checker()
    
    test_cases = [
        ("security@demo.org", "MEDIUM"),  # 1 breach
        ("user@test.com", "HIGH"),        # 2 breaches
        ("test@example.com", "HIGH"),     # 3 breaches
        ("demo@cyberguardx.com", "CRITICAL")  # 5 breaches
    ]
    
    all_correct = True
    for email, expected_risk in test_cases:
        result = checker.check_email_breach(email)
        
        if result["risk_level"] == expected_risk:
            print(f"✅ {email}: {result['risk_level']} (pwned {result['pwned_count']}x)")
        else:
            print(f"❌ {email}: Expected {expected_risk}, got {result['risk_level']}")
            all_correct = False
    
    return all_correct


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("🔍 ENHANCED EMAIL BREACH DETECTION TEST SUITE")
    print("="*60)
    
    tests = [
        ("Breach Dataset", test_breach_generator),
        ("Hashing Utility", test_hashing_utility),
        ("Breach Checker Service", test_breach_checker_service),
        ("HIBP API Client", test_hibp_client),
        ("Response Structure", test_response_structure),
        ("Risk Level Calculation", test_risk_levels)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
        print("\nNext steps:")
        print("1. Start backend server: uvicorn app.main:app --reload --port 8000")
        print("2. Start frontend server: python -m http.server 3000")
        print("3. Test in browser: http://localhost:3000")
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
    
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
