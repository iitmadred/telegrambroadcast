import asyncio
import io
import os
from typing import List, Tuple

import nest_asyncio
import requests
import streamlit as st
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

# Allow nested event loops (important on Streamlit Cloud)
nest_asyncio.apply()

# ---------- UI ----------
st.set_page_config(page_title="Telegram Broadcast", page_icon="📣", layout="centered")
st.title("📣 Telegram Broadcast")
st.caption("Send a formatted post and optional image to many chats concurrently.")

with st.expander("🔑 Bot Token", expanded=True):
    use_secrets = st.checkbox("Use st.secrets['TELEGRAM_TOKEN'] (recommended)", value=True)
    token = ""
    if use_secrets:
        try:
            token = st.secrets["TELEGRAM_TOKEN"]
            st.success("Loaded token from st.secrets.")
        except Exception:
            st.warning("Add TELEGRAM_TOKEN to your app secrets.")
    else:
        token = st.text_input("Paste your Telegram Bot Token", type="password")

with st.expander("📝 Compose Message", expanded=True):
    st.write("Write your caption using **Telegram HTML** tags (e.g., `<b>bold</b>`, `<i>italic</i>`, `<a href='https://...'>link</a>`).")
    caption_html = st.text_area(
        "Caption (Telegram HTML)",
        height=220,
        placeholder="""<b>🚀 AI Power Combo – Just ₹1899!</b>

Unlock the smartest AI tools at the lowest price!

✅ Feature 1
✅ Feature 2

<b>Claim your spot</b> ...""",
    )
    st.write("Preview (HTML rendered in Streamlit, will be sent to Telegram as HTML):")
    st.markdown(caption_html, unsafe_allow_html=True)

with st.expander("🖼️ Thumbnail / Image (optional)"):
    image_file = st.file_uploader("Upload image to send as photo (JPG/PNG)", type=["jpg", "jpeg", "png"])

with st.expander("👥 Chat IDs Source", expanded=True):
    source = st.radio(
        "How do you want to provide chat IDs?",
        ["Upload .txt", "Paste IDs", "GitHub raw URL"],
        index=0,
    )

    chat_ids: List[str] = []

    if source == "Upload .txt":
        uploaded = st.file_uploader(
            "Upload a .txt file with ONE chat ID per line (lines starting with # are ignored)",
            type=["txt"],
            key="chat_ids_upload",
        )
        if uploaded is not None:
            for raw in io.StringIO(uploaded.getvalue().decode("utf-8", errors="ignore")).read().splitlines():
                line = raw.strip()
                if line and not line.startswith("#"):
                    chat_ids.append(line)

    elif source == "Paste IDs":
        pasted = st.text_area(
            "Paste chat IDs here (one per line)",
            height=160,
            placeholder="123456789\n987654321\n...",
        )
        if pasted:
            for raw in pasted.splitlines():
                line = raw.strip()
                if line and not line.startswith("#"):
                    chat_ids.append(line)

    else:  # GitHub raw URL
        raw_url = st.text_input(
            "GitHub raw URL to chat_ids.txt",
            placeholder="https://raw.githubusercontent.com/<user>/<repo>/<branch>/chat_ids.txt",
        )
        if raw_url:
            try:
                resp = requests.get(raw_url, timeout=15)
                resp.raise_for_status()
                for raw in resp.text.splitlines():
                    line = raw.strip()
                    if line and not line.startswith("#"):
                        chat_ids.append(line)
                st.success(f"Loaded {len(chat_ids)} chat IDs from URL.")
            except Exception as e:
                st.error(f"Failed to load chat IDs from URL: {e}")

    st.info(f"Current chat ID count: {len(chat_ids)}")

with st.expander("⚙️ Sending Options", expanded=True):
    max_concurrent = st.slider("Max concurrent sends", min_value=1, max_value=50, value=10)
    dry_run = st.checkbox("Dry run (log only, do not send)")
    confirm_optin = st.checkbox("I confirm recipients have opted in to receive messages.", value=False)

# ---------- Sender Logic ----------
async def send_one(bot: Bot, chat_id: str, image_bytes: bytes | None, caption: str, sem: asyncio.Semaphore) -> Tuple[str, str]:
    async with sem:
        try:
            if dry_run:
                return chat_id, "dry_run"

            if image_bytes:
                # Send as photo w/ caption
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=image_bytes,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
            else:
                # Send as message
                await bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False,
                )
            return chat_id, "success"
        except TelegramError as te:
            return chat_id, f"telegram_error: {te}"
        except Exception as e:
            return chat_id, f"error: {e}"

async def broadcast(token: str, chat_ids: List[str], image_bytes: bytes | None, caption: str, max_concurrent: int, progress_slot, table_slot):
    bot = Bot(token=token)
    sem = asyncio.Semaphore(max_concurrent)

    total = len(chat_ids)
    results: List[Tuple[str, str]] = []

    async def worker(cid: str):
        res = await send_one(bot, cid, image_bytes, caption, sem)
        results.append(res)
        # update UI
        progress_slot.progress(len(results) / max(1, total))
        # Live table
        table_slot.write(
            {
                "sent": sum(1 for _, s in results if s == "success"),
                "failed": sum(1 for _, s in results if s not in ("success", "dry_run")),
                "dry_run": sum(1 for _, s in results if s == "dry_run"),
            }
        )

    await asyncio.gather(*(worker(cid) for cid in chat_ids))
    return results

# ---------- Run ----------
start = st.button("🚀 Send Broadcast", use_container_width=True, type="primary")

if start:
    if not token:
        st.error("Bot token is required.")
        st.stop()
    if not caption_html.strip():
        st.error("Caption is required.")
        st.stop()
    if not chat_ids:
        st.error("No chat IDs loaded.")
        st.stop()
    if not confirm_optin:
        st.error("Please confirm recipients have opted in.")
        st.stop()

    img_bytes = None
    if image_file is not None:
        img_bytes = image_file.getvalue()

    progress_slot = st.empty()
    table_slot = st.empty()
    log_area = st.empty()

    st.info(f"Starting broadcast to {len(chat_ids)} chats with concurrency={max_concurrent} (dry_run={dry_run}).")

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    results = loop.run_until_complete(
        broadcast(token, chat_ids, img_bytes, caption_html, max_concurrent, progress_slot, table_slot)
    )

    # Detailed log
    ok = sum(1 for _, s in results if s == "success")
    dr = sum(1 for _, s in results if s == "dry_run")
    fail = len(results) - ok - dr

    st.success(f"Done. Success: {ok}, Dry-run: {dr}, Failed: {fail}")
    with st.expander("View per-chat results"):
        st.dataframe({
            "chat_id": [cid for cid, _ in results],
            "status": [s for _, s in results],
        })

st.markdown("""
---
### Notes
- Use **HTML parse mode** only with Telegram-supported tags: `<b>`, `<i>`, `<u>`, `<s>`, `<a href>`, `<code>`, `<pre>`, etc.
- Respect Telegram anti-spam and rate limits. Large fan-outs may require throttling.
- Keep your bot token in **Secrets**, never commit it to the repo.
- ⚠️ Please only message recipients who have opted in. Respect Telegram's anti-spam rules and rate limits.
""")
