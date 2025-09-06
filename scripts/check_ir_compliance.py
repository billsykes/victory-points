"""
Check IR Compliance - Main Script
Performs daily IR compliance checks and sends email notifications
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent))

from yahoo_client import YahooFantasyClient
from ir_compliance_checker import IRComplianceChecker
from email_notifier import EmailNotifier
from secure_notifiers import get_secure_notifier
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function for IR compliance checking"""
    parser = argparse.ArgumentParser(description='Check IR slot compliance and send notifications')
    parser.add_argument('--week', type=int, help='Week number to check (default: current week)')
    parser.add_argument('--output-dir', type=str, default='data', help='Output directory for reports')
    parser.add_argument('--no-email', action='store_true', help='Skip sending email notification')
    parser.add_argument('--dry-run', action='store_true', help='Perform check without sending emails')
    parser.add_argument('--force-email', action='store_true', help='Send email even if no violations found')
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting IR compliance check...")
        
        # Initialize Yahoo client
        logger.info("Initializing Yahoo Fantasy client...")
        yahoo_client = YahooFantasyClient()
        
        # Get league info for context
        league_info = yahoo_client.get_league_info()
        logger.info(f"Connected to league: {league_info['name']} (Season {league_info['season']})")
        
        # Initialize compliance checker
        checker = IRComplianceChecker(yahoo_client)
        
        # Run compliance check
        logger.info("Running IR compliance check...")
        compliance_report = checker.check_all_teams(args.week)
        
        # Save report
        report_path = checker.save_report(compliance_report, args.output_dir)
        logger.info(f"Report saved to: {report_path}")
        
        # Print summary to console
        week = compliance_report['week']
        total_violations = compliance_report['summary']['total_violations']
        teams_with_violations = compliance_report['summary']['teams_with_violations']
        
        print(f"\n{'='*60}")
        print(f"IR COMPLIANCE CHECK RESULTS - Week {week}")
        print(f"League: {league_info['name']}")
        print(f"{'='*60}")
        print(f"Total Teams Checked: {compliance_report['summary']['total_teams']}")
        print(f"Violations Found: {total_violations}")
        print(f"Teams with Violations: {teams_with_violations}")
        print(f"Compliant Teams: {compliance_report['summary']['compliant_teams']}")
        
        if compliance_report['violations']:
            print(f"\n⚠️ VIOLATIONS DETECTED:")
            for team_violation in compliance_report['violations']:
                print(f"\n{team_violation['team_name']} ({team_violation['manager']}):")
                for violation in team_violation['violations']:
                    print(f"  • {violation['player_name']} - Status: {violation['current_status']}")
                    if violation.get('injury_note'):
                        print(f"    Note: {violation['injury_note']}")
        else:
            print(f"\n✅ All teams are in compliance with IR slot rules!")
        
        # Handle notifications (secure methods preferred)
        if not args.no_email and not args.dry_run:
            # Try secure notifier first
            secure_notifier = get_secure_notifier()
            
            # Determine if we should send notification
            should_send_notification = (
                total_violations > 0 or  # Always send if violations found
                args.force_email or     # Force send if requested
                os.getenv('ALWAYS_SEND_IR_REPORT', 'false').lower() == 'true'  # Environment setting
            )
            
            if should_send_notification:
                logger.info("Preparing notification...")
                subject, body = checker.generate_email_report(compliance_report)
                
                # Add league context
                body = f"**League:** {league_info['name']} (Season {league_info['season']})\n\n" + body
                
                success = secure_notifier.send_ir_compliance_report(subject, body)
                
                if success:
                    notifier_type = type(secure_notifier).__name__
                    print(f"\n📨 Notification sent successfully via {notifier_type}!")
                    logger.info(f"Notification sent via {notifier_type}")
                else:
                    print(f"\n❌ Failed to send notification")
                    logger.error("Failed to send notification")
                    
                    # Fallback to email if configured
                    email_notifier = EmailNotifier()
                    if email_notifier.is_configured():
                        print("🔄 Trying email fallback...")
                        email_success = email_notifier.send_ir_compliance_report(subject, body)
                        if email_success:
                            print("📧 Email notification sent as fallback")
                        else:
                            print("❌ Email fallback also failed")
                            return 1
                    else:
                        return 1
            else:
                print(f"\n📨 No notification sent (no violations found and not forced)")
                logger.info("No notification sent - no violations found")
        elif args.dry_run:
            print(f"\n🔍 DRY RUN: Email would be sent with the following content:")
            subject, body = checker.generate_email_report(compliance_report)
            print(f"\nSubject: {subject}")
            print(f"\nBody:\n{body}")
        else:
            print(f"\n📧 Email notification skipped (--no-email)")
        
        # Return appropriate exit code
        return 0 if total_violations == 0 else 1
        
    except Exception as e:
        logger.error(f"IR compliance check failed: {e}")
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
