"""
Email Notifier
Handles sending email notifications for IR compliance reports
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Handles email notifications for league commissioners"""
    
    def __init__(self):
        """Initialize email notifier with configuration from environment variables"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.commissioner_email = os.getenv('COMMISSIONER_EMAIL')
        
        # Validate required configuration
        if not all([self.sender_email, self.sender_password, self.commissioner_email]):
            missing = []
            if not self.sender_email:
                missing.append('SENDER_EMAIL')
            if not self.sender_password:
                missing.append('SENDER_PASSWORD')
            if not self.commissioner_email:
                missing.append('COMMISSIONER_EMAIL')
            
            logger.warning(f"Email configuration incomplete. Missing: {', '.join(missing)}")
            logger.info("Email notifications will be disabled. Set the missing environment variables to enable.")
    
    def is_configured(self) -> bool:
        """Check if email notification is properly configured"""
        return all([self.sender_email, self.sender_password, self.commissioner_email])
    
    def send_ir_compliance_report(self, subject: str, body: str, 
                                 additional_recipients: Optional[List[str]] = None) -> bool:
        """Send IR compliance report via email
        
        Args:
            subject: Email subject line
            body: Email body content
            additional_recipients: Optional list of additional email addresses
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.error("Email not configured. Cannot send notification.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['Subject'] = subject
            
            # Set recipients
            recipients = [self.commissioner_email]
            if additional_recipients:
                recipients.extend(additional_recipients)
            
            msg['To'] = ', '.join(recipients)
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable encryption
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg, to_addrs=recipients)
            
            logger.info(f"IR compliance report sent successfully to {len(recipients)} recipient(s)")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Email authentication failed: {e}")
            logger.info("Please check your SENDER_EMAIL and SENDER_PASSWORD environment variables")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """Send a test email to verify configuration
        
        Returns:
            True if test email sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.error("Email not configured. Cannot send test email.")
            return False
        
        subject = "🏈 Fantasy Football IR Compliance - Test Email"
        body = """
This is a test email from your Fantasy Football IR Compliance system.

If you're receiving this email, the notification system is working correctly!

Configuration Details:
- SMTP Server: {smtp_server}:{smtp_port}
- Sender Email: {sender_email}
- Commissioner Email: {commissioner_email}

The system will send daily reports about IR slot compliance in your league.

--
Fantasy Football IR Compliance System
""".format(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            sender_email=self.sender_email,
            commissioner_email=self.commissioner_email
        )
        
        return self.send_ir_compliance_report(subject, body)


def get_commissioner_email_from_yahoo(yahoo_client) -> Optional[str]:
    """Attempt to get commissioner email from Yahoo API
    
    Args:
        yahoo_client: Configured Yahoo Fantasy client
        
    Returns:
        Commissioner email if available, None otherwise
    """
    try:
        # This is a placeholder - the Yahoo API may not expose email addresses
        # due to privacy restrictions. Most likely this will not work and you'll
        # need to use the environment variable approach.
        logger.info("Attempting to retrieve commissioner email from Yahoo API...")
        
        # Try to get league info and look for commissioner details
        league_info = yahoo_client.get_league_info()
        teams = yahoo_client.get_teams()
        
        # Look for commissioner/admin designation
        # Note: This may not be available through the public API
        for team in teams:
            # Check if team has commissioner flag (this is speculative)
            if hasattr(team, 'is_commissioner') and team.is_commissioner:
                # Email addresses are typically not exposed by Yahoo API for privacy
                logger.warning("Commissioner found but email not available through Yahoo API")
                return None
        
        logger.info("Commissioner email not available through Yahoo API")
        return None
        
    except Exception as e:
        logger.warning(f"Could not retrieve commissioner email from Yahoo API: {e}")
        return None


def main():
    """Test email configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test email notification configuration')
    parser.add_argument('--test', action='store_true', help='Send test email')
    parser.add_argument('--config-check', action='store_true', help='Check email configuration')
    
    args = parser.parse_args()
    
    notifier = EmailNotifier()
    
    if args.config_check:
        print("Email Configuration Check")
        print("=" * 30)
        print(f"SMTP Server: {notifier.smtp_server}:{notifier.smtp_port}")
        print(f"Sender Email: {notifier.sender_email or 'NOT SET'}")
        print(f"Sender Password: {'SET' if notifier.sender_password else 'NOT SET'}")
        print(f"Commissioner Email: {notifier.commissioner_email or 'NOT SET'}")
        print(f"Configured: {'✅ YES' if notifier.is_configured() else '❌ NO'}")
        
        if not notifier.is_configured():
            print("\nTo configure email notifications, set these environment variables:")
            if not notifier.sender_email:
                print("- SENDER_EMAIL=your-gmail@gmail.com")
            if not notifier.sender_password:
                print("- SENDER_PASSWORD=your-app-password")
            if not notifier.commissioner_email:
                print("- COMMISSIONER_EMAIL=commissioner@email.com")
            print("\nFor Gmail, use an App Password instead of your regular password:")
            print("https://support.google.com/accounts/answer/185833")
    
    if args.test:
        if notifier.is_configured():
            print("Sending test email...")
            success = notifier.send_test_email()
            if success:
                print("✅ Test email sent successfully!")
            else:
                print("❌ Failed to send test email. Check logs for details.")
        else:
            print("❌ Email not configured. Use --config-check to see what's missing.")
    
    if not args.test and not args.config_check:
        parser.print_help()


if __name__ == "__main__":
    main()
