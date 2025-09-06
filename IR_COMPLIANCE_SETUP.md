# IR Compliance Setup Instructions

This guide explains how to set up automated IR (Injured Reserve) slot compliance checking for your Yahoo Fantasy Football league.

## Overview

The IR compliance system:
- ✅ Checks all teams' IR slots daily
- ✅ Identifies players who no longer qualify for IR designation
- ✅ Sends email reports to the commissioner
- ✅ Runs automatically via GitHub Actions
- ✅ Saves detailed compliance reports

## Quick Setup

### 1. Configure Environment Variables

Add these variables to your `.env` file or GitHub repository secrets:

#### Required for IR Compliance:
```bash
# Email Configuration (Required for notifications)
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-app-password  # Use Gmail App Password
COMMISSIONER_EMAIL=commissioner@email.com

# Optional Email Settings
SMTP_SERVER=smtp.gmail.com  # Default: smtp.gmail.com
SMTP_PORT=587               # Default: 587
```

#### Optional IR Configuration:
```bash
# Customize IR eligible statuses (default: IR,O,PUP,NFI,SUSP,NA)
IR_ELIGIBLE_STATUSES=IR,O,PUP,NFI

# Always send report even if no violations (default: false)
ALWAYS_SEND_IR_REPORT=true
```

### 2. Set Up Gmail App Password

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification**
3. Scroll down to **App passwords**
4. Generate a new app password for "Fantasy Football"
5. Use this password (not your regular Gmail password) for `SENDER_PASSWORD`

### 3. GitHub Repository Secrets

Add these secrets to your GitHub repository:

**Required Secrets:**
- `SENDER_EMAIL` - Your Gmail address
- `SENDER_PASSWORD` - Your Gmail app password
- `COMMISSIONER_EMAIL` - Commissioner's email address

**Optional Secrets:**
- `SMTP_SERVER` - Custom SMTP server (default: smtp.gmail.com)
- `SMTP_PORT` - Custom SMTP port (default: 587)
- `IR_ELIGIBLE_STATUSES` - Custom eligible statuses (default: IR,O,PUP,NFI,SUSP,NA)
- `ALWAYS_SEND_IR_REPORT` - Send email even without violations (default: false)

### 4. Enable GitHub Action

The IR compliance check will run automatically daily at 9 AM EST. You can also trigger it manually:

1. Go to **Actions** tab in your repository
2. Select **IR Compliance Check** workflow
3. Click **Run workflow** button

## Usage

### Manual Testing

Test your IR compliance setup locally:

```bash
# Check email configuration
python scripts/email_notifier.py --config-check

# Send test email
python scripts/email_notifier.py --test

# Run IR compliance check (no email)
python scripts/check_ir_compliance.py --no-email

# Run IR compliance check with email
python scripts/check_ir_compliance.py

# Dry run (see what email would be sent)
python scripts/check_ir_compliance.py --dry-run

# Force email even if no violations
python scripts/check_ir_compliance.py --force-email
```

### Manual GitHub Action Trigger

You can manually trigger the IR compliance check:

1. Go to **Actions** → **IR Compliance Check**
2. Click **Run workflow**
3. Optional parameters:
   - **Week**: Specific week to check (leave empty for current)
   - **Force email**: Send email even if no violations
   - **Dry run**: Check without sending emails

## IR Slot Rules

### Default Eligible Statuses
Players with these statuses can be placed in IR slots:
- **IR**: Injured Reserve
- **O**: Out
- **PUP**: Physically Unable to Perform
- **NFI**: Non-Football Injury
- **SUSP**: Suspended (configurable)
- **NA**: Not Active

### Ineligible Statuses
Players with these statuses should NOT be in IR slots:
- **Q**: Questionable
- **D**: Doubtful
- **P**: Probable
- **Active**: Healthy/Active

### Customizing Rules

To customize which statuses are eligible for IR slots, set the `IR_ELIGIBLE_STATUSES` environment variable:

```bash
# Example: Only allow IR and Out players
IR_ELIGIBLE_STATUSES=IR,O

# Example: Include suspended players
IR_ELIGIBLE_STATUSES=IR,O,PUP,NFI,SUSP,NA
```

## Email Reports

### Violation Report Example
```
Subject: ⚠️ IR Compliance Violations - Week 5: 2 Violation(s) Found

**Fantasy Football IR Compliance Report - Week 5**

⚠️ **VIOLATIONS DETECTED** - Immediate attention required!

**Summary:**
- Total Teams Checked: 12
- Teams with Violations: 2
- Total Violations: 2

**VIOLATIONS DETAILS:**

**Team Alpha (Manager: John)**
Violations: 1

  • Christian McCaffrey
    - Current Status: Q
    - Issue: Player Christian McCaffrey has status 'Q' which is not eligible for IR slot

**Team Beta (Manager: Sarah)**  
Violations: 1

  • Saquon Barkley
    - Current Status: D
    - Issue: Player Saquon Barkley has status 'D' which is not eligible for IR slot
```

### Compliance Report Example
```
Subject: ✅ IR Compliance Check - Week 5: All Teams Compliant

**Fantasy Football IR Compliance Report - Week 5**

🎉 **GREAT NEWS!** All teams are in compliance with IR slot rules.

**Summary:**
- Total Teams Checked: 12
- Teams in Compliance: 12
- Violations Found: 0
```

## Troubleshooting

### Common Issues

**Email not sending:**
1. Verify Gmail App Password is correct
2. Check that 2-Factor Authentication is enabled on Gmail
3. Confirm `SENDER_EMAIL` and `COMMISSIONER_EMAIL` are valid
4. Test with: `python scripts/email_notifier.py --test`

**No violations detected but should be:**
1. Check `IR_ELIGIBLE_STATUSES` configuration
2. Verify Yahoo API is returning correct player statuses
3. Test with: `python scripts/check_ir_compliance.py --no-email`

**GitHub Action failing:**
1. Verify all required secrets are set in repository
2. Check Yahoo API credentials are still valid
3. Review Action logs for specific error messages

### Debug Commands

```bash
# Check email configuration
python scripts/email_notifier.py --config-check

# Test Yahoo API connection
python scripts/yahoo_client.py

# Run IR check with detailed output
python scripts/ir_compliance_checker.py --email-report

# View saved reports
ls -la data/ir_compliance_*.json
```

## Schedule

The IR compliance check runs:
- **Automatically**: Daily at 9 AM EST via GitHub Actions
- **Manually**: Anytime via GitHub Actions or command line
- **Reports**: Saved to `data/` directory with timestamps

## Security Notes

- Gmail App Passwords are more secure than regular passwords
- Environment variables keep credentials secure
- Email addresses are only used for compliance notifications
- No sensitive data is stored in compliance reports

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review GitHub Action logs
3. Test components individually using debug commands
4. Verify all environment variables are set correctly
