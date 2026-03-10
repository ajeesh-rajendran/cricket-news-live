import streamlit as st
import feedparser
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🏏 Cricket News Live",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Auto-refresh every 1 hour (3600 * 1000 ms) ────────────────────────────────
st_autorefresh(interval=3600 * 1000, limit=None, key="cricket_news_refresh")

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}

/* Header */
.header-container {
    background: linear-gradient(135deg, #0d9646 0%, #004d25 50%, #0a0f1a 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 200, 83, 0.15);
}
.header-container::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
    border-radius: 50%;
}
.header-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
}
.header-subtitle {
    font-size: 1rem;
    color: rgba(255,255,255,0.7);
    margin-top: 0.3rem;
    font-weight: 400;
}
.header-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.75rem;
    color: #ffffff;
    margin-top: 0.8rem;
    font-weight: 500;
}
.live-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #00E676;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

/* News Card */
.news-card {
    background: #1A1F2B;
    border-radius: 12px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.06);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: relative;
}
.news-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 200, 83, 0.3);
    box-shadow: 0 8px 24px rgba(0, 200, 83, 0.08);
}
.news-card-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: #F5F5F5;
    margin: 0 0 0.5rem 0;
    line-height: 1.4;
}
.news-card-title a {
    color: #F5F5F5;
    text-decoration: none;
}
.news-card-title a:hover {
    color: #00E676;
}
.news-card-meta {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.7rem;
    flex-wrap: wrap;
}
.meta-item {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.45);
    font-weight: 400;
}
.source-badge {
    background: rgba(0, 200, 83, 0.12);
    color: #00E676;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.news-card-summary {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.55);
    line-height: 1.6;
    margin: 0;
}
.read-more {
    display: inline-block;
    margin-top: 0.8rem;
    font-size: 0.82rem;
    color: #00C853;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}
.read-more:hover {
    color: #00E676;
}

/* Stats bar */
.stats-bar {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-chip {
    background: #1A1F2B;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 0.7rem 1.2rem;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.6);
    font-weight: 500;
}
.stat-chip strong {
    color: #00E676;
    font-weight: 700;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem 0 1rem;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.25);
}

/* Divider */
.section-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,200,83,0.2), transparent);
    margin: 0.5rem 0 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ─── RSS Feed Sources ───────────────────────────────────────────────────────────
RSS_FEEDS = {
    "ESPN Cricinfo": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "Google News - Cricket": "https://news.google.com/rss/search?q=cricket&hl=en-IN&gl=IN&ceid=IN:en",
    "ICC Cricket": "https://www.icc-cricket.com/rss/feed",
}


# ─── Fetch & Parse Feeds ────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cricket_news():
    """Fetch and merge cricket news from multiple RSS feeds."""
    articles = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:15]:  # limit per source
                # Extract published time
                published = ""
                if hasattr(entry, "published"):
                    published = entry.published
                elif hasattr(entry, "updated"):
                    published = entry.updated

                # Extract summary
                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary
                    # Strip HTML tags from summary
                    import re
                    summary = re.sub(r"<[^>]+>", "", summary).strip()
                    if len(summary) > 250:
                        summary = summary[:250] + "…"

                articles.append({
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", "#"),
                    "source": source_name,
                    "published": published,
                    "summary": summary,
                })
        except Exception:
            # Silently skip feeds that fail
            continue

    return articles


def format_time_ago(published_str):
    """Try to convert published string to a relative 'time ago' format."""
    if not published_str:
        return ""
    try:
        from email.utils import parsedate_to_datetime
        pub_dt = parsedate_to_datetime(published_str)
        now = datetime.now(timezone.utc)
        diff = now - pub_dt
        seconds = int(diff.total_seconds())
        if seconds < 0:
            return published_str
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            m = seconds // 60
            return f"{m}m ago"
        elif seconds < 86400:
            h = seconds // 3600
            return f"{h}h ago"
        else:
            d = seconds // 86400
            return f"{d}d ago"
    except Exception:
        return published_str


# ─── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <div class="header-title">🏏 Cricket News Live</div>
    <div class="header-subtitle">Latest headlines from the cricket world — updated every hour</div>
    <div class="header-badge"><span class="live-dot"></span>Auto-refreshing every 60 minutes</div>
</div>
""", unsafe_allow_html=True)


# ─── Fetch News ─────────────────────────────────────────────────────────────────
with st.spinner("🏏 Fetching the latest cricket news…"):
    articles = fetch_cricket_news()

if not articles:
    st.warning("⚠️ Could not fetch any news at the moment. Please try again later.")
    st.stop()


# ─── Stats Bar ──────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
sources_count = len(set(a["source"] for a in articles))
st.markdown(f"""
<div class="stats-bar">
    <div class="stat-chip">📰 <strong>{len(articles)}</strong> articles</div>
    <div class="stat-chip">📡 <strong>{sources_count}</strong> sources</div>
    <div class="stat-chip">🕐 Last refreshed: <strong>{now_str}</strong></div>
</div>
<hr class="section-divider">
""", unsafe_allow_html=True)


# ─── Sidebar Filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filter News")
    all_sources = sorted(set(a["source"] for a in articles))
    selected_sources = st.multiselect(
        "Sources",
        options=all_sources,
        default=all_sources,
        help="Select which news sources to display",
    )
    search_query = st.text_input(
        "🔎 Search headlines",
        placeholder="e.g. IPL, World Cup, Kohli…",
    )

# Apply filters
filtered = [
    a for a in articles
    if a["source"] in selected_sources
    and (not search_query or search_query.lower() in a["title"].lower()
         or search_query.lower() in a.get("summary", "").lower())
]


# ─── Display News Cards ─────────────────────────────────────────────────────────
if not filtered:
    st.info("No articles match your filters. Try adjusting your selection.")
else:
    for article in filtered:
        time_ago = format_time_ago(article["published"])
        time_html = f'<span class="meta-item">🕒 {time_ago}</span>' if time_ago else ""

        summary_html = ""
        if article["summary"]:
            summary_html = f'<p class="news-card-summary">{article["summary"]}</p>'

        st.markdown(f"""
        <div class="news-card">
            <div class="news-card-title">
                <a href="{article['link']}" target="_blank" rel="noopener noreferrer">{article['title']}</a>
            </div>
            <div class="news-card-meta">
                <span class="source-badge">{article['source']}</span>
                {time_html}
            </div>
            {summary_html}
            <a class="read-more" href="{article['link']}" target="_blank" rel="noopener noreferrer">Read full article →</a>
        </div>
        """, unsafe_allow_html=True)


# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built with ❤️ using Streamlit • News sourced via RSS feeds • Auto-refreshes every hour
</div>
""", unsafe_allow_html=True)
