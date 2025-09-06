"""
Secure Notification Methods
Alternative notification methods that don't require storing email credentials
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SlackNotifier:
    """Send notifications via Slack webhook - much more secure"""
    
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.channel = os.getenv('SLACK_CHANNEL', '#fantasy-football')
        
    def is_configured(self) -> bool:
        return bool(self.webhook_url)
    
    def send_ir_compliance_report(self, subject: str, body: str) -> bool:
        """Send IR compliance report to Slack"""
        if not self.is_configured():
            logger.error("Slack webhook not configured")
            return False
        
        try:
            # Format for Slack
            message = {
                "channel": self.channel,
                "username": "IR Compliance Bot",
                "icon_emoji": ":football:",
                "attachments": [
                    {
                        "color": "danger" if "Violations" in subject else "good",
                        "title": subject,
                        "text": body,
                        "footer": "Fantasy Football IR Compliance System",
                        "ts": int(os.times()[4])  # timestamp
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("IR compliance report sent to Slack successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False


class DiscordNotifier:
    """Send notifications via Discord webhook - secure alternative"""
    
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
    def is_configured(self) -> bool:
        return bool(self.webhook_url)
    
    def send_ir_compliance_report(self, subject: str, body: str) -> bool:
        """Send IR compliance report to Discord"""
        if not self.is_configured():
            logger.error("Discord webhook not configured")
            return False
        
        try:
            # Format for Discord
            color = 0xFF0000 if "Violations" in subject else 0x00FF00  # Red or Green
            
            message = {
                "username": "IR Compliance Bot",
                "avatar_url": "https://static.clubs.nfl.com/image/private/t_editorial_landscape_8_desktop_mobile/f_auto/nfl/ahsylvrbibqb6agywzr3",
                "embeds": [
                    {
                        "title": subject,
                        "description": body[:2000],  # Discord limit
                        "color": color,
                        "footer": {
                            "text": "Fantasy Football IR Compliance System"
                        }
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("IR compliance report sent to Discord successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False


class GitHubIssueNotifier:
    """Create GitHub issues for violations - uses existing repo access"""
    
    def __init__(self):
        self.repo = os.getenv('GITHUB_REPOSITORY')  # Set automatically in Actions
        self.token = os.getenv('GITHUB_TOKEN')      # Set automatically in Actions
        
    def is_configured(self) -> bool:
        return bool(self.repo and self.token)
    
    def send_ir_compliance_report(self, subject: str, body: str) -> bool:
        """Create GitHub issue for IR violations"""
        if not self.is_configured():
            logger.error("GitHub issue creation not configured")
            return False
        
        # Only create issues for violations (configurable)
        create_for_all = os.getenv('IR_ISSUES_FOR_ALL_REPORTS', 'false').lower() == 'true'
        
        if "Violations" not in subject and not create_for_all:
            logger.info("No violations found, skipping GitHub issue creation")
            return True
        
        try:
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Format body with better GitHub markdown
            formatted_body = self._format_issue_body(subject, body)
            
            issue_data = {
                'title': subject,
                'body': formatted_body,
                'labels': ['ir-violation', 'commissioner-action-required', 'automated']
            }
            
            # Add assignee if configured
            assignee = os.getenv('IR_ISSUE_ASSIGNEE')
            if assignee:
                issue_data['assignee'] = assignee
            
            url = f"https://api.github.com/repos/{self.repo}/issues"
            response = requests.post(url, json=issue_data, headers=headers, timeout=10)
            response.raise_for_status()
            
            issue_number = response.json()['number']
            logger.info(f"Created GitHub issue #{issue_number} for IR violations")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create GitHub issue: {e}")
            return False
    
    def _format_issue_body(self, subject: str, body: str) -> str:
        """Format the issue body with proper GitHub markdown"""
        
        # Extract week and violation count from subject
        import re
        week_match = re.search(r'Week (\d+)', subject)
        count_match = re.search(r'(\d+) Violation\(s\)', subject)
        
        week = week_match.group(1) if week_match else "Unknown"
        count = count_match.group(1) if count_match else "Unknown"
        
        # Format with GitHub issue template structure
        formatted = f"""## 🚨 IR Compliance Violation Report

**This issue was automatically created by the IR compliance monitoring system.**

### 📊 Summary
- **Week:** {week}
- **Total Violations:** {count}
- **Date Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

### ⚠️ Violations Detected

{body}

### ✅ Required Actions

- [ ] Contact affected team managers
- [ ] Verify player status changes  
- [ ] Ensure IR slot compliance
- [ ] Follow up on corrections
- [ ] Close this issue once resolved

### 📋 IR Eligible Statuses
Players with these statuses may be placed in IR slots:
- **IR** - Injured Reserve
- **O** - Out  
- **PUP** - Physically Unable to Perform
- **NFI** - Non-Football Injury
- **SUSP** - Suspended (if allowed by league rules)
- **NA** - Not Active

### 🔄 Next Steps
1. Review the violations listed above
2. Contact the team managers to correct their lineups  
3. Set a deadline for compliance
4. Close this issue once violations are resolved

---
*This issue will be automatically resolved when no violations are detected in subsequent checks.*"""

        return formatted


class SendGridNotifier:
    """Use SendGrid API - more secure than direct email credentials"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@yourleague.com')
        self.to_email = os.getenv('COMMISSIONER_EMAIL')
        
    def is_configured(self) -> bool:
        return bool(self.api_key and self.to_email)
    
    def send_ir_compliance_report(self, subject: str, body: str) -> bool:
        """Send email via SendGrid API"""
        if not self.is_configured():
            logger.error("SendGrid not configured")
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'personalizations': [
                    {
                        'to': [{'email': self.to_email}],
                        'subject': subject
                    }
                ],
                'from': {'email': self.from_email},
                'content': [
                    {
                        'type': 'text/plain',
                        'value': body
                    }
                ]
            }
            
            response = requests.post(
                'https://api.sendgrid.com/v3/mail/send',
                json=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("IR compliance report sent via SendGrid successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SendGrid email: {e}")
            return False


class FileNotifier:
    """Save reports to files - simplest and most secure"""
    
    def __init__(self):
        self.output_dir = os.getenv('NOTIFICATION_OUTPUT_DIR', 'notifications')
        self.commit_files = os.getenv('FILE_NOTIFICATIONS_COMMIT', 'true').lower() == 'true'
        
    def is_configured(self) -> bool:
        return True  # Always available
    
    def send_ir_compliance_report(self, subject: str, body: str) -> bool:
        """Save notification to file"""
        try:
            from pathlib import Path
            from datetime import datetime
            
            output_path = Path(self.output_dir)
            output_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ir_notification_{timestamp}.txt"
            filepath = output_path / filename
            
            content = f"Subject: {subject}\n\n{body}"
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            logger.info(f"IR compliance notification saved to {filepath}")
            print(f"📄 Notification saved to: {filepath}")
            
            if not self.commit_files:
                print(f"📝 File commit disabled - notification saved locally only")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save notification file: {e}")
            return False


def get_secure_notifier():
    """Get the best available secure notifier"""
    
    # Try in order of preference (most secure first)
    notifiers = [
        ('Slack', SlackNotifier()),
        ('Discord', DiscordNotifier()),
        ('GitHub Issues', GitHubIssueNotifier()),
        ('SendGrid', SendGridNotifier()),
        ('File', FileNotifier())  # Always available fallback
    ]
    
    for name, notifier in notifiers:
        if notifier.is_configured():
            logger.info(f"Using {name} notifier")
            return notifier
    
    # Fallback to file notifier
    logger.warning("No secure notifiers configured, using file notifier")
    return FileNotifier()


def main():
    """Test secure notifiers"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test secure notification methods')
    parser.add_argument('--test-all', action='store_true', help='Test all configured notifiers')
    parser.add_argument('--check-config', action='store_true', help='Check notification configuration')
    
    args = parser.parse_args()
    
    if args.check_config:
        print("Secure Notification Configuration")
        print("=" * 40)
        
        notifiers = [
            ('Slack', SlackNotifier()),
            ('Discord', DiscordNotifier()),
            ('GitHub Issues', GitHubIssueNotifier()),
            ('SendGrid', SendGridNotifier()),
            ('File', FileNotifier())
        ]
        
        for name, notifier in notifiers:
            status = "✅ Configured" if notifier.is_configured() else "❌ Not configured"
            print(f"{name}: {status}")
        
        print(f"\nRecommended: Use Slack or Discord webhooks for best security")
        print(f"Current choice: {type(get_secure_notifier()).__name__}")
    
    if args.test_all:
        subject = "🧪 Test IR Compliance Notification"
        body = "This is a test notification from the secure IR compliance system."
        
        notifier = get_secure_notifier()
        success = notifier.send_ir_compliance_report(subject, body)
        
        if success:
            print("✅ Test notification sent successfully!")
        else:
            print("❌ Failed to send test notification")
    
    if not args.check_config and not args.test_all:
        parser.print_help()


if __name__ == "__main__":
    main()
