import asyncio
import io
import os
from typing import List, Tuple
from datetime import datetime

import nest_asyncio
import requests
import streamlit as st
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

# Allow nested event loops (important on Streamlit Cloud)
nest_asyncio.apply()

# ---------- CUSTOM CSS & STYLING ----------
st.set_page_config(
    page_title="Telegram Broadcast Pro",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #0088cc;
        --secondary-color: #00a8e8;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }

    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }

    /* Card styling */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }

    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }

    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }

    /* Formatting toolbar */
    .format-toolbar {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .format-btn {
        background: white;
        border: 1px solid #dee2e6;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
        font-family: monospace;
    }

    .format-btn:hover {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }

    /* Preview box */
    .preview-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px dashed #dee2e6;
        min-height: 150px;
        margin-top: 1rem;
    }

    /* Progress styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    /* Info boxes */
    .info-box {
        background: #e7f3ff;
        border-left: 4px solid #0088cc;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }

    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }

    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="main-header">
    <h1>📢 Telegram Broadcast Pro</h1>
    <p>Professional Broadcasting Tool with Advanced Features</p>
</div>
""", unsafe_allow_html=True)

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
            st.success("✓ Token loaded from secrets")
        except Exception:
            st.error("⚠️ Add TELEGRAM_TOKEN to secrets")
    else:
        token = st.text_input("Bot Token", type="password", placeholder="Enter your bot token")

    st.markdown("---")

    # Sending Options
    st.markdown("#### 🎚️ Send Settings")
    max_concurrent = st.slider(
        "Concurrent Sends",
        min_value=1,
        max_value=50,
        value=10,
        help="Number of messages sent simultaneously"
    )

    send_delay = st.slider(
        "Delay Between Batches (seconds)",
        min_value=0,
        max_value=10,
        value=1,
        help="Helps avoid rate limits"
    )

    dry_run = st.checkbox(
        "🧪 Dry Run Mode",
        help="Test without actually sending messages"
    )

    st.markdown("---")

    # Statistics
    st.markdown("#### 📊 Quick Stats")
    if 'total_sent' not in st.session_state:
        st.session_state.total_sent = 0
    if 'total_failed' not in st.session_state:
        st.session_state.total_failed = 0

    st.metric("Total Sent (Session)", st.session_state.total_sent)
    st.metric("Total Failed (Session)", st.session_state.total_failed)

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

        templates = {
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

        template_choice = None
        for i, (name, template) in enumerate(templates.items()):
            with template_cols[i]:
                if st.button(f"📄 {name}", use_container_width=True):
                    template_choice = template

        # Formatting Toolbar
        st.markdown("#### 🎨 Formatting Toolbar")

        format_cols = st.columns(8)
        format_help = {
            "Bold": "<b>text</b>",
            "Italic": "<i>text</i>",
            "Underline": "<u>text</u>",
            "Strike": "<s>text</s>",
            "Code": "<code>text</code>",
            "Link": "<a href='URL'>text</a>",
            "Pre": "<pre>code</pre>",
            "Clear": "Clear all"
        }

        with format_cols[0]:
            if st.button("**B**", help=format_help["Bold"], use_container_width=True):
                st.info("Wrap text with: `<b>text</b>`")
        with format_cols[1]:
            if st.button("*I*", help=format_help["Italic"], use_container_width=True):
                st.info("Wrap text with: `<i>text</i>`")
        with format_cols[2]:
            if st.button("<u>U</u>", help=format_help["Underline"], use_container_width=True):
                st.info("Wrap text with: `<u>text</u>`")
        with format_cols[3]:
            if st.button("~~S~~", help=format_help["Strike"], use_container_width=True):
                st.info("Wrap text with: `<s>text</s>`")
        with format_cols[4]:
            if st.button("`<>`", help=format_help["Code"], use_container_width=True):
                st.info("Wrap text with: `<code>text</code>`")
        with format_cols[5]:
            if st.button("🔗", help=format_help["Link"], use_container_width=True):
                st.info("Format: `<a href='URL'>text</a>`")
        with format_cols[6]:
            if st.button("{ }", help=format_help["Pre"], use_container_width=True):
                st.info("Wrap code with: `<pre>code</pre>`")

        # Text Editor
        st.markdown("#### 📝 Message Content")
        caption_html = st.text_area(
            "Compose your message (HTML supported)",
            height=300,
            value=template_choice if template_choice else "",
            placeholder="Type your message here...\n\nUse HTML tags for formatting:\n<b>Bold</b>, <i>Italic</i>, <u>Underline</u>, <s>Strike</s>\n<code>Code</code>, <pre>Preformatted</pre>\n<a href='URL'>Link</a>",
            key="message_content"
        )

        # Character count
        char_count = len(caption_html)
        if char_count > 1024:
            st.warning(f"⚠️ Message length: {char_count} characters (Telegram limit with photo: 1024)")
        else:
            st.info(f"📊 Character count: {char_count}/1024")

        # Image Upload
        st.markdown("#### 🖼️ Attach Image (Optional)")
        image_file = st.file_uploader(
            "Upload an image to send with your message",
            type=["jpg", "jpeg", "png", "gif"],
            help="Supports JPG, PNG, and GIF formats"
        )

        if image_file:
            st.success(f"✓ Image attached: {image_file.name} ({image_file.size / 1024:.1f} KB)")

    with col2:
        st.markdown("### 👀 Live Preview")

        # Preview card
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        if caption_html.strip():
            st.markdown(caption_html, unsafe_allow_html=True)
        else:
            st.markdown("*Your message preview will appear here...*")
        st.markdown('</div>', unsafe_allow_html=True)

        if image_file:
            st.markdown("#### 📷 Image Preview")
            st.image(image_file, use_container_width=True)

        # HTML Code View
        with st.expander("📄 View HTML Source"):
            st.code(caption_html, language="html")

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
                type=["txt"],
                key="chat_ids_upload",
                help="Lines starting with # are treated as comments"
            )
            if uploaded is not None:
                for raw in io.StringIO(uploaded.getvalue().decode("utf-8", errors="ignore")).read().splitlines():
                    line = raw.strip()
                    if line and not line.startswith("#"):
                        chat_ids.append(line)
                st.success(f"✓ Loaded {len(chat_ids)} chat IDs from file")

        elif source == "✏️ Paste Manually":
            pasted = st.text_area(
                "Paste chat IDs here (one per line)",
                height=200,
                placeholder="123456789\n987654321\n...",
                help="You can also include comments using # at the start of a line"
            )
            if pasted:
                for raw in pasted.splitlines():
                    line = raw.strip()
                    if line and not line.startswith("#"):
                        chat_ids.append(line)

        elif source == "🌐 GitHub URL":
            raw_url = st.text_input(
                "GitHub raw URL to chat_ids.txt",
                placeholder="https://raw.githubusercontent.com/username/repo/branch/chat_ids.txt",
                help="Paste the raw URL to your chat_ids.txt file"
            )
            if raw_url:
                try:
                    with st.spinner("Loading chat IDs from GitHub..."):
                        resp = requests.get(raw_url, timeout=15)
                        resp.raise_for_status()
                        for raw in resp.text.splitlines():
                            line = raw.strip()
                            if line and not line.startswith("#"):
                                chat_ids.append(line)
                    st.success(f"✓ Loaded {len(chat_ids)} chat IDs from URL")
                except Exception as e:
                    st.error(f"❌ Failed to load: {e}")

        else:  # Load from History
            st.info("💡 This feature saves your previously used chat ID lists for quick reuse")
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []

            if st.session_state.chat_history:
                history_choice = st.selectbox(
                    "Select a saved list:",
                    range(len(st.session_state.chat_history)),
                    format_func=lambda i: f"List from {st.session_state.chat_history[i]['date']} ({st.session_state.chat_history[i]['count']} IDs)"
                )
                chat_ids = st.session_state.chat_history[history_choice]['ids']
            else:
                st.warning("No saved lists yet. Send a broadcast to create history.")

    with col2:
        # Statistics Card
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Recipients</div>
            <div class="stat-number">{len(chat_ids)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Validation
        if chat_ids:
            valid_count = sum(1 for cid in chat_ids if cid.isdigit() or (cid.startswith('-') and cid[1:].isdigit()))
            invalid_count = len(chat_ids) - valid_count

            if invalid_count > 0:
                st.warning(f"⚠️ {invalid_count} invalid chat ID(s) detected")
            else:
                st.success(f"✓ All {valid_count} chat IDs are valid")

    # Preview chat IDs
    if chat_ids:
        with st.expander(f"📋 Preview Chat IDs ({len(chat_ids)} total)"):
            preview_count = min(20, len(chat_ids))
            st.code("\n".join(chat_ids[:preview_count]), language="text")
            if len(chat_ids) > preview_count:
                st.info(f"Showing first {preview_count} of {len(chat_ids)} chat IDs")

        # Download chat IDs
        chat_ids_text = "\n".join(chat_ids)
        st.download_button(
            "💾 Download Chat IDs",
            data=chat_ids_text,
            file_name="chat_ids.txt",
            mime="text/plain",
            use_container_width=True
        )

# ========== TAB 3: SEND ==========
with tab3:
    st.markdown("### 🚀 Send Broadcast")

    # Pre-flight checks
    st.markdown("#### ✈️ Pre-flight Checklist")
    check_cols = st.columns(4)

    with check_cols[0]:
        token_check = "✅" if token else "❌"
        st.markdown(f"{token_check} **Bot Token**")

    with check_cols[1]:
        message_check = "✅" if caption_html.strip() else "❌"
        st.markdown(f"{message_check} **Message**")

    with check_cols[2]:
        recipients_check = "✅" if chat_ids else "❌"
        st.markdown(f"{recipients_check} **Recipients**")

    with check_cols[3]:
        confirm_check = "❌"
        st.markdown(f"{confirm_check} **Confirmation**")

    st.markdown("---")

    # Confirmation
    confirm_optin = st.checkbox(
        "✋ I confirm that all recipients have opted in to receive these messages",
        help="Required for legal compliance and Telegram ToS"
    )

    # Send button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        send_button = st.button(
            "🚀 SEND BROADCAST" if not dry_run else "🧪 TEST BROADCAST (Dry Run)",
            use_container_width=True,
            type="primary",
            disabled=not (token and caption_html.strip() and chat_ids and confirm_optin)
        )

    if send_button:
        # Save to history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        st.session_state.chat_history.append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'count': len(chat_ids),
            'ids': chat_ids.copy()
        })

        # Keep only last 10 entries
        if len(st.session_state.chat_history) > 10:
            st.session_state.chat_history = st.session_state.chat_history[-10:]

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

        # Sender Logic
        async def send_one(bot: Bot, chat_id: str, image_bytes: bytes | None, caption: str, sem: asyncio.Semaphore) -> Tuple[str, str]:
            async with sem:
                try:
                    if dry_run:
                        await asyncio.sleep(0.1)  # Simulate send
                        return chat_id, "dry_run"

                    if image_bytes:
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=image_bytes,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                        )
                    else:
                        await bot.send_message(
                            chat_id=chat_id,
                            text=caption,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=False,
                        )

                    await asyncio.sleep(send_delay / max_concurrent)
                    return chat_id, "success"

                except TelegramError as te:
                    return chat_id, f"telegram_error: {te}"
                except Exception as e:
                    return chat_id, f"error: {e}"

        async def broadcast(token: str, chat_ids: List[str], image_bytes: bytes | None, caption: str, max_concurrent: int):
            bot = Bot(token=token)
            sem = asyncio.Semaphore(max_concurrent)

            total = len(chat_ids)
            results: List[Tuple[str, str]] = []
            start_time = datetime.now()

            async def worker(cid: str):
                res = await send_one(bot, cid, image_bytes, caption, sem)
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

            await asyncio.gather(*(worker(cid) for cid in chat_ids))
            return results

        # Run broadcast
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        results = loop.run_until_complete(
            broadcast(token, chat_ids, img_bytes, caption_html, max_concurrent)
        )

        # Final results
        ok = sum(1 for _, s in results if s == "success")
        dr = sum(1 for _, s in results if s == "dry_run")
        fail = len(results) - ok - dr

        # Update session stats
        st.session_state.total_sent += ok
        st.session_state.total_failed += fail

        st.markdown("---")

        if dry_run:
            st.success(f"🧪 **Dry Run Complete!** Tested {dr} messages successfully")
        else:
            if fail == 0:
                st.success(f"🎉 **Broadcast Complete!** Successfully sent to all {ok} recipients!")
            else:
                st.warning(f"✅ Sent: {ok} | ❌ Failed: {fail}")

        # Detailed results
        with st.expander("📋 View Detailed Results"):
            results_data = {
                "Chat ID": [cid for cid, _ in results],
                "Status": ["✅ Success" if s == "success" else "🧪 Dry Run" if s == "dry_run" else "❌ Failed" for _, s in results],
                "Details": [s for _, s in results]
            }
            st.dataframe(results_data, use_container_width=True)

            # Download results
            results_csv = "Chat ID,Status,Details\n"
            for cid, status in results:
                results_csv += f"{cid},{status.split(':')[0]},{status}\n"

            st.download_button(
                "💾 Download Results (CSV)",
                data=results_csv,
                file_name=f"broadcast_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# ========== TAB 4: HISTORY ==========
with tab4:
    st.markdown("### 📈 Broadcast History")

    if st.session_state.total_sent > 0 or st.session_state.total_failed > 0:
        # Session summary
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Sent</div>
                <div class="stat-number">{st.session_state.total_sent}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="stat-label">Total Failed</div>
                <div class="stat-number">{st.session_state.total_failed}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            success_rate = (st.session_state.total_sent / max(1, st.session_state.total_sent + st.session_state.total_failed)) * 100
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="stat-label">Success Rate</div>
                <div class="stat-number">{success_rate:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # Saved lists
        st.markdown("### 💾 Saved Recipient Lists")
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            for i, entry in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"📅 {entry['date']} - {entry['count']} recipients"):
                    st.code("\n".join(entry['ids'][:10]), language="text")
                    if entry['count'] > 10:
                        st.info(f"Showing first 10 of {entry['count']} chat IDs")
        else:
            st.info("No saved lists yet. Your broadcast history will appear here.")

        # Reset button
        if st.button("🔄 Reset Session Statistics", type="secondary"):
            st.session_state.total_sent = 0
            st.session_state.total_failed = 0
            st.session_state.chat_history = []
            st.rerun()

    else:
        st.info("📭 No broadcasts sent yet in this session. Your history will appear here after sending messages.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p><b>⚠️ Important Reminders</b></p>
    <p>• Only message recipients who have explicitly opted in</p>
    <p>• Respect Telegram's anti-spam rules and rate limits</p>
    <p>• Keep your bot token secure - never share it publicly</p>
    <p>• Use dry run mode to test before sending to real recipients</p>
    <hr style="margin: 1rem auto; width: 50%; opacity: 0.3;">
    <p style="font-size: 0.9rem; opacity: 0.7;">Made with ❤️ using Streamlit | © 2024</p>
</div>
""", unsafe_allow_html=True)
