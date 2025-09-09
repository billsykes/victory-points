"""
Debug Yahoo API Data Structure
Helps troubleshoot the Yahoo Fantasy API data format
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent))

from yahoo_client import YahooFantasyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def debug_team_structure():
    """Debug team and manager data structure"""
    print("🔍 Debugging Team Data Structure")
    print("=" * 50)
    
    try:
        client = YahooFantasyClient()
        
        # Get raw teams data
        teams = client.yahoo_query.get_league_teams()
        
        print(f"Number of teams: {len(teams)}")
        
        for i, team in enumerate(teams[:1]):  # Just look at first team
            print(f"\nTeam {i+1}:")
            print(f"  Type: {type(team)}")
            print(f"  Dir: {[attr for attr in dir(team) if not attr.startswith('_')]}")
            
            # Basic team info
            print(f"  team_id: {getattr(team, 'team_id', 'Not found')}")
            print(f"  team_key: {getattr(team, 'team_key', 'Not found')}")
            print(f"  name: {getattr(team, 'name', 'Not found')}")
            
            # Manager info
            print(f"  managers: {hasattr(team, 'managers')}")
            if hasattr(team, 'managers'):
                managers = team.managers
                print(f"  managers type: {type(managers)}")
                print(f"  managers length: {len(managers) if managers else 'None'}")
                
                if managers:
                    manager = managers[0]
                    print(f"  manager type: {type(manager)}")
                    print(f"  manager dir: {[attr for attr in dir(manager) if not attr.startswith('_')]}")
                    print(f"  manager nickname: {getattr(manager, 'nickname', 'Not found')}")
                    print(f"  manager name: {getattr(manager, 'name', 'Not found')}")
        
        return True
        
    except Exception as e:
        print(f"Error in debug_team_structure: {e}")
        import traceback
        traceback.print_exc()
        return False


def debug_roster_structure():
    """Debug roster data structure"""
    print("\n🔍 Debugging Roster Data Structure")
    print("=" * 50)
    
    try:
        client = YahooFantasyClient()
        
        # Get teams first
        teams = client.get_teams()
        if not teams:
            print("No teams found!")
            return False
        
        team = teams[0]
        print(f"Getting roster for team: {team['name']}")
        
        # Get raw roster data
        week = client.get_current_week()
        roster = client.yahoo_query.get_team_roster_by_week(team['team_id'], week)
        
        print(f"Roster type: {type(roster)}")
        print(f"Roster dir: {[attr for attr in dir(roster) if not attr.startswith('_')]}")
        
        # The roster might have a 'players' attribute
        if hasattr(roster, 'players'):
            players = roster.players
            print(f"Players type: {type(players)}")
            print(f"Number of players: {len(players)}")
            
            for i, player in enumerate(players[:2]):  # Just look at first 2 players
                print(f"\nPlayer {i+1}:")
                print(f"  Type: {type(player)}")
                print(f"  Dir: {[attr for attr in dir(player) if not attr.startswith('_')]}")
                
                # Basic player info
                print(f"  player_id: {getattr(player, 'player_id', 'Not found')}")
                print(f"  player_key: {getattr(player, 'player_key', 'Not found')}")
                
                # Name handling
                if hasattr(player, 'name'):
                    name_obj = player.name
                    print(f"  name type: {type(name_obj)}")
                    print(f"  name dir: {[attr for attr in dir(name_obj) if not attr.startswith('_')]}")
                    print(f"  name.full: {getattr(name_obj, 'full', 'Not found')}")
                    print(f"  name str: {str(name_obj)}")
                
                # Position info
                print(f"  primary_position: {getattr(player, 'primary_position', 'Not found')}")
                print(f"  editorial_team_abbr: {getattr(player, 'editorial_team_abbr', 'Not found')}")
                print(f"  status: {getattr(player, 'status', 'Not found')}")
                
                # Selected position (roster position)
                if hasattr(player, 'selected_position'):
                    pos_obj = player.selected_position
                    print(f"  selected_position type: {type(pos_obj)}")
                    print(f"  selected_position dir: {[attr for attr in dir(pos_obj) if not attr.startswith('_')]}")
                    print(f"  selected_position.position: {getattr(pos_obj, 'position', 'Not found')}")
        else:
            print("No 'players' attribute found on roster")
        
        return True
        
    except Exception as e:
        print(f"Error in debug_roster_structure: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fixed_methods():
    """Test the fixed methods"""
    print("\n🧪 Testing Fixed Methods")
    print("=" * 50)
    
    try:
        client = YahooFantasyClient()
        
        # Test get_teams
        print("Testing get_teams()...")
        teams = client.get_teams()
        print(f"✅ Got {len(teams)} teams")
        for team in teams:
            print(f"  {team['name']} (Manager: {team['manager']})")
        
        # Test get_team_roster
        if teams:
            print(f"\nTesting get_team_roster() for {teams[0]['name']}...")
            roster = client.get_team_roster(teams[0]['team_id'])
            print(f"✅ Got roster with {len(roster['players'])} players")
            print(f"✅ Found {len(roster['ir_players'])} players in IR slots")
            
            for ir_player in roster['ir_players']:
                print(f"  IR: {ir_player['name']} - {ir_player['status']} ({ir_player['selected_position']})")
        
        return True
        
    except Exception as e:
        print(f"Error in test_fixed_methods: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all debug tests"""
    print("🏈 Yahoo API Debug Tool")
    print("=" * 60)
    
    success = True
    
    # Test team structure
    if not debug_team_structure():
        success = False
    
    # Test roster structure
    if not debug_roster_structure():
        success = False
    
    # Test fixed methods
    if not test_fixed_methods():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All debug tests completed successfully!")
    else:
        print("❌ Some debug tests failed - check logs above")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
