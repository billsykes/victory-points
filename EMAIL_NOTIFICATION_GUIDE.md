# Email Notification Guide

## 📧 **Will File Notifications Send You Emails?**

**Short Answer:** Yes, potentially - but you have full control over this!

## 🔄 **How Email Notifications Work**

### **File Notification Flow:**
```
1. Daily IR check runs (9 AM EST)
2. Creates notification file: notifications/ir_notification_TIMESTAMP.txt
3. Commits file to repository (if enabled)
4. GitHub sends you commit notification email
```

### **When You Get Emails:**

#### **✅ You WILL get emails for:**
- 📋 **New commits** (when files are committed to repo)
- ❌ **GitHub Action failures** (if something breaks)
- 🔧 **Repository activity** (if you have notifications enabled)

#### **📝 Sample Commit Email:**
```
Subject: [your-username/victory-points] New commit by github-actions[bot]

📋 Update IR compliance reports - 2024-09-06 09:00

Files changed:
+ data/ir_compliance_week_05_20240906_090015.json
+ notifications/ir_notification_20240906_090015.txt

View commit: https://github.com/your-username/victory-points/commit/abc123
```

## 🎛️ **Control Your Email Notifications**

### **Option 1: Disable File Commits (Recommended)**
Set this in your environment or GitHub secrets:
```bash
FILE_NOTIFICATIONS_COMMIT=false
```

**Result:** 
- ✅ Files still created for violation tracking
- ✅ No commits = No commit emails
- ✅ Files available in GitHub Action logs
- ❌ No persistent storage in repository

### **Option 2: Use GitHub Issues Instead**
Configure GitHub Issues for violations only:
```bash
# Don't set any webhook URLs - system will use GitHub Issues
# Files will be created but not committed
FILE_NOTIFICATIONS_COMMIT=false
```

**Result:**
- ✅ GitHub Issues created ONLY when violations occur
- ✅ Issues email relevant people automatically
- ✅ No daily spam emails
- ✅ Proper tracking and assignment workflow

### **Option 3: Disable Repository Email Notifications**

**In GitHub:**
1. Go to your repository
2. Click **Watch** dropdown (top right)
3. Select **Custom** 
4. Uncheck **Pushes**
5. Keep **Issues** and **Pull Requests** if desired

**In Your GitHub Account:**
1. Settings → Notifications
2. Uncheck "Email" for various activities
3. Keep web/mobile notifications if desired

### **Option 4: Email Filtering**
Set up email filters for:
- `From: notifications@github.com`
- `Subject: [your-repo-name]`
- `From: github-actions[bot]`

## 🎯 **Recommended Configuration**

### **For Minimal Emails:**
```bash
# Use GitHub Issues for violations only
FILE_NOTIFICATIONS_COMMIT=false
GITHUB_ISSUES_FOR_ALL_REPORTS=false  # Only violations create issues

# Result: 
# - No daily emails
# - Issues created only when action needed
# - Files still saved for audit trail
```

### **For Slack/Discord Users:**
```bash
# Use webhook notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
FILE_NOTIFICATIONS_COMMIT=false

# Result:
# - Instant notifications in Slack/Discord
# - No email spam
# - Rich formatting and mobile alerts
```

## 📊 **Notification Comparison**

| Method | Daily Emails | Violation Alerts | Setup | Control |
|--------|--------------|------------------|--------|---------|
| **File (commit=true)** | ✅ Yes | ✅ Yes | None | GitHub settings |
| **File (commit=false)** | ❌ No | ❌ No* | None | Perfect |
| **GitHub Issues** | ❌ No | ✅ Yes | None | Built-in |
| **Slack/Discord** | ❌ No | ✅ Yes | Easy | Webhook |
| **Email (legacy)** | ❌ No | ✅ Yes | Hard | Email filters |

*Files still created, just not committed to repo

## 🧪 **Test Your Configuration**

```bash
# Check what notifications will be used
python scripts/secure_notifiers.py --check-config

# Test notification (won't commit anything)
python scripts/secure_notifiers.py --test-all

# Run IR check without committing files
FILE_NOTIFICATIONS_COMMIT=false python scripts/check_ir_compliance.py --dry-run
```

## 🚨 **Emergency: Stop All Emails**

If you're getting too many emails:

1. **Immediate:** Repository → Watch → Ignore
2. **GitHub Account:** Settings → Notifications → Uncheck everything
3. **Email:** Set up filters to delete/folder GitHub emails
4. **Long-term:** Configure `FILE_NOTIFICATIONS_COMMIT=false`

## 💡 **Pro Tips**

### **Silent Monitoring:**
```bash
FILE_NOTIFICATIONS_COMMIT=false
SLACK_WEBHOOK_URL=your-webhook-url
```
**Result:** Silent file tracking + Slack alerts for violations only

### **Issues for Important Stuff:**
```bash
FILE_NOTIFICATIONS_COMMIT=false
# No webhooks configured - will use GitHub Issues
```
**Result:** GitHub Issues created for violations, email notifications from GitHub Issues system (controllable)

### **Complete Silence:**
```bash
FILE_NOTIFICATIONS_COMMIT=false
# No other notification methods configured
```
**Result:** Files created in Action logs only, zero emails, manual monitoring via GitHub Actions tab

The system gives you complete control over when and how you get notified! 🎛️
