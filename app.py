import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time
from datetime import datetime
from rss_feeds import RSS_FEEDS
from rss_parser import fetch_feed
from utils import generate_parody_from_news, load_ideas, save_ideas, generate_comedy_with_groq, DEFAULT_GROQ_KEY, generate_live_trends_with_groq, generate_fallback_live_trends, load_problem_solving, save_problem_solving, generate_new_problem_with_groq

# 1. Page Configuration & Theme Initialization
st.set_page_config(
    page_title="NewArticleAgent | Curated Intel Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>


/* Hide Default Streamlit Menu, Deploy Button, & Footer for clean look */

.stAppDeployButton {visibility: hidden; display: none !important;}
footer {visibility: hidden;}

/* Adjust margins/padding of main layout */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1300px;
}

/* Custom Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

/* Custom Container Cards (Glassmorphism) */
div[data-testid="stVerticalBlockBorderbox"] {
    background: rgba(21, 31, 50, 0.45) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 18px !important;
    padding: 22px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}

div[data-testid="stVerticalBlockBorderbox"]:hover {
    transform: translateY(-4px) !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
    box-shadow: 0 12px 30px rgba(99, 102, 241, 0.15) !important;
    background: rgba(21, 31, 50, 0.65) !important;
}

/* Metric Cards Customization */
div[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #818CF8 0%, #A78BFA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

div[data-testid="stMetricLabel"] {
    font-weight: 600 !important;
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.75rem !important;
}

/* Custom Buttons (Standard & Link) */
.stButton>button, .stLinkButton>a {
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    background: rgba(255, 255, 255, 0.03) !important;
    color: #f8fafc !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 8px 16px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-align: center;
    text-decoration: none;
    display: inline-flex;
    justify-content: center;
    align-items: center;
}

.stButton>button:hover, .stLinkButton>a:hover {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    border-color: #6366F1 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35) !important;
    transform: scale(1.02) !important;
}

/* Tabs Styling Override */
button[data-baseweb="tab"] {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #64748B !important;
    border-bottom: 2px solid transparent !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #f8fafc !important;
    border-bottom: 2px solid #6366F1 !important;
}

/* Search bar & inputs override */
div[data-testid="stTextInput"] input {
    background: #0f172a !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
    padding: 12px 16px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0b0f19;
}
::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 6px;
}
::-webkit-scrollbar-thumb:hover {
    background: #334155;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Persistent Bookmarks System
BOOKMARKS_FILE = "bookmarks.json"

def load_bookmarks():
    if "bookmarks" not in st.session_state:
        if os.path.exists(BOOKMARKS_FILE):
            try:
                with open(BOOKMARKS_FILE, "r") as f:
                    st.session_state.bookmarks = json.load(f)
            except Exception:
                st.session_state.bookmarks = {}
        else:
            st.session_state.bookmarks = {}

def save_bookmarks():
    try:
        with open(BOOKMARKS_FILE, "w") as f:
            json.dump(st.session_state.bookmarks, f, indent=4)
    except Exception as e:
        st.sidebar.error(f"Error saving bookmarks: {e}")

load_bookmarks()

# 4. Cached RSS Feed Data Fetching
@st.cache_data(ttl=600)
def fetch_all_category_feeds(category):
    feeds = RSS_FEEDS[category]
    articles = []
    diagnostics = {}
    
    for source, url in feeds.items():
        start_time = time.time()
        try:
            feed_articles = fetch_feed(source, url)
            articles.extend(feed_articles)
            elapsed = time.time() - start_time
            diagnostics[source] = {
                "status": "✅ Active",
                "count": len(feed_articles),
                "speed": f"{elapsed:.2f}s",
                "url": url
            }
        except Exception as e:
            diagnostics[source] = {
                "status": f"❌ Error: {str(e)}",
                "count": 0,
                "speed": "0.00s",
                "url": url
            }
    return articles, diagnostics

# 5. Helper function for source tag colors
def get_source_color(source):
    colors = {
        "TechCrunch": "#00F5D4",      # Neon Teal
        "The Verge": "#FF007F",       # Hot Pink
        "Ars Technica": "#FF6B6B",    # Light Coral
        "Wired": "#E0E0E0",           # Pure Gray
        "MIT Tech Review": "#FF5A5F", # Soft Red
        "VentureBeat": "#FFB800",     # Neon Amber
        "GitHub Blog": "#8B5CF6",     # Soft Purple
        "Python": "#38BDF8",          # Sky Blue
        "AWS": "#F59E0B",             # AWS Orange
        "Azure": "#2563EB",           # Windows Blue
        "The Hacker News": "#EF4444", # Cyber Red
        "Krebs": "#F43F5E",           # Rose
        "The Hindu Tech": "#0D9488",  # Teal
        "Indian Express Tech": "#3B82F6", # Bright Blue
        "BBC Tech": "#DC2626",        # Crimson
        "Reuters Tech": "#64748B",    # Muted Slate
        "The Onion": "#10B981",       # Emerald Green
        "Programmer Humor": "#EC4899",# Hot Pink
        "Y Combinator Jobs": "#F97316" # Orange
    }
    return colors.get(source, "#6366F1") # Default Indigo

# 6. Sidebar Dashboard Panel
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 1.5rem;'>
        <h2 style='color: #f8fafc; font-weight: 800; font-size: 1.5rem; margin-bottom: 0.2rem;'>NewArticleAgent</h2>
        <p style='color: #64748B; font-size: 0.8rem; letter-spacing: 0.05em; text-transform: uppercase;'>Curated News Feed</p>
    </div>
    """,
    unsafe_allow_html=True
)

category = st.sidebar.selectbox(
    "📂 Feed Category",
    list(RSS_FEEDS.keys())
)

# Fetch current category's articles and status
articles, diagnostics = fetch_all_category_feeds(category)

# Parse to dataframe and deduplicate
if articles:
    df_raw = pd.DataFrame(articles)
    df_all = df_raw.drop_duplicates(subset=["link"])
else:
    df_all = pd.DataFrame(columns=["source", "title", "link", "summary", "clean_summary", "image", "published", "timestamp", "time_ago", "read_time", "author"])

# Sidebar Source Selection
available_sources = list(RSS_FEEDS[category].keys())
st.sidebar.markdown("<br><b style='color:#f8fafc;'>📡 Filter Sources</b>", unsafe_allow_html=True)
all_sources_selected = st.sidebar.checkbox("Toggle All Sources", value=True)

selected_sources = []
for src in available_sources:
    default_val = True if all_sources_selected else False
    if st.sidebar.checkbox(src, value=default_val):
        selected_sources.append(src)

# Force-sync button in sidebar
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔄 Sync Feeds Now", width="stretch"):
    st.cache_data.clear()
    st.toast("Connecting to RSS servers & re-syncing...", icon="🔄")
    time.sleep(0.5)
    st.rerun()

st.sidebar.markdown(
    f"""
    <div style='margin-top: 3rem; padding: 12px; border-radius: 10px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); text-align: center;'>
        <span style='color: #64748B; font-size: 0.75rem;'>Sync Cache Status:</span><br>
        <span style='color: #10B981; font-size: 0.8rem; font-weight:600;'>🟢 Fully Cached</span>
    </div>
    """,
    unsafe_allow_html=True
)

# 7. Main Dashboard Content Area
# Top Hero Branding Section
st.markdown(
    """
    <div style='background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.05) 100%); padding: 30px; border-radius: 20px; border: 1px solid rgba(99, 102, 241, 0.15); margin-bottom: 2rem; text-align: center;'>
        <h1 style='background: linear-gradient(135deg, #818CF8 0%, #C084FC 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.8rem; margin: 0;'>NewArticleAgent</h1>
        <p style='color: #94A3B8; font-size: 1.1rem; margin-top: 5px; margin-bottom: 0;'>Your Production-Grade intelligence Hub & Reader</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Active tab definition
tab_live, tab_parody, tab_problems, tab_saved, tab_analytics, tab_diag = st.tabs([
    "📰 Live Intel Feed",
    "🎙️ Creator & Parody Studio",
    "🧩 Problem Solving",
    "⭐ Saved Bookmarks",
    "📊 Platform Analytics",
    "⚙️ Feed Health System"
])

# 8. LIVE INTEL FEED TAB
with tab_live:
    # Quick Summary Statistics bar
    total_found = len(df_all)
    active_selected_df = df_all[df_all["source"].isin(selected_sources)] if not df_all.empty else df_all
    
    # Filter search
    search_col1, search_col2, search_col3 = st.columns([3, 1, 1])
    with search_col1:
        search = st.text_input(
            "🔍 Search live feed...",
            placeholder="AI, startups, cloud, specific keywords..."
        )
    with search_col2:
        sort_by = st.selectbox("Sort By", ["Newest First", "Oldest First", "Alphabetical"])
    with search_col3:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: right; color:#94A3B8; font-weight: 600; font-size: 0.9rem; padding-top: 5px;'>Showing {len(active_selected_df)} of {total_found} articles</div>", unsafe_allow_html=True)

    # Apply search filter
    df_filtered = active_selected_df.copy()
    if search and not df_filtered.empty:
        df_filtered = df_filtered[
            df_filtered["title"].str.contains(search, case=False, na=False) |
            df_filtered["clean_summary"].str.contains(search, case=False, na=False)
        ]

    # Apply Sorting
    if not df_filtered.empty:
        if sort_by == "Newest First":
            df_filtered = df_filtered.sort_values(by="timestamp", ascending=False)
        elif "Oldest First" in sort_by:
            df_filtered = df_filtered.sort_values(by="timestamp", ascending=True)
        elif sort_by == "Alphabetical":
            df_filtered = df_filtered.sort_values(by="title", ascending=True)

    # Display Article Grid
    if df_filtered.empty:
        st.markdown(
            """
            <div style='padding: 50px; text-align: center; border: 1px dashed rgba(255,255,255,0.08); border-radius: 18px; background: rgba(255,255,255,0.01);'>
                <h3 style='color: #64748B;'>No articles found matching filters</h3>
                <p style='color: #475569;'>Try altering your search or selecting different feeds from the sidebar.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # 2-column grid layout
        grid_cols = st.columns(2)
        for idx, (_, row) in enumerate(df_filtered.iterrows()):
            col_target = grid_cols[idx % 2]
            with col_target:
                with st.container(border=True):
                    # 1. Custom Image Header (Dynamic Image Overlay & Fallback)
                    img_src = row.get("image")
                    img_html = f'<img src="{img_src}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 2;" onerror="this.style.display=\'none\';">' if img_src else ''
                    st.markdown(
                        f"""
                        <div style="position: relative; border-radius: 12px; overflow: hidden; margin-bottom: 12px; height: 160px; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(255, 255, 255, 0.05); background: linear-gradient(135deg, #151f32 0%, #0b0f19 100%);">
                            <span style="position: absolute; font-weight:700; color:{get_source_color(row['source'])}; font-size:1.2rem; letter-spacing:0.04em; text-transform:uppercase; z-index: 1;">{row['source']}</span>
                            {img_html}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # 2. Source Badge & Read Time
                    source_col = get_source_color(row['source'])
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="background-color: {source_col}18; color: {source_col}; border: 1px solid {source_col}33; padding: 3px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">
                                {row['source']}
                            </span>
                            <span style="color: #64748B; font-size: 0.72rem; font-weight: 600;">
                                ⏱️ {row['read_time']}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # 3. Title
                    st.markdown(
                        f"""
                        <h3 style="color: #f8fafc; font-size: 1.15rem; font-weight: 700; margin: 4px 0 10px 0; line-height: 1.45; min-height: 52px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            {row['title']}
                        </h3>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # 4. Meta Row
                    author_txt = f" • By {row['author']}" if row['author'] else ""
                    st.markdown(
                        f"""
                        <div style="color: #475569; font-size: 0.72rem; font-weight: 600; margin-bottom: 12px;">
                            📅 {row['time_ago']}{author_txt}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # 5. Cleaned Description
                    st.markdown(
                        f"""
                        <p style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5; margin-bottom: 16px; min-height: 55px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                            {row['clean_summary']}
                        </p>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # 6. Action buttons
                    act1, act2 = st.columns([3, 1])
                    with act1:
                        st.link_button("Read Original Article ↗", row["link"], width="stretch")
                    with act2:
                        is_saved = row["link"] in st.session_state.bookmarks
                        btn_label = "★" if is_saved else "☆"
                        help_text = "Remove bookmark" if is_saved else "Save for later"
                        
                        if st.button(btn_label, key=f"feed_bookmark_{row['link']}", width="stretch", help=help_text):
                            if is_saved:
                                del st.session_state.bookmarks[row["link"]]
                                st.toast("Removed from bookmarks!", icon="🗑️")
                            else:
                                st.session_state.bookmarks[row["link"]] = {
                                    "title": row["title"],
                                    "link": row["link"],
                                    "source": row["source"],
                                    "clean_summary": row["clean_summary"],
                                    "image": row["image"],
                                    "time_ago": row["time_ago"],
                                    "read_time": row["read_time"],
                                    "author": row["author"],
                                    "summary": row["summary"]
                                }
                                st.toast("Saved to bookmarks!", icon="⭐")
                            save_bookmarks()
                            st.rerun()
                    
                    # 7. Embed full content preview in expander
                    if row["summary"] and len(row["summary"]) > len(row["clean_summary"]):
                        with st.expander("🔍 Interactive Preview"):
                            st.markdown(
                                f"""
                                <div style="background-color: #080d16; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); max-height: 220px; overflow-y: auto; color: #cbd5e1; font-size: 0.85rem; line-height: 1.5;">
                                    {row['summary']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

# 9. CREATOR & PARODY STUDIO TAB
with tab_parody:
    st.markdown(
        """
        <div style='background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%); padding: 25px; border-radius: 18px; border: 1px solid rgba(168, 85, 247, 0.2); margin-bottom: 2rem;'>
            <h2 style='color: #f8fafc; font-weight: 800; font-size: 1.8rem; margin: 0;'>🎙️ Corporate Creator & Parody Studio</h2>
            <p style='color: #cbd5e1; font-size: 1rem; margin-top: 5px; margin-bottom: 0;'>
                Turn dry corporate tech news into viral comedies, reels/shorts scripts, and parody songs. Target the tech-office crowd (devs, PMs, remote workers, IT managers) who love to laugh at their own pain.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    studio_tab_vault, studio_tab_generator, studio_tab_ideas = st.tabs([
        "🔥 Live Meme & Reels Formats",
        "🤖 AI React & Script Generator",
        "💡 Creator Ideas Board"
    ])
    
    # --- SUB-TAB 1: LIVE MEME & REELS FORMATS ---
    with studio_tab_vault:
        st.markdown(
            """
            <div style='margin-bottom: 1.5rem;'>
                <h3 style='color: #f8fafc; font-size: 1.3rem; font-weight:700;'>🔥 Live Meme & Reels Formats</h3>
                <p style='color: #94A3B8; font-size:0.9rem;'>Dynamically analyze the latest tech news stories and generate viral Reels/TikTok B-roll concepts, hooks, and overlay captions.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Audience toggle inside trends tab
        trend_col1, trend_col2 = st.columns([2, 1])
        with trend_col1:
            trend_audience = st.radio(
                "🌏 Region Focus",
                ["🌐 Global Tech Bro", "🇮🇳 Indian Corporate"],
                index=0,
                horizontal=True,
                key="trend_audience_selection",
                help="Tailors the trending jokes and reference points to the selected region."
            )
        with trend_col2:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            refresh_trends = st.button("🔄 Generate Live Trends", key="refresh_trends_btn", use_container_width=True)
            
        trend_audience_val = "Indian" if "Indian" in trend_audience else "Global"
        
        # Check if trends are cached in session state or need generation
        if "live_trends" not in st.session_state:
            st.session_state.live_trends = None
            st.session_state.cached_audience = None
            
        # Trigger generation if clicked or if empty or if audience focus changed
        if refresh_trends or st.session_state.live_trends is None or st.session_state.cached_audience != trend_audience_val:
            with st.spinner("Analyzing active feeds and drafting memes via Groq LLM..."):
                st.session_state.cached_audience = trend_audience_val
                
                # Retrieve active news items
                news_list = []
                if not df_all.empty:
                    news_list = df_all.to_dict('records')
                
                try:
                    if len(news_list) > 0:
                        # Call Groq LLM with latest articles
                        res = generate_live_trends_with_groq(DEFAULT_GROQ_KEY, news_list, trend_audience_val)
                        st.session_state.live_trends = res.get("trends", [])
                    else:
                        # No news loaded, use fallback
                        res = generate_fallback_live_trends(trend_audience_val)
                        st.session_state.live_trends = res.get("trends", [])
                except Exception as e:
                    st.warning(f"Groq API call failed. Using local template trends fallback. Error: {e}")
                    res = generate_fallback_live_trends(trend_audience_val)
                    st.session_state.live_trends = res.get("trends", [])
                    
        # Render the trending memes in cards
        if st.session_state.live_trends:
            # 2-column grid layout
            trend_grid = st.columns(2)
            for idx, trend in enumerate(st.session_state.live_trends):
                target_col = trend_grid[idx % 2]
                with target_col:
                    with st.container(border=True):
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="background-color: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.3); padding: 3px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">
                                    📹 {trend.get('video_type', 'Reels Format')}
                                </span>
                                <span style="color: #34D399; font-size: 0.75rem; font-weight: 700;">
                                    🔥 Relatable
                                </span>
                            </div>
                            <h3 style="color: #f8fafc; font-size: 1.25rem; font-weight: 800; margin: 4px 0 6px 0;">{trend.get('title', 'Untitled Trend')}</h3>
                            <p style="color: #64748B; font-size: 0.75rem; margin-bottom: 12px;"><b>Inspired by:</b> {trend.get('news_inspiration', 'Latest News')}</p>
                            
                            <div style="background-color: rgba(99, 102, 241, 0.08); border-left: 4px solid #6366F1; padding: 10px; border-radius: 4px; margin-bottom: 12px;">
                                <span style="color:#818CF8; font-size:0.7rem; font-weight:700; text-transform:uppercase;">🪝 Video Hook (Text Overlay)</span>
                                <div style="margin:2px 0 0 0; color:#f8fafc; font-size:0.9rem; font-weight:700;">"{trend.get('video_hook', '')}"</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Expanders for recording details
                        with st.expander("📷 B-Roll Recording Guide"):
                            b_roll_clean = trend.get('visual_b_roll', '').replace('->', ' ➡️ ')
                            st.markdown(f"<div style='color:#cbd5e1; font-size:0.85rem; line-height:1.45;'>{b_roll_clean}</div>", unsafe_allow_html=True)
                            
                        with st.expander("💬 Text Overlay Schedule"):
                            overlay_html = ""
                            for s_idx, slide in enumerate(trend.get('text_overlays', [])):
                                overlay_html += f"<div style='margin-bottom:6px; font-size:0.82rem; color:#f8fafc;'><b>Slide {s_idx+1}:</b> {slide}</div>"
                            st.markdown(overlay_html, unsafe_allow_html=True)
                            
                        with st.expander("🔊 Background Music Style"):
                            st.markdown(f"<div style='color:#94a3b8; font-size:0.82rem;'>🎵 <i>{trend.get('bg_music', 'Sarcastic office beat')}</i></div>", unsafe_allow_html=True)
                            
                        with st.expander("💡 Relatability / Sharing Hook"):
                            st.markdown(f"<div style='color:#a78bfa; font-size:0.82rem; font-style:italic;'>{trend.get('relatability_reason', '')}</div>", unsafe_allow_html=True)
                            
                        # Save action
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                        if st.button(f"💾 Save Trend Concept: {trend.get('title')}", key=f"save_trend_card_{idx}", use_container_width=True):
                            ideas = load_ideas()
                            
                            blueprint_md = f"""### 🪝 Hook (Text on Screen)
"{trend.get('video_hook', '')}"

### 🔊 BG Music Recommendation
{trend.get('bg_music', '')}

### 🎥 Visual B-Roll Guide
{trend.get('visual_b_roll', '')}

### 💬 Text Overlays
""" + "\n".join([f"- {txt}" for txt in trend.get('text_overlays', [])])

                            new_idea = {
                                "title": trend.get('title', 'Trending Meme'),
                                "original_song": f"Background Audio ({trend.get('bg_music', '')})",
                                "target_audience": f"Trending ({trend_audience_val} Focus)",
                                "lyrics": f"Relatability Reason: {trend.get('relatability_reason', '')}",
                                "creator_blueprint": blueprint_md,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            ideas.append(new_idea)
                            save_ideas(ideas)
                            st.toast("Saved trend concept to Ideas Board!", icon="💾")
                            time.sleep(0.3)
                            st.rerun()

    # --- SUB-TAB 2: CORPORATE-TO-MEME GENERATOR ---
    with studio_tab_generator:
        st.markdown(
            """
            <div style='margin-bottom: 1.5rem;'>
                <h3 style='color: #f8fafc; font-size: 1.3rem; font-weight:700;'>🤖 AI React & Script Generator (Groq-Powered)</h3>
                <p style='color: #94A3B8; font-size:0.9rem;'>Select a trending news article from your feed, choose your comedic persona, and let Groq generate scripts, parodies, and reaction hooks on the right.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # We use a 2-column layout. Left: Inputs & Choose News. Right: Generated Script & Assets.
        gen_col_left, gen_col_right = st.columns([2, 3])
        
        with gen_col_left:
            # 1. Groq Settings Container
            with st.container(border=True):
                st.markdown("<b style='color:#f8fafc;'>⚙️ Groq LLM Configuration</b>", unsafe_allow_html=True)
                groq_key = st.text_input(
                    "🔑 Groq API Key", 
                    value=DEFAULT_GROQ_KEY, 
                    type="password",
                    help="Free API Key is pre-loaded. You can replace it with your own key if needed.",
                    key="groq_api_key"
                )
                comedy_tone = st.selectbox(
                    "🎭 Comedy Tone / Persona",
                    [
                        "Sarcastic & Relatable Dev", 
                        "Existential Dev Dread (Overworked Coder)", 
                        "Toxic Positivity PM (Story Points & Agile)", 
                        "Boomer Manager (In-Person Synergy)", 
                        "Hyper-Active TikTok Creator"
                    ],
                    index=0
                )
                audience_focus = st.radio(
                    "🌏 Target Audience Region",
                    ["🌐 Global Tech Bro", "🇮🇳 Indian Corporate"],
                    index=0,
                    horizontal=True,
                    help="Tailors the generated jokes, B-roll cues, and local references to your selected region."
                )
                
            # 2. Trending News Selector Container
            with st.container(border=True):
                st.markdown("<b style='color:#f8fafc;'>📻 Select Latest Trending News</b>", unsafe_allow_html=True)
                
                source_opt = ["Enter Manually"]
                article_map = {}
                
                # Add bookmarks if any
                if st.session_state.bookmarks:
                    for link, b in st.session_state.bookmarks.items():
                        title_short = b['title'][:55] + "..." if len(b['title']) > 55 else b['title']
                        label = f"⭐ Saved: {title_short}"
                        source_opt.append(label)
                        article_map[label] = {
                            "title": b['title'],
                            "clean_summary": b['clean_summary'],
                            "source": b['source']
                        }
                
                # Add latest feed items
                if not df_all.empty:
                    latest_articles = df_all.sort_values(by="timestamp", ascending=False).head(15)
                    for idx, r in latest_articles.iterrows():
                        title_short = r['title'][:55] + "..." if len(r['title']) > 55 else r['title']
                        label = f"🔥 {r['source']}: {title_short}"
                        if label not in source_opt:
                            source_opt.append(label)
                            article_map[label] = {
                                "title": r['title'],
                                "clean_summary": r['clean_summary'],
                                "source": r['source']
                            }
                
                selected_article_label = st.selectbox(
                    "📄 Choose Article",
                    source_opt,
                    key="parody_source_article_v2",
                    help="Select a trending news article from the active feed to react to and generate content."
                )
                
                if selected_article_label == "Enter Manually":
                    inp_title = st.text_input("Headline / Topic", key="parody_manual_title_v2", placeholder="e.g. ChatGPT replaces senior developers")
                    inp_summary = st.text_area("Article Summary / Details", key="parody_manual_summary_v2", placeholder="e.g. A company announced that they are replacing coders...")
                else:
                    article_data = article_map[selected_article_label]
                    inp_title = st.text_input("Headline / Topic", key="parody_mapped_title_v2", value=article_data['title'])
                    inp_summary = st.text_area("Article Summary / Details", key="parody_mapped_summary_v2", value=article_data['clean_summary'])
            
            run_gen = st.button("🚀 Generate Comedy Package", key="parody_run_button_v2", use_container_width=True)
            
            if run_gen:
                if not inp_title:
                    st.error("Please enter a news headline or topic.")
                elif not groq_key:
                    st.error("Please provide a valid Groq API key.")
                else:
                    audience_val = "Indian" if "Indian" in audience_focus else "Global"
                    with st.spinner("Writing B-roll comedy script via Groq LLM..."):
                        try:
                            res = generate_comedy_with_groq(groq_key, inp_title, inp_summary, comedy_tone, audience_val)
                            st.session_state.current_comedy = res
                            st.toast("Comedy script generated successfully!", icon="🔥")
                        except Exception as e:
                            st.warning(f"Groq API call failed. Using local template engine fallback. Error: {e}")
                            res = generate_parody_from_news(inp_title, inp_summary, audience_val)
                            st.session_state.current_comedy = res
                            
        with gen_col_right:
            if "current_comedy" not in st.session_state:
                st.session_state.current_comedy = None
                
            if st.session_state.current_comedy is None:
                st.markdown(
                    """
                    <div style='padding: 80px 20px; text-align: center; border: 1px dashed rgba(255,255,255,0.08); border-radius: 18px; background: rgba(255,255,255,0.01); height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;'>
                        <h4 style='color: #64748B; margin-top:0;'>🎬 Content Script Panel (Right Side)</h4>
                        <p style='color: #475569; font-size: 0.85rem; max-width: 320px;'>
                            Choose a trending news item on the left, select your persona tone, and click <b>Generate Comedy Package</b> to generate content scripts in real-time.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                comedy_output = st.session_state.current_comedy
                video_blueprint = comedy_output.get('video_blueprint', {})
                audience_val = "Indian" if "Indian" in audience_focus else "Global"
                
                st.markdown(
                    f"""
                    <div style='background-color: rgba(168, 85, 247, 0.05); padding: 12px; border-radius: 10px; border: 1px solid rgba(168, 85, 247, 0.2); margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='color: #A78BFA; font-size: 0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;'>Category:</span>
                            <span style='color: #f8fafc; font-weight:600; font-size: 0.85rem;'> {comedy_output.get('detected_category', 'Tech Satire')}</span>
                        </div>
                        <span style='background-color: rgba(34, 197, 94, 0.15); color: #4ADE80; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 8px;'>⚡ Groq Powered</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f"""
                    <div style="background-color: rgba(255, 255, 255, 0.02); padding: 15px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 1rem;">
                        <span style='color: #38BDF8; font-size: 0.7rem; font-weight:700; text-transform:uppercase;'>📰 Satirical Hook / Onion Headline</span>
                        <h3 style='color: #f8fafc; font-size: 1.25rem; font-weight:800; line-height: 1.4; margin: 4px 0 0 0;'>"{comedy_output['custom_satirical_headline']}"</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                r_tab_script, r_tab_song, r_tab_reacts, r_tab_lingo = st.tabs([
                    "🎬 Silent B-Roll Blueprint",
                    "🎵 Parody Song",
                    "🚨 Reaction Hooks",
                    "💼 Lingo Translation"
                ])
                
                with r_tab_script:
                    st.markdown(
                        f"""
                        <div style="background-color: rgba(99, 102, 241, 0.08); border-left: 5px solid #6366F1; padding: 15px; border-radius: 8px; margin-bottom: 1.5rem;">
                            <span style="color:#818CF8; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">🪝 Scroll-Stopping Hook (Text on Screen)</span>
                            <h4 style="margin:5px 0 0 0; color:#f8fafc; font-size:1.15rem; font-weight:800;">"{video_blueprint.get('video_hook', 'Day 1 of pretending to...')}"</h4>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("<b style='color:#f8fafc; font-size:0.95rem;'>📷 Video Recording Guide (Faceless B-Roll)</b>", unsafe_allow_html=True)
                    b_roll_clean_v2 = video_blueprint.get('visual_b_roll', '').replace('->', ' ➡️ ')
                    st.markdown(f"<div style='background-color:#080d16; padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.03); color:#cbd5e1; font-size:0.85rem; margin-bottom:1.5rem;'>{b_roll_clean_v2}</div>", unsafe_allow_html=True)
                    
                    st.markdown("<b style='color:#f8fafc; font-size:0.95rem;'>💬 Text Overlays to Place on the Video</b>", unsafe_allow_html=True)
                    overlay_html = ""
                    for idx, slide in enumerate(video_blueprint.get('text_overlays', [])):
                        overlay_html += f"""
                        <div style='background-color:rgba(255,255,255,0.02); padding:10px; border-radius:6px; border:1px solid rgba(255,255,255,0.05); margin-bottom:8px; font-size:0.85rem; color:#f8fafc;'>
                            <b>Segment {idx+1}:</b> {slide}
                        </div>
                        """
                    st.markdown(overlay_html, unsafe_allow_html=True)
                    
                    st.markdown("<b style='color:#f8fafc; font-size:0.95rem;'>🔊 Audio Recommendation (Background Music)</b>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color:#94a3b8; font-size:0.85rem; margin-top:2px;'>🎵 <i>{video_blueprint.get('bg_music', 'Sarcastic office beats')}</i> (No talking/voiceover needed)</div>", unsafe_allow_html=True)
                    
                with r_tab_song:
                    song_parody = comedy_output['parody_song']
                    st.markdown(
                        f"""
                        <div style="background-color: rgba(236, 72, 153, 0.02); padding: 18px; border-radius: 12px; border: 1px solid rgba(236, 72, 153, 0.1);">
                            <span style='color: #EC4899; font-size: 0.72rem; font-weight:700; text-transform:uppercase;'>Parody Title:</span>
                            <h4 style='color: #f8fafc; font-size: 1.15rem; margin: 2px 0 0 0;'>{song_parody.get('title', 'Untitled Parody')}</h4>
                            <p style='color: #94A3B8; font-size: 0.78rem; margin-top: 2px; margin-bottom: 12px;'>Inspiration: <i>{song_parody.get('original_song', "God's Plan - Drake")}</i></p>
                            <pre style="background-color: #080d16; padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); font-family: 'Courier New', monospace; font-size: 0.85rem; color: #F472B6; line-height: 1.5; white-space: pre-wrap; max-height: 250px; overflow-y: auto;">{song_parody.get('lyrics', '')}</pre>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                with r_tab_reacts:
                    st.markdown("<b style='color:#f8fafc; font-size:0.9rem;'>🔥 3 Viral Hooks to React & Get Views:</b>", unsafe_allow_html=True)
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    
                    react_html = ""
                    for hook in comedy_output.get('reaction_hooks', []):
                        react_html += f"""
                        <div style="background-color: rgba(56, 189, 248, 0.05); border-left: 4px solid #38BDF8; padding: 12px; border-radius: 0 8px 8px 0; margin-bottom: 10px; color:#cbd5e1; font-size:0.85rem; line-height:1.4;">
                            {hook}
                        </div>
                        """
                    st.markdown(react_html, unsafe_allow_html=True)
                    
                with r_tab_lingo:
                    st.markdown("<span style='color: #34D399; font-size: 0.72rem; font-weight:700; text-transform:uppercase;'>💼 Corporate Translation Glossary</span>", unsafe_allow_html=True)
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    
                    trans_html = ""
                    for corp_speak, real_meaning in comedy_output['corporate_lingo']:
                        trans_html += f"""
                        <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                            <div style="width: 35%; color: #34D399; font-weight:600; font-size:0.85rem;">"{corp_speak}"</div>
                            <div style="width: 5%; color: #64748B; text-align:center;">➡️</div>
                            <div style="width: 60%; color: #CBD5E1; font-size:0.85rem;"><i>{real_meaning}</i></div>
                        </div>
                        """
                    st.markdown(trans_html, unsafe_allow_html=True)
                    
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Save Generated Parody Concept to Ideas Board", key="save_gen_parody_btn_v2", use_container_width=True):
                    ideas = load_ideas()
                    
                    b_roll_clean_v3 = video_blueprint.get('visual_b_roll', '').replace('->', ' ➡️ ')
                    blueprint_md = f"""### 🪝 Hook (Text on Screen)
"{video_blueprint.get('video_hook', '')}"

### 🔊 BG Music Recommendation
{video_blueprint.get('bg_music', '')}

### 🎥 Visual B-Roll Guide
{b_roll_clean_v3}

### 💬 Text Overlays
""" + "\n".join([f"- {txt}" for txt in video_blueprint.get('text_overlays', [])])

                    new_idea = {
                        "title": comedy_output['custom_satirical_headline'],
                        "original_song": comedy_output['parody_song']['original_song'] + " (Parody: " + comedy_output['parody_song']['title'] + ")",
                        "target_audience": comedy_output.get('detected_category', 'Tech Satire') + f" ({audience_val} Focus)",
                        "lyrics": comedy_output['parody_song']['lyrics'],
                        "creator_blueprint": blueprint_md,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    ideas.append(new_idea)
                    save_ideas(ideas)
                    st.toast("Concept saved to Ideas Board!", icon="💾")
                    time.sleep(0.3)
                    st.rerun()

    # --- SUB-TAB 3: CREATOR IDEAS BOARD ---
    with studio_tab_ideas:
        st.markdown(
            """
            <div style='margin-bottom: 1.5rem;'>
                <h3 style='color: #f8fafc; font-size: 1.3rem; font-weight:700;'>💡 My Content Ideas Board</h3>
                <p style='color: #94A3B8; font-size:0.9rem;'>Store your drafts, hooks, parody ideas, and upcoming videos here. Persists locally on disk.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        idea_col1, idea_col2 = st.columns([3, 2])
        
        with idea_col2:
            with st.container(border=True):
                st.markdown("<h4 style='color:#f8fafc; margin-top:0;'>💡 Jot down a New Idea</h4>", unsafe_allow_html=True)
                
                f_title = st.text_input("Content Title / Working Name", key="f_title_val", placeholder="e.g. Git Commit and Cry V2")
                f_audio = st.text_input("Audio / Song Inspiration", key="f_audio_val", placeholder="e.g. God's Plan - Drake")
                f_audience = st.text_input("Target Audience", key="f_audience_val", placeholder="e.g. Junior Developers, Remote PMs")
                f_lyrics = st.text_area("Lyrics / Video Script Draft", key="f_lyrics_val", placeholder="Describe scenes, dialogues, or sing-along lyrics...")
                f_blueprint = st.text_area("Creator Blueprint / Notes", key="f_blueprint_val", placeholder="Visual notes, angles, captions, hashtags...")
                
                if st.button("➕ Save to Board", key="save_manual_idea_btn", use_container_width=True):
                    if not f_title:
                        st.error("Please enter a title for your idea.")
                    else:
                        ideas = load_ideas()
                        ideas.append({
                            "title": f_title,
                            "original_song": f_audio,
                            "target_audience": f_audience,
                            "lyrics": f_lyrics,
                            "creator_blueprint": f_blueprint,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        save_ideas(ideas)
                        st.toast("New idea saved!", icon="💡")
                        time.sleep(0.3)
                        st.rerun()
                        
        with idea_col1:
            ideas = load_ideas()
            if not ideas:
                st.markdown(
                    """
                    <div style='padding: 50px; text-align: center; border: 1px dashed rgba(255,255,255,0.08); border-radius: 12px; background: rgba(255,255,255,0.01);'>
                        <h4 style='color: #64748B;'>No ideas saved yet</h4>
                        <p style='color: #475569;'>Use the form on the right to add your own concept, or bookmark presets and generated parodies from the other sub-tabs.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                for idx, idea in enumerate(reversed(ideas)):
                    actual_idx = len(ideas) - 1 - idx
                    with st.container(border=True):
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="background-color: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 8px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">
                                    🎵 {idea.get('original_song', 'Custom Audio')}
                                </span>
                                <span style="color: #64748B; font-size: 0.7rem;">
                                    🕒 {idea.get('timestamp', 'Recent')}
                                </span>
                            </div>
                            <h3 style="color: #f8fafc; font-size: 1.15rem; font-weight: 700; margin: 4px 0 6px 0;">{idea['title']}</h3>
                            <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 12px;"><b>Audience:</b> {idea.get('target_audience', 'Developers')}</p>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        if idea.get('lyrics'):
                            with st.expander("📝 View Script / Lyrics"):
                                st.markdown(f"<pre style='background:#080d16; padding:12px; border-radius:6px; font-family:monospace; font-size:0.8rem; color:#f8fafc; white-space:pre-wrap;'>{idea['lyrics']}</pre>", unsafe_allow_html=True)
                                
                        if idea.get('creator_blueprint'):
                            with st.expander("🎬 View Blueprint / Notes"):
                                st.markdown(f"<div style='background:rgba(255,255,255,0.02); padding:10px; border-radius:6px; font-size:0.82rem; color:#cbd5e1; border:1px solid rgba(255,255,255,0.05);'>{idea['creator_blueprint']}</div>", unsafe_allow_html=True)
                        
                        del_col, _ = st.columns([1, 3])
                        with del_col:
                            if st.button("🗑️ Delete", key=f"del_idea_{actual_idx}", use_container_width=True):
                                ideas.pop(actual_idx)
                                save_ideas(ideas)
                                st.toast("Deleted idea!", icon="🗑️")
                                time.sleep(0.3)
                                st.rerun()

# 10. PROBLEM SOLVING TAB
with tab_problems:
    st.markdown(
        """
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: #f8fafc; font-size: 1.3rem; font-weight:700;'>🧩 Daily Engineering Problem Solving Vault</h3>
            <p style='color: #94A3B8; font-size:0.9rem;'>Explore curated programming questions (LeetCode in Python) and production bug studies (scaling, concurrency, systems, GenAI) with full source code and root cause analysis.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 1. Load data
    prob_data = load_problem_solving()
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Auto-refresh if the date changes
    if prob_data.get("last_refreshed") != current_date_str:
        import random
        prob_data["last_refreshed"] = current_date_str
        # Rotate/shuffle the problems pool
        shuffled = list(prob_data.get("problems", []))
        random.shuffle(shuffled)
        prob_data["problems"] = shuffled
        save_problem_solving(prob_data)
        st.toast("Daily vault refresh: Shuffled problem list for today!", icon="🔄")
        
    # 2. Status & Refresh Trigger bar
    col_status, col_btn = st.columns([3, 1])
    with col_status:
        st.markdown(
            f"""
            <div style='padding: 8px 14px; border-radius: 12px; background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.15); display: inline-block;'>
                <span style='color: #818CF8; font-size: 0.85rem; font-weight: 600;'>📅 Last Refreshed: {prob_data.get("last_refreshed")}</span>
                <span style='color: #94A3B8; font-size: 0.85rem; margin-left: 12px;'>| Active Problems: {len(prob_data.get("problems", []))} (Daily Min: 20)</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_btn:
        if st.button("🔄 Trigger Daily Refresh", key="trigger_problem_refresh", use_container_width=True):
            with st.spinner("Refreshing vault and generating a new study with Groq..."):
                g_key = st.session_state.get("groq_api_key", DEFAULT_GROQ_KEY)
                try:
                    new_problem = generate_new_problem_with_groq(g_key)
                    if new_problem and isinstance(new_problem, dict) and "title" in new_problem:
                        prob_list = prob_data.get("problems", [])
                        titles = [p.get("title") for p in prob_list]
                        if new_problem["title"] not in titles:
                            new_problem["id"] = max([p.get("id", 0) for p in prob_list] or [0]) + 1
                            prob_list.insert(0, new_problem)
                        
                        # Cache up to 50 problems
                        if len(prob_list) > 50:
                            prob_list = prob_list[:50]
                            
                        prob_data["problems"] = prob_list
                        st.toast("Success! Generated a new problem with Groq AI.", icon="🤖")
                except Exception as ex:
                    st.toast(f"AI generation skipped/failed. Shuffling existing set. ({ex})", icon="⚠️")
                
                # Shuffle/rotate
                import random
                shuffled = list(prob_data.get("problems", []))
                random.shuffle(shuffled)
                prob_data["problems"] = shuffled
                prob_data["last_refreshed"] = current_date_str
                save_problem_solving(prob_data)
                time.sleep(0.3)
                st.rerun()
                
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # 3. Filtering
    filter_col_search, filter_col_cat, filter_col_diff = st.columns([2, 1, 1])
    with filter_col_search:
        prob_search = st.text_input("🔍 Search problems, topics, or code keywords...", placeholder="e.g. DP, memory leak, Redis...", key="prob_search_input")
    with filter_col_cat:
        prob_cat = st.selectbox("Filter Category", ["All", "LeetCode Python", "Production Scaling & Systems", "Generative AI & LLMs"], key="prob_cat_select")
    with filter_col_diff:
        prob_diff = st.selectbox("Filter Difficulty", ["All", "Easy", "Medium", "Hard"], key="prob_diff_select")
        
    # Apply Filtering
    all_problems = prob_data.get("problems", [])
    filtered_problems = []
    
    for p in all_problems:
        if prob_cat != "All" and p.get("category") != prob_cat:
            continue
        if prob_diff != "All" and p.get("difficulty") != prob_diff:
            continue
        if prob_search:
            q = prob_search.lower()
            text_to_search = (p.get("title", "") + " " + p.get("summary", "") + " " + p.get("problem_description", "") + " " + p.get("solution_code", "") + " " + " ".join(p.get("tags", []))).lower()
            if q not in text_to_search:
                continue
        filtered_problems.append(p)
        
    # Render List
    if not filtered_problems:
        st.markdown(
            """
            <div style='padding: 50px; text-align: center; border: 1px dashed rgba(255,255,255,0.08); border-radius: 18px; background: rgba(255,255,255,0.01);'>
                <h3 style='color: #64748B;'>No problems found matching filters</h3>
                <p style='color: #475569;'>Try altering your search text or filter options.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for idx, p in enumerate(filtered_problems):
            p_title = p.get("title", "Untitled Problem")
            p_cat = p.get("category", "Uncategorized")
            p_diff = p.get("difficulty", "Medium")
            p_summary = p.get("summary", "")
            p_desc = p.get("problem_description", "")
            p_code = p.get("solution_code", "")
            p_expl = p.get("explanation", "")
            p_tags = p.get("tags", [])
            
            diff_color = "#34D399" if p_diff == "Easy" else ("#F59E0B" if p_diff == "Medium" else "#EF4444")
            cat_color = "#6366F1" if p_cat == "LeetCode Python" else ("#10B981" if p_cat == "Production Scaling & Systems" else "#EC4899")
            
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 8px;">
                        <span style="font-size: 1.15rem; font-weight: 800; color: #f8fafc;">{p_title}</span>
                        <div style="display: flex; gap: 8px;">
                            <span style="background-color: {cat_color}18; color: {cat_color}; border: 1px solid {cat_color}33; padding: 3px 8px; border-radius: 10px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase;">
                                {p_cat}
                            </span>
                            <span style="background-color: {diff_color}18; color: {diff_color}; border: 1px solid {diff_color}33; padding: 3px 8px; border-radius: 10px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase;">
                                {p_diff}
                            </span>
                        </div>
                    </div>
                    <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 12px; font-weight: 500;">{p_summary}</div>
                    """,
                    unsafe_allow_html=True
                )
                
                with st.expander("📖 View Problem Statement / Bug Scenario"):
                    st.markdown(f"<div style='color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;'>{p_desc}</div>", unsafe_allow_html=True)
                    
                with st.expander("💻 View Python Solution / Production Fix"):
                    st.code(p_code, language="python")
                    
                with st.expander("💡 View Deep Explanation & Analysis"):
                    st.markdown(f"<div style='color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;'>{p_expl}</div>", unsafe_allow_html=True)
                
                tag_html = "".join([f"<span style='background: rgba(255,255,255,0.04); color: #94A3B8; padding: 2px 8px; border-radius: 6px; font-size: 0.68rem; margin-right: 6px; font-weight:600;'>#{tag}</span>" for tag in p_tags])
                st.markdown(
                    f"""
                    <div style="margin-top: 10px; display: flex; align-items: center; flex-wrap: wrap;">
                        <span style="font-size: 0.68rem; color: #475569; font-weight: 700; text-transform: uppercase; margin-right: 8px;">Tags:</span>
                        {tag_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# 11. SAVED BOOKMARKS TAB
with tab_saved:
    st.subheader("⭐ Bookmarked Articles")
    
    if not st.session_state.bookmarks:
        st.markdown(
            """
            <div style='padding: 60px; text-align: center; border: 1px dashed rgba(255,255,255,0.08); border-radius: 18px; background: rgba(255,255,255,0.01);'>
                <h3 style='color: #64748B;'>No Bookmarked Articles</h3>
                <p style='color: #475569;'>Click the "☆" icon on any article card in the live feed to save them here. Your bookmarks persist across browser restarts!</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Convert bookmarks to list
        saved_list = list(st.session_state.bookmarks.values())
        
        # Grid of bookmarks (2 columns)
        saved_cols = st.columns(2)
        for idx, bookmark in enumerate(saved_list):
            target_col = saved_cols[idx % 2]
            with target_col:
                with st.container(border=True):
                    # Image header (Dynamic Image Overlay & Fallback)
                    img_src = bookmark.get("image")
                    img_html = f'<img src="{img_src}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 2;" onerror="this.style.display=\'none\';">' if img_src else ''
                    st.markdown(
                        f"""
                        <div style="position: relative; border-radius: 12px; overflow: hidden; margin-bottom: 12px; height: 140px; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(255, 255, 255, 0.05); background: linear-gradient(135deg, #151f32 0%, #0b0f19 100%);">
                            <span style="position: absolute; font-weight:700; color:{get_source_color(bookmark['source'])}; font-size:1.1rem; letter-spacing:0.04em; text-transform:uppercase; z-index: 1;">{bookmark['source']}</span>
                            {img_html}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                        
                    # Source badge & info
                    b_color = get_source_color(bookmark['source'])
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="background-color: {b_color}18; color: {b_color}; border: 1px solid {b_color}33; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">
                                {bookmark['source']}
                            </span>
                            <span style="color: #64748B; font-size: 0.7rem; font-weight: 600;">
                                ⏱️ {bookmark['read_time']}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Title & Author
                    st.markdown(
                        f"""
                        <h3 style="color: #f8fafc; font-size: 1.1rem; font-weight: 700; margin: 4px 0 10px 0; line-height: 1.45; min-height: 48px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            {bookmark['title']}
                        </h3>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    auth_meta = f" • By {bookmark['author']}" if bookmark['author'] else ""
                    st.markdown(
                        f"""
                        <div style="color: #475569; font-size: 0.7rem; font-weight: 600; margin-bottom: 12px;">
                            Saved • {bookmark.get('time_ago', 'Recent')}{auth_meta}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Description
                    st.markdown(
                        f"""
                        <p style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5; margin-bottom: 16px; min-height: 50px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            {bookmark['clean_summary']}
                        </p>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Actions
                    sb1, sb2 = st.columns([3, 1])
                    with sb1:
                        st.link_button("Read Original Article ↗", bookmark["link"], width="stretch")
                    with sb2:
                        if st.button("🗑️", key=f"saved_remove_{bookmark['link']}", width="stretch", help="Remove from Saved Bookmarks"):
                            del st.session_state.bookmarks[bookmark["link"]]
                            save_bookmarks()
                            st.toast("Removed from bookmarks!", icon="🗑️")
                            st.rerun()

# 10. PLATFORM ANALYTICS TAB
with tab_analytics:
    st.subheader("📊 Content Distribution & Analytics")
    
    if df_all.empty:
        st.info("Insufficient data loaded to generate analytics.")
    else:
        # KPI summary metrics cards
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        with kpi_col1:
            st.metric("Curated Category", category)
        with kpi_col2:
            st.metric("Total Unique Articles", f"{len(df_all)}")
        with kpi_col3:
            st.metric("Total Active Channels", f"{df_all['source'].nunique()}")
        with kpi_col4:
            st.metric("Total Bookmarks", f"{len(st.session_state.bookmarks)}")
            
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("<b style='color:#f8fafc; font-size:1.1rem;'>📡 Article Count by Source</b>", unsafe_allow_html=True)
            source_series = df_all["source"].value_counts()
            st.bar_chart(source_series, color="#6366F1")
            
        with chart_col2:
            st.markdown("<b style='color:#f8fafc; font-size:1.1rem;'>🏷️ Top Keyword Density in Headlines</b>", unsafe_allow_html=True)
            # Extracted keywords frequency analysis
            keywords = ["AI", "Python", "Cloud", "Apple", "Google", "Microsoft", "Security", "Hacker", "Linux", "AWS", "Startup", "Tech", "Cyber", "Data", "CEO"]
            keyword_counts = {}
            for kw in keywords:
                count = df_all["title"].str.contains(kw, case=False, na=False).sum()
                if count > 0:
                    keyword_counts[kw] = count
            
            if keyword_counts:
                kw_df = pd.DataFrame(list(keyword_counts.items()), columns=["Keyword", "Frequency"]).sort_values(by="Frequency", ascending=False)
                st.bar_chart(kw_df.set_index("Keyword"), color="#A78BFA")
            else:
                st.info("No matching trend keywords detected in current articles list.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Length & reading time estimation distribution
        time_chart_col1, time_chart_col2 = st.columns([1, 2])
        with time_chart_col1:
            st.markdown("<b style='color:#f8fafc; font-size:1.1rem;'>⏳ Average Reading Time Distribution</b>", unsafe_allow_html=True)
            # Group read times
            read_groups = df_all["read_time"].value_counts().sort_index()
            st.bar_chart(read_groups, color="#34D399")
        with time_chart_col2:
            st.markdown("<b style='color:#f8fafc; font-size:1.1rem;'>📈 Detailed Article Feed Summary Table</b>", unsafe_allow_html=True)
            summary_table = df_all.groupby("source").agg(
                Articles_Count=("title", "count"),
                Average_Reading_Time=("read_time", lambda x: f"{round(pd.to_numeric(x.str.replace(' min read', ''), errors='coerce').mean(), 1)} min")
            ).reset_index()
            st.dataframe(summary_table, width="stretch", hide_index=True)

# 11. FEED HEALTH SYSTEM TAB
with tab_diag:
    st.subheader("⚙️ Channel Diagnostics & Status Dashboard")
    
    diag_list = []
    for source, data in diagnostics.items():
        diag_list.append({
            "Feed Source Channel": source,
            "Target RSS Endpoint": data["url"],
            "Connection Status": data["status"],
            "Synced Volume": data["count"],
            "Load Latency": data["speed"]
        })
        
    diag_df = pd.DataFrame(diag_list)
    
    # Custom colored column values using dataframe formatting or standard tables
    st.markdown(
        """
        <p style='color: #94A3B8; font-size:0.9rem;'>
            NewArticleAgent performs concurrent RSS requests to retrieve the latest feed items. 
            Below is the status of the data pipeline. Cache TTL is set to 600s.
        </p>
        """, 
        unsafe_allow_html=True
    )
    
    st.dataframe(
        diag_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Connection Status": st.column_config.TextColumn("Status", help="Connection health status"),
            "Synced Volume": st.column_config.NumberColumn("Articles Count"),
            "Load Latency": st.column_config.TextColumn("Response Time")
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # System logs panel
    with st.container(border=True):
        st.markdown("<b style='color:#f8fafc;'>⚙️ Pipeline System Information</b>", unsafe_allow_html=True)
        col_sys1, col_sys2 = st.columns(2)
        with col_sys1:
            st.code(
                f"""
                OS Platform: Linux
                Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                Active Session ID: {id(st.session_state)}
                """,
                language="yaml"
            )
        with col_sys2:
            st.code(
                f"""
                Total Cache Entries: {len(df_all)}
                Total Bookmarked size: {len(st.session_state.bookmarks)}
                Active Category: {category}
                """,
                language="yaml"
            )