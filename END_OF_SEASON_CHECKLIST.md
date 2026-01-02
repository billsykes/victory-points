# End of Season Checklist

This guide helps you complete end-of-season tasks for your Victory Points fantasy football league.

## 📸 Save Final Rosters

At the end of each season, you should save a snapshot of all team rosters for historical records.

### Option 1: Run Locally (Recommended)

```bash
# Make sure you're in the project directory
cd /path/to/victory-points

# Save rosters with detailed summary
python scripts/save_final_rosters.py --summary

# Or for a specific week (e.g., Week 14 - end of regular season)
python scripts/save_final_rosters.py --week 14 --season 2024 --summary
```

### Option 2: Run via GitHub Actions

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **"Save Final Season Rosters"** workflow
4. Click **"Run workflow"** button
5. Fill in the parameters:
   - **Week**: Leave empty for current week, or specify (e.g., `14`)
   - **Season**: Leave empty for current season, or specify (e.g., `2024`)
   - **Show summary**: Check this to see detailed roster info in logs
6. Click **"Run workflow"**

The workflow will:
- Fetch all team rosters from Yahoo
- Save to `data/final_rosters_YYYY.json`
- Automatically commit and push to your repository

## 📋 What Gets Saved

The final roster file includes:
- ✅ Team names and managers
- ✅ Complete player lists with positions
- ✅ NFL team affiliations
- ✅ Injury status (if applicable)
- ✅ IR slot assignments
- ✅ Timestamp of when data was saved

## 🗓️ When to Save Rosters

### Regular Season End
After the last regular season week (typically Week 14):
```bash
python scripts/save_final_rosters.py --week 14 --summary
```

### Playoff/Championship End
After the championship game (typically Week 17):
```bash
python scripts/save_final_rosters.py --week 17 --summary
```

### Both (Recommended)
Save rosters at both milestones to track any roster changes during playoffs.

## 📁 File Organization

Roster files are saved as:
```
data/final_rosters_2024.json
```

If you want to save multiple snapshots:
```bash
# Save regular season rosters
python scripts/save_final_rosters.py --week 14 --output-dir data/historical

# Then manually rename
mv data/historical/final_rosters_2024.json data/historical/final_rosters_2024_week14.json

# Save championship rosters
python scripts/save_final_rosters.py --week 17 --output-dir data/historical

# Then manually rename
mv data/historical/final_rosters_2024.json data/historical/final_rosters_2024_week17.json
```

## 🔍 Viewing Saved Rosters

The JSON file can be:
- Opened in any text editor
- Parsed by other scripts
- Viewed using online JSON viewers
- Imported into spreadsheet tools

Example structure:
```json
{
  "season": 2024,
  "week": 14,
  "league_name": "Your League",
  "rosters": [
    {
      "team_name": "Team Name",
      "manager": "Manager Name",
      "players": [
        {
          "name": "Player Name",
          "position": "QB",
          "nfl_team": "KC",
          "roster_position": "QB"
        }
      ]
    }
  ]
}
```

## ✅ Post-Season Tasks

- [ ] Save final regular season rosters (Week 14)
- [ ] Save final championship rosters (Week 17)
- [ ] Review season standings in `data/season_standings.json`
- [ ] Archive all data files for the season
- [ ] Update documentation for next season
- [ ] Celebrate your league champion! 🏆

## 🆘 Troubleshooting

### "No data available"
- Make sure the week has been completed
- Verify you're connected to the correct league
- Check that your Yahoo API tokens are valid

### "Authentication failed"
- Run `python scripts/generate_oauth_tokens.py` to refresh tokens
- Update your `.env` file or GitHub secrets with new tokens

### "Import errors"
- Make sure dependencies are installed: `pip install -r requirements.txt`
- Verify you're in the correct directory

## 📚 Additional Resources

- **Full Documentation**: See `FINAL_ROSTERS_GUIDE.md` for detailed information
- **Script Source**: `scripts/save_final_rosters.py`
- **GitHub Workflow**: `.github/workflows/save-final-rosters.yml`

---

*Remember: Preserving roster history helps track team evolution and makes for great offseason analysis!* 📊

