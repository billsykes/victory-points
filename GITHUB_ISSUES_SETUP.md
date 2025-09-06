# GitHub Issues Setup for IR Compliance

## 🎯 **Perfect Choice!** 

GitHub Issues is the ideal solution for IR compliance notifications:
- ✅ **Zero additional credentials** - uses existing repository access
- ✅ **Smart notifications** - issues created ONLY when violations occur
- ✅ **No daily email spam** - unlike file commits
- ✅ **Proper workflow** - assign, track, and close violations
- ✅ **Automatic formatting** - professional violation reports
- ✅ **Built-in audit trail** - full history of all violations

## 🚀 **Quick Setup (2 Minutes)**

### **Step 1: Add GitHub Secrets**

Go to your repository: **Settings** → **Secrets and variables** → **Actions**

Add these **Repository Secrets:**

```
Secret Name: FILE_NOTIFICATIONS_COMMIT
Secret Value: false

Secret Name: GITHUB_ISSUES_FOR_ALL_REPORTS
Secret Value: false
```

**Optional (recommended):**
```
Secret Name: GITHUB_ISSUE_ASSIGNEE
Secret Value: your-github-username
```

### **Step 2: Enable Issues (if needed)**

Go to: **Settings** → **General** → **Features**
- ✅ Check "Issues" if not already enabled

### **Step 3: Test the Setup**

Go to: **Actions** → **IR Compliance Check** → **Run workflow**
- Set "Dry run" to `true`
- Click "Run workflow"

**That's it!** 🎉

## 📋 **How It Works**

### **Daily Automatic Checks:**
```
1. GitHub Action runs at 9 AM EST
2. Checks all teams' IR slots
3. IF violations found → Creates GitHub Issue
4. IF no violations → Does nothing (no spam!)
```

### **When Violations Are Found:**

**GitHub Issue Created:**
- **Title:** `⚠️ IR Compliance Violations - Week 5: 2 Violation(s) Found`
- **Labels:** `ir-violation`, `commissioner-action-required`, `automated`
- **Assignee:** You (if configured)
- **Body:** Detailed violation report with checkboxes

**Email Notification:**
- GitHub sends you email about new issue (controllable)
- Subject: `[victory-points] New issue: IR Compliance Violations`

### **Sample GitHub Issue:**

```markdown
## 🚨 IR Compliance Violation Report

**This issue was automatically created by the IR compliance monitoring system.**

### 📊 Summary
- **Week:** 5
- **Total Violations:** 2
- **Date Generated:** 2024-09-06 14:30 UTC

### ⚠️ Violations Detected

**Team Alpha (Manager: John)**
Violations: 1

  • Christian McCaffrey
    - Current Status: Q
    - Issue: Player Christian McCaffrey has status 'Q' which is not eligible for IR slot

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

### 🔄 Next Steps
1. Review the violations listed above
2. Contact the team managers to correct their lineups  
3. Set a deadline for compliance
4. Close this issue once violations are resolved
```

## ⚙️ **Configuration Options**

### **Basic Setup (Recommended):**
```bash
FILE_NOTIFICATIONS_COMMIT=false           # No daily commits/emails
GITHUB_ISSUES_FOR_ALL_REPORTS=false       # Only violations create issues
```

### **Advanced Options:**
```bash
GITHUB_ISSUE_ASSIGNEE=your-github-username  # Auto-assign issues to you
IR_ELIGIBLE_STATUSES=IR,O,PUP,NFI          # Custom eligible statuses
```

### **Alternative Configurations:**

**Weekly Summary Issues:**
```bash
GITHUB_ISSUES_FOR_ALL_REPORTS=true  # Create issues even without violations
```

**Silent Monitoring:**
```bash
FILE_NOTIFICATIONS_COMMIT=false
# No other notification methods = files only in Action logs
```

## 📧 **Email Notification Control**

### **You Get Emails For:**
- ✅ **New GitHub Issues** (violations only)
- ✅ **Issue comments** (when people respond)
- ✅ **Issue assignments** (when assigned to you)

### **You DON'T Get Emails For:**
- ❌ Daily compliance checks (when no violations)
- ❌ File commits (disabled)
- ❌ GitHub Action runs (unless they fail)

### **Customize Notifications:**

**Repository Level:**
- Go to repository → **Watch** → **Custom**
- Choose which activities send emails

**Account Level:**
- **Settings** → **Notifications**
- Configure global email preferences

## 🧪 **Testing Your Setup**

### **Test 1: Configuration Check**
```bash
python scripts/secure_notifiers.py --check-config
# Should show: "Current choice: GitHubIssueNotifier"
```

### **Test 2: Dry Run**
```bash
python scripts/check_ir_compliance.py --dry-run
# Shows what would happen without actually creating issues
```

### **Test 3: Manual Action**
- Go to **Actions** → **IR Compliance Check**
- Click **Run workflow**
- Set "Dry run" = `true`
- Check the logs to see what would happen

## 🎯 **Benefits of This Approach**

### **Compared to Email:**
- ✅ **Better tracking** - Issues vs lost emails
- ✅ **Collaborative** - Others can comment/help
- ✅ **Actionable** - Built-in checkboxes and workflow
- ✅ **No credentials** - Uses repository permissions

### **Compared to File Commits:**
- ✅ **No spam** - Only creates issues for violations
- ✅ **Smart notifications** - GitHub's notification system
- ✅ **Professional** - Proper issue templates and formatting

### **Compared to Slack/Discord:**
- ✅ **Zero setup** - No webhooks to configure
- ✅ **Persistent** - Issues don't get lost in chat
- ✅ **Assignable** - Can assign to specific people

## 🔧 **Issue Management Workflow**

### **When Issue Is Created:**
1. **Review violations** listed in issue
2. **Contact team managers** via your usual communication method
3. **Set deadline** for compliance (add comment to issue)
4. **Check boxes** as you complete actions

### **When Violations Are Fixed:**
1. **Verify compliance** in next day's check
2. **Close issue** manually or wait for auto-resolution
3. **Add closing comment** documenting resolution

### **Recurring Violations:**
- Issues stay open until resolved
- New violations get new issues
- Easy to see patterns and repeat offenders

## 📊 **Sample Repository Secrets Configuration**

Here's exactly what to add in **Settings** → **Secrets and variables** → **Actions**:

| Secret Name | Secret Value | Purpose |
|-------------|--------------|---------|
| `FILE_NOTIFICATIONS_COMMIT` | `false` | Prevent daily commit emails |
| `GITHUB_ISSUES_FOR_ALL_REPORTS` | `false` | Only violations create issues |
| `GITHUB_ISSUE_ASSIGNEE` | `your-username` | Auto-assign violations to you |

**Optional league customization:**
| Secret Name | Example Value | Purpose |
|-------------|---------------|---------|
| `IR_ELIGIBLE_STATUSES` | `IR,O,PUP` | Custom IR eligibility rules |
| `ALWAYS_SEND_IR_REPORT` | `false` | Force notifications even without violations |

## 🎉 **You're All Set!**

With this configuration:
- ✅ **Zero credentials** to manage
- ✅ **No daily email spam**
- ✅ **Professional violation tracking**
- ✅ **Automatic monitoring** every day at 9 AM EST
- ✅ **Smart notifications** only when action needed

The system will now automatically monitor your league's IR compliance and create professional GitHub Issues whenever violations occur! 🏈
