import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time
from datetime import datetime
from rss_feeds import RSS_FEEDS
from rss_parser import fetch_feed

# 1. Page Configuration & Theme Initialization
st.set_page_config(
    page_title="NewArticleAgent | Curated Intel Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom Premium CSS (Aesthetics & UX)
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

/* Global Font Override */
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Hide Default Streamlit Menu & Footer for White-labeled SaaS look */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
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
tab_live, tab_saved, tab_analytics, tab_diag = st.tabs([
    "📰 Live Intel Feed",
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

# 9. SAVED BOOKMARKS TAB
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