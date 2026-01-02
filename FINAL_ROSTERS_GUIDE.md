# Final Rosters Guide

## Overview

At the end of each fantasy football season, it's important to save a snapshot of each team's final roster for historical record-keeping. This allows you to look back and see exactly who was on each team when the season ended.

## Usage

### Basic Usage

Save the current rosters at the end of the season:

```bash
python scripts/save_final_rosters.py
```

### With Options

```bash
# Save with a detailed summary printed to console
python scripts/save_final_rosters.py --summary

# Save rosters from a specific week and season
python scripts/save_final_rosters.py --week 14 --season 2024

# Save to a custom directory
python scripts/save_final_rosters.py --output-dir archived_data
```

## Output Format

The script creates a file named `final_rosters_YYYY.json` (where YYYY is the season year) with the following structure:

```json
{
  "season": 2024,
  "week": 14,
  "league_name": "Your League Name",
  "league_id": "244820",
  "date_saved": "2025-01-02T10:30:00.123456",
  "num_teams": 12,
  "rosters": [
    {
      "team_id": 1,
      "team_key": "461.l.244820.t.1",
      "team_name": "Team Name",
      "manager": "Manager Name",
      "num_players": 16,
      "num_ir_players": 1,
      "players": [
        {
          "player_id": "12345",
          "player_key": "461.p.12345",
          "name": "Patrick Mahomes",
          "position": "QB",
          "nfl_team": "KC",
          "roster_position": "QB",
          "status": "Unknown",
          "is_ir_slot": false
        },
        {
          "player_id": "67890",
          "player_key": "461.p.67890",
          "name": "Christian McCaffrey",
          "position": "RB",
          "nfl_team": "SF",
          "roster_position": "RB",
          "status": "IR",
          "is_ir_slot": true,
          "injury_note": "Knee injury"
        }
        // ... more players
      ]
    }
    // ... more teams
  ]
}
```

## Field Descriptions

### Root Level
- `season`: The NFL season year
- `week`: The week number when rosters were saved
- `league_name`: Name of your fantasy league
- `league_id`: Yahoo league ID
- `date_saved`: ISO timestamp of when the data was saved
- `num_teams`: Total number of teams in the league
- `rosters`: Array of all team rosters

### Team Level
- `team_id`: Yahoo team ID
- `team_key`: Yahoo team key (used for API calls)
- `team_name`: Fantasy team name
- `manager`: Team manager's name
- `num_players`: Total number of players on roster
- `num_ir_players`: Number of players in IR slots
- `players`: Array of all players on the team

### Player Level
- `player_id`: Yahoo player ID
- `player_key`: Yahoo player key
- `name`: Player's full name
- `position`: Player's primary position (QB, RB, WR, TE, K, DEF)
- `nfl_team`: NFL team abbreviation
- `roster_position`: Position in your fantasy roster (QB, RB, WR, TE, FLEX, BN, IR, etc.)
- `status`: Injury/eligibility status (O, IR, Q, D, etc.)
- `is_ir_slot`: Boolean indicating if player is in an IR slot
- `injury_note`: (Optional) Description of injury if available

## Best Practices

### When to Save Rosters

1. **End of Regular Season**: Save rosters after Week 14 (or your league's last regular season week)
   ```bash
   python scripts/save_final_rosters.py --week 14 --summary
   ```

2. **End of Playoffs**: Save rosters after the championship week
   ```bash
   python scripts/save_final_rosters.py --week 17 --summary
   ```

3. **Both**: You can save multiple snapshots by specifying different weeks
   ```bash
   # Regular season
   python scripts/save_final_rosters.py --week 14 --output-dir data/historical
   
   # Championship
   python scripts/save_final_rosters.py --week 17 --output-dir data/historical
   ```

### File Management

The script automatically names files as `final_rosters_YYYY.json`. If you want to keep multiple snapshots:

1. Save to different directories:
   ```bash
   python scripts/save_final_rosters.py --output-dir data/2024_week14
   ```

2. Or manually rename files after saving:
   ```bash
   python scripts/save_final_rosters.py
   mv data/final_rosters_2024.json data/final_rosters_2024_week14.json
   ```

## Example Summary Output

When using the `--summary` flag, you'll see output like:

```
================================================================================
FINAL ROSTERS - 2024 SEASON
League: Your League Name
Week 14 - Saved: 2025-01-02T10:30:00.123456
================================================================================

Team Name (Manager Name)
  Total Players: 16
  IR Players: 1
  Starters:
    QB: Patrick Mahomes - KC
    RB: Derrick Henry - BAL
    RB: Saquon Barkley - PHI
    WR: Tyreek Hill - MIA
    WR: CeeDee Lamb - DAL
    TE: Travis Kelce - KC
    FLEX: Kenneth Walker III - SEA
    K: Justin Tucker - BAL
    DEF: San Francisco - SF
  Bench: 6 players
  IR: 1 players

[... more teams ...]
```

## Troubleshooting

### Authentication Issues

If you get authentication errors, make sure:
1. Your Yahoo API credentials are properly configured
2. Your OAuth tokens are up to date
3. You can run other scripts like `fetch_data.py` successfully

### No Data Available

If the script says "No data available", verify:
1. The week number exists and has completed
2. You're connected to the correct league
3. The season parameter matches your current season

### Missing Players

If some players are missing from the roster:
1. Check if the Yahoo API returned all players
2. Verify the week you're querying has accurate data
3. Some leagues have roster changes that lock after certain weeks

## Technical Notes

- The script uses the same `YahooFantasyClient` as other scripts in the project
- Roster data is fetched using the Yahoo Fantasy Sports API
- All data is saved in JSON format for easy parsing and archival
- Player status codes: O (Out), IR (Injured Reserve), Q (Questionable), D (Doubtful), P (Probable)
- Position codes: BN (Bench), IR/IR+ (Injured Reserve slots)

