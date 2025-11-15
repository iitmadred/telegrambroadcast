"""
CSS styles for the Telegram Broadcast application.
"""

CUSTOM_CSS = """
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

    .error-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
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

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        margin-top: 3rem;
        border-top: 1px solid #dee2e6;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
"""


def get_header_html(title: str, subtitle: str, icon: str = "📢") -> str:
    """
    Generate header HTML.

    Args:
        title: Main title text
        subtitle: Subtitle text
        icon: Icon emoji

    Returns:
        HTML string for header
    """
    return f"""
    <div class="main-header">
        <h1>{icon} {title}</h1>
        <p>{subtitle}</p>
    </div>
    """


def get_stat_card_html(label: str, value: str, gradient: str = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)") -> str:
    """
    Generate stat card HTML.

    Args:
        label: Stat label
        value: Stat value
        gradient: CSS gradient for background

    Returns:
        HTML string for stat card
    """
    return f"""
    <div class="stat-card" style="background: {gradient};">
        <div class="stat-label">{label}</div>
        <div class="stat-number">{value}</div>
    </div>
    """


def get_footer_html() -> str:
    """
    Generate footer HTML.

    Returns:
        HTML string for footer
    """
    return """
    <div class="footer">
        <p><b>⚠️ Important Reminders</b></p>
        <p>• Only message recipients who have explicitly opted in</p>
        <p>• Respect Telegram's anti-spam rules and rate limits</p>
        <p>• Keep your bot token secure - never share it publicly</p>
        <p>• Use dry run mode to test before sending to real recipients</p>
        <hr style="margin: 1rem auto; width: 50%; opacity: 0.3;">
        <p style="font-size: 0.9rem; opacity: 0.7;">Made with ❤️ using Streamlit | © 2024</p>
    </div>
    """
