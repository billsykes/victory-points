#!/usr/bin/env python3
"""
Website Configuration Generator
Generates configuration file for the frontend based on environment variables
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file if it exists"""
    env_vars = {}
    env_file = Path(env_path)
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars


def get_config_value(key: str, env_vars: Dict[str, str]) -> Optional[str]:
    """Get configuration value from environment variables or .env file"""
    # First check environment variables
    value = os.environ.get(key)
    if value:
        return value
    
    # Then check .env file
    value = env_vars.get(key)
    if value and value != "":
        return value
    
    return None


def generate_league_url(league_id: str) -> str:
    """Generate Yahoo Fantasy League URL from league ID"""
    if not league_id or league_id == "your_league_id_here":
        return ""
    
    return f"https://football.fantasysports.yahoo.com/f1/{league_id}/"


def generate_website_config(output_dir: str = "data") -> str:
    """Generate website configuration file
    
    Args:
        output_dir: Directory to save configuration file
        
    Returns:
        Path to generated configuration file
    """
    # Load environment variables from .env file
    env_vars = load_env_file()
    
    # Get configuration values
    league_id = get_config_value("LEAGUE_ID", env_vars)
    league_rules_url = get_config_value("LEAGUE_RULES_URL", env_vars)
    
    config = {
        "league": {
            "id": league_id,
            "url": generate_league_url(league_id) if league_id else "",
            "rules_url": league_rules_url or ""
        },
        "features": {
            "show_league_link": bool(league_id and league_id != "your_league_id_here"),
            "show_rules_link": bool(league_rules_url and league_rules_url.strip())
        },
        "generated_at": "{{ generated_timestamp }}"
    }
    
    # Replace timestamp placeholder and add run timestamp for git change detection
    from datetime import datetime
    now = datetime.now()
    config["generated_at"] = now.isoformat()
    config["run_timestamp"] = int(now.timestamp() * 1000000)  # Microsecond precision for uniqueness
    config["run_uuid"] = str(hash(now.isoformat() + str(now.microsecond)))  # Additional uniqueness
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save configuration file
    config_file = output_path / "website_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Generated website configuration: {config_file}")
    logger.info(f"League URL: {config['league']['url'] or 'Not configured'}")
    logger.info(f"Rules URL: {config['league']['rules_url'] or 'Not configured'}")
    
    return str(config_file)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate website configuration from environment variables')
    parser.add_argument('--output-dir', type=str, default='data', 
                       help='Output directory for configuration file')
    
    args = parser.parse_args()
    
    try:
        config_path = generate_website_config(args.output_dir)
        print(f"Configuration generated: {config_path}")
        return 0
    except Exception as e:
        logger.error(f"Failed to generate configuration: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
