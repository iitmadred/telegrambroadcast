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

# ---------- MODERN UI CONFIGURATION ----------
st.set_page_config(
    page_title="Telegram Broadcast Pro",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'total_sent' not in st.session_state:
    st.session_state.total_sent = 0
if 'total_failed' not in st.session_state:
    st.session_state.total_failed = 0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'auto_loaded_ids' not in st.session_state:
    st.session_state.auto_loaded_ids = []

# ---------- ADVANCED CSS WITH GLASSMORPHISM & DARK MODE ----------
dark_mode = st.session_state.dark_mode

# Color schemes
if dark_mode:
    bg_primary = "#0f0f23"
    bg_secondary = "#1a1a2e"
    text_primary = "#eaeaea"
    text_secondary = "#b4b4b4"
    glass_bg = "rgba(255, 255, 255, 0.05)"
    glass_border = "rgba(255, 255, 255, 0.1)"
    card_bg = "rgba(26, 26, 46, 0.6)"
else:
    bg_primary = "#f5f7fa"
    bg_secondary = "#ffffff"
    text_primary = "#2d3748"
    text_secondary = "#718096"
    glass_bg = "rgba(255, 255, 255, 0.7)"
    glass_border = "rgba(255, 255, 255, 0.3)"
    card_bg = "rgba(255, 255, 255, 0.8)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global Styles */
    * {{
        font-family: 'Inter', sans-serif;
    }}

    .main {{
        background: {'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' if not dark_mode else 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%)'};
    }}

    /* Glassmorphism Cards */
    .glass-card {{
        background: {glass_bg};
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-radius: 20px;
        border: 1px solid {glass_border};
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1.5rem;
    }}

    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }}

    /* Hero Header with Gradient Mesh */
    .hero-header {{
        position: relative;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 3rem 2rem;
        border-radius: 30px;
        margin-bottom: 2rem;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    }}

    .hero-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }}

    @keyframes rotate {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    .hero-content {{
        position: relative;
        z-index: 1;
        text-align: center;
    }}

    .hero-title {{
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        letter-spacing: -1px;
    }}

    .hero-subtitle {{
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.95);
        margin-top: 1rem;
        font-weight: 400;
    }}

    .hero-badge {{
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        margin-top: 1rem;
        font-size: 0.9rem;
        color: white;
        font-weight: 600;
    }}

    /* Modern Stat Cards */
    .stat-card-modern {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}

    .stat-card-modern::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: translateX(-100%);
        transition: transform 0.6s;
    }}

    .stat-card-modern:hover::before {{
        transform: translateX(100%);
    }}

    .stat-card-modern:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }}

    .stat-number {{
        font-size: 3rem;
        font-weight: 800;
        margin: 0.5rem 0;
        position: relative;
        z-index: 1;
    }}

    .stat-label {{
        font-size: 0.95rem;
        opacity: 0.95;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        z-index: 1;
    }}

    /* Floating Action Button */
    .fab {{
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 9999;
    }}

    .fab:hover {{
        transform: scale(1.1) rotate(90deg);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
    }}

    /* Modern Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }}

    .stButton>button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }}

    .stButton>button:hover::before {{
        left: 100%;
    }}

    .stButton>button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
    }}

    .stButton>button:active {{
        transform: translateY(-1px);
    }}

    /* Template Buttons */
    .template-btn {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        border: 2px solid {glass_border};
        border-radius: 15px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }}

    .template-btn:hover {{
        border-color: #667eea;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }}

    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1rem;
        background: {card_bg};
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 0.5rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 15px;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(102, 126, 234, 0.1);
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }}

    /* Progress Bar */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 10px;
    }}

    /* Text Areas and Inputs */
    .stTextArea textarea, .stTextInput input {{
        background: {card_bg} !important;
        backdrop-filter: blur(10px);
        border: 2px solid {glass_border} !important;
        border-radius: 15px !important;
        color: {text_primary} !important;
        transition: all 0.3s ease;
    }}

    .stTextArea textarea:focus, .stTextInput input:focus {{
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }}

    /* Preview Box */
    .preview-box {{
        background: {card_bg};
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        border: 2px dashed {glass_border};
        min-height: 200px;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }}

    .preview-box:hover {{
        border-color: #667eea;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }}

    section[data-testid="stSidebar"] > div {{
        background: transparent;
    }}

    /* Metric Cards */
    [data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: 700;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid {glass_border};
        font-weight: 600;
        transition: all 0.3s ease;
    }}

    .streamlit-expanderHeader:hover {{
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }}

    /* Checkbox */
    .stCheckbox {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 15px;
        border: 1px solid {glass_border};
        transition: all 0.3s ease;
    }}

    .stCheckbox:hover {{
        border-color: #667eea;
    }}

    /* Slider */
    .stSlider {{
        padding: 1rem;
    }}

    /* Radio */
    .stRadio > div {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 15px;
        border: 1px solid {glass_border};
    }}

    /* File Uploader */
    [data-testid="stFileUploader"] {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 2px dashed {glass_border};
        padding: 2rem;
        transition: all 0.3s ease;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: #667eea;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }}

    /* Notifications */
    .stAlert {{
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: none;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }}

    /* Format Toolbar */
    .format-toolbar {{
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        padding: 1rem;
        background: {card_bg};
        backdrop-filter: blur(10px);
        border-radius: 15px;
        margin: 1rem 0;
    }}

    /* Dark Mode Toggle */
    .dark-mode-toggle {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 9998;
        background: {card_bg};
        backdrop-filter: blur(20px);
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        border: 1px solid {glass_border};
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }}

    .dark-mode-toggle:hover {{
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }}

    /* Loading Animation */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}

    .loading {{
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}

    /* Smooth Scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}

    ::-webkit-scrollbar-track {{
        background: {bg_primary};
    }}

    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }}

    /* Auto-load Badge */
    .auto-badge {{
        display: inline-block;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }}
</style>
""", unsafe_allow_html=True)

# ---------- HERO HEADER ----------
st.markdown("""
<div class="hero-header">
    <div class="hero-content">
        <div class="hero-title">📢 Telegram Broadcast Pro</div>
        <div class="hero-subtitle">Next-Gen Broadcasting Platform with AI-Powered Features</div>
        <div class="hero-badge">✨ Auto-Load • 🎨 Modern UI • ⚡ Lightning Fast</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- AUTO-LOAD CHAT IDs FROM REPO ----------
def load_chat_ids_from_file():
    """Auto-load chat IDs from the repo's chat_ids.txt file"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'chat_ids.txt')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                ids = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ids.append(line)
                return ids
        return []
    except Exception as e:
        return []

# Auto-load on first run
if not st.session_state.auto_loaded_ids:
    st.session_state.auto_loaded_ids = load_chat_ids_from_file()

# ---------- SIDEBAR CONFIGURATION ----------
with st.sidebar:
    # Dark Mode Toggle at top
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🌓", help="Toggle Dark Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
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
            st.success("✓ Token loaded")
        except Exception:
            st.error("⚠️ Add token to secrets")
    else:
        token = st.text_input("Bot Token", type="password", placeholder="Enter token")

    st.markdown("---")

    # Advanced Settings
    st.markdown("#### 🎚️ Advanced Settings")

    max_concurrent = st.slider(
        "⚡ Concurrent Sends",
        min_value=1,
        max_value=50,
        value=10,
        help="Parallel message sends"
    )

    send_delay = st.slider(
        "⏱️ Batch Delay (s)",
        min_value=0,
        max_value=10,
        value=1,
        help="Prevents rate limiting"
    )

    dry_run = st.checkbox(
        "🧪 Dry Run Mode",
        help="Test without sending"
    )

    st.markdown("---")

    # Session Statistics
    st.markdown("#### 📊 Session Stats")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sent", st.session_state.total_sent, delta=None)
    with col2:
        st.metric("Failed", st.session_state.total_failed, delta=None)

    if st.session_state.total_sent > 0 or st.session_state.total_failed > 0:
        success_rate = (st.session_state.total_sent / max(1, st.session_state.total_sent + st.session_state.total_failed)) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")

    st.markdown("---")

    # Auto-loaded IDs info
    if st.session_state.auto_loaded_ids:
        st.markdown("#### 💾 Auto-Loaded")
        st.success(f"✓ {len(st.session_state.auto_loaded_ids)} IDs from repo")
        if st.button("🔄 Reload from File", use_container_width=True):
            st.session_state.auto_loaded_ids = load_chat_ids_from_file()
            st.rerun()

    st.markdown("---")
    st.markdown("##### 💡 Pro Tips")
    st.info("• Use dry run first\n• Check character limits\n• Test with small groups")

# ---------- MAIN CONTENT TABS ----------
tab1, tab2, tab3, tab4 = st.tabs(["✍️ Compose", "👥 Recipients", "🚀 Send", "📈 Analytics"])

# ========== TAB 1: COMPOSE ==========
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### ✍️ Message Composer")

        # Quick Templates
        st.markdown("#### 📋 Quick Templates")
        template_cols = st.columns(4)

        templates = {
            "📢 Announcement": """<b>📢 Important Announcement</b>

[Your message here]

<i>- Team</i>""",
            "🎉 Promotion": """<b>🎉 Special Offer Alert!</b>

✨ [Offer Details]

💰 <b>Price:</b> [Amount]
⏰ <b>Valid Until:</b> [Date]

<a href='[link]'>Claim Now →</a>""",
            "🔔 Update": """<b>🔔 Platform Update</b>

We're excited to announce:

• [Feature 1]
• [Feature 2]
• [Feature 3]

<i>Stay tuned for more!</i>""",
            "📅 Event": """<b>📅 You're Invited!</b>

📍 <b>Where:</b> [Location]
🕐 <b>When:</b> [Time]
📆 <b>Date:</b> [Date]

<a href='[link]'>RSVP Now →</a>"""
        }

        template_choice = None
        for i, (name, template) in enumerate(templates.items()):
            with template_cols[i]:
                if st.button(name, use_container_width=True, key=f"template_{i}"):
                    template_choice = template

        # Formatting Toolbar
        st.markdown("#### 🎨 Formatting Tools")

        format_cols = st.columns(7)

        with format_cols[0]:
            if st.button("**Bold**", use_container_width=True, help="<b>text</b>"):
                st.info("`<b>text</b>`")
        with format_cols[1]:
            if st.button("*Italic*", use_container_width=True, help="<i>text</i>"):
                st.info("`<i>text</i>`")
        with format_cols[2]:
            if st.button("__Under__", use_container_width=True, help="<u>text</u>"):
                st.info("`<u>text</u>`")
        with format_cols[3]:
            if st.button("~~Strike~~", use_container_width=True, help="<s>text</s>"):
                st.info("`<s>text</s>`")
        with format_cols[4]:
            if st.button("`Code`", use_container_width=True, help="<code>text</code>"):
                st.info("`<code>text</code>`")
        with format_cols[5]:
            if st.button("🔗 Link", use_container_width=True, help="<a href>text</a>"):
                st.info("`<a href='URL'>text</a>`")
        with format_cols[6]:
            if st.button("{ Pre }", use_container_width=True, help="<pre>code</pre>"):
                st.info("`<pre>code</pre>`")

        # Message Editor
        st.markdown("#### 📝 Your Message")
        caption_html = st.text_area(
            "Compose with HTML formatting",
            height=350,
            value=template_choice if template_choice else "",
            placeholder="Start typing your message...\n\nSupported HTML tags:\n<b>Bold</b> <i>Italic</i> <u>Underline</u> <s>Strike</s>\n<code>Code</code> <pre>Pre</pre> <a href='URL'>Link</a>",
            key="message_content"
        )

        # Character Counter with Visual Feedback
        char_count = len(caption_html)
        max_chars = 1024
        percentage = (char_count / max_chars) * 100

        if percentage > 100:
            color = "#dc3545"
            icon = "⚠️"
            message = f"Exceeds limit by {char_count - max_chars} characters!"
        elif percentage > 80:
            color = "#ffc107"
            icon = "⚡"
            message = f"{max_chars - char_count} characters remaining"
        else:
            color = "#28a745"
            icon = "✓"
            message = f"{char_count}/{max_chars} characters"

        st.markdown(f"""
        <div style="background: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1);
                    padding: 1rem; border-radius: 10px; border-left: 4px solid {color};">
            <b>{icon} {message}</b>
            <div style="background: #eee; height: 8px; border-radius: 10px; margin-top: 0.5rem; overflow: hidden;">
                <div style="background: {color}; height: 100%; width: {min(percentage, 100)}%;
                           border-radius: 10px; transition: all 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Image Upload
        st.markdown("#### 🖼️ Attach Media")
        image_file = st.file_uploader(
            "Upload image (Optional)",
            type=["jpg", "jpeg", "png", "gif", "webp"],
            help="Supported: JPG, PNG, GIF, WebP"
        )

        if image_file:
            file_size = image_file.size / 1024
            st.success(f"✓ **{image_file.name}** ({file_size:.1f} KB)")

    with col2:
        st.markdown("### 👀 Live Preview")

        # Preview Card
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        if caption_html.strip():
            st.markdown(caption_html, unsafe_allow_html=True)
        else:
            st.markdown("*Your message preview will appear here...*")
        st.markdown('</div>', unsafe_allow_html=True)

        if image_file:
            st.markdown("#### 📷 Image Preview")
            st.image(image_file, use_container_width=True)

        # HTML Source
        with st.expander("📄 View HTML Source"):
            st.code(caption_html, language="html")

        # Quick Actions
        st.markdown("#### ⚡ Quick Actions")
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.info("💡 Use Ctrl+C to copy the message")

        if caption_html.strip():
            if st.button("🗑️ Clear Message", use_container_width=True):
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ========== TAB 2: RECIPIENTS ==========
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 👥 Recipient Management")

    # Auto-loaded indicator
    if st.session_state.auto_loaded_ids:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    padding: 1rem; border-radius: 15px; color: white; margin-bottom: 1rem;">
            <b>🎯 Auto-Loaded from Repository:</b> {len(st.session_state.auto_loaded_ids)} chat IDs ready to broadcast!
        </div>
        """, unsafe_allow_html=True)

    source = st.radio(
        "📡 Select Input Method:",
        ["🎯 Use Auto-Loaded (Repo)", "📁 Upload File", "✏️ Paste Manually", "🌐 GitHub URL", "💾 Load from History"],
        horizontal=True
    )

    chat_ids: List[str] = []

    col1, col2 = st.columns([2, 1])

    with col1:
        if source == "🎯 Use Auto-Loaded (Repo)":
            chat_ids = st.session_state.auto_loaded_ids.copy()
            if chat_ids:
                st.success(f"✓ Using {len(chat_ids)} auto-loaded chat IDs from `chat_ids.txt`")

                # Show sample
                with st.expander("👁️ Preview Auto-Loaded IDs"):
                    preview_count = min(10, len(chat_ids))
                    st.code("\n".join(chat_ids[:preview_count]), language="text")
                    if len(chat_ids) > preview_count:
                        st.info(f"Showing first {preview_count} of {len(chat_ids)} IDs")
            else:
                st.warning("⚠️ No chat IDs found in `chat_ids.txt`. Choose another method.")

        elif source == "📁 Upload File":
            uploaded = st.file_uploader(
                "Upload .txt file with chat IDs",
                type=["txt"],
                key="chat_ids_upload",
                help="One chat ID per line, # for comments"
            )
            if uploaded is not None:
                for raw in io.StringIO(uploaded.getvalue().decode("utf-8", errors="ignore")).read().splitlines():
                    line = raw.strip()
                    if line and not line.startswith("#"):
                        chat_ids.append(line)
                st.success(f"✓ Loaded {len(chat_ids)} chat IDs from file")

        elif source == "✏️ Paste Manually":
            pasted = st.text_area(
                "Paste chat IDs (one per line)",
                height=250,
                placeholder="123456789\n987654321\n# Comments start with #",
                help="Paste your chat IDs here"
            )
            if pasted:
                for raw in pasted.splitlines():
                    line = raw.strip()
                    if line and not line.startswith("#"):
                        chat_ids.append(line)

        elif source == "🌐 GitHub URL":
            raw_url = st.text_input(
                "GitHub Raw URL",
                placeholder="https://raw.githubusercontent.com/user/repo/branch/chat_ids.txt",
                help="Direct link to your chat_ids.txt"
            )
            if raw_url:
                try:
                    with st.spinner("🔄 Fetching from GitHub..."):
                        resp = requests.get(raw_url, timeout=15)
                        resp.raise_for_status()
                        for raw in resp.text.splitlines():
                            line = raw.strip()
                            if line and not line.startswith("#"):
                                chat_ids.append(line)
                    st.success(f"✓ Loaded {len(chat_ids)} IDs from GitHub")
                except Exception as e:
                    st.error(f"❌ Failed: {e}")

        else:  # History
            st.info("💡 Previously used recipient lists")
            if st.session_state.chat_history:
                history_choice = st.selectbox(
                    "Select saved list:",
                    range(len(st.session_state.chat_history)),
                    format_func=lambda i: f"📅 {st.session_state.chat_history[i]['date']} ({st.session_state.chat_history[i]['count']} IDs)"
                )
                chat_ids = st.session_state.chat_history[history_choice]['ids']
                st.success(f"✓ Loaded {len(chat_ids)} IDs from history")
            else:
                st.warning("No saved lists. Send a broadcast to create history.")

    with col2:
        # Modern Stat Card
        gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        if len(chat_ids) > 1000:
            gradient = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
        elif len(chat_ids) > 100:
            gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"

        st.markdown(f"""
        <div class="stat-card-modern" style="background: {gradient};">
            <div class="stat-label">Total Recipients</div>
            <div class="stat-number">{len(chat_ids):,}</div>
        </div>
        """, unsafe_allow_html=True)

        # Validation
        if chat_ids:
            valid_count = sum(1 for cid in chat_ids if cid.isdigit() or (cid.startswith('-') and cid[1:].isdigit()))
            invalid_count = len(chat_ids) - valid_count

            if invalid_count > 0:
                st.warning(f"⚠️ {invalid_count} invalid ID(s)")
            else:
                st.success(f"✓ All {valid_count:,} IDs valid")

            # Statistics breakdown
            st.markdown("#### 📊 Breakdown")
            st.metric("Valid IDs", f"{valid_count:,}")
            st.metric("Invalid IDs", invalid_count)

    # Preview and Download
    if chat_ids:
        col1, col2 = st.columns(2)

        with col1:
            with st.expander(f"📋 Preview IDs ({len(chat_ids):,} total)"):
                preview_count = min(20, len(chat_ids))
                st.code("\n".join(chat_ids[:preview_count]), language="text")
                if len(chat_ids) > preview_count:
                    st.info(f"Showing {preview_count} of {len(chat_ids):,}")

        with col2:
            chat_ids_text = "\n".join(chat_ids)
            st.download_button(
                "💾 Download List",
                data=chat_ids_text,
                file_name=f"chat_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

# ========== TAB 3: SEND ==========
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Launch Broadcast")

    # Pre-flight Checklist
    st.markdown("#### ✈️ Pre-flight Checklist")

    checks = {
        "Bot Token": bool(token),
        "Message": bool(caption_html.strip()),
        "Recipients": bool(chat_ids),
        "Confirmation": False
    }

    check_cols = st.columns(len(checks))
    for i, (name, status) in enumerate(checks.items()):
        with check_cols[i]:
            icon = "✅" if status else "❌"
            st.markdown(f"### {icon}\n**{name}**")

    st.markdown("---")

    # Confirmation
    confirm_optin = st.checkbox(
        "✋ I confirm all recipients have opted in to receive messages",
        help="Required by Telegram ToS and legal compliance"
    )

    # Send Button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        send_enabled = token and caption_html.strip() and chat_ids and confirm_optin
        button_text = "🧪 TEST BROADCAST" if dry_run else "🚀 SEND BROADCAST"

        send_button = st.button(
            button_text,
            use_container_width=True,
            type="primary",
            disabled=not send_enabled
        )

    if send_button:
        # Save to history
        st.session_state.chat_history.append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'count': len(chat_ids),
            'ids': chat_ids.copy()
        })

        if len(st.session_state.chat_history) > 10:
            st.session_state.chat_history = st.session_state.chat_history[-10:]

        img_bytes = image_file.getvalue() if image_file else None

        # Progress UI
        st.markdown("---")
        st.markdown("### 📊 Broadcast in Progress")

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Live metrics
        metric_cols = st.columns(4)
        sent_metric = metric_cols[0].empty()
        failed_metric = metric_cols[1].empty()
        pending_metric = metric_cols[2].empty()
        rate_metric = metric_cols[3].empty()

        # Broadcast Logic
        async def send_one(bot: Bot, chat_id: str, image_bytes: bytes | None, caption: str, sem: asyncio.Semaphore) -> Tuple[str, str]:
            async with sem:
                try:
                    if dry_run:
                        await asyncio.sleep(0.1)
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

                progress = len(results) / max(1, total)
                progress_bar.progress(progress)

                sent = sum(1 for _, s in results if s == "success")
                failed = sum(1 for _, s in results if s not in ("success", "dry_run"))
                dry = sum(1 for _, s in results if s == "dry_run")
                pending = total - len(results)

                elapsed = (datetime.now() - start_time).total_seconds()
                rate = len(results) / max(1, elapsed)

                status_text.text(f"Processing: {len(results):,}/{total:,}")
                sent_metric.metric("✅ Sent", f"{sent if not dry_run else dry:,}")
                failed_metric.metric("❌ Failed", f"{failed:,}")
                pending_metric.metric("⏳ Pending", f"{pending:,}")
                rate_metric.metric("⚡ Rate", f"{rate:.1f}/s")

            await asyncio.gather(*(worker(cid) for cid in chat_ids))
            return results

        # Execute
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        results = loop.run_until_complete(
            broadcast(token, chat_ids, img_bytes, caption_html, max_concurrent)
        )

        # Results
        ok = sum(1 for _, s in results if s == "success")
        dr = sum(1 for _, s in results if s == "dry_run")
        fail = len(results) - ok - dr

        st.session_state.total_sent += ok
        st.session_state.total_failed += fail

        st.markdown("---")

        if dry_run:
            st.success(f"🧪 **Dry Run Complete!** Tested {dr:,} messages")
        else:
            if fail == 0:
                st.balloons()
                st.success(f"🎉 **Perfect! Successfully sent to all {ok:,} recipients!**")
            else:
                st.warning(f"✅ Sent: {ok:,} | ❌ Failed: {fail:,}")

        # Detailed Results
        with st.expander("📋 Detailed Results"):
            results_data = {
                "Chat ID": [cid for cid, _ in results],
                "Status": ["✅" if s == "success" else "🧪" if s == "dry_run" else "❌" for _, s in results],
                "Details": [s for _, s in results]
            }
            st.dataframe(results_data, use_container_width=True)

            results_csv = "Chat ID,Status,Details\n"
            for cid, status in results:
                results_csv += f"{cid},{status.split(':')[0]},{status}\n"

            st.download_button(
                "💾 Download Results (CSV)",
                data=results_csv,
                file_name=f"broadcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

# ========== TAB 4: ANALYTICS ==========
with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Analytics Dashboard")

    if st.session_state.total_sent > 0 or st.session_state.total_failed > 0:
        # Stats Cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="stat-card-modern">
                <div class="stat-label">Total Sent</div>
                <div class="stat-number">{st.session_state.total_sent:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="stat-card-modern" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="stat-label">Total Failed</div>
                <div class="stat-number">{st.session_state.total_failed:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            success_rate = (st.session_state.total_sent / max(1, st.session_state.total_sent + st.session_state.total_failed)) * 100
            st.markdown(f"""
            <div class="stat-card-modern" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="stat-label">Success Rate</div>
                <div class="stat-number">{success_rate:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # History
        st.markdown("### 💾 Broadcast History")
        if st.session_state.chat_history:
            for i, entry in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"📅 {entry['date']} — {entry['count']:,} recipients"):
                    st.code("\n".join(entry['ids'][:10]), language="text")
                    if entry['count'] > 10:
                        st.info(f"Showing 10 of {entry['count']:,} IDs")

        # Reset
        if st.button("🔄 Reset All Statistics", type="secondary", use_container_width=True):
            st.session_state.total_sent = 0
            st.session_state.total_failed = 0
            st.session_state.chat_history = []
            st.success("✓ Statistics reset!")
            st.rerun()

    else:
        st.info("📭 No analytics data yet. Your statistics will appear after sending broadcasts.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #888;">
    <p style="font-size: 1.1rem;"><b>⚠️ Important Guidelines</b></p>
    <p>✓ Only message recipients who opted in • ✓ Respect Telegram's ToS and rate limits</p>
    <p>✓ Keep your bot token secure • ✓ Use dry run for testing</p>
    <hr style="margin: 1.5rem auto; width: 50%; opacity: 0.3;">
    <p style="font-size: 0.9rem; opacity: 0.7;">
        Made with ❤️ using Streamlit • Powered by Telegram Bot API<br>
        <span style="opacity: 0.5;">© 2024 Telegram Broadcast Pro</span>
    </p>
</div>
""", unsafe_allow_html=True)
