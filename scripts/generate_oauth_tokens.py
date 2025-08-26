#!/usr/bin/env python3
"""
OAuth Token Generator for Yahoo Fantasy API

This script helps you generate OAuth tokens locally that can be used
in non-interactive environments like GitHub Actions.

Run this script locally after setting up your Yahoo API credentials.
It will guide you through the OAuth flow and output the tokens you need
to add as GitHub Secrets.
"""

import os
import sys
from pathlib import Path
import logging

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from yfpy import YahooFantasySportsQuery

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_tokens():
    """Generate OAuth tokens for Yahoo Fantasy API"""
    
    print("🔐 Yahoo Fantasy OAuth Token Generator")
    print("=" * 50)
    
    # Get credentials from environment or user input
    consumer_key = os.getenv('YAHOO_CONSUMER_KEY')
    consumer_secret = os.getenv('YAHOO_CONSUMER_SECRET')
    league_id = os.getenv('LEAGUE_ID')
    
    if not consumer_key:
        consumer_key = input("Enter your Yahoo Consumer Key: ").strip()
    if not consumer_secret:
        consumer_secret = input("Enter your Yahoo Consumer Secret: ").strip()
    if not league_id:
        league_id = input("Enter your League ID: ").strip()
    
    if not all([consumer_key, consumer_secret, league_id]):
        print("❌ Missing required credentials!")
        return False
    
    try:
        print("\n🚀 Starting OAuth flow...")
        print("📱 Your browser will open for Yahoo authentication")
        print("🔗 After authorizing, you'll get a verification code")
        
        # Create auth directory
        auth_dir = Path("config/auth")
        auth_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Yahoo client with browser OAuth
        yahoo_query = YahooFantasySportsQuery(
            league_id=league_id,
            game_code='nfl',
            game_id=None,
            yahoo_consumer_key=consumer_key,
            yahoo_consumer_secret=consumer_secret,
            env_file_location=Path.cwd(),
            save_token_data_to_env_file=True,
            browser_callback=True
        )
        
        # Test the connection by getting league info
        print("\n🏈 Testing connection...")
        league = yahoo_query.get_league_info()
        print(f"✅ Successfully connected to league: {league.name}")
        
        # Read the generated tokens from .env file
        load_dotenv(override=True)  # Reload to get new tokens
        
        # Collect all OAuth tokens that yfpy generates
        oauth_tokens = {
            'YAHOO_ACCESS_TOKEN': os.getenv('YAHOO_ACCESS_TOKEN'),
            'YAHOO_REFRESH_TOKEN': os.getenv('YAHOO_REFRESH_TOKEN'),
            'YAHOO_GUID': os.getenv('YAHOO_GUID'),
            'YAHOO_TOKEN_TIME': os.getenv('YAHOO_TOKEN_TIME'),
            'YAHOO_TOKEN_TYPE': os.getenv('YAHOO_TOKEN_TYPE')
        }
        
        # Check if we got the essential tokens
        if oauth_tokens['YAHOO_ACCESS_TOKEN'] and oauth_tokens['YAHOO_REFRESH_TOKEN']:
            print("\n🎉 OAuth tokens generated successfully!")
            print("=" * 60)
            print("📋 Add these as GitHub Secrets:")
            
            # Display all tokens that were found
            for key, value in oauth_tokens.items():
                if value:  # Only show non-empty values
                    print(f"   {key}: {value}")
                else:
                    print(f"   {key}: (not found - will use default)")
            
            print("\n🔧 Steps to add GitHub Secrets:")
            print("   1. Go to your GitHub repository")
            print("   2. Settings → Secrets and variables → Actions")
            print("   3. Click 'New repository secret'")
            print("   4. Add all the tokens shown above")
            print("   Note: If a token shows '(not found)', you can skip adding it")
            
            print("\n📝 Required Secrets Summary:")
            print("   - YAHOO_CONSUMER_KEY (you already have this)")
            print("   - YAHOO_CONSUMER_SECRET (you already have this)")
            print("   - LEAGUE_ID (you already have this)")
            for key, value in oauth_tokens.items():
                status = "✅ FOUND" if value else "⚠️  Optional"
                print(f"   - {key}: {status}")
            
            print("\n✅ Your GitHub Action should now work!")
            return True
        else:
            print("❌ Failed to generate essential tokens (ACCESS_TOKEN or REFRESH_TOKEN)")
            print("Check your Yahoo API credentials and try again.")
            return False
            
    except Exception as e:
        print(f"❌ Error during OAuth flow: {e}")
        return False


if __name__ == "__main__":
    success = generate_tokens()
    sys.exit(0 if success else 1)
