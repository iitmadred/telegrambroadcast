"""
Configuration and constants for Telegram Broadcast application.
"""

# Application Constants
APP_TITLE = "Telegram Broadcast Pro"
APP_ICON = "📢"
PAGE_LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Telegram API Limits
MAX_CAPTION_LENGTH = 1024
MAX_MESSAGE_LENGTH = 4096
MAX_CONCURRENT_SENDS_LIMIT = 50
MIN_CONCURRENT_SENDS = 1
DEFAULT_CONCURRENT_SENDS = 10

# Rate Limiting
MAX_SEND_DELAY = 10
MIN_SEND_DELAY = 0
DEFAULT_SEND_DELAY = 1
DRY_RUN_DELAY = 0.1

# File Upload
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "gif"]
SUPPORTED_TEXT_TYPES = ["txt"]

# UI Configuration
PREVIEW_CHAT_IDS_LIMIT = 20
MAX_HISTORY_ENTRIES = 10

# Formatting Toolbar
HTML_TAGS = {
    "Bold": "<b>text</b>",
    "Italic": "<i>text</i>",
    "Underline": "<u>text</u>",
    "Strike": "<s>text</s>",
    "Code": "<code>text</code>",
    "Link": "<a href='URL'>text</a>",
    "Pre": "<pre>code</pre>",
}

# Message Templates
MESSAGE_TEMPLATES = {
    "Announcement": """<b>📢 Announcement</b>

[Your announcement here]

<i>- Your Team</i>""",
    "Promotion": """<b>🎉 Special Offer!</b>

✨ [Offer details]

💰 <b>Price:</b> [Amount]

🔗 <a href='[link]'>Learn More</a>""",
    "Update": """<b>🔔 Update</b>

We're excited to share:

• [Update 1]
• [Update 2]
• [Update 3]

Stay tuned for more!""",
    "Event": """<b>📅 Event Invitation</b>

📍 <b>Location:</b> [Place]
🕐 <b>Time:</b> [Time]
📆 <b>Date:</b> [Date]

<a href='[link]'>Register Now</a>"""
}

# Error Messages
ERROR_MESSAGES = {
    "no_token": "⚠️ Please add TELEGRAM_TOKEN to secrets or enter manually",
    "invalid_token": "❌ Invalid bot token format",
    "no_message": "⚠️ Please enter a message to send",
    "no_recipients": "⚠️ Please provide at least one recipient",
    "invalid_chat_ids": "⚠️ Some chat IDs are invalid",
    "message_too_long": "⚠️ Message exceeds maximum length",
    "github_fetch_failed": "❌ Failed to load from GitHub URL",
    "broadcast_failed": "❌ Broadcast failed",
}

# Success Messages
SUCCESS_MESSAGES = {
    "token_loaded": "✓ Token loaded from secrets",
    "file_uploaded": "✓ Loaded {count} chat IDs from file",
    "github_loaded": "✓ Loaded {count} chat IDs from URL",
    "all_valid": "✓ All {count} chat IDs are valid",
    "broadcast_complete": "🎉 Broadcast Complete! Successfully sent to all {count} recipients!",
    "dry_run_complete": "🧪 Dry Run Complete! Tested {count} messages successfully",
}

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
