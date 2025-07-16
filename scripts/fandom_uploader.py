#!/usr/bin/env python3
"""
Fandom Wiki Image Uploader
Uploads images to Fandom wikis using MediaWiki API with environment variable configuration.
"""

import os
import time
import requests
from pathlib import Path
import argparse
from typing import List, Optional
import logging
import mimetypes
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fandom_upload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FandomUploader:
    def __init__(self, wiki_url: str, bot_username: str, bot_password: str):
        """
        Initialize the Fandom uploader with bot credentials.
        
        Args:
            wiki_url: URL of the wiki (e.g., 'darkeden-legend.fandom.com')
            bot_username: Your bot username (format: Username@BotName)
            bot_password: Your bot password from Special:BotPasswords
        """
        self.wiki_url = wiki_url
        self.bot_username = bot_username
        self.bot_password = bot_password
        self.base_url = f"https://{wiki_url}"
        self.api_url = f"{self.base_url}/api.php"
        self.session = None
        self.csrf_token = None
        
    def connect(self) -> bool:
        """Connect and login to the wiki using manual API calls."""
        try:
            logger.info(f"Connecting to {self.wiki_url}...")
            
            # Create session with proper headers
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'FandomUploader/2.0 (Bot upload tool)'
            })
            
            # Step 1: Get login token
            logger.info("Getting login token...")
            token_params = {
                'action': 'query',
                'meta': 'tokens',
                'type': 'login',
                'format': 'json'
            }
            
            token_response = self.session.get(self.api_url, params=token_params)
            token_data = token_response.json()
            
            if 'query' not in token_data or 'tokens' not in token_data['query']:
                logger.error(f"Failed to get login token: {token_data}")
                return False
                
            login_token = token_data['query']['tokens']['logintoken']
            logger.info("✓ Got login token")
            
            # Step 2: Login
            logger.info(f"Logging in as: {self.bot_username}")
            login_params = {
                'action': 'login',
                'lgname': self.bot_username,
                'lgpassword': self.bot_password,
                'lgtoken': login_token,
                'format': 'json'
            }
            
            login_response = self.session.post(self.api_url, data=login_params)
            login_data = login_response.json()
            
            if login_data.get('login', {}).get('result') == 'Success':
                logger.info("✓ Successfully logged in!")
                
                # Step 3: Get CSRF token for uploads
                csrf_params = {
                    'action': 'query',
                    'meta': 'tokens',
                    'type': 'csrf',
                    'format': 'json'
                }
                
                csrf_response = self.session.get(self.api_url, params=csrf_params)
                csrf_data = csrf_response.json()
                
                if 'query' in csrf_data and 'tokens' in csrf_data['query']:
                    self.csrf_token = csrf_data['query']['tokens']['csrftoken']
                    logger.info("✓ Got CSRF token for uploads")
                    
                    # Verify permissions
                    return self._verify_permissions()
                else:
                    logger.error(f"Failed to get CSRF token: {csrf_data}")
                    return False
                    
            else:
                logger.error(f"Login failed: {login_data}")
                return False
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def _verify_permissions(self) -> bool:
        """Verify user has upload permissions."""
        try:
            user_params = {
                'action': 'query',
                'meta': 'userinfo',
                'uiprop': 'rights|groups',
                'format': 'json'
            }
            
            user_response = self.session.get(self.api_url, params=user_params)
            user_data = user_response.json()
            
            rights = user_data['query']['userinfo'].get('rights', [])
            groups = user_data['query']['userinfo'].get('groups', [])
            
            logger.info(f"User groups: {', '.join(groups)}")
            
            upload_rights = [r for r in rights if 'upload' in r.lower()]
            if upload_rights:
                logger.info(f"✓ Upload permissions: {', '.join(upload_rights)}")
                return True
            else:
                logger.warning("⚠ No upload permissions found")
                logger.info(f"Available rights: {', '.join(rights[:10])}...")
                return False
                
        except Exception as e:
            logger.warning(f"Could not verify permissions: {e}")
            return True  # Proceed anyway

    def file_exists(self, filename: str) -> bool:
        """Check if a file already exists on the wiki."""
        try:
            params = {
                'action': 'query',
                'titles': f'File:{filename}',
                'format': 'json'
            }
            
            response = self.session.get(self.api_url, params=params)
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_info in pages.items():
                if page_id != '-1':  # -1 means page doesn't exist
                    return True
            return False
            
        except Exception as e:
            logger.warning(f"Could not check if file {filename} exists: {e}")
            return False

    def upload_file(self, file_path: Path, description: str = "") -> str:
        """Upload a single file to the wiki.
        
        Returns:
            'uploaded' - File was successfully uploaded
            'skipped' - File already exists, was skipped
            'failed' - Upload failed
        """
        try:
            filename = file_path.name
            
            # Check if file already exists
            if self.file_exists(filename):
                logger.info(f"File {filename} already exists, skipping...")
                return 'skipped'
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Prepare upload parameters
            upload_params = {
                'action': 'upload',
                'filename': filename,
                'comment': description or f"Uploaded {filename}",
                'text': description or f"== Summary ==\n[[Category:Images]]\n[[Category:Rare Skills]]",
                'token': self.csrf_token,
                'format': 'json'
            }
            
            # Prepare file data
            with open(file_path, 'rb') as f:
                files = {
                    'file': (filename, f, mime_type)
                }
                
                response = self.session.post(self.api_url, data=upload_params, files=files)
                result = response.json()
            
            if 'upload' in result and result['upload'].get('result') == 'Success':
                logger.info(f"✓ Successfully uploaded: {filename}")
                return 'uploaded'
            else:
                logger.error(f"✗ Failed to upload {filename}: {result}")
                return 'failed'
                
        except Exception as e:
            logger.error(f"✗ Error uploading {file_path.name}: {e}")
            return 'failed'

    def get_image_files(self, directory: str) -> List[Path]:
        """Get list of image files from directory."""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
        directory_path = Path(directory)
        
        if not directory_path.exists():
            logger.error(f"Directory not found: {directory}")
            return []
        
        image_files = []
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_files.append(file_path)
        
        return sorted(image_files)

    def upload_batch(self, image_files: List[Path], batch_size: int = 10, delay_seconds: int = 120, dry_run: bool = False) -> dict:
        """Upload files in batches with rate limiting."""
        total_files = len(image_files)
        
        if dry_run:
            logger.info(f"DRY RUN MODE - No files will be uploaded")
            logger.info(f"Would upload {total_files} files:")
            for file_path in image_files:
                logger.info(f"  - {file_path.name}")
            return {'total': total_files, 'uploaded': 0, 'skipped': 0, 'failed': 0}
        
        if total_files == 0:
            logger.warning("No image files found to upload")
            return {'total': 0, 'uploaded': 0, 'skipped': 0, 'failed': 0}
        
        logger.info(f"Starting batch upload of {total_files} files...")
        logger.info(f"Batch size: {batch_size}, Delay between batches: {delay_seconds} seconds")
        
        stats = {'total': total_files, 'uploaded': 0, 'skipped': 0, 'failed': 0}
        
        for i in range(0, total_files, batch_size):
            batch = image_files[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_files + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} files)...")
            
            for file_path in batch:
                result = self.upload_file(file_path)
                if result == 'uploaded':
                    stats['uploaded'] += 1
                elif result == 'skipped':
                    stats['skipped'] += 1
                else:  # 'failed'
                    stats['failed'] += 1
            
            logger.info(f"Batch {batch_num} complete. " +
                       f"Uploaded: {stats['uploaded']}, Skipped: {stats['skipped']}, Failed: {stats['failed']}")
            
            # Wait between batches (except for the last batch)
            if i + batch_size < total_files:
                logger.info(f"Waiting {delay_seconds} seconds before next batch...")
                time.sleep(delay_seconds)
        
        return stats


def load_config():
    """Load configuration from environment variables."""
    # Load .env file if it exists
    load_dotenv()
    
    config = {
        'wiki_url': os.getenv('WIKI_URL', 'darkeden-legend.fandom.com'),
        'bot_username': os.getenv('BOT_USERNAME'),
        'bot_password': os.getenv('BOT_PASSWORD'),
        'image_dir': 'pages/rare skills/missing_icons',
        'batch_size': int(os.getenv('BATCH_SIZE', '10')),
        'delay': int(os.getenv('DELAY', '120'))
    }
    
    return config


def main():
    """Main function."""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    parser = argparse.ArgumentParser(description='Upload images to Fandom wiki')
    parser.add_argument('--wiki', help='Wiki URL (default: from .env)')
    parser.add_argument('--bot-username', help='Bot username (default: from .env)')
    parser.add_argument('--bot-password', help='Bot password (default: from .env)')
    parser.add_argument('--directory', help='Image directory (default: from .env)')
    parser.add_argument('--batch-size', type=int, help='Batch size (default: from .env)')
    parser.add_argument('--delay', type=int, help='Delay between batches in seconds (default: from .env)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode - don\'t actually upload')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Override with command line arguments if provided
    wiki_url = args.wiki or config['wiki_url']
    bot_username = args.bot_username or config['bot_username']
    bot_password = args.bot_password or config['bot_password']
    directory = args.directory or config['image_dir']
    batch_size = args.batch_size or config['batch_size']
    delay = args.delay or config['delay']
    
    # Validate required parameters
    if not all([wiki_url, bot_username, bot_password]):
        logger.error("Missing required configuration. Please set in .env file or command line:")
        logger.error("  WIKI_URL, BOT_USERNAME, BOT_PASSWORD")
        logger.error("\nExample .env file:")
        logger.error("WIKI_URL=darkeden-legend.fandom.com")
        logger.error("BOT_USERNAME=YourUsername@BotName")
        logger.error("BOT_PASSWORD=your_bot_password")
        return 1
    
    # Initialize uploader
    uploader = FandomUploader(wiki_url, bot_username, bot_password)
    
    # Connect to wiki
    if not uploader.connect():
        logger.error("Failed to connect to wiki")
        return 1
    
    # Get image files
    image_files = uploader.get_image_files(directory)
    logger.info(f"Found {len(image_files)} image files in {directory}")
    
    if not image_files:
        logger.warning("No image files found to upload")
        return 1
    
    # Upload files
    stats = uploader.upload_batch(image_files, batch_size, delay, args.dry_run)
    
    # Print summary
    logger.info("="*50)
    logger.info("UPLOAD SUMMARY")
    logger.info("="*50)
    logger.info(f"Total files: {stats['total']}")
    logger.info(f"Uploaded: {stats['uploaded']}")
    logger.info(f"Skipped (already exist): {stats['skipped']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info("="*50)
    
    if stats['failed'] > 0:
        logger.warning(f"{stats['failed']} files failed to upload. Check logs for details.")
        return 1
    
    logger.info("Upload completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
