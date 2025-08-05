# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a web scraping tool for downloading product images from Musinsa (Korean fashion e-commerce) purchase history. The project uses Selenium WebDriver with Firefox to automate login, navigate purchase history pages, and download product images.

## Architecture

### Core Components

- **crawler_main_firefox.py**: Main Firefox-based crawler with advanced image extraction capabilities
- **utils.py**: Image analysis, organization, and conversion utilities
- **crawler_config.json**: Configuration file for crawler behavior

### Key Classes

- `AdvancedMusinsaCrawlerFirefox`: Main crawler class with login, navigation, and image extraction
- `ImageAnalyzer`: Post-download image analysis and duplicate detection
- `ImageOrganizer`: Brand/date-based folder organization
- `ImageConverter`: Format conversion and resizing utilities
- `MusinsaImageManager`: Interactive management interface

## Common Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt
# or using uv (preferred)
uv pip install -r requirements.txt
```

### Running the Crawler
```bash
# Main Firefox crawler (recommended)
python crawler_main_firefox.py

# Image management utilities
python utils.py <image_folder_path>
```

### Configuration
- Configuration is managed through `crawler_config.json`
- Default config is auto-generated on first run
- Key settings: max_images, download_delay, headless_mode, image_quality_filter

## Project Structure

```
Purchase_History_Image_Crawler/
├── crawler_main_firefox.py    # Main crawler implementation
├── utils.py                   # Image processing utilities
├── crawler_config.json        # Runtime configuration
├── requirements.txt           # Python dependencies
└── README.md                 # Korean documentation
```

## Image Processing Pipeline

1. **Extraction**: Multi-selector approach for various image elements
2. **URL Enhancement**: Convert thumbnails to high-resolution versions
3. **Quality Filtering**: Remove small/low-quality images (configurable)
4. **Download**: Progress tracking with retry logic and rate limiting
5. **Organization**: Brand-based and date-based folder structures

## Browser Compatibility

- **Primary**: Firefox (via geckodriver and webdriver-manager)
- **Note**: Chrome version removed due to ChromeDriver compatibility issues
- Firefox handles lazy-loading images and provides better stability

## Output Structure

Downloaded images are organized as:
```
musinsa_images_YYYYMMDD_HHMMSS/
├── musinsa_brand_productid_001.jpg
├── download_info.json          # Download metadata
└── session_log.json           # Session logging
```

## Security Notes

This is a defensive web scraping tool for personal use only. The tool:
- Respects rate limiting and server load
- Includes proper user agent headers
- Implements retry logic with exponential backoff
- Downloads images for personal archival purposes only