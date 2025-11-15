# Telegram Broadcast Pro 📢

A professional-grade Streamlit application for broadcasting Telegram messages to multiple recipients with advanced features, comprehensive error handling, and security measures.

## 🌟 Features

### Core Features
- **Concurrent Broadcasting**: Send messages to thousands of recipients simultaneously
- **HTML Message Formatting**: Full support for Telegram's HTML formatting
- **Image Support**: Send images with captions
- **Multiple Input Methods**: File upload, manual paste, GitHub URL, or history
- **Dry Run Mode**: Test broadcasts without actually sending messages
- **Real-time Progress Tracking**: Live updates on send status, success/failure rates

### Advanced Features
- **Comprehensive Input Validation**: Validates bot tokens, chat IDs, URLs, and message lengths
- **HTML Sanitization**: Automatic removal of potentially harmful HTML tags
- **Rate Limiting**: Configurable concurrent sends and delays to avoid API limits
- **Error Handling**: Detailed error messages for different failure scenarios
- **Session History**: Track broadcast statistics and save recipient lists
- **CSV Export**: Download detailed results of each broadcast

### Security Features
- **Token Validation**: Validates Telegram bot token format
- **HTML Sanitization**: Removes script tags, event handlers, and javascript: protocols
- **Input Validation**: Comprehensive validation of all user inputs
- **Secure Secrets Management**: Support for Streamlit secrets

## 📁 Project Structure

```
telegrambroadcast/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration and constants
├── validators.py         # Input validation utilities
├── utils.py              # Utility functions and helpers
├── styles.py             # CSS styles and HTML generators
├── requirements.txt      # Python dependencies
├── chat_ids.txt          # Sample chat IDs file
└── README.md             # This file
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd telegrambroadcast
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your bot token**

   Create a `.streamlit/secrets.toml` file:
   ```toml
   TELEGRAM_TOKEN = "your_bot_token_here"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. **Fork this repository**

2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select this repository

3. **Add Secrets**
   - In Streamlit Cloud dashboard, go to your app settings
   - Add secrets:
     ```toml
     TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"
     ```

4. **Deploy**
   - Your app will automatically deploy!

## 📖 Usage Guide

### 1. Compose Tab ✍️

**Create Your Message:**
- Use the text editor to compose your message
- Apply HTML formatting using the toolbar buttons
- Choose from pre-built templates (Announcement, Promotion, Update, Event)
- See live preview of your formatted message
- Upload an optional image (JPG, PNG, GIF)

**Supported HTML Tags:**
- `<b>text</b>` - Bold
- `<i>text</i>` - Italic
- `<u>text</u>` - Underline
- `<s>text</s>` - Strikethrough
- `<code>text</code>` - Inline code
- `<pre>code</pre>` - Code block
- `<a href='URL'>text</a>` - Link

### 2. Recipients Tab 👥

**Add Recipients:**

Choose from multiple input methods:

1. **Upload File**: Upload a `.txt` file with one chat ID per line
2. **Paste Manually**: Copy and paste chat IDs directly
3. **GitHub URL**: Provide a raw GitHub URL to your chat_ids.txt file
4. **Load from History**: Reuse previously saved recipient lists

**File Format:**
```
# Comments start with #
123456789
987654321
-1001234567890  # Group chat IDs start with -
```

**Validation:**
- All chat IDs are automatically validated
- Invalid IDs are flagged and excluded
- View validation statistics in real-time

### 3. Send Tab 🚀

**Pre-flight Checklist:**
- ✅ Bot Token validated
- ✅ Message content and length validated
- ✅ Recipients loaded and validated
- ✅ Legal confirmation checkbox

**Broadcast Options:**
- **Concurrent Sends**: 1-50 simultaneous sends (default: 10)
- **Delay Between Batches**: 0-10 seconds (default: 1)
- **Dry Run Mode**: Test without actually sending

**Monitor Progress:**
- Real-time progress bar
- Live statistics (sent, failed, pending, rate)
- Detailed results with export option

### 4. History Tab 📈

**View Statistics:**
- Total messages sent (session)
- Total failures (session)
- Success rate percentage
- Number of broadcasts
- Last broadcast time

**Saved Lists:**
- Access previously used recipient lists
- Download historical lists
- Reset session statistics

## ⚙️ Configuration

### Bot Token

Get your bot token from [@BotFather](https://t.me/botfather):

1. Send `/newbot` to create a new bot
2. Follow the prompts to set name and username
3. Receive your bot token
4. Add it to secrets or enter manually in the app

### Rate Limiting

Adjust these settings to avoid hitting Telegram's rate limits:

- **Concurrent Sends**: Number of simultaneous API requests
- **Delay Between Batches**: Pause between message groups

**Recommendations:**
- Start with 10 concurrent sends and 1 second delay
- Increase gradually while monitoring for errors
- Reduce if you encounter rate limit errors

## 🛡️ Security Best Practices

1. **Never commit your bot token** to version control
2. **Use Streamlit secrets** for production deployments
3. **Only message opted-in recipients** to comply with Telegram ToS
4. **Test with dry run** before sending to real recipients
5. **Review HTML content** for potentially malicious code
6. **Validate all inputs** before processing

## 🔧 Advanced Configuration

### Custom Templates

Edit `config.py` to add custom message templates:

```python
MESSAGE_TEMPLATES = {
    "Your Template": """<b>Custom Template</b>

Your content here

<i>- Signature</i>"""
}
```

### Logging

Adjust log level in `config.py`:

```python
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Validation Rules

Modify validation in `validators.py`:

```python
MAX_CAPTION_LENGTH = 1024  # Telegram limit with photo
MAX_MESSAGE_LENGTH = 4096  # Telegram limit without photo
```

## 📊 API Limits

**Telegram Bot API Limits:**
- Messages: 30 messages per second
- Group messages: 20 messages per minute
- Broadcasts to 30 or fewer users: 1 per second

**Message Length Limits:**
- Text messages: 4096 characters
- Photo captions: 1024 characters

## 🐛 Troubleshooting

### Common Issues

**"Invalid bot token format"**
- Check your token format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789`
- Ensure no extra spaces or characters

**"Bot was blocked by user"**
- User must start a conversation with your bot first
- Or bot must be added to the group

**"Message too long"**
- Reduce message length
- Or send without image to increase limit to 4096 chars

**Rate limit errors**
- Reduce concurrent sends
- Increase delay between batches
- Wait before retrying

### Error Codes

- `forbidden`: Bot blocked or chat not found
- `bad_request`: Invalid request parameters
- `network_error`: Connection issues
- `telegram_error`: General Telegram API error

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is provided as-is for educational purposes.

## ⚠️ Important Legal Notice

- **Only message users who have explicitly opted in**
- **Respect Telegram's Terms of Service and anti-spam policies**
- **Do not use for spam or unsolicited messages**
- **You are responsible for compliance with applicable laws**

## 🔗 Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Streamlit Documentation](https://docs.streamlit.io)
- [python-telegram-bot Library](https://github.com/python-telegram-bot/python-telegram-bot)

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

## 🎯 Roadmap

Future enhancements:
- [ ] Scheduled broadcasts
- [ ] Message scheduling calendar
- [ ] Multiple bot support
- [ ] Advanced analytics dashboard
- [ ] Template library
- [ ] A/B testing capabilities
- [ ] Webhook support
- [ ] Database integration for persistent storage

---

Made with ❤️ using Streamlit | © 2024
