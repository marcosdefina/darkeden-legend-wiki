#!/usr/bin/env python3
"""
Fandom Authentication Tester
Tests different authentication methods to find what works with your Fandom wiki.
"""

import requests
import mwclient
import json
import sys

def test_manual_login(wiki_url, username, password):
    """Test manual login using requests to get login token"""
    print(f"\n=== Testing Manual Login Method ===")
    
    try:
        base_url = f"https://{wiki_url}"
        api_url = f"{base_url}/api.php"
        
        # Step 1: Get login token
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'FandomAuthTester/1.0 (Contact: admin@example.com)'
        })
        
        print("Getting login token...")
        token_params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json'
        }
        
        token_response = session.get(api_url, params=token_params)
        token_data = token_response.json()
        
        if 'query' not in token_data or 'tokens' not in token_data['query']:
            print(f"❌ Failed to get login token: {token_data}")
            return False
            
        login_token = token_data['query']['tokens']['logintoken']
        print(f"✓ Got login token: {login_token[:20]}...")
        
        # Step 2: Attempt login
        print(f"Attempting login with: {username}")
        login_params = {
            'action': 'login',
            'lgname': username,
            'lgpassword': password,
            'lgtoken': login_token,
            'format': 'json'
        }
        
        login_response = session.post(api_url, data=login_params)
        login_data = login_response.json()
        
        print(f"Login response: {json.dumps(login_data, indent=2)}")
        
        if login_data.get('login', {}).get('result') == 'Success':
            print("✓ Manual login successful!")
            
            # Test getting user info
            user_params = {
                'action': 'query',
                'meta': 'userinfo',
                'uiprop': 'rights|groups',
                'format': 'json'
            }
            user_response = session.get(api_url, params=user_params)
            user_data = user_response.json()
            
            print(f"User info: {json.dumps(user_data, indent=2)}")
            return True
        else:
            print(f"❌ Manual login failed: {login_data}")
            return False
            
    except Exception as e:
        print(f"❌ Manual login error: {e}")
        return False

def test_mwclient_methods(wiki_url, username, password):
    """Test different mwclient authentication methods"""
    print(f"\n=== Testing mwclient Methods ===")
    
    methods = [
        ("Standard", {}),
        ("Force Login", {'force_login': True}),
        ("Custom User Agent", {'force_login': False}),
    ]
    
    for method_name, kwargs in methods:
        try:
            print(f"\nTrying {method_name}...")
            
            if method_name == "Custom User Agent":
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'FandomAuthTester/1.0 (Contact: admin@example.com)'
                })
                kwargs['pool'] = session
            
            site = mwclient.Site(
                wiki_url,
                path='/',
                scheme='https',
                retry_timeout=30,
                **kwargs
            )
            
            print(f"  Attempting login: {username}")
            result = site.login(username, password)
            
            if result:
                print(f"  ✓ {method_name} login successful!")
                
                # Test API call
                try:
                    user_info = site.api('query', meta='userinfo', uiprop='rights')
                    rights = user_info['query']['userinfo'].get('rights', [])
                    print(f"  User rights: {', '.join(rights[:5])}...")
                    
                    if 'upload' in rights:
                        print(f"  ✓ Upload permission confirmed!")
                    else:
                        print(f"  ⚠ Upload permission missing")
                    
                    return True
                except Exception as api_error:
                    print(f"  ⚠ Login successful but API test failed: {api_error}")
                    return True
            else:
                print(f"  ❌ {method_name} login failed")
                
        except Exception as e:
            print(f"  ❌ {method_name} error: {e}")
    
    return False

def test_alternative_format(wiki_url, base_username, bot_name, bot_password):
    """Test the alternative username format mentioned in bot creation"""
    print(f"\n=== Testing Alternative Format ===")
    print(f"Base username: {base_username}")
    print(f"Bot password format: {bot_name}@{bot_password}")
    
    try:
        site = mwclient.Site(
            wiki_url,
            path='/',
            scheme='https',
            retry_timeout=30
        )
        
        # Try the alternative format mentioned in the bot creation
        alt_password = f"{bot_name}@{bot_password}"
        print(f"Trying login with username: {base_username}, password: {alt_password[:20]}...")
        
        result = site.login(base_username, alt_password)
        
        if result:
            print("✓ Alternative format login successful!")
            return True
        else:
            print("❌ Alternative format login failed")
            return False
            
    except Exception as e:
        print(f"❌ Alternative format error: {e}")
        return False

def main():
    # Your credentials
    wiki_url = "darkeden-legend.fandom.com"
    bot_username = "MarcosDefina@darkeden-legend-bot"
    bot_password = "101qih0ro6e83irtfa663j7fea7lqp5j"
    
    # Extract parts for alternative testing
    base_username = "MarcosDefina"
    bot_name = "darkeden-legend-bot"
    
    print("🔍 Fandom Authentication Diagnostic Tool")
    print("=" * 50)
    print(f"Wiki: {wiki_url}")
    print(f"Bot Username: {bot_username}")
    print(f"Bot Password: {bot_password[:10]}...")
    
    # Test methods
    success = False
    
    # Test 1: Manual API login
    if test_manual_login(wiki_url, bot_username, bot_password):
        success = True
    
    # Test 2: Different mwclient methods
    if test_mwclient_methods(wiki_url, bot_username, bot_password):
        success = True
    
    # Test 3: Alternative format
    if test_alternative_format(wiki_url, base_username, bot_name, bot_password):
        success = True
    
    print(f"\n{'='*50}")
    if success:
        print("✅ At least one authentication method worked!")
        print("Use the successful method in your upload script.")
    else:
        print("❌ All authentication methods failed.")
        print("\nTroubleshooting suggestions:")
        print("1. Verify the bot password is correct")
        print("2. Check if the bot has the right permissions")
        print("3. Try creating a new bot password")
        print("4. Contact the wiki administrators")
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
