"""
Input validation utilities for Telegram Broadcast application.
"""
import re
from typing import List, Tuple
from config import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH


def validate_bot_token(token: str) -> bool:
    """
    Validate Telegram bot token format.

    Args:
        token: Bot token string

    Returns:
        bool: True if token format is valid
    """
    if not token or not isinstance(token, str):
        return False

    # Telegram bot token format: numbers:alphanumeric
    pattern = r'^\d+:[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, token.strip()))


def validate_chat_id(chat_id: str) -> bool:
    """
    Validate a single chat ID.

    Args:
        chat_id: Chat ID string

    Returns:
        bool: True if chat ID is valid
    """
    if not chat_id or not isinstance(chat_id, str):
        return False

    chat_id = chat_id.strip()

    # Chat ID can be positive or negative integers
    if chat_id.startswith('-'):
        return chat_id[1:].isdigit() and len(chat_id) > 1

    return chat_id.isdigit()


def validate_chat_ids(chat_ids: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate a list of chat IDs.

    Args:
        chat_ids: List of chat ID strings

    Returns:
        Tuple of (valid_chat_ids, invalid_chat_ids)
    """
    valid = []
    invalid = []

    for chat_id in chat_ids:
        if validate_chat_id(chat_id):
            valid.append(chat_id.strip())
        else:
            invalid.append(chat_id)

    return valid, invalid


def validate_message_length(message: str, with_photo: bool = False) -> Tuple[bool, int]:
    """
    Validate message length according to Telegram limits.

    Args:
        message: Message text
        with_photo: Whether message will be sent with a photo

    Returns:
        Tuple of (is_valid, length)
    """
    length = len(message)
    max_length = MAX_CAPTION_LENGTH if with_photo else MAX_MESSAGE_LENGTH

    return length <= max_length, length


def sanitize_html(html: str) -> str:
    """
    Basic HTML sanitization for Telegram messages.
    Note: Telegram supports only specific HTML tags.

    Args:
        html: HTML string

    Returns:
        str: Sanitized HTML
    """
    # Telegram supported tags: b, strong, i, em, u, ins, s, strike, del,
    # span, tg-spoiler, a, tg-emoji, code, pre

    # Remove script tags and their content
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)

    # Remove style tags and their content
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)

    # Remove event handlers (onclick, onerror, etc.)
    html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    html = re.sub(r'\s*on\w+\s*=\s*[^\s>]+', '', html, flags=re.IGNORECASE)

    # Remove javascript: protocols in links
    html = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', '', html, flags=re.IGNORECASE)

    return html.strip()


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL string

    Returns:
        bool: True if URL format is valid
    """
    if not url or not isinstance(url, str):
        return False

    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_pattern.match(url))


def parse_chat_ids_from_text(text: str) -> List[str]:
    """
    Parse chat IDs from text, ignoring comments.

    Args:
        text: Text containing chat IDs

    Returns:
        List of chat ID strings
    """
    chat_ids = []

    for line in text.splitlines():
        line = line.strip()
        # Skip empty lines and comments
        if line and not line.startswith('#'):
            chat_ids.append(line)

    return chat_ids


def validate_image_size(file_size: int, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    Validate image file size.

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB

    Returns:
        Tuple of (is_valid, message)
    """
    max_bytes = max_size_mb * 1024 * 1024

    if file_size > max_bytes:
        return False, f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds maximum allowed ({max_size_mb} MB)"

    return True, f"File size: {file_size / 1024:.1f} KB"
