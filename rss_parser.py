import feedparser
from datetime import datetime, timezone
import time
import re
from bs4 import BeautifulSoup

def extract_image(item):
    # 1. Try media_content
    media_content = item.get("media_content")
    if media_content and isinstance(media_content, list) and len(media_content) > 0:
        for media in media_content:
            if media.get("medium") == "image" or "image" in media.get("type", ""):
                return media.get("url")
            
    # 2. Try media_thumbnail
    media_thumbnail = item.get("media_thumbnail")
    if media_thumbnail and isinstance(media_thumbnail, list) and len(media_thumbnail) > 0:
        return media_thumbnail[0].get("url")
        
    # 3. Try enclosure link
    links = item.get("links", [])
    for link in links:
        if "image" in link.get("type", ""):
            return link.get("href")
            
    # 4. Try parsing HTML summary for <img> tag
    summary = item.get("summary") or item.get("description")
    if summary:
        try:
            soup = BeautifulSoup(summary, "html.parser")
            img = soup.find("img")
            if img and img.get("src"):
                return img.get("src")
        except Exception:
            pass
            
    # 5. Try parsing content values for <img> tag
    content_list = item.get("content")
    if content_list and isinstance(content_list, list):
        for content in content_list:
            val = content.get("value")
            if val:
                try:
                    soup = BeautifulSoup(val, "html.parser")
                    img = soup.find("img")
                    if img and img.get("src"):
                        return img.get("src")
                except Exception:
                    pass

    return None

def clean_summary(summary_html):
    if not summary_html:
        return ""
    try:
        soup = BeautifulSoup(summary_html, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=" ")
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Limit to 200 characters for a clean preview card
        if len(text) > 200:
            return text[:197] + "..."
        return text
    except Exception:
        # Fallback to simple regex strip
        clean = re.sub(r'<[^>]+>', '', summary_html)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) > 200:
            return clean[:197] + "..."
        return clean

def get_time_ago(struct_time):
    if not struct_time:
        return "Recent"
    try:
        # Convert struct_time to timestamp then datetime
        pub_time = datetime.fromtimestamp(time.mktime(struct_time), tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - pub_time
        
        seconds = diff.total_seconds()
        if seconds < 0:
            return "Just now"
        
        minutes = int(seconds // 60)
        hours = int(minutes // 60)
        days = int(hours // 24)
        
        if seconds < 60:
            return "Just now"
        elif minutes < 60:
            return f"{minutes}m ago"
        elif hours < 24:
            return f"{hours}h ago"
        elif days < 30:
            return f"{days}d ago"
        else:
            return pub_time.strftime("%b %d, %Y")
    except Exception:
        return "Recent"

def estimate_read_time(text):
    if not text:
        return "1 min read"
    words = len(text.split())
    # assume 200 words per minute
    wpm = 200
    minutes = max(1, round(words / wpm))
    return f"{minutes} min read"

def fetch_feed(source_name, url):
    feed = feedparser.parse(url)
    articles = []

    for item in feed.entries:
        raw_summary = item.get("summary") or item.get("description") or ""
        cleaned_sum = clean_summary(raw_summary)
        img_url = extract_image(item)
        
        # Get published timestamp for sorting
        pub_struct = item.get("published_parsed")
        pub_timestamp = time.mktime(pub_struct) if pub_struct else 0.0
        
        # Estimate read time on full raw summary
        read_time = estimate_read_time(raw_summary)
        
        # Extract author
        author = item.get("author") or item.get("creator") or ""
        # Clean up author if it is a list/dict or has email
        if author and "(" in author:
            # e.g., "email@domain.com (Author Name)"
            matches = re.search(r'\((.*?)\)', author)
            if matches:
                author = matches.group(1)
        
        articles.append({
            "source": source_name,
            "title": item.get("title", "Untitled"),
            "link": item.get("link", ""),
            "summary": raw_summary,
            "clean_summary": cleaned_sum,
            "image": img_url,
            "published": item.get("published", ""),
            "published_parsed": pub_struct,
            "timestamp": pub_timestamp,
            "time_ago": get_time_ago(pub_struct),
            "read_time": read_time,
            "author": author,
        })

    return articles