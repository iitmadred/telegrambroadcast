"""
Telegram Broadcast Pro - A professional broadcasting tool for Telegram
with advanced features, error handling, and comprehensive validation.
"""
import asyncio
import io
from datetime import datetime
from typing import List, Optional

import nest_asyncio
import requests
import streamlit as st
from telegram import Bot
from telegram.error import TelegramError

# Import custom modules
from config import *
from validators import *
from utils import *
from styles import CUSTOM_CSS, get_header_html, get_stat_card_html, get_footer_html

# Allow nested event loops (important on Streamlit Cloud)
nest_asyncio.apply()

# Setup logging
logger = setup_logging()

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# ---------- HEADER ----------
st.markdown(
    get_header_html(APP_TITLE, "Professional Broadcasting Tool with Advanced Features"),
    unsafe_allow_html=True
)

# ---------- SIDEBAR CONFIGURATION ----------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/telegram-app--v1.png", width=80)
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")

    # Bot Token Section
    st.markdown("#### 🔑 Bot Token")
    use_secrets = st.checkbox("Use st.secrets", value=True, help="Recommended for production")
    token = ""

    if use_secrets:
        try:
            token = st.secrets["TELEGRAM_TOKEN"]
            if validate_bot_token(token):
                st.success(SUCCESS_MESSAGES["token_loaded"])
                logger.info("Bot token loaded from secrets")
            else:
                st.error(ERROR_MESSAGES["invalid_token"])
                logger.error("Invalid bot token format in secrets")
                token = ""
        except Exception as e:
            st.error(ERROR_MESSAGES["no_token"])
            logger.warning(f"Failed to load token from secrets: {e}")
    else:
        token_input = st.text_input("Bot Token", type="password", placeholder="Enter your bot token")
        if token_input:
            if validate_bot_token(token_input):
                token = token_input
                st.success("✓ Valid token format")
            else:
                st.error(ERROR_MESSAGES["invalid_token"])
                logger.warning("Invalid token format entered")

    st.markdown("---")

    # Sending Options
    st.markdown("#### 🎚️ Send Settings")
    max_concurrent = st.slider(
        "Concurrent Sends",
        min_value=MIN_CONCURRENT_SENDS,
        max_value=MAX_CONCURRENT_SENDS_LIMIT,
        value=DEFAULT_CONCURRENT_SENDS,
        help="Number of messages sent simultaneously"
    )

    send_delay = st.slider(
        "Delay Between Batches (seconds)",
        min_value=MIN_SEND_DELAY,
        max_value=MAX_SEND_DELAY,
        value=DEFAULT_SEND_DELAY,
        help="Helps avoid rate limits"
    )

    dry_run = st.checkbox(
        "🧪 Dry Run Mode",
        help="Test without actually sending messages"
    )

    st.markdown("---")

    # Statistics
    st.markdown("#### 📊 Quick Stats")
    st.metric("Total Sent (Session)", st.session_state.total_sent)
    st.metric("Total Failed (Session)", st.session_state.total_failed)

    if st.session_state.total_sent > 0 or st.session_state.total_failed > 0:
        success_rate = calculate_success_rate()
        st.metric("Success Rate", f"{success_rate:.1f}%")

    st.markdown("---")
    st.markdown("##### 💡 Tips")
    st.info("Start with dry run to test your message formatting!")

# ---------- MAIN CONTENT ----------
tab1, tab2, tab3, tab4 = st.tabs(["✍️ Compose", "👥 Recipients", "🚀 Send", "📈 History"])

# ========== TAB 1: COMPOSE MESSAGE ==========
with tab1:
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### ✍️ Message Composer")

        # Message Templates
        st.markdown("#### 📋 Quick Templates")
        template_cols = st.columns(4)

        template_choice = None
        for i, (name, template) in enumerate(MESSAGE_TEMPLATES.items()):
            with template_cols[i]:
                if st.button(f"📄 {name}", use_container_width=True, key=f"template_{name}"):
                    template_choice = template

        # Formatting Toolbar
        st.markdown("#### 🎨 Formatting Toolbar")

        format_cols = st.columns(8)

        with format_cols[0]:
            if st.button("**B**", help=HTML_TAGS["Bold"], use_container_width=True):
                st.info(f"Wrap text with: `{HTML_TAGS['Bold']}`")
        with format_cols[1]:
            if st.button("*I*", help=HTML_TAGS["Italic"], use_container_width=True):
                st.info(f"Wrap text with: `{HTML_TAGS['Italic']}`")
        with format_cols[2]:
            if st.button("<u>U</u>", help=HTML_TAGS["Underline"], use_container_width=True):
                st.info(f"Wrap text with: `{HTML_TAGS['Underline']}`")
        with format_cols[3]:
            if st.button("~~S~~", help=HTML_TAGS["Strike"], use_container_width=True):
                st.info(f"Wrap text with: `{HTML_TAGS['Strike']}`")
        with format_cols[4]:
            if st.button("`<>`", help=HTML_TAGS["Code"], use_container_width=True):
                st.info(f"Wrap text with: `{HTML_TAGS['Code']}`")
        with format_cols[5]:
            if st.button("🔗", help=HTML_TAGS["Link"], use_container_width=True):
                st.info(f"Format: `{HTML_TAGS['Link']}`")
        with format_cols[6]:
            if st.button("{ }", help=HTML_TAGS["Pre"], use_container_width=True):
                st.info(f"Wrap code with: `{HTML_TAGS['Pre']}`")

        # Text Editor
        st.markdown("#### 📝 Message Content")
        caption_html = st.text_area(
            "Compose your message (HTML supported)",
            height=300,
            value=template_choice if template_choice else st.session_state.get("last_message", ""),
            placeholder="Type your message here...\n\nUse HTML tags for formatting:\n<b>Bold</b>, <i>Italic</i>, <u>Underline</u>, <s>Strike</s>\n<code>Code</code>, <pre>Preformatted</pre>\n<a href='URL'>Link</a>",
            key="message_content"
        )

        # Sanitize HTML
        if caption_html:
            caption_html = sanitize_html(caption_html)
            st.session_state["last_message"] = caption_html

        # Character count and validation
        char_count = len(caption_html)
        image_file = st.session_state.get("image_file", None)

        is_valid_length, _ = validate_message_length(caption_html, with_photo=image_file is not None)

        if not is_valid_length:
            max_len = MAX_CAPTION_LENGTH if image_file else MAX_MESSAGE_LENGTH
            st.error(f"⚠️ Message length: {char_count} characters (Telegram limit: {max_len})")
        else:
            max_len = MAX_CAPTION_LENGTH if image_file else MAX_MESSAGE_LENGTH
            st.info(f"📊 Character count: {char_count}/{max_len}")

        # Image Upload
        st.markdown("#### 🖼️ Attach Image (Optional)")
        uploaded_image = st.file_uploader(
            "Upload an image to send with your message",
            type=SUPPORTED_IMAGE_TYPES,
            help="Supports JPG, PNG, and GIF formats",
            key="image_uploader"
        )

        if uploaded_image:
            # Validate image size
            is_valid_size, size_msg = validate_image_size(uploaded_image.size)
            if is_valid_size:
                st.success(f"✓ Image attached: {uploaded_image.name} ({size_msg})")
                st.session_state["image_file"] = uploaded_image
                logger.info(f"Image uploaded: {uploaded_image.name}, size: {uploaded_image.size}")
            else:
                st.error(f"❌ {size_msg}")
                st.session_state["image_file"] = None
        else:
            st.session_state["image_file"] = None

    with col2:
        st.markdown("### 👀 Live Preview")

        # Preview card
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        if caption_html.strip():
            st.markdown(caption_html, unsafe_allow_html=True)
        else:
            st.markdown("*Your message preview will appear here...*")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.get("image_file"):
            st.markdown("#### 📷 Image Preview")
            st.image(st.session_state["image_file"], use_container_width=True)

        # HTML Code View
        with st.expander("📄 View HTML Source"):
            st.code(caption_html, language="html")

        # Validation Status
        with st.expander("✅ Validation Status"):
            st.write("**Message Validation:**")
            if caption_html.strip():
                st.success("✓ Message content present")
            else:
                st.warning("⚠ Message is empty")

            if is_valid_length:
                st.success("✓ Message length within limits")
            else:
                st.error("✗ Message too long")

# ========== TAB 2: RECIPIENTS ==========
with tab2:
    st.markdown("### 👥 Manage Recipients")

    source = st.radio(
        "Choose how to provide chat IDs:",
        ["📁 Upload File", "✏️ Paste Manually", "🌐 GitHub URL", "💾 Load from History"],
        horizontal=True
    )

    chat_ids: List[str] = []

    col1, col2 = st.columns([2, 1])

    with col1:
        if source == "📁 Upload File":
            uploaded = st.file_uploader(
                "Upload a .txt file with chat IDs (one per line)",
                type=SUPPORTED_TEXT_TYPES,
                key="chat_ids_upload",
                help="Lines starting with # are treated as comments"
            )
            if uploaded is not None:
                try:
                    text_content = uploaded.getvalue().decode("utf-8", errors="ignore")
                    chat_ids = parse_chat_ids_from_text(text_content)
                    st.success(SUCCESS_MESSAGES["file_uploaded"].format(count=len(chat_ids)))
                    logger.info(f"Loaded {len(chat_ids)} chat IDs from uploaded file")
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
                    logger.error(f"Error reading uploaded file: {e}")

        elif source == "✏️ Paste Manually":
            pasted = st.text_area(
                "Paste chat IDs here (one per line)",
                height=200,
                placeholder="123456789\n987654321\n...",
                help="You can also include comments using # at the start of a line"
            )
            if pasted:
                chat_ids = parse_chat_ids_from_text(pasted)

        elif source == "🌐 GitHub URL":
            raw_url = st.text_input(
                "GitHub raw URL to chat_ids.txt",
                placeholder="https://raw.githubusercontent.com/username/repo/branch/chat_ids.txt",
                help="Paste the raw URL to your chat_ids.txt file"
            )
            if raw_url:
                if validate_url(raw_url):
                    try:
                        with st.spinner("Loading chat IDs from GitHub..."):
                            resp = requests.get(raw_url, timeout=15)
                            resp.raise_for_status()
                            chat_ids = parse_chat_ids_from_text(resp.text)
                        st.success(SUCCESS_MESSAGES["github_loaded"].format(count=len(chat_ids)))
                        logger.info(f"Loaded {len(chat_ids)} chat IDs from GitHub URL")
                    except requests.RequestException as e:
                        st.error(f"{ERROR_MESSAGES['github_fetch_failed']}: {str(e)}")
                        logger.error(f"Failed to fetch from GitHub: {e}")
                    except Exception as e:
                        st.error(f"❌ Error processing URL: {str(e)}")
                        logger.error(f"Error processing GitHub URL: {e}")
                else:
                    st.error("❌ Invalid URL format")

        else:  # Load from History
            st.info("💡 This feature saves your previously used chat ID lists for quick reuse")

            if st.session_state.chat_history:
                history_choice = st.selectbox(
                    "Select a saved list:",
                    range(len(st.session_state.chat_history)),
                    format_func=lambda i: f"List from {st.session_state.chat_history[i]['date']} ({st.session_state.chat_history[i]['count']} IDs)"
                )
                chat_ids = st.session_state.chat_history[history_choice]['ids']
            else:
                st.warning("No saved lists yet. Send a broadcast to create history.")

    # Validate chat IDs
    valid_chat_ids, invalid_chat_ids = validate_chat_ids(chat_ids)

    # Store in session state
    st.session_state["valid_chat_ids"] = valid_chat_ids
    st.session_state["invalid_chat_ids"] = invalid_chat_ids

    with col2:
        # Statistics Card
        st.markdown(
            get_stat_card_html("Total Recipients", str(len(valid_chat_ids))),
            unsafe_allow_html=True
        )

        # Validation
        if chat_ids:
            if invalid_chat_ids:
                st.warning(f"⚠️ {len(invalid_chat_ids)} invalid chat ID(s) detected")
                with st.expander("View Invalid IDs"):
                    st.code("\n".join(invalid_chat_ids), language="text")
            else:
                st.success(SUCCESS_MESSAGES["all_valid"].format(count=len(valid_chat_ids)))

    # Preview chat IDs
    if valid_chat_ids:
        with st.expander(f"📋 Preview Valid Chat IDs ({len(valid_chat_ids)} total)"):
            preview_count = min(PREVIEW_CHAT_IDS_LIMIT, len(valid_chat_ids))
            st.code("\n".join(valid_chat_ids[:preview_count]), language="text")
            if len(valid_chat_ids) > preview_count:
                st.info(f"Showing first {preview_count} of {len(valid_chat_ids)} chat IDs")

        # Download chat IDs
        chat_ids_text = "\n".join(valid_chat_ids)
        st.download_button(
            "💾 Download Valid Chat IDs",
            data=chat_ids_text,
            file_name=f"chat_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ========== TAB 3: SEND ==========
with tab3:
    st.markdown("### 🚀 Send Broadcast")

    # Get values from session
    valid_chat_ids = st.session_state.get("valid_chat_ids", [])
    image_file = st.session_state.get("image_file", None)

    # Pre-flight checks
    st.markdown("#### ✈️ Pre-flight Checklist")
    check_cols = st.columns(4)

    with check_cols[0]:
        token_check = "✅" if token and validate_bot_token(token) else "❌"
        st.markdown(f"{token_check} **Bot Token**")

    with check_cols[1]:
        message_valid = caption_html.strip() and validate_message_length(caption_html, with_photo=image_file is not None)[0]
        message_check = "✅" if message_valid else "❌"
        st.markdown(f"{message_check} **Message**")

    with check_cols[2]:
        recipients_check = "✅" if valid_chat_ids else "❌"
        st.markdown(f"{recipients_check} **Recipients**")

    with check_cols[3]:
        confirm_check = "❌"
        st.markdown(f"{confirm_check} **Confirmation**")

    st.markdown("---")

    # Confirmation
    confirm_optin = st.checkbox(
        "✋ I confirm that all recipients have explicitly opted in to receive these messages",
        help="Required for legal compliance and Telegram ToS"
    )

    # Send button
    can_send = (token and validate_bot_token(token) and message_valid and
                valid_chat_ids and confirm_optin)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        send_button = st.button(
            "🚀 SEND BROADCAST" if not dry_run else "🧪 TEST BROADCAST (Dry Run)",
            use_container_width=True,
            type="primary",
            disabled=not can_send
        )

    if send_button:
        logger.info(f"Starting broadcast: dry_run={dry_run}, recipients={len(valid_chat_ids)}")

        # Save to history
        add_to_chat_history(valid_chat_ids)

        img_bytes = None
        if image_file is not None:
            img_bytes = image_file.getvalue()

        # Progress tracking
        st.markdown("---")
        st.markdown("### 📊 Broadcast Progress")

        progress_bar = st.progress(0)
        status_text = st.empty()
        stats_container = st.container()

        # Live stats
        with stats_container:
            stat_cols = st.columns(4)
            sent_metric = stat_cols[0].empty()
            failed_metric = stat_cols[1].empty()
            pending_metric = stat_cols[2].empty()
            rate_metric = stat_cols[3].empty()

        # Broadcast Logic
        async def broadcast_messages(
            token: str,
            chat_ids: List[str],
            image_bytes: Optional[bytes],
            caption: str,
            max_concurrent: int,
            send_delay: float,
            dry_run: bool
        ):
            """Execute the broadcast to all recipients."""
            bot = Bot(token=token)
            sem = asyncio.Semaphore(max_concurrent)

            total = len(chat_ids)
            results: List[Tuple[str, str]] = []
            start_time = datetime.now()

            async def worker(cid: str):
                res = await send_message_to_chat(bot, cid, image_bytes, caption, sem, dry_run)
                results.append(res)

                # Update UI
                progress = len(results) / max(1, total)
                progress_bar.progress(progress)

                sent = sum(1 for _, s in results if s == "success")
                failed = sum(1 for _, s in results if s not in ("success", "dry_run"))
                dry = sum(1 for _, s in results if s == "dry_run")
                pending = total - len(results)

                elapsed = (datetime.now() - start_time).total_seconds()
                rate = len(results) / max(1, elapsed)

                status_text.text(f"Processing: {len(results)}/{total}")
                sent_metric.metric("✅ Sent", sent if not dry_run else dry)
                failed_metric.metric("❌ Failed", failed)
                pending_metric.metric("⏳ Pending", pending)
                rate_metric.metric("⚡ Rate", f"{rate:.1f}/s")

                # Apply delay
                if send_delay > 0:
                    await asyncio.sleep(send_delay / max_concurrent)

            await asyncio.gather(*(worker(cid) for cid in chat_ids))
            return results

        # Run broadcast
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            results = loop.run_until_complete(
                broadcast_messages(token, valid_chat_ids, img_bytes, caption_html,
                                 max_concurrent, send_delay, dry_run)
            )

            # Process results
            ok = sum(1 for _, s in results if s == "success")
            dr = sum(1 for _, s in results if s == "dry_run")
            fail = len(results) - ok - dr

            # Update session stats
            if not dry_run:
                update_broadcast_stats(ok, fail)

            st.markdown("---")

            # Show results
            if dry_run:
                st.success(SUCCESS_MESSAGES["dry_run_complete"].format(count=dr))
                logger.info(f"Dry run completed: {dr} messages tested")
            else:
                if fail == 0:
                    st.success(SUCCESS_MESSAGES["broadcast_complete"].format(count=ok))
                    logger.info(f"Broadcast completed successfully: {ok} messages sent")
                else:
                    st.warning(f"✅ Sent: {ok} | ❌ Failed: {fail}")
                    logger.warning(f"Broadcast completed with errors: {ok} sent, {fail} failed")

            # Detailed results
            with st.expander("📋 View Detailed Results"):
                results_data = format_results_for_display(results, dry_run)
                st.dataframe(results_data, use_container_width=True)

                # Download results
                results_csv = generate_csv_results(results)
                st.download_button(
                    "💾 Download Results (CSV)",
                    data=results_csv,
                    file_name=f"broadcast_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        except TelegramError as e:
            st.error(f"{ERROR_MESSAGES['broadcast_failed']}: {str(e)}")
            logger.error(f"Telegram error during broadcast: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            logger.exception(f"Unexpected error during broadcast: {e}")

# ========== TAB 4: HISTORY ==========
with tab4:
    st.markdown("### 📈 Broadcast History")

    if st.session_state.total_sent > 0 or st.session_state.total_failed > 0:
        # Session summary
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                get_stat_card_html("Total Sent", str(st.session_state.total_sent)),
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                get_stat_card_html("Total Failed", str(st.session_state.total_failed),
                                   "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"),
                unsafe_allow_html=True
            )

        with col3:
            success_rate = calculate_success_rate()
            st.markdown(
                get_stat_card_html("Success Rate", f"{success_rate:.1f}%",
                                   "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"),
                unsafe_allow_html=True
            )

        # Additional stats
        if st.session_state.broadcast_count > 0:
            st.markdown(f"**Total Broadcasts:** {st.session_state.broadcast_count}")

        if st.session_state.last_broadcast_time:
            st.markdown(f"**Last Broadcast:** {st.session_state.last_broadcast_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Saved lists
        st.markdown("### 💾 Saved Recipient Lists")
        if st.session_state.chat_history:
            for i, entry in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"📅 {entry['date']} - {entry['count']} recipients"):
                    st.code("\n".join(entry['ids'][:10]), language="text")
                    if entry['count'] > 10:
                        st.info(f"Showing first 10 of {entry['count']} chat IDs")

                    # Download option
                    st.download_button(
                        "💾 Download this list",
                        data="\n".join(entry['ids']),
                        file_name=f"chat_ids_{entry['date'].replace(':', '-').replace(' ', '_')}.txt",
                        mime="text/plain",
                        key=f"download_history_{i}"
                    )
        else:
            st.info("No saved lists yet. Your broadcast history will appear here.")

        # Reset button
        st.markdown("---")
        if st.button("🔄 Reset Session Statistics", type="secondary"):
            reset_session_stats()
            st.rerun()

    else:
        st.info("📭 No broadcasts sent yet in this session. Your history will appear here after sending messages.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown(get_footer_html(), unsafe_allow_html=True)
