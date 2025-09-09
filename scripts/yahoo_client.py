"""
Yahoo Fantasy Sports API Client
Handles authentication and data fetching from Yahoo Fantasy Sports API
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from yfpy import YahooFantasySportsQuery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YahooFantasyClient:
    """Client for interacting with Yahoo Fantasy Sports API"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Yahoo Fantasy client
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.yahoo_query = None
        self._initialize_yahoo_client()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment variables"""
        config = {
            'consumer_key': os.getenv('YAHOO_CONSUMER_KEY'),
            'consumer_secret': os.getenv('YAHOO_CONSUMER_SECRET'),
            'league_id': os.getenv('LEAGUE_ID'),
            'game_key': os.getenv('GAME_KEY', 'nfl'),
            'current_season': int(os.getenv('CURRENT_SEASON', '2024'))
        }
        
        # Load from JSON config file if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config.get('yahoo_oauth', {}))
                config.update(file_config.get('league_config', {}))
        
        # Validate required config
        required_fields = ['consumer_key', 'consumer_secret', 'league_id']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        return config
    
    def _initialize_yahoo_client(self):
        """Initialize the YFPY Yahoo client"""
        try:
            # Create auth directory if it doesn't exist
            auth_dir = Path("config/auth")
            auth_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if we're running in a non-interactive environment (like GitHub Actions)
            is_non_interactive = os.getenv('CI') == 'true' or not os.isatty(0)
            
            if is_non_interactive:
                logger.info("Running in non-interactive mode, checking for pre-existing tokens...")
                # In CI/non-interactive mode, try to use existing tokens or fail gracefully
                self._initialize_non_interactive()
            else:
                logger.info("Running in interactive mode, enabling browser OAuth...")
                self._initialize_interactive()
                
        except Exception as e:
            logger.error(f"Failed to initialize Yahoo client: {e}")
            raise
    
    def _initialize_interactive(self):
        """Initialize with interactive browser OAuth"""
        self.yahoo_query = YahooFantasySportsQuery(
            league_id=self.config['league_id'],
            game_code=self.config['game_key'],
            game_id=None,  # Will be determined automatically
            yahoo_consumer_key=self.config['consumer_key'],
            yahoo_consumer_secret=self.config['consumer_secret'],
            env_file_location=Path.cwd(),  # Path object, not string
            save_token_data_to_env_file=True,  # Save tokens to .env file
            browser_callback=True  # Enable browser-based OAuth
        )
        logger.info("Yahoo Fantasy client initialized with interactive OAuth")
    
    def _initialize_non_interactive(self):
        """Initialize in non-interactive mode using existing tokens"""
        # Check for existing OAuth tokens in environment variables
        oauth_tokens = {
            'YAHOO_ACCESS_TOKEN': os.getenv('YAHOO_ACCESS_TOKEN'),
            'YAHOO_REFRESH_TOKEN': os.getenv('YAHOO_REFRESH_TOKEN'),
            'YAHOO_GUID': os.getenv('YAHOO_GUID'),
            'YAHOO_TOKEN_TIME': os.getenv('YAHOO_TOKEN_TIME'),
            'YAHOO_TOKEN_TYPE': os.getenv('YAHOO_TOKEN_TYPE', 'bearer')
        }
        
        # Check if we have the essential tokens
        essential_tokens = oauth_tokens['YAHOO_ACCESS_TOKEN'] and oauth_tokens['YAHOO_REFRESH_TOKEN']
        
        if essential_tokens:
            logger.info("Found essential OAuth tokens in environment variables")
            
            # Create .env file with all available OAuth tokens
            env_content = []
            valid_tokens = 0
            
            for key, value in oauth_tokens.items():
                if value and value != 'None' and value.strip():  # Only add valid, non-None values
                    # Validate token format to avoid header issues
                    cleaned_value = value.strip()
                    
                    # Check for problematic characters that might cause header issues
                    if any(ord(char) > 127 or char in '\r\n\t' for char in cleaned_value):
                        logger.warning(f"Token {key} contains invalid characters, skipping")
                        continue
                    
                    env_content.append(f"{key}={cleaned_value}")
                    valid_tokens += 1
                    logger.debug(f"Added {key}: {cleaned_value[:10]}...")  # Log first 10 chars for debugging
                else:
                    logger.debug(f"Skipping {key}: value is None or empty")
            
            # Also add the consumer credentials to .env for yfpy
            env_content.extend([
                f"YAHOO_CONSUMER_KEY={self.config['consumer_key']}",
                f"YAHOO_CONSUMER_SECRET={self.config['consumer_secret']}"
            ])
            
            # Write all tokens to .env file for yfpy to read
            env_file_content = "\n".join(env_content) + "\n"
            with open('.env', 'w') as f:  # Overwrite instead of append
                f.write(env_file_content)
            
            logger.info(f"Written {valid_tokens} OAuth tokens and 2 consumer credentials to .env file")
            
            # Debug: Show which tokens were written (without exposing full values)
            for key, value in oauth_tokens.items():
                if value and value != 'None' and value.strip():
                    logger.info(f"Token {key}: length={len(value)}, first_chars={value[:6]}...")
        else:
            logger.warning("Missing essential OAuth tokens (ACCESS_TOKEN or REFRESH_TOKEN)")
            logger.info("Available tokens: " + ", ".join([k for k, v in oauth_tokens.items() if v]))
        
        # Try to initialize with all available authentication data
        self.yahoo_query = YahooFantasySportsQuery(
            league_id=self.config['league_id'],
            game_code=self.config['game_key'],
            game_id=None,  # Will be determined automatically
            yahoo_consumer_key=self.config['consumer_key'],
            yahoo_consumer_secret=self.config['consumer_secret'],
            env_file_location=Path.cwd(),
            save_token_data_to_env_file=False,  # Don't try to save in CI
            browser_callback=False,  # Disable browser-based OAuth
            env_var_fallback=True  # Enable reading from environment variables
        )
        logger.info("Yahoo Fantasy client initialized in non-interactive mode")
    
    def get_league_info(self) -> Dict[str, Any]:
        """Get basic league information"""
        try:
            league = self.yahoo_query.get_league_info()
            return {
                'league_id': league.league_id,
                'name': league.name.decode('utf-8') if isinstance(league.name, bytes) else str(league.name),
                'season': league.season,
                'num_teams': league.num_teams,
                'current_week': league.current_week,
                'start_week': league.start_week,
                'end_week': league.end_week
            }
        except Exception as e:
            logger.error(f"Failed to fetch league info: {e}")
            raise
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams in the league"""
        try:
            teams = self.yahoo_query.get_league_teams()
            team_list = []
            
            for team in teams:
                # Handle manager information safely
                manager_name = 'Unknown'
                if hasattr(team, 'managers') and team.managers:
                    manager = team.managers[0]
                    if hasattr(manager, 'nickname'):
                        manager_name = manager.nickname.decode('utf-8') if isinstance(manager.nickname, bytes) else str(manager.nickname)
                    elif hasattr(manager, 'name'):
                        manager_name = manager.name.decode('utf-8') if isinstance(manager.name, bytes) else str(manager.name)
                
                team_info = {
                    'team_id': team.team_id,
                    'team_key': team.team_key,
                    'name': team.name.decode('utf-8') if isinstance(team.name, bytes) else str(team.name),
                    'manager': manager_name
                }
                team_list.append(team_info)
            
            return team_list
        except Exception as e:
            logger.error(f"Failed to fetch teams: {e}")
            raise
    
    def get_week_matchups(self, week: int) -> List[Dict[str, Any]]:
        """Get matchups for a specific week"""
        try:
            matchups = self.yahoo_query.get_league_matchups_by_week(week)
            matchup_list = []
            
            for matchup in matchups:
                if hasattr(matchup, 'teams') and len(matchup.teams) == 2:
                    team1, team2 = matchup.teams[0], matchup.teams[1]
                    
                    # Extract points from TeamPoints objects
                    team1_points = 0
                    if hasattr(team1, 'team_points') and team1.team_points:
                        if hasattr(team1.team_points, 'total'):
                            team1_points = float(team1.team_points.total)
                        else:
                            # Fallback: try to get total as attribute or use the object directly
                            team1_points = float(getattr(team1.team_points, 'total', team1.team_points))
                    
                    team2_points = 0
                    if hasattr(team2, 'team_points') and team2.team_points:
                        if hasattr(team2.team_points, 'total'):
                            team2_points = float(team2.team_points.total)
                        else:
                            # Fallback: try to get total as attribute or use the object directly
                            team2_points = float(getattr(team2.team_points, 'total', team2.team_points))

                    matchup_info = {
                        'week': week,
                        'matchup_id': getattr(matchup, 'matchup_id', None),
                        'team1': {
                            'team_id': team1.team_id,
                            'team_key': team1.team_key,
                            'name': team1.name.decode('utf-8') if isinstance(team1.name, bytes) else str(team1.name),
                            'points': team1_points
                        },
                        'team2': {
                            'team_id': team2.team_id,
                            'team_key': team2.team_key,
                            'name': team2.name.decode('utf-8') if isinstance(team2.name, bytes) else str(team2.name),
                            'points': team2_points
                        }
                    }
                    matchup_list.append(matchup_info)
            
            return matchup_list
        except Exception as e:
            logger.error(f"Failed to fetch week {week} matchups: {e}")
            raise
    
    def get_week_scores(self, week: int) -> List[Dict[str, Any]]:
        """Get all team scores for a specific week"""
        try:
            # Get matchups which contain the scores
            matchups = self.get_week_matchups(week)
            scores = []
            
            for matchup in matchups:
                scores.append({
                    'team_id': matchup['team1']['team_id'],
                    'team_key': matchup['team1']['team_key'],
                    'team_name': matchup['team1']['name'],
                    'score': float(matchup['team1']['points']),
                    'week': week
                })
                scores.append({
                    'team_id': matchup['team2']['team_id'],
                    'team_key': matchup['team2']['team_key'],
                    'team_name': matchup['team2']['name'],
                    'score': float(matchup['team2']['points']),
                    'week': week
                })
            
            # Sort by score descending
            scores.sort(key=lambda x: x['score'], reverse=True)
            return scores
            
        except Exception as e:
            logger.error(f"Failed to fetch week {week} scores: {e}")
            raise
    
    def get_current_week(self) -> int:
        """Get the current week number"""
        try:
            league_info = self.get_league_info()
            return league_info['current_week']
        except Exception as e:
            logger.error(f"Failed to get current week: {e}")
            return 1
    
    def get_team_roster(self, team_id: str, week: Optional[int] = None) -> Dict[str, Any]:
        """Get team roster with player information including IR slot
        
        Args:
            team_id: Yahoo team ID
            week: Week number (defaults to current week)
            
        Returns:
            Dictionary containing roster data with players and their positions
        """
        try:
            if week is None:
                week = self.get_current_week()
            
            # Get team roster for specific week
            roster = self.yahoo_query.get_team_roster_by_week(team_id, week)
            
            roster_data = {
                'team_id': team_id,
                'week': week,
                'players': [],
                'ir_players': []
            }
            
            # Extract players from roster object
            players = roster.players if hasattr(roster, 'players') else []
            
            for player in players:
                try:
                    # Safely extract player name
                    player_name = 'Unknown'
                    if hasattr(player, 'name'):
                        if hasattr(player.name, 'full'):
                            player_name = player.name.full.decode('utf-8') if isinstance(player.name.full, bytes) else str(player.name.full)
                        else:
                            player_name = str(player.name)
                    
                    player_info = {
                        'player_id': getattr(player, 'player_id', 'Unknown'),
                        'player_key': getattr(player, 'player_key', 'Unknown'),
                        'name': player_name,
                        'position': getattr(player, 'primary_position', 'Unknown'),
                        'team': getattr(player, 'editorial_team_abbr', 'Unknown'),
                        'status': getattr(player, 'status', 'Unknown'),
                        'injury_note': getattr(player, 'injury_note', ''),
                        'selected_position': None,
                        'is_ir_slot': False
                    }
                    
                    # Get selected position from roster positions
                    if hasattr(player, 'selected_position'):
                        if hasattr(player.selected_position, 'position'):
                            player_info['selected_position'] = player.selected_position.position
                            # Check if player is in IR slot
                            if player.selected_position.position in ['IR', 'IR+']:
                                player_info['is_ir_slot'] = True
                                roster_data['ir_players'].append(player_info)
                    
                    roster_data['players'].append(player_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to process player in roster: {e}")
                    continue
            
            return roster_data
            
        except Exception as e:
            logger.error(f"Failed to fetch roster for team {team_id}, week {week}: {e}")
            raise
    
    def get_all_team_rosters(self, week: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get rosters for all teams in the league
        
        Args:
            week: Week number (defaults to current week)
            
        Returns:
            List of roster dictionaries for all teams
        """
        try:
            teams = self.get_teams()
            rosters = []
            
            for team in teams:
                try:
                    roster = self.get_team_roster(team['team_id'], week)
                    roster['team_name'] = team['name']
                    roster['manager'] = team['manager']
                    rosters.append(roster)
                except Exception as e:
                    logger.warning(f"Failed to get roster for team {team['name']}: {e}")
                    continue
            
            return rosters
            
        except Exception as e:
            logger.error(f"Failed to fetch all team rosters: {e}")
            raise
    
    def get_player_details(self, player_key: str) -> Dict[str, Any]:
        """Get detailed player information including current status
        
        Args:
            player_key: Yahoo player key
            
        Returns:
            Dictionary with detailed player information
        """
        try:
            player = self.yahoo_query.get_player_details_by_key(player_key)
            
            player_details = {
                'player_key': player_key,
                'player_id': getattr(player, 'player_id', ''),
                'name': player.name.full if hasattr(player.name, 'full') else str(player.name),
                'position': getattr(player, 'primary_position', 'Unknown'),
                'team': getattr(player, 'editorial_team_abbr', 'Unknown'),
                'status': getattr(player, 'status', 'Unknown'),
                'injury_note': getattr(player, 'injury_note', ''),
                'is_ir_eligible': False
            }
            
            # Determine IR eligibility based on status
            ir_eligible_statuses = ['IR', 'O', 'PUP', 'NFI', 'SUSP', 'NA']
            player_details['is_ir_eligible'] = player_details['status'] in ir_eligible_statuses
            
            return player_details
            
        except Exception as e:
            logger.error(f"Failed to fetch player details for {player_key}: {e}")
            raise


if __name__ == "__main__":
    # Test the client
    try:
        client = YahooFantasyClient()
        
        print("Testing Yahoo Fantasy Client...")
        league_info = client.get_league_info()
        print(f"League: {league_info['name']} (Season {league_info['season']})")
        print(f"Teams: {league_info['num_teams']}")
        print(f"Current Week: {league_info['current_week']}")
        
        teams = client.get_teams()
        print(f"\nTeams in league:")
        for team in teams:
            print(f"  {team['name']} (Manager: {team['manager']})")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to:")
        print("1. Set up your Yahoo Developer App")
        print("2. Configure your credentials in environment variables or config file")
        print("3. Install dependencies: pip install -r requirements.txt")
