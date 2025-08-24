"""
Main Data Fetcher
Orchestrates fetching data from Yahoo API and calculating custom standings
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent))

from yahoo_client import YahooFantasyClient
from scoring_calculator import ScoringCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_and_calculate_week(client: YahooFantasyClient, 
                           calculator: ScoringCalculator, 
                           week: int) -> bool:
    """Fetch data and calculate standings for a specific week
    
    Args:
        client: Yahoo Fantasy client
        calculator: Scoring calculator
        week: Week number to process
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing week {week}...")
        
        # Fetch matchups and scores
        matchups = client.get_week_matchups(week)
        week_scores = client.get_week_scores(week)
        
        if not matchups or not week_scores:
            logger.warning(f"No data available for week {week}")
            return False
        
        logger.info(f"Fetched {len(matchups)} matchups and {len(week_scores)} team scores")
        
        # Calculate results
        week_results = calculator.calculate_week_results(matchups, week_scores)
        
        # Save week data
        calculator.save_week_data(week_results)
        
        # Print week summary
        print_week_summary(week_results)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to process week {week}: {e}")
        return False


def print_week_summary(week_data):
    """Print a formatted summary of week results"""
    week = week_data['week']
    results = week_data['team_results']
    summary = week_data['week_summary']
    
    print(f"\n{'='*60}")
    print(f"WEEK {week} RESULTS")
    print(f"{'='*60}")
    
    print(f"{'Team':<20} {'Score':<8} {'H2H':<5} {'Perf':<5} {'Total':<7} {'Rank'}")
    print(f"{'-'*60}")
    
    for i, team in enumerate(results):
        print(f"{team['team_name'][:19]:<20} "
              f"{team['week_score']:<8.1f} "
              f"{team['h2h_result']:<5} "
              f"{team['performance_result']:<5} "
              f"{team['total_wins']}-{team['total_losses']:<5} "
              f"{i+1}")
    
    print(f"\nWeek {week} Summary:")
    print(f"  Highest Score: {summary['highest_score']:.1f}")
    print(f"  Lowest Score: {summary['lowest_score']:.1f}")
    print(f"  Average Score: {summary['average_score']:.1f}")
    print(f"  Perfect Weeks (2-0): {summary['perfect_weeks']}")
    print(f"  Winless Weeks (0-2): {summary['winless_weeks']}")


def print_season_standings(standings_data):
    """Print formatted season standings"""
    standings = standings_data['standings']
    summary = standings_data['season_summary']
    weeks_included = standings_data['weeks_included']
    
    print(f"\n{'='*80}")
    print(f"SEASON STANDINGS (Through Week {weeks_included})")
    print(f"{'='*80}")
    
    print(f"{'Rank':<5} {'Team':<20} {'Record':<8} {'H2H':<8} {'Perf':<8} {'Points':<8} {'Avg':<8}")
    print(f"{'-'*80}")
    
    for team in standings:
        h2h_record = f"{team['total_h2h_wins']}-{team['total_h2h_losses']}"
        if team['total_h2h_ties'] > 0:
            h2h_record += f"-{team['total_h2h_ties']}"
        
        perf_record = f"{team['total_performance_wins']}-{team['total_performance_losses']}"
        total_record = f"{team['total_wins']}-{team['total_losses']}"
        
        print(f"{team['rank']:<5} "
              f"{team['team_name'][:19]:<20} "
              f"{total_record:<8} "
              f"{h2h_record:<8} "
              f"{perf_record:<8} "
              f"{team['total_points']:<8.1f} "
              f"{team['average_score']:<8.1f}")
    
    print(f"\nSeason Summary:")
    print(f"  Leader: {summary['leader']} ({summary['leader_wins']} wins)")
    print(f"  Most Points: {summary['most_points']} ({summary['highest_total_points']:.1f} pts)")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Fetch Yahoo Fantasy data and calculate custom standings')
    parser.add_argument('--week', type=int, help='Specific week to process (default: current week)')
    parser.add_argument('--all-weeks', action='store_true', help='Process all available weeks')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--output-dir', type=str, default='data', help='Output directory for data files')
    parser.add_argument('--standings-only', action='store_true', help='Only calculate season standings from existing data')
    
    args = parser.parse_args()
    
    try:
        # Initialize components
        logger.info("Initializing Yahoo Fantasy client...")
        client = YahooFantasyClient(args.config)
        
        calculator = ScoringCalculator(args.output_dir)
        
        if args.standings_only:
            # Only calculate season standings from existing data
            logger.info("Calculating season standings from existing data...")
            weeks_data = calculator.load_all_weeks_data()
            
            if not weeks_data:
                logger.error("No existing week data found")
                return 1
            
            season_standings = calculator.calculate_season_standings(weeks_data)
            calculator.save_season_standings(season_standings)
            print_season_standings(season_standings)
            return 0
        
        # Get league info
        league_info = client.get_league_info()
        logger.info(f"Connected to league: {league_info['name']} (Season {league_info['season']})")
        
        success_count = 0
        
        if args.all_weeks:
            # Process all weeks from start to current
            start_week = league_info['start_week']
            current_week = league_info['current_week']
            
            for week in range(start_week, current_week + 1):
                if fetch_and_calculate_week(client, calculator, week):
                    success_count += 1
        else:
            # Process specific week or current week
            week_to_process = args.week if args.week else league_info['current_week']
            
            if fetch_and_calculate_week(client, calculator, week_to_process):
                success_count += 1
        
        if success_count > 0:
            # Calculate and display season standings
            logger.info("Calculating season standings...")
            weeks_data = calculator.load_all_weeks_data()
            
            if weeks_data:
                season_standings = calculator.calculate_season_standings(weeks_data)
                calculator.save_season_standings(season_standings)
                print_season_standings(season_standings)
        
        logger.info(f"Successfully processed {success_count} week(s)")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
