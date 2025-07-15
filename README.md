# Dark Eden Legend Wiki

Welcome to the **Dark Eden Legend Wiki** repository!  
This project serves as the central hub for storing documents, media, and automation tools for the [Dark Eden Legend Fandom Wiki](https://darkeden-legend.fandom.com/wiki/Darkeden_Legend_Wiki).

## 🎯 Project Status

✅ **Image Upload Complete**: All 91 rare skill icons successfully uploaded to Fandom wiki!  
✅ **Automation Ready**: Streamlined upload process with environment variable configuration  
✅ **Clean Structure**: Organized codebase with proper separation of concerns  

## 📁 Project Structure

```
├── 📁 scripts/           # Automation tools
│   ├── fandom_uploader.py   # Main image uploader (environment-based)
│   └── upload.sh           # Convenience script
├── 📁 tests/             # Testing tools
│   └── auth_tester.py      # Authentication testing
├── 📁 logs/              # Upload logs and history
├── 📁 pages/             # Wiki content
│   └── rare skills/        # Rare skills documentation & icons
├── 📁 personal/          # Personal files (ignored)
├── .env                  # Environment variables (keep private!)
├── requirements.txt      # Python dependencies
└── README_UPLOADER.md    # Detailed uploader documentation
```

## 🚀 Quick Start

### Upload Images to Fandom Wiki

```bash
# One-time setup: Configure credentials in .env
# Then run:
bash scripts/upload.sh
```

For detailed instructions, see [README_UPLOADER.md](README_UPLOADER.md)

## 🔧 Configuration

Set up your `.env` file with bot credentials:

```bash
WIKI_URL=darkeden-legend.fandom.com
BOT_USERNAME=YourUsername@BotName
BOT_PASSWORD=your_bot_password
IMAGE_DIR=pages/rare skills/icons
BATCH_SIZE=10
DELAY=120
```

## 📚 Documentation

- **[Uploader Guide](README_UPLOADER.md)** - Complete documentation for the image uploader
- **[Dark Eden Legend Wiki](https://darkeden-legend.fandom.com)** - The live wiki
- **[Special:ListFiles](https://darkeden-legend.fandom.com/wiki/Special:ListFiles)** - View uploaded images

## 🎮 Content Overview

- **Rare Skills**: Complete documentation with 91 skill icons
- **Game Guides**: Gameplay documentation and resources
- **Media Assets**: Images, PDFs, and reference materials

## 🤝 Contributing

1. **Fork** this repository and create a feature branch
2. Add or update content in the appropriate folders
3. Test uploads with `bash scripts/upload.sh --dry-run`
4. Submit a **pull request** with clear description

## 📄 License

Content follows Fandom's policies and copyright guidelines.

---

*Building the Dark Eden Legend community together!* 🎮