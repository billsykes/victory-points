# Victory Points - Yahoo Fantasy Football Custom Scoring

A tool to calculate and display custom fantasy football standings that combine head-to-head matchups with league-wide performance scoring.

## Scoring System

Each team gets **two** results each week:
1. **Head-to-Head**: Win or loss against their weekly opponent (standard Yahoo scoring)
2. **Performance**: Win if they score in the top half of the league that week, loss if bottom half

## Project Structure

```
├── scripts/           # Python scripts for data fetching and processing
├── website/          # Static website files
├── data/             # Generated JSON data files
├── config/           # Configuration files
└── requirements.txt  # Python dependencies
```

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Yahoo API credentials in `config/yahoo_config.json`

3. Run the data fetcher:
   ```bash
   python scripts/fetch_data.py
   ```

4. Open `website/index.html` to view standings

## Features

### Victory Points Scoring
- **Head-to-Head**: Win or loss against weekly opponent (standard Yahoo scoring)
- **Performance**: Win if team scores in top half of league that week

### IR Compliance Monitoring
- **Daily Checks**: Automated verification of IR slot usage
- **Smart Notifications**: GitHub Issues created for violations only (no spam!)
- **Professional Workflow**: Assign, track, and resolve violations
- **Multiple Alert Options**: GitHub Issues, Slack, Discord, or email

## Season-End Tasks

### Save Final Rosters

At the end of each season, save a snapshot of all team rosters for historical record-keeping:

```bash
python scripts/save_final_rosters.py
```

**Options:**
- `--week WEEK`: Specific week to save rosters from (default: current week)
- `--season YEAR`: Season year (default: current season)
- `--summary`: Print detailed roster summary
- `--output-dir DIR`: Output directory (default: data/)

**Example:**
```bash
# Save current rosters with detailed summary
python scripts/save_final_rosters.py --summary

# Save rosters from a specific week/season
python scripts/save_final_rosters.py --week 14 --season 2024 --summary
```

This creates a `final_rosters_YYYY.json` file containing:
- Team information (name, manager, ID)
- Complete roster with player details
- Position assignments and IR status
- Timestamp of when rosters were saved

## Automation

The project uses GitHub Actions to:
- **Weekly**: Fetch data and update standings
- **Daily**: Check IR slot compliance and send violation reports
