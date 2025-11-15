"""
Utility functions for Telegram Broadcast application.
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Tuple
import streamlit as st
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError, BadRequest, Forbidden, NetworkError

from config import LOG_FORMAT, LOG_LEVEL, DRY_RUN_DELAY


def setup_logging(level: str = LOG_LEVEL) -> logging.Logger:
    """
    Setup logging configuration.

    Args:
        level: Logging level (default from config)

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        format=LOG_FORMAT,
        level=getattr(logging, level.upper()),
        force=True
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class BroadcastResult:
    """Data class for broadcast results."""

    def __init__(self):
        self.successful: List[str] = []
        self.failed: List[Tuple[str, str]] = []
        self.dry_run: List[str] = []

    @property
    def total(self) -> int:
        """Total number of attempts."""
        return len(self.successful) + len(self.failed) + len(self.dry_run)

    @property
    def success_count(self) -> int:
        """Number of successful sends."""
        return len(self.successful)

    @property
    def failure_count(self) -> int:
        """Number of failed sends."""
        return len(self.failed)

    @property
    def dry_run_count(self) -> int:
        """Number of dry run attempts."""
        return len(self.dry_run)

    def add_success(self, chat_id: str):
        """Add a successful send."""
        self.successful.append(chat_id)

    def add_failure(self, chat_id: str, error: str):
        """Add a failed send."""
        self.failed.append((chat_id, error))

    def add_dry_run(self, chat_id: str):
        """Add a dry run attempt."""
        self.dry_run.append(chat_id)


async def send_message_to_chat(
    bot: Bot,
    chat_id: str,
    image_bytes: Optional[bytes],
    caption: str,
    semaphore: asyncio.Semaphore,
    dry_run: bool = False
) -> Tuple[str, str]:
    """
    Send a message to a single chat.

    Args:
        bot: Telegram Bot instance
        chat_id: Target chat ID
        image_bytes: Optional image bytes to send
        caption: Message caption/text
        semaphore: Asyncio semaphore for rate limiting
        dry_run: If True, simulate sending without actually sending

    Returns:
        Tuple of (chat_id, status_message)
    """
    async with semaphore:
        try:
            if dry_run:
                await asyncio.sleep(DRY_RUN_DELAY)
                logger.info(f"[DRY RUN] Would send to chat_id: {chat_id}")
                return chat_id, "dry_run"

            if image_bytes:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=image_bytes,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
                logger.info(f"Successfully sent photo with caption to chat_id: {chat_id}")
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False,
                )
                logger.info(f"Successfully sent message to chat_id: {chat_id}")

            return chat_id, "success"

        except Forbidden as e:
            error_msg = f"forbidden: Bot was blocked by user or chat not found - {str(e)}"
            logger.warning(f"Chat {chat_id}: {error_msg}")
            return chat_id, error_msg

        except BadRequest as e:
            error_msg = f"bad_request: Invalid request - {str(e)}"
            logger.error(f"Chat {chat_id}: {error_msg}")
            return chat_id, error_msg

        except NetworkError as e:
            error_msg = f"network_error: Connection issue - {str(e)}"
            logger.error(f"Chat {chat_id}: {error_msg}")
            return chat_id, error_msg

        except TelegramError as e:
            error_msg = f"telegram_error: {str(e)}"
            logger.error(f"Chat {chat_id}: {error_msg}")
            return chat_id, error_msg

        except Exception as e:
            error_msg = f"error: {str(e)}"
            logger.exception(f"Unexpected error for chat {chat_id}: {error_msg}")
            return chat_id, error_msg


def format_results_for_display(results: List[Tuple[str, str]], dry_run: bool = False) -> dict:
    """
    Format broadcast results for display.

    Args:
        results: List of (chat_id, status) tuples
        dry_run: Whether this was a dry run

    Returns:
        Dictionary with formatted results
    """
    data = {
        "Chat ID": [],
        "Status": [],
        "Details": []
    }

    for chat_id, status in results:
        data["Chat ID"].append(chat_id)

        if status == "success":
            data["Status"].append("✅ Success")
        elif status == "dry_run":
            data["Status"].append("🧪 Dry Run")
        else:
            data["Status"].append("❌ Failed")

        data["Details"].append(status)

    return data


def generate_csv_results(results: List[Tuple[str, str]]) -> str:
    """
    Generate CSV format results.

    Args:
        results: List of (chat_id, status) tuples

    Returns:
        CSV formatted string
    """
    csv_content = "Chat ID,Status,Details\n"

    for chat_id, status in results:
        status_type = status.split(':')[0]
        csv_content += f"{chat_id},{status_type},{status}\n"

    return csv_content


def get_session_state_value(key: str, default=None):
    """
    Safely get a value from Streamlit session state.

    Args:
        key: Session state key
        default: Default value if key doesn't exist

    Returns:
        Session state value or default
    """
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def set_session_state_value(key: str, value):
    """
    Set a value in Streamlit session state.

    Args:
        key: Session state key
        value: Value to set
    """
    st.session_state[key] = value


def initialize_session_state():
    """Initialize all required session state variables."""
    defaults = {
        'total_sent': 0,
        'total_failed': 0,
        'chat_history': [],
        'last_broadcast_time': None,
        'broadcast_count': 0
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def add_to_chat_history(chat_ids: List[str]):
    """
    Add chat IDs to history.

    Args:
        chat_ids: List of chat IDs to save
    """
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    entry = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'count': len(chat_ids),
        'ids': chat_ids.copy()
    }

    st.session_state.chat_history.append(entry)

    # Keep only last 10 entries
    from config import MAX_HISTORY_ENTRIES
    if len(st.session_state.chat_history) > MAX_HISTORY_ENTRIES:
        st.session_state.chat_history = st.session_state.chat_history[-MAX_HISTORY_ENTRIES:]


def update_broadcast_stats(successful: int, failed: int):
    """
    Update session broadcast statistics.

    Args:
        successful: Number of successful sends
        failed: Number of failed sends
    """
    st.session_state.total_sent += successful
    st.session_state.total_failed += failed
    st.session_state.last_broadcast_time = datetime.now()
    st.session_state.broadcast_count += 1


def calculate_success_rate() -> float:
    """
    Calculate overall success rate.

    Returns:
        Success rate as percentage
    """
    total = st.session_state.total_sent + st.session_state.total_failed
    if total == 0:
        return 0.0
    return (st.session_state.total_sent / total) * 100


def reset_session_stats():
    """Reset all session statistics."""
    st.session_state.total_sent = 0
    st.session_state.total_failed = 0
    st.session_state.chat_history = []
    st.session_state.last_broadcast_time = None
    st.session_state.broadcast_count = 0
