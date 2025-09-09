"""
Custom Scoring Calculator
Implements the victory points scoring system that combines head-to-head and performance-based wins
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ScoringCalculator:
    """Calculator for custom victory points scoring system"""
    
    def __init__(self, output_dir: str = "data"):
        """Initialize the scoring calculator
        
        Args:
            output_dir: Directory to save calculated data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def calculate_week_results(self, matchups: List[Dict], week_scores: List[Dict]) -> Dict[str, Any]:
        """Calculate results for a single week
        
        Args:
            matchups: List of head-to-head matchup data
            week_scores: List of all team scores for the week
            
        Returns:
            Dictionary containing week results and standings
        """
        week = week_scores[0]['week'] if week_scores else 1
        
        # Check if this week has valid data (not all zero scores)
        if self._is_invalid_week_data(week_scores):
            logger.warning(f"Week {week} appears to have invalid data (all zero scores) - skipping calculation")
            return None
        
        # Calculate head-to-head results
        h2h_results = self._calculate_h2h_results(matchups)
        
        # Calculate performance results (top half vs bottom half)
        performance_results = self._calculate_performance_results(week_scores)
        
        # Combine results
        combined_results = self._combine_results(h2h_results, performance_results, week_scores)
        
        week_data = {
            'week': week,
            'date_calculated': datetime.now().isoformat(),
            'team_results': combined_results,
            'week_summary': self._generate_week_summary(combined_results, week_scores)
        }
        
        return week_data
    
    def _is_invalid_week_data(self, week_scores: List[Dict]) -> bool:
        """Check if week data is invalid (all zero scores)
        
        Args:
            week_scores: List of team scores for the week
            
        Returns:
            True if week data appears invalid, False otherwise
        """
        if not week_scores:
            return True
        
        # Check if all scores are zero
        all_zero = all(team['score'] == 0.0 for team in week_scores)
        return all_zero
    
    def _calculate_h2h_results(self, matchups: List[Dict]) -> Dict[str, str]:
        """Calculate head-to-head win/loss results
        
        Returns:
            Dictionary mapping team_id to 'W' or 'L'
        """
        h2h_results = {}
        
        for matchup in matchups:
            team1 = matchup['team1']
            team2 = matchup['team2']
            
            team1_score = float(team1['points'])
            team2_score = float(team2['points'])
            
            if team1_score > team2_score:
                h2h_results[team1['team_id']] = 'W'
                h2h_results[team2['team_id']] = 'L'
            elif team2_score > team1_score:
                h2h_results[team1['team_id']] = 'L'
                h2h_results[team2['team_id']] = 'W'
            else:
                # Tie
                h2h_results[team1['team_id']] = 'T'
                h2h_results[team2['team_id']] = 'T'
        
        return h2h_results
    
    def _calculate_performance_results(self, week_scores: List[Dict]) -> Dict[str, float]:
        """Calculate performance-based win/loss results with tie handling
        
        Teams in top half get 1.0 (win), bottom half get 0.0 (loss).
        Teams tied at the boundary split the points.
        
        Returns:
            Dictionary mapping team_id to performance wins (float between 0.0 and 1.0)
        """
        # Scores should already be sorted by score descending
        sorted_scores = sorted(week_scores, key=lambda x: x['score'], reverse=True)
        
        num_teams = len(sorted_scores)
        top_half_size = num_teams // 2
        
        performance_results = {}
        
        # Group teams by score to handle ties
        score_groups = {}
        for i, team_data in enumerate(sorted_scores):
            score = team_data['score']
            if score not in score_groups:
                score_groups[score] = []
            score_groups[score].append((i, team_data['team_id']))
        
        # Process each score group
        for score, teams_with_positions in score_groups.items():
            positions = [pos for pos, _ in teams_with_positions]
            team_ids = [team_id for _, team_id in teams_with_positions]
            
            # Check if this group straddles the top/bottom half boundary
            min_pos = min(positions)
            max_pos = max(positions)
            
            if max_pos < top_half_size:
                # All teams in this group are in top half - all get wins
                for team_id in team_ids:
                    performance_results[team_id] = 1.0
            elif min_pos >= top_half_size:
                # All teams in this group are in bottom half - all get losses
                for team_id in team_ids:
                    performance_results[team_id] = 0.0
            else:
                # Group straddles the boundary - split the points
                teams_in_top = sum(1 for pos in positions if pos < top_half_size)
                teams_in_bottom = len(teams_with_positions) - teams_in_top
                
                # Calculate the split: each team gets the average of wins they would get
                total_wins = teams_in_top * 1.0 + teams_in_bottom * 0.0
                wins_per_team = total_wins / len(teams_with_positions)
                
                for team_id in team_ids:
                    performance_results[team_id] = wins_per_team
        
        return performance_results
    
    def _combine_results(self, h2h_results: Dict[str, str], 
                        performance_results: Dict[str, float],
                        week_scores: List[Dict]) -> List[Dict[str, Any]]:
        """Combine head-to-head and performance results
        
        Returns:
            List of team results with combined scoring
        """
        combined_results = []
        
        # Create a mapping for easy team data lookup
        team_score_map = {team['team_id']: team for team in week_scores}
        
        for team_id in h2h_results:
            if team_id not in team_score_map:
                continue
                
            team_data = team_score_map[team_id]
            h2h_result = h2h_results[team_id]
            performance_wins_float = performance_results[team_id]
            
            # Calculate wins and losses
            h2h_wins = 1 if h2h_result == 'W' else 0
            h2h_losses = 1 if h2h_result == 'L' else 0
            h2h_ties = 1 if h2h_result == 'T' else 0
            
            # Performance results are now float values (0.0 to 1.0)
            performance_wins = performance_wins_float
            performance_losses = 1.0 - performance_wins_float
            
            total_wins = h2h_wins + performance_wins
            total_losses = h2h_losses + performance_losses
            
            # Convert performance result back to display format
            if performance_wins_float == 1.0:
                performance_result_display = 'W'
            elif performance_wins_float == 0.0:
                performance_result_display = 'L'
            else:
                performance_result_display = f'T({performance_wins_float:.1f})'
            
            team_result = {
                'team_id': team_id,
                'team_name': team_data['team_name'],
                'team_key': team_data['team_key'],
                'week_score': team_data['score'],
                'h2h_result': h2h_result,
                'performance_result': performance_result_display,
                'h2h_wins': h2h_wins,
                'h2h_losses': h2h_losses,
                'h2h_ties': h2h_ties,
                'performance_wins': performance_wins,
                'performance_losses': performance_losses,
                'total_wins': total_wins,
                'total_losses': total_losses,
                'victory_points': total_wins  # Alternative name for total wins
            }
            
            combined_results.append(team_result)
        
        # Sort by total wins (victory points) descending, then by score
        combined_results.sort(key=lambda x: (x['total_wins'], x['week_score']), reverse=True)
        
        return combined_results
    
    def _generate_week_summary(self, results: List[Dict], week_scores: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics for the week"""
        if not results:
            return {}
        
        week = week_scores[0]['week'] if week_scores else 1
        scores = [team['week_score'] for team in results]
        
        summary = {
            'week': week,
            'total_teams': len(results),
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0,
            'average_score': sum(scores) / len(scores) if scores else 0,
            'perfect_weeks': len([team for team in results if team['total_wins'] == 2]),
            'winless_weeks': len([team for team in results if team['total_wins'] == 0])
        }
        
        return summary
    
    def calculate_season_standings(self, weeks_data: List[Dict]) -> Dict[str, Any]:
        """Calculate cumulative season standings from multiple weeks
        
        Args:
            weeks_data: List of week result dictionaries
            
        Returns:
            Season standings dictionary
        """
        if not weeks_data:
            return {}
        
        # Sort weeks data by week number to ensure proper ordering
        weeks_data_sorted = sorted(weeks_data, key=lambda x: x['week'])
        
        # Initialize team totals
        team_totals = {}
        
        for week_data in weeks_data_sorted:
            for team_result in week_data['team_results']:
                team_id = team_result['team_id']
                
                if team_id not in team_totals:
                    team_totals[team_id] = {
                        'team_id': team_id,
                        'team_name': team_result['team_name'],
                        'team_key': team_result['team_key'],
                        'total_h2h_wins': 0,
                        'total_h2h_losses': 0,
                        'total_h2h_ties': 0,
                        'total_performance_wins': 0,
                        'total_performance_losses': 0,
                        'total_wins': 0,
                        'total_losses': 0,
                        'total_points': 0,
                        'weeks_played': 0,
                        'recent_scores': []  # Track recent week scores for tiebreaking
                    }
                
                # Add week totals
                totals = team_totals[team_id]
                totals['total_h2h_wins'] += team_result['h2h_wins']
                totals['total_h2h_losses'] += team_result['h2h_losses']
                totals['total_h2h_ties'] += team_result['h2h_ties']
                totals['total_performance_wins'] += team_result['performance_wins']
                totals['total_performance_losses'] += team_result['performance_losses']
                totals['total_wins'] += team_result['total_wins']
                totals['total_losses'] += team_result['total_losses']
                totals['total_points'] += team_result['week_score']
                totals['weeks_played'] += 1
                
                # Store week score for tiebreaking (most recent first)
                totals['recent_scores'].append({
                    'week': week_data['week'],
                    'score': team_result['week_score']
                })
        
        # Sort recent scores by week (most recent first) for each team
        for team_id, totals in team_totals.items():
            totals['recent_scores'].sort(key=lambda x: x['week'], reverse=True)
        
        # Calculate additional stats
        for team_id, totals in team_totals.items():
            weeks_played = totals['weeks_played']
            if weeks_played > 0:
                totals['average_score'] = totals['total_points'] / weeks_played
                totals['win_percentage'] = totals['total_wins'] / (weeks_played * 2)  # Max 2 wins per week
            else:
                totals['average_score'] = 0
                totals['win_percentage'] = 0
        
        # Enhanced tiebreaker system following Yahoo Fantasy Football standards
        standings = list(team_totals.values())
        standings.sort(key=lambda x: self._create_tiebreaker_key(x), reverse=True)
        
        # Add ranking
        for i, team in enumerate(standings):
            team['rank'] = i + 1
        
        season_standings = {
            'last_updated': datetime.now().isoformat(),
            'weeks_included': len(weeks_data_sorted),
            'standings': standings,
            'season_summary': self._generate_season_summary(standings, weeks_data_sorted)
        }
        
        return season_standings
    
    def _create_tiebreaker_key(self, team: Dict[str, Any]) -> Tuple:
        """Create a tiebreaker key following Yahoo Fantasy Football standards
        
        Tiebreaker hierarchy:
        1. Total Victory Points (total_wins) - Primary ranking criteria
        2. Total Fantasy Points (total_points) - Yahoo's #1 tiebreaker  
        3. Most Recent Week Score - Yahoo's #2 tiebreaker
        4. Second Most Recent Week Score - Yahoo's #3 tiebreaker
        5. Continue back through all weeks - Yahoo's pattern
        
        Args:
            team: Team dictionary with stats and recent_scores
            
        Returns:
            Tuple for sorting (higher values rank better)
        """
        tiebreaker_key = [
            team['total_wins'],      # Primary: Victory Points
            team['total_points'],    # Secondary: Total points (Yahoo standard)
        ]
        
        # Add recent week scores in chronological order (most recent first)
        # This follows Yahoo's pattern of going back week by week
        recent_scores = team.get('recent_scores', [])
        for week_score in recent_scores:
            tiebreaker_key.append(week_score['score'])
        
        # Pad with zeros if team has fewer weeks (shouldn't happen in practice)
        # This ensures all teams have the same number of tiebreaker elements
        max_weeks = 18  # Standard NFL season length
        while len(tiebreaker_key) < (2 + max_weeks):
            tiebreaker_key.append(0.0)
        
        return tuple(tiebreaker_key)
    
    def _generate_season_summary(self, standings: List[Dict], weeks_data: List[Dict]) -> Dict[str, Any]:
        """Generate season summary statistics"""
        if not standings:
            return {}
        
        total_weeks = len(weeks_data)
        
        summary = {
            'total_weeks': total_weeks,
            'total_teams': len(standings),
            'leader': standings[0]['team_name'] if standings else 'Unknown',
            'leader_wins': standings[0]['total_wins'] if standings else 0,
            'most_points': max(standings, key=lambda x: x['total_points'])['team_name'] if standings else 'Unknown',
            'highest_total_points': max(standings, key=lambda x: x['total_points'])['total_points'] if standings else 0
        }
        
        return summary
    
    def save_week_data(self, week_data: Dict[str, Any]) -> str:
        """Save week data to JSON file
        
        Returns:
            Path to saved file
        """
        week = week_data['week']
        filename = f"week_{week:02d}_results.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(week_data, f, indent=2)
        
        logger.info(f"Saved week {week} data to {filepath}")
        return str(filepath)
    
    def save_season_standings(self, standings_data: Dict[str, Any]) -> str:
        """Save season standings to JSON file
        
        Returns:
            Path to saved file
        """
        filename = "season_standings.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(standings_data, f, indent=2)
        
        logger.info(f"Saved season standings to {filepath}")
        return str(filepath)
    
    def load_all_weeks_data(self) -> List[Dict[str, Any]]:
        """Load all existing week data files
        
        Returns:
            List of week data dictionaries, sorted by week, excluding invalid weeks
        """
        weeks_data = []
        
        for json_file in self.output_dir.glob("week_*_results.json"):
            try:
                with open(json_file, 'r') as f:
                    week_data = json.load(f)
                    
                    # Check if this week has valid data by examining scores
                    team_results = week_data.get('team_results', [])
                    if team_results:
                        # Create a simplified score list to check validity
                        week_scores = [{'score': team['week_score']} for team in team_results]
                        if not self._is_invalid_week_data(week_scores):
                            weeks_data.append(week_data)
                        else:
                            logger.info(f"Skipping invalid week data from {json_file}")
                    
            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")
        
        # Sort by week number
        weeks_data.sort(key=lambda x: x['week'])
        return weeks_data
