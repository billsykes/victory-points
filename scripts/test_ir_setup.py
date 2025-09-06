"""
Test IR Compliance Setup
Verify that all components of the IR compliance system are working
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import yahoo_client
        print("✅ yahoo_client imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import yahoo_client: {e}")
        return False
    
    try:
        import ir_compliance_checker
        print("✅ ir_compliance_checker imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ir_compliance_checker: {e}")
        return False
    
    try:
        import email_notifier
        print("✅ email_notifier imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import email_notifier: {e}")
        return False
    
    try:
        import check_ir_compliance
        print("✅ check_ir_compliance imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import check_ir_compliance: {e}")
        return False
    
    return True


def test_yahoo_connection():
    """Test Yahoo API connection"""
    print("\nTesting Yahoo API connection...")
    
    try:
        from yahoo_client import YahooFantasyClient
        client = YahooFantasyClient()
        
        # Try to get league info
        league_info = client.get_league_info()
        print(f"✅ Connected to league: {league_info['name']}")
        print(f"   Season: {league_info['season']}")
        print(f"   Teams: {league_info['num_teams']}")
        print(f"   Current Week: {league_info['current_week']}")
        
        return True
    except Exception as e:
        print(f"❌ Yahoo API connection failed: {e}")
        return False


def test_email_config():
    """Test email configuration"""
    print("\nTesting email configuration...")
    
    try:
        from email_notifier import EmailNotifier
        notifier = EmailNotifier()
        
        if notifier.is_configured():
            print("✅ Email configuration complete")
            print(f"   SMTP: {notifier.smtp_server}:{notifier.smtp_port}")
            print(f"   Sender: {notifier.sender_email}")
            print(f"   Commissioner: {notifier.commissioner_email}")
            return True
        else:
            print("⚠️ Email configuration incomplete")
            print("   Set SENDER_EMAIL, SENDER_PASSWORD, and COMMISSIONER_EMAIL")
            return False
    except Exception as e:
        print(f"❌ Email configuration test failed: {e}")
        return False


def test_ir_checker():
    """Test IR compliance checker initialization"""
    print("\nTesting IR compliance checker...")
    
    try:
        from yahoo_client import YahooFantasyClient
        from ir_compliance_checker import IRComplianceChecker
        
        client = YahooFantasyClient()
        checker = IRComplianceChecker(client)
        
        print(f"✅ IR compliance checker initialized")
        print(f"   Eligible statuses: {checker.ir_eligible_statuses}")
        
        return True
    except Exception as e:
        print(f"❌ IR compliance checker test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🏈 IR Compliance System Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Yahoo API", test_yahoo_connection),
        ("Email Config", test_email_config),
        ("IR Checker", test_ir_checker)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n{'=' * 40}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! IR compliance system is ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Check configuration and dependencies.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
