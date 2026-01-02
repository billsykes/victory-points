"""
Save Final Season Rosters
Saves each team's final roster at the end of the season for historical record keeping
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent))

from yahoo_client import YahooFantasyClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def save_final_rosters(client: YahooFantasyClient, 
                       output_dir: str = 'data',
                       week: Optional[int] = None,
                       season: Optional[int] = None) -> dict:
    """Save all team rosters to a JSON file
    
    Args:
        client: Yahoo Fantasy client
        output_dir: Directory to save roster data
        week: Specific week to save rosters from (defaults to current week)
        season: Season year (defaults to league's current season)
        
    Returns:
        Dictionary containing all roster data
    """
    try:
        # Get league info
        league_info = client.get_league_info()
        
        if season is None:
            season = league_info['season']
        
        if week is None:
            week = league_info['current_week']
        
        logger.info(f"Fetching final rosters for {season} season (Week {week})...")
        
        # Get all team rosters
        rosters = client.get_all_team_rosters(week)
        
        # Build output data structure
        roster_data = {
            'season': season,
            'week': week,
            'league_name': league_info['name'],
            'league_id': league_info['league_id'],
            'date_saved': datetime.now().isoformat(),
            'num_teams': len(rosters),
            'rosters': []
        }
        
        # Process each team's roster
        for roster in rosters:
            team_roster = {
                'team_id': roster['team_id'],
                'team_key': roster['team_key'],
                'team_name': roster['team_name'],
                'manager': roster['manager'],
                'num_players': len(roster['players']),
                'num_ir_players': len(roster['ir_players']),
                'players': []
            }
            
            # Add player details
            for player in roster['players']:
                player_info = {
                    'player_id': player['player_id'],
                    'player_key': player['player_key'],
                    'name': player['name'],
                    'position': player['position'],
                    'nfl_team': player['team'],
                    'roster_position': player['selected_position'],
                    'status': player['status'],
                    'is_ir_slot': player['is_ir_slot']
                }
                
                # Add injury note if present
                if player.get('injury_note'):
                    player_info['injury_note'] = player['injury_note']
                
                team_roster['players'].append(player_info)
            
            roster_data['rosters'].append(team_roster)
            logger.info(f"  {roster['team_name']}: {len(roster['players'])} players")
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        output_file = output_path / f'final_rosters_{season}.json'
        with open(output_file, 'w') as f:
            json.dump(roster_data, f, indent=2)
        
        logger.info(f"Final rosters saved to: {output_file}")
        logger.info(f"Total teams: {len(rosters)}")
        logger.info(f"Total players: {sum(len(r['players']) for r in rosters)}")
        
        return roster_data
        
    except Exception as e:
        logger.error(f"Failed to save final rosters: {e}")
        raise


def print_roster_summary(roster_data: dict):
    """Print a formatted summary of saved rosters"""
    print(f"\n{'='*80}")
    print(f"FINAL ROSTERS - {roster_data['season']} SEASON")
    print(f"League: {roster_data['league_name']}")
    print(f"Week {roster_data['week']} - Saved: {roster_data['date_saved']}")
    print(f"{'='*80}\n")
    
    for team in roster_data['rosters']:
        print(f"{team['team_name']} ({team['manager']})")
        print(f"  Total Players: {team['num_players']}")
        if team['num_ir_players'] > 0:
            print(f"  IR Players: {team['num_ir_players']}")
        
        # Group players by position
        positions = {}
        for player in team['players']:
            pos = player['roster_position'] or player['position']
            if pos not in positions:
                positions[pos] = []
            positions[pos].append(player)
        
        # Print starters (non-BN, non-IR)
        print(f"  Starters:")
        starter_positions = [p for p in positions.keys() if p not in ['BN', 'IR', 'IR+']]
        for pos in sorted(starter_positions):
            for player in positions[pos]:
                status_str = f" ({player['status']})" if player['status'] != 'Unknown' else ""
                print(f"    {pos}: {player['name']} - {player['nfl_team']}{status_str}")
        
        # Print bench
        if 'BN' in positions:
            print(f"  Bench: {len(positions['BN'])} players")
        
        # Print IR
        ir_players = [p for p in team['players'] if p['is_ir_slot']]
        if ir_players:
            print(f"  IR: {len(ir_players)} players")
        
        print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Save final rosters for all teams at the end of the season'
    )
    parser.add_argument(
        '--week', 
        type=int, 
        help='Specific week to save rosters from (default: current week)'
    )
    parser.add_argument(
        '--season',
        type=int,
        help='Season year (default: current season)'
    )
    parser.add_argument(
        '--config', 
        type=str, 
        help='Path to configuration file'
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='data',
        help='Output directory for roster data (default: data)'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print detailed roster summary'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Yahoo Fantasy client
        logger.info("Initializing Yahoo Fantasy client...")
        client = YahooFantasyClient(args.config)
        
        # Save final rosters
        roster_data = save_final_rosters(
            client,
            output_dir=args.output_dir,
            week=args.week,
            season=args.season
        )
        
        # Print summary if requested
        if args.summary:
            print_roster_summary(roster_data)
        
        logger.info("✓ Final rosters saved successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to save rosters: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

