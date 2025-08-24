#!/usr/bin/env python3
"""
Setup script for Victory Points Fantasy Football project
Helps configure the Yahoo API credentials and test the connection
"""

import os
import json
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    env_template_path = Path("env.template")
    env_path = Path(".env")
    
    if env_path.exists():
        print("✓ .env file already exists")
        return
    
    if not env_template_path.exists():
        print("❌ env.template file not found")
        return
    
    # Copy template to .env
    with open(env_template_path, 'r') as template:
        content = template.read()
    
    with open(env_path, 'w') as env_file:
        env_file.write(content)
    
    print("✓ Created .env file from template")
    print("📝 Please edit .env file with your Yahoo API credentials")

def create_config_file():
    """Create config file from template"""
    config_template_path = Path("config/yahoo_config_template.json")
    config_path = Path("config/yahoo_config.json")
    
    if config_path.exists():
        print("✓ yahoo_config.json already exists")
        return
    
    if not config_template_path.exists():
        print("❌ yahoo_config_template.json not found")
        return
    
    # Copy template to config
    with open(config_template_path, 'r') as template:
        config_data = json.load(template)
    
    with open(config_path, 'w') as config_file:
        json.dump(config_data, config_file, indent=2)
    
    print("✓ Created yahoo_config.json from template")
    print("📝 Please edit config/yahoo_config.json with your credentials")

def check_dependencies():
    """Check if required Python packages are installed"""
    try:
        import yfpy
        print("✓ yfpy is installed")
    except ImportError:
        print("❌ yfpy not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        import pandas
        print("✓ pandas is installed")
    except ImportError:
        print("❌ pandas not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv is installed")
    except ImportError:
        print("❌ python-dotenv not found. Run: pip install -r requirements.txt")
        return False
    
    return True

def test_yahoo_connection():
    """Test connection to Yahoo API"""
    try:
        sys.path.append('scripts')
        from yahoo_client import YahooFantasyClient
        
        print("\n🔌 Testing Yahoo API connection...")
        
        client = YahooFantasyClient()
        league_info = client.get_league_info()
        
        print(f"✓ Successfully connected to league: {league_info['name']}")
        print(f"  Season: {league_info['season']}")
        print(f"  Teams: {league_info['num_teams']}")
        print(f"  Current Week: {league_info['current_week']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Yahoo API: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you've set up your Yahoo Developer App")
        print("2. Check your credentials in .env or config/yahoo_config.json")
        print("3. Ensure your league ID is correct")
        return False

def show_yahoo_setup_instructions():
    """Show instructions for setting up Yahoo Developer App"""
    print("\n" + "="*60)
    print("YAHOO DEVELOPER SETUP INSTRUCTIONS")
    print("="*60)
    print("""
1. Go to https://developer.yahoo.com/apps/create/
2. Create a new application:
   - Application Name: Victory Points Fantasy
   - Application Type: Web Application
   - Description: Custom fantasy football scoring
   - Home Page URL: http://localhost (or your domain)
   - Redirect URI: oob (out of band)
3. Select API Permissions:
   - Fantasy Sports: Read/Write
4. Create the app and note your:
   - Client ID (Consumer Key)
   - Client Secret (Consumer Secret)
5. Find your League ID:
   - Go to your Yahoo Fantasy league
   - Look at the URL: https://football.fantasysports.yahoo.com/f1/XXXXXXX
   - The number after f1/ is your League ID
""")

def main():
    """Main setup function"""
    print("🏈 Victory Points Fantasy Football Setup")
    print("="*50)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Create necessary files
    create_env_file()
    create_config_file()
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n💡 Install dependencies with: pip install -r requirements.txt")
        return
    
    # Show setup instructions
    show_yahoo_setup_instructions()
    
    # Check for credentials
    env_path = Path(".env")
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv()
        
        consumer_key = os.getenv('YAHOO_CONSUMER_KEY')
        league_id = os.getenv('LEAGUE_ID')
        
        if consumer_key and consumer_key != 'your_consumer_key_here' and league_id and league_id != 'your_league_id_here':
            # Credentials seem to be configured, test connection
            if test_yahoo_connection():
                print("\n🎉 Setup complete! You can now run:")
                print("   python scripts/fetch_data.py --week 1")
                print("   # or")
                print("   python scripts/fetch_data.py --all-weeks")
            else:
                print("\n🔧 Please check your credentials and try again")
        else:
            print("\n📝 Please configure your credentials in .env file, then run:")
            print("   python setup.py")
    else:
        print("\n📝 Please configure your credentials in .env file, then run:")
        print("   python setup.py")

if __name__ == "__main__":
    main()
