"""
IR Compliance Checker
Checks each team's IR slot to ensure players are properly designated according to league rules
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent))

from yahoo_client import YahooFantasyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IRComplianceChecker:
    """Checks IR slot compliance across all teams in the league"""
    
    def __init__(self, yahoo_client: YahooFantasyClient):
        """Initialize the IR compliance checker
        
        Args:
            yahoo_client: Configured Yahoo Fantasy client
        """
        self.yahoo_client = yahoo_client
        self.ir_eligible_statuses = [
            'IR',    # Injured Reserve
            'IR-R',  # Injured Reserve - Return
            'O',     # Out
            'PUP',   # Physically Unable to Perform
            'PUP-R', # Physically Unable to Perform - Return
            'NFI',   # Non-Football Injury
            'NFI-R', # Non-Football Injury - Return
            'SUSP',  # Suspended (some leagues allow this)
            'NA'     # Not Active
        ]
        
        # Get league-specific IR eligibility rules from environment if available
        custom_statuses = os.getenv('IR_ELIGIBLE_STATUSES')
        if custom_statuses:
            self.ir_eligible_statuses = [status.strip() for status in custom_statuses.split(',')]
            logger.info(f"Using custom IR eligible statuses: {self.ir_eligible_statuses}")
    
    def check_all_teams(self, week: Optional[int] = None) -> Dict[str, Any]:
        """Check IR compliance for all teams in the league
        
        Args:
            week: Week number to check (defaults to current week)
            
        Returns:
            Dictionary containing compliance report
        """
        try:
            if week is None:
                week = self.yahoo_client.get_current_week()
            
            logger.info(f"Checking IR compliance for week {week}")
            
            # Get all team rosters
            rosters = self.yahoo_client.get_all_team_rosters(week)
            
            compliance_report = {
                'check_date': datetime.now().isoformat(),
                'week': week,
                'total_teams': len(rosters),
                'violations': [],
                'compliant_teams': [],
                'summary': {
                    'total_violations': 0,
                    'teams_with_violations': 0,
                    'compliant_teams': 0
                }
            }
            
            for roster in rosters:
                team_violations = self._check_team_compliance(roster)
                
                if team_violations:
                    compliance_report['violations'].append({
                        'team_id': roster['team_id'],
                        'team_name': roster['team_name'],
                        'manager': roster['manager'],
                        'violations': team_violations,
                        'violation_count': len(team_violations)
                    })
                    compliance_report['summary']['total_violations'] += len(team_violations)
                else:
                    compliance_report['compliant_teams'].append({
                        'team_id': roster['team_id'],
                        'team_name': roster['team_name'],
                        'manager': roster['manager'],
                        'ir_players_count': len(roster['ir_players'])
                    })
            
            # Update summary
            compliance_report['summary']['teams_with_violations'] = len(compliance_report['violations'])
            compliance_report['summary']['compliant_teams'] = len(compliance_report['compliant_teams'])
            
            logger.info(f"IR compliance check complete: {compliance_report['summary']['total_violations']} violations found")
            
            return compliance_report
            
        except Exception as e:
            logger.error(f"Failed to check IR compliance: {e}")
            raise
    
    def _check_team_compliance(self, roster: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check IR compliance for a single team
        
        Args:
            roster: Team roster data
            
        Returns:
            List of violations found for this team
        """
        violations = []
        
        for ir_player in roster['ir_players']:
            # Check if player's current status allows IR slot
            is_eligible = self._is_player_ir_eligible(ir_player)
            
            if not is_eligible:
                violation = {
                    'player_name': ir_player['name'],
                    'player_key': ir_player['player_key'],
                    'current_status': ir_player['status'],
                    'eligible_statuses': self.ir_eligible_statuses,
                    'injury_note': ir_player.get('injury_note', ''),
                    'violation_type': 'ineligible_status',
                    'description': f"Player {ir_player['name']} has status '{ir_player['status']}' which is not eligible for IR slot"
                }
                violations.append(violation)
        
        return violations
    
    def _is_player_ir_eligible(self, player: Dict[str, Any]) -> bool:
        """Check if a player is eligible for the IR slot
        
        Args:
            player: Player data dictionary
            
        Returns:
            True if player is eligible for IR slot, False otherwise
        """
        player_status = player.get('status', '').upper()
        
        # Handle empty or unknown status
        if not player_status or player_status in ['', 'UNKNOWN', 'ACTIVE']:
            return False
        
        # Check if status is in the eligible list
        return player_status in [status.upper() for status in self.ir_eligible_statuses]
    
    def generate_email_report(self, compliance_report: Dict[str, Any]) -> str:
        """Generate a formatted email report from compliance data
        
        Args:
            compliance_report: Compliance report data
            
        Returns:
            Formatted email body as string
        """
        week = compliance_report['week']
        total_violations = compliance_report['summary']['total_violations']
        teams_with_violations = compliance_report['summary']['teams_with_violations']
        
        if total_violations == 0:
            subject = f"✅ IR Compliance Check - Week {week}: All Teams Compliant"
            body = f"""
**Fantasy Football IR Compliance Report - Week {week}**

🎉 **GREAT NEWS!** All teams are in compliance with IR slot rules.

**Summary:**
- Total Teams Checked: {compliance_report['total_teams']}
- Teams in Compliance: {compliance_report['summary']['compliant_teams']}
- Violations Found: 0

**Teams with IR Players (All Compliant):**
"""
            for team in compliance_report['compliant_teams']:
                if team['ir_players_count'] > 0:
                    body += f"- {team['team_name']} ({team['manager']}): {team['ir_players_count']} IR player(s)\n"
            
            body += f"""

**IR Eligible Statuses:** {', '.join(self.ir_eligible_statuses)}

*Report generated on {compliance_report['check_date']}*
"""
        else:
            subject = f"⚠️ IR Compliance Violations - Week {week}: {total_violations} Violation(s) Found"
            body = f"""
**Fantasy Football IR Compliance Report - Week {week}**

⚠️ **VIOLATIONS DETECTED** - Immediate attention required!

**Summary:**
- Total Teams Checked: {compliance_report['total_teams']}
- Teams with Violations: {teams_with_violations}
- Total Violations: {total_violations}

**VIOLATIONS DETAILS:**

"""
            for team_violation in compliance_report['violations']:
                body += f"**{team_violation['team_name']} ({team_violation['manager']})**\n"
                body += f"Violations: {team_violation['violation_count']}\n\n"
                
                for violation in team_violation['violations']:
                    body += f"  • **{violation['player_name']}**\n"
                    body += f"    - Current Status: {violation['current_status']}\n"
                    body += f"    - Issue: {violation['description']}\n"
                    if violation.get('injury_note'):
                        body += f"    - Injury Note: {violation['injury_note']}\n"
                    body += "\n"
            
            if compliance_report['compliant_teams']:
                body += "**Compliant Teams:**\n"
                for team in compliance_report['compliant_teams']:
                    body += f"- {team['team_name']} ({team['manager']})\n"
                body += "\n"
            
            body += f"""**IR Eligible Statuses:** {', '.join(self.ir_eligible_statuses)}

**ACTION REQUIRED:**
Please contact the teams with violations to correct their IR slot usage. Players must be moved out of the IR slot if they no longer qualify.

*Report generated on {compliance_report['check_date']}*
"""
        
        return subject, body
    
    def save_report(self, compliance_report: Dict[str, Any], output_dir: str = "data") -> str:
        """Save compliance report to JSON file
        
        Args:
            compliance_report: Compliance report data
            output_dir: Directory to save the report
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        week = compliance_report['week']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ir_compliance_week_{week:02d}_{timestamp}.json"
        filepath = output_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(compliance_report, f, indent=2)
        
        logger.info(f"Saved IR compliance report to {filepath}")
        return str(filepath)


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check IR slot compliance for fantasy football league')
    parser.add_argument('--week', type=int, help='Week number to check (default: current week)')
    parser.add_argument('--output-dir', type=str, default='data', help='Output directory for reports')
    parser.add_argument('--save-report', action='store_true', help='Save report to JSON file')
    parser.add_argument('--email-report', action='store_true', help='Generate email report format')
    
    args = parser.parse_args()
    
    try:
        # Initialize Yahoo client
        logger.info("Initializing Yahoo Fantasy client...")
        yahoo_client = YahooFantasyClient()
        
        # Initialize compliance checker
        checker = IRComplianceChecker(yahoo_client)
        
        # Run compliance check
        compliance_report = checker.check_all_teams(args.week)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"IR COMPLIANCE CHECK - Week {compliance_report['week']}")
        print(f"{'='*60}")
        print(f"Total Teams: {compliance_report['summary']['total_teams']}")
        print(f"Violations Found: {compliance_report['summary']['total_violations']}")
        print(f"Teams with Violations: {compliance_report['summary']['teams_with_violations']}")
        print(f"Compliant Teams: {compliance_report['summary']['compliant_teams']}")
        
        if compliance_report['violations']:
            print(f"\n⚠️ VIOLATIONS DETECTED:")
            for team_violation in compliance_report['violations']:
                print(f"\n{team_violation['team_name']} ({team_violation['manager']}):")
                for violation in team_violation['violations']:
                    print(f"  • {violation['player_name']} - Status: {violation['current_status']}")
        else:
            print(f"\n✅ All teams are in compliance!")
        
        # Save report if requested
        if args.save_report:
            report_path = checker.save_report(compliance_report, args.output_dir)
            print(f"\n📄 Report saved to: {report_path}")
        
        # Generate email report if requested
        if args.email_report:
            subject, body = checker.generate_email_report(compliance_report)
            print(f"\n📧 EMAIL REPORT:")
            print(f"Subject: {subject}")
            print(f"\nBody:\n{body}")
        
        return 0 if compliance_report['summary']['total_violations'] == 0 else 1
        
    except Exception as e:
        logger.error(f"IR compliance check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
