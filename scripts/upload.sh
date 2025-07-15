#!/bin/bash

# Fandom Wiki Image Uploader
# Uses environment variables from .env file

echo "🚀 Fandom Wiki Image Uploader"
echo "=============================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create a .env file with your bot credentials:"
    echo "WIKI_URL=your-wiki.fandom.com"
    echo "BOT_USERNAME=YourUsername@BotName"
    echo "BOT_PASSWORD=your_bot_password"
    echo "IMAGE_DIR=path/to/images"
    echo "BATCH_SIZE=10"
    echo "DELAY=120"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "📁 Starting upload..."
echo ""

# Run the uploader
python3 scripts/fandom_uploader.py $@

echo ""
echo "✅ Done!"
