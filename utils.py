import json
import os
import re
import requests
from groq import Groq

# File to store user-created parody ideas
IDEAS_FILE = "creator_ideas.json"
DEFAULT_GROQ_KEY = "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"

def generate_parody_from_news(title, summary, audience_focus="Global"):
    """
    Fallback comedy generator utilizing pre-defined templates optimized for 
    faceless B-roll creators, support for Indian and Global corporate cultures.
    """
    text = (title + " " + summary).lower()
    
    # Keyword theme routing
    if any(k in text for k in ["ai", "gpt", "claude", "llm", "copilot", "gpu", "nvidia", "openai", "gemini", "llama", "chatbot"]):
        category = "AI Hype"
        emoji_theme = "🤖 AI Hype & LLM Mania"
        
        if audience_focus == "Indian":
            satirical_headline = "Indian Startup replaces 95% developers with AI chatbot, customer care flooded with queries written in Hindi prompt injection"
            video_hook = "Using ChatGPT to write appraisal self-evaluation forms in Bengaluru"
            b_roll = "[Clip 1: Senior developer staring at ChatGPT with tea cup] ➡️ [Clip 2: Copied code pasted into production IDE] ➡️ [Clip 3: Server monitor showing red errors]"
            text_overlays = [
                "Slide 1: Manager asks why I need 3 months notice period if I use AI.",
                "Slide 2: I tell him AI takes 2 months to compile code that actually works.",
                "Slide 3: Pushing 'make it run' to the main repo and going for chai."
            ]
            bg_music = "Dramatic classic sitar or upbeat sarod instrumental"
            lingo = [
                ("Leveraging GenAI Solutions", "We fired our interns and are copy-pasting code from a chatbot."),
                ("Prompt Engineering Specialist", "A coder who can say 'please refactor this' in three different languages."),
                ("70-Hour work week optimization", "We expect you to code for 10 hours and prompt the AI for the other 60.")
            ]
        else:
            satirical_headline = "Company replaces engineering team with autonomous AI agent, which spends its entire budget buying H100 GPUs and trying to work remote from Bali"
            video_hook = "When the boss asks how I solved the blocker in 10 seconds"
            b_roll = "[Clip 1: Person sipping iced coffee in front of monitor] ➡️ [Clip 2: Claude typing out a huge code block] ➡️ [Clip 3: Closing laptop at 2 PM]"
            text_overlays = [
                "Slide 1: Junior developer asks how I fixed the production bug in 5 minutes.",
                "Slide 2: Me explaining a complex data structure theory...",
                "Slide 3: (Reality: I just prompted Claude to 'fix this compile error please'.)"
            ]
            bg_music = "Chill lofi synthwave beats"
            lingo = [
                ("AI-Driven Synergies", "Using a $20 AI tool to do $200k worth of engineering work."),
                ("Prompt Engineer", "A developer who writes long paragraphs to a bot instead of reading docs."),
                ("Autonomous Agent", "An expensive loop of API requests that burns cloud credits to generate print statements.")
            ]
            
        song_parody = {
            "title": "Claude's Plan",
            "original_song": "God's Plan - Drake",
            "lyrics": "I drop a prompt, it write the code, they think I'm a god / Claude's plan, Claude's plan / I hold back on the commit, I don't wanna show my hand / I go to sleep at 2 PM..."
        }
    elif any(k in text for k in ["layoff", "fired", "restruct", "rto", "office", "remote", "zoom", "hybrid", "commute", "ceo", "wfh"]):
        category = "Corporate Culture / RTO"
        emoji_theme = "💼 Corporate Overlords & RTO Battles"
        
        if audience_focus == "Indian":
            satirical_headline = "CEO who works from luxury penthouse in South Delhi claims 'mandatory 5-day RTO builds collaborative synergy'"
            video_hook = "Bengaluru dev traveling 10km on Outer Ring Road (ORR) to join a Zoom call with Gurgaon"
            b_roll = "[Clip 1: Car dashboard showing traffic jam under metro construction] ➡️ [Clip 2: Dev sitting at desk with heavy noise-cancelling headphones] ➡️ [Clip 3: Zoom call screen on laptop]"
            text_overlays = [
                "Slide 1: Spent 2.5 hours in Bengaluru ORR traffic because office culture is 'mandatory'.",
                "Slide 2: Reached desk, put on ANC headphones to block office noise.",
                "Slide 3: Joined a Zoom meeting with my team lead who is working from Noida."
            ]
            bg_music = "Slow, depressing flute or acoustic guitar cover"
            lingo = [
                ("Office Collaboration", "Sitting in a cubicle wearing headphones because the open-floor layout is too loud."),
                ("Synergy Tapri Breaks", "Discussing notice periods and salary hikes over 10-rupee cutting chai."),
                ("Workplace Commute", "Active physical meditation in bumper-to-bumper traffic.")
            ]
        else:
            satirical_headline = "CEO mandates return-to-office to 'increase collaboration', rents out desks to coworking startup next day"
            video_hook = "Checking into Slack active status while still in bed"
            b_roll = "[Clip 1: Wiggling physical mouse to keep Slack status green] ➡️ [Clip 2: Sleeping dev cuddling pillow] ➡️ [Clip 3: Slack notification active on phone]"
            text_overlays = [
                "Slide 1: CEO says in-office synergy leads to spontaneous innovation.",
                "Slide 2: My spontaneous innovation is wiggling the mouse to stay online.",
                "Slide 3: While I collaborate with my duvet from 9 AM to 11 AM."
            ]
            bg_music = "Upbeat classic swing jazz"
            lingo = [
                ("In-Person Synergy", "Paying lease on an expensive building because of a contract signed in 2018."),
                ("Coffee Badging", "Scanning your badge at the office gate, drinking free coffee, and leaving after 30 minutes."),
                ("Quiet Quitting", "Doing exactly what is written in your contract and going home at 5 PM.")
            ]
            
        song_parody = {
            "title": "Stayin' Online",
            "original_song": "Stayin' Alive - Bee Gees",
            "lyrics": "Well, you can tell by the way I wiggle my mouse, / I'm a remote worker, never leave the house. / Stayin' online, stayin' online..."
        }
    else:
        # Default Tech Bro theme
        category = "Tech Bro Culture"
        emoji_theme = "🧢 Tech Bro Culture & VC Hype"
        
        if audience_focus == "Indian":
            satirical_headline = "Tech Bro edits LinkedIn bio to 'Stealth Startup Founder' after getting laid off from service company"
            video_hook = "Explaining variable pay to parents during appraisal season"
            b_roll = "[Clip 1: Dev looking at appraisal letter with shocked face] ➡️ [Clip 2: Finger scrolling through job portals] ➡️ [Clip 3: Pouring tea slowly]"
            text_overlays = [
                "Slide 1: Manager says you got a 'solid performer' rating this year.",
                "Slide 2: Hike percentage: 2.5% (below inflation).",
                "Slide 3: variable pay component: 'Depending on company profits' (which are zero)."
            ]
            bg_music = "Sarcastic harmonium or sitar beats"
            lingo = [
                ("Stealth Startup", "I have a pitch deck and a WhatsApp group, but zero revenue."),
                ("Variable CTC", "The money we showed you on paper to get you to sign, which you will never actually see."),
                ("Notice Period", "A 90-day cooling off period where you interview at other startups on office laptop.")
            ]
        else:
            satirical_headline = "Startup founder raises $10M pre-revenue, spends $8M on branded Patagonia vests and ergonomic office chairs"
            video_hook = "Reading LinkedIn 'Thought Leader' posts at 8 AM"
            b_roll = "[Clip 1: Scrolling fast through a LinkedIn post with single-sentence spacing] ➡️ [Clip 2: Facepalm gesture] ➡️ [Clip 3: Closing the browser tab]"
            text_overlays = [
                "Slide 1: LinkedIn influencer explaining how waking up at 4 AM helped them negotiate a merger.",
                "Slide 2: Me reading it at 10 AM in pajamas with cereal crumbs on my shirt.",
                "Slide 3: Wondering why I became a software engineer instead of a thought leader."
            ]
            bg_music = "Comedic retro circus organ music"
            lingo = [
                ("LinkedIn Thought Leader", "Someone who writes long paragraph posts about leadership based on buying a bagel."),
                ("Pre-revenue", "We have a nice logo, a Figma design, and burn $100k a month of venture money."),
                ("Stealth Mode", "We are afraid that if people find out what we are building, they will laugh at us.")
            ]
            
        song_parody = {
            "title": "LinkedIn Paradise",
            "original_song": "Gangsta's Paradise - Coolio",
            "lyrics": "As I walk through the valley of the tech bro grind / I take a look at my network and realize there's no mind..."
        }

    # B-roll style reaction ideas
    reaction_hooks = [
        "1. Visual: Close-up of typing furiously. Overlay: 'When the meeting could have been a 3-word Slack message.'",
        "2. Visual: Wiggling mouse jiggler. Overlay: 'WFH status active vs actually in bed sleeping.'",
        "3. Visual: Closing laptop gently and smiling. Overlay: 'Friday 5:00 PM: Pushed code directly to main, now it is DevOps' problem.'"
    ]

    companies = ["Google", "Microsoft", "Apple", "Meta", "Amazon", "Netflix", "OpenAI", "Nvidia", "CrowdStrike", "AWS"]
    found_target = "Our Company"
    for comp in companies:
        if comp.lower() in title.lower():
            found_target = comp
            break
            
    custom_satirical_headline = satirical_headline.replace("Company", found_target)
    
    return {
        "detected_category": category,
        "theme_name": emoji_theme,
        "custom_satirical_headline": custom_satirical_headline,
        "video_blueprint": {
            "video_hook": video_hook,
            "visual_b_roll": b_roll,
            "text_overlays": text_overlays,
            "bg_music": bg_music
        },
        "parody_song": song_parody,
        "corporate_lingo": lingo,
        "reaction_hooks": reaction_hooks
    }

# 3. Persistence Helpers for User's Creator Ideas Board
def load_ideas():
    if os.path.exists(IDEAS_FILE):
        try:
            with open(IDEAS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_ideas(ideas):
    try:
        with open(IDEAS_FILE, "w") as f:
            json.dump(ideas, f, indent=4)
        return True
    except Exception:
        return False

def generate_comedy_with_groq(api_key, title, summary, tone="sarcastic", audience_focus="Global"):
    """
    Calls Groq Chat Completions API using the official Groq SDK to generate a full comedy package 
    optimized for silent B-roll, text overlay videos, targeting Indian or Global audiences.
    """
    if not api_key:
        api_key = DEFAULT_GROQ_KEY
        
    client = Groq(api_key=api_key)
    
    audience_context = ""
    if audience_focus == "Indian":
        audience_context = (
            "Target Audience: Indian corporate office workers (Bengaluru, Noida, Gurugram tech ecosystem). "
            "Use relatable Indian corporate tropes like: Outer Ring Road (ORR) traffic, cutting chai/tapri breaks, "
            "notice periods (3 months), variable CTC, 70-hour work week discussions, toxic managers calling on WhatsApp/weekends, "
            "switching companies for 30% hikes, TCS/Infosys service vs startup product roles."
        )
    else:
        audience_context = (
            "Target Audience: Global tech workers and remote corporate employees (Silicon Valley, Europe, remote hubs). "
            "Use global tech-bro/corporate tropes like: remote work in Bali/Portugal, San Francisco rent, Patagonia vests, "
            "unlimited PTO (but taking 0 days), RTO (return-to-office) mandates, coffee-badging, Zoom meeting fatigue, "
            "stock option packages (RSUs/options), startup pitch decks, timezone overlapping."
        )
        
    prompt = f"""
    You are a professional comedy writer for tech content creators. Your target audience is corporate office workers (software engineers, product managers, DevOps, QA, IT support). 
    
    {audience_context}
    
    FORMAT REQUIREMENT:
    The creator is a silent/faceless creator. They do NOT show their face or speak. The video is a B-roll style video (e.g. typing on keyboard, sipping coffee, screen recording, zoom call animation) with text overlay captions, set to background music.
    
    Generate a tech parody package for the following news item:
    Headline: {title}
    Summary / Context: {summary}
    Comedy Persona: {tone}

    Return a JSON object matching this schema exactly. Do not add any markdown wrapper around the JSON:
    {{
      "detected_category": "Short category name (e.g. AI Hype, RTO, JIRA Jungle, Cyber Security, Tech Bro Culture)",
      "theme_name": "Emoji-prefixed theme name",
      "custom_satirical_headline": "A satirical Onion-style headline about this news",
      "video_blueprint": {{
        "video_hook": "A scroll-stopping opening text overlay hook to capture the viewer (e.g. 'Day 45 of pretending to...')" ,
        "visual_b_roll": "Step-by-step description of B-roll footage/clips to record (e.g., [Clip 1: Close up of fingers typing furiously on keyboard], [Clip 2: Zooming out to show the screen has a game open])",
        "text_overlays": [
          "Slide 1 Text: (e.g. 'When the CEO says return to office increases synergy...')",
          "Slide 2 Text: (e.g. 'But the only person you talk to is a developer in London...')",
          "Slide 3 Text: (e.g. 'So you commuted 2 hours to sit on Zoom in a glass box.')"
        ],
        "bg_music": "Style of background music to search for and overlay (e.g. 'Sarcastic elevator jazz', 'Upbeat retro synthwave', 'Tense acoustic guitar')"
      }},
      "parody_song": {{
        "title": "Funny parody title",
        "original_song": "Original pop song name & artist",
        "lyrics": "A song parody chorus snippet adapted to this news"
      }},
      "corporate_lingo": [
        ["Corporate Phrase 1", "Funny translation 1"],
        ["Corporate Phrase 2", "Funny translation 2"],
        ["Corporate Phrase 3", "Funny translation 3"]
      ],
      "reaction_hooks": [
        "1. Reel Idea: Show B-roll of developer making tea while code runs with screen text: [Insert hook]",
        "2. Reel Idea: Show B-roll of closed laptop at 5:01 PM with screen text: [Insert hook]",
        "3. Reel Idea: Show B-roll of developer making tea while code runs with screen text: [Insert hook]"
      ]
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            timeout=15.0
        )
        content = completion.choices[0].message.content
        comedy_data = json.loads(content)
        return comedy_data
    except Exception as e:
        raise RuntimeError(f"Groq API Error: {str(e)}")

def generate_live_trends_with_groq(api_key, news_articles, audience_focus="Global"):
    """
    Queries Groq to analyze the latest tech news headlines and generate 
    a set of 4 highly trending, faceless video concepts and memes using the Groq SDK.
    """
    if not api_key:
        api_key = DEFAULT_GROQ_KEY
        
    client = Groq(api_key=api_key)
    
    # Format headlines list
    headlines_text = "\n".join([f"- {art['title']} (Source: {art['source']})" for art in news_articles[:10]])
    
    audience_context = ""
    if audience_focus == "Indian":
        audience_context = (
            "Target Audience: Indian corporate employees (Bengaluru, Noida, Gurugram tech hubs). "
            "Use references like ORR traffic, notice periods (3 months), appraisal ratings, variable pay, tea breaks / tapri, service vs product startups, 70-hour work week."
        )
    else:
        audience_context = (
            "Target Audience: Global tech workers and remote employees. "
            "Use references like unlimited PTO, return-to-office gates, Patagonia vests, Bali remote work, timezone mismatch, stock options (RSUs)."
        )
        
    prompt = f"""
    You are a professional comedy writer and viral social media strategist. 
    Analyze the following latest trending tech news items:
    {headlines_text}
    
    {audience_context}
    
    Based on these news stories, generate 4 distinct, highly trending video formats and meme concepts (Reels, TikToks, Shorts) designed to go viral among corporate office workers. 
    
    IMPORTANT: The creator is a silent, faceless creator who does NOT show their face or speak. They use B-roll footage, text-on-screen overlays, and background music.
    
    The concepts should NOT just be song parodies. They can include POV sketches, CapCut templates, green-screen reactions, silent loops, or screenshare gags.
    
    Return a JSON object containing a key 'trends' which is a list of exactly 4 objects. Each object must have these keys:
    - 'title': A catchy, sarcastic title for the trend.
    - 'video_type': The format type (e.g. POV B-Roll, CapCut Meme Template, Screen Share Satire, Silent Loop).
    - 'news_inspiration': Which news item from the list inspired this trend.
    - 'video_hook': Sarcastic scroll-stopping hook (text overlay).
    - 'visual_b_roll': Detailed description of B-roll footage to record or use.
    - 'text_overlays': A list of 3-4 slides of text overlays to place on screen.
    - 'bg_music': Background audio/music style suggestion.
    - 'relatability_reason': Why corporate workers will share this in their private team Slack channels.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.85,
            timeout=20.0
        )
        content = completion.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        raise RuntimeError(f"Groq API Error: {str(e)}")

def generate_fallback_live_trends(audience_focus="Global"):
    """
    Returns 4 high-quality fallback Reels/TikTok trends for the silent creator format,
    tailored to Indian or Global corporate workers.
    """
    if audience_focus == "Indian":
        return {
            "trends": [
                {
                    "title": "ORR Traffic vs Office Mandate",
                    "video_type": "POV B-Roll Sketch",
                    "news_inspiration": "RTO Synergies & Back-to-Office Mandates",
                    "video_hook": "When they mandate 5-day office synergy but ORR traffic takes 3 hours",
                    "visual_b_roll": "[Clip: Laptop open in a stationary car with red taillights in traffic. Cut to finger wiggling a mouse jiggler on the steering wheel.]",
                    "text_overlays": [
                        "Slide 1: Manager: 'Returning to office builds team collaboration!'",
                        "Slide 2: Me: Sitting in Silk Board traffic for 2 hours...",
                        "Slide 3: To join a Zoom meeting with a colleague sitting in Gurgaon."
                    ],
                    "bg_music": "Sarcastic harmonium or classic Indian comedy background score",
                    "relatability_reason": "Indian developers will share this instantly because they face ORR/Silk Board traffic every day."
                },
                {
                    "title": "The 3-Month Notice Period KT",
                    "video_type": "CapCut Meme Template",
                    "news_inspiration": "Tech Industry Appraisal & Hiring Trends",
                    "video_hook": "Day 45 of my 3-month notice period",
                    "visual_b_roll": "[Clip: Developer wearing sunglasses in front of a laptop inside a dark room, slowly sipping cutting chai while doing absolutely nothing.]",
                    "text_overlays": [
                        "Slide 1: HR: 'Please finish the knowledge transfer this week.'",
                        "Slide 2: Me: Already cleared my desk, attending standups in mute...",
                        "Slide 3: Having 12 active job offers while updating my LinkedIn bio."
                    ],
                    "bg_music": "Upbeat Punjabi Dhol beat or sarcastic flute cover",
                    "relatability_reason": "Relates to the uniquely long 3-month notice periods in Indian service/product companies."
                },
                {
                    "title": "70-Hour Week Synergy",
                    "video_type": "Silent Loop / Green Screen",
                    "news_inspiration": "Workplace Optimization Guidelines",
                    "video_hook": "Calculating how to fit 70 hours into a 5-day week",
                    "visual_b_roll": "[Clip: Sarcastic zooming in on calculator app showing 70 / 5 = 14 hours a day, then camera pans to a developer asleep on his keyboard.]",
                    "text_overlays": [
                        "Slide 1: Founders: 'Young people must work 70 hours a week for national growth!'",
                        "Slide 2: Reality: Devs spending 20 hours in meetings, 10 hours in traffic...",
                        "Slide 3: And the other 40 hours wiggling the mouse to stay active on Slack."
                    ],
                    "bg_music": "Tense cinematic strings or dramatic orchestra",
                    "relatability_reason": "Direct poke at the viral 70-hour work week comments that trended in Indian corporate social media."
                },
                {
                    "title": "The Variable Pay Appraisal",
                    "video_type": "POV Reaction",
                    "news_inspiration": "Company Annual Appraisal Announcements",
                    "video_hook": "Explaining my 2.5% appraisal hike to my parents",
                    "visual_b_roll": "[Clip: Developer holding appraisal letter, looking blankly at a cup of tea tapri tea, then facepalming in slow motion.]",
                    "text_overlays": [
                        "Slide 1: Manager: 'You did a fantastic job, solid performance rating!'",
                        "Slide 2: Appraisal letter: 2.5% hike (less than inflation).",
                        "Slide 3: Variable CTC: 'Will be paid next year if the company makes a profit.'"
                    ],
                    "bg_music": "Sad, comedic violin music",
                    "relatability_reason": "Appraisal hikes and variable CTC are highly shared pain points for Indian tech workers."
                }
            ]
        }
    else:
        return {
            "trends": [
                {
                    "title": "Unlimited PTO Guilt Trip",
                    "video_type": "CapCut Meme Template",
                    "news_inspiration": "Company Holiday & Benefits Policies",
                    "video_hook": "Taking 2 days off in an 'unlimited PTO' company",
                    "visual_b_roll": "[Clip: Developer sitting on a beach chair on holiday, typing frantically on a laptop with sand on the keyboard.]",
                    "text_overlays": [
                        "Slide 1: Unlimited PTO sounds great on paper.",
                        "Slide 2: Reality: Having to write a 3-page handover document...",
                        "Slide 3: And checking Slack every 10 minutes from a beach chair."
                    ],
                    "bg_music": "Chill lofi beats mixed with distant notifications sound effects",
                    "relatability_reason": "Global tech workers experience extreme guilt and backlog pressure with unlimited PTO policies."
                },
                {
                    "title": "The RTO Coffee Badger",
                    "video_type": "Silent POV Loop",
                    "news_inspiration": "RTO Synergy Gate Scans",
                    "video_hook": "How to achieve mandatory collaboration in 15 minutes",
                    "visual_b_roll": "[Clip: Scan security badge at office turnstile, walk directly to coffee machine, pour coffee, scan badge to exit, walk back to car.]",
                    "text_overlays": [
                        "Slide 1: CEO: 'Mandatory in-office attendance will be monitored by gate scans.'",
                        "Slide 2: Developer: Scanning card at 9:00 AM, grabbing coffee...",
                        "Slide 3: Scanning card out at 9:15 AM to work from home where it is quiet."
                    ],
                    "bg_music": "Upbeat retro synthwave or cheeky jazz beat",
                    "relatability_reason": "The 'coffee badging' trend is highly viral among global corporate workers fighting RTO mandates."
                },
                {
                    "title": "The Remote Nomad Mismatch",
                    "video_type": "POV B-Roll",
                    "news_inspiration": "Work From Anywhere Corporate Guidelines",
                    "video_hook": "Living the 'Work from Bali' dream life",
                    "visual_b_roll": "[Clip: Sunny beach scenery, then panning to developer in beach shorts sitting in a dark room under a fan at 3 AM attending a standup.]",
                    "text_overlays": [
                        "Slide 1: 'Work from anywhere!' says the tech startup recruiter.",
                        "Slide 2: Reality: You move to Bali to enjoy the beach...",
                        "Slide 3: But your team is in San Francisco, so your standup is at 3 AM."
                    ],
                    "bg_music": "Relaxing beach wave sounds transitioning into a loud alarm clock",
                    "relatability_reason": "Relatable to digital nomads and remote workers dealing with timezone differences."
                },
                {
                    "title": "The GPU Priority List",
                    "video_type": "Screen Recording Satire",
                    "news_inspiration": "Nvidia GPU Shipment Announcements",
                    "video_hook": "When the company budget cuts hit engineering to buy GPUs",
                    "visual_b_roll": "[Clip: Screen recording of developer requesting a new keyboard license gets rejected, next to a news article showing company buying 10,000 H100s.]",
                    "text_overlays": [
                        "Slide 1: Finance: 'We are cutting free snacks and keyboard replacements to save budget.'",
                        "Slide 2: Same company: Announces purchase of $100M worth of AI servers...",
                        "Slide 3: To run a chatbot that tells employees how to save paper."
                    ],
                    "bg_music": "Epic tension cinematic music",
                    "relatability_reason": "Satirizes the massive corporate spend on AI hardware while engineering budgets are being cut."
                }
            ]
        }


def load_problem_solving():
    import os
    import json
    from datetime import datetime
    from problem_solving_data import DEFAULT_PROBLEMS
    
    file_path = "problem_solving.json"
    
    # Default structure
    default_structure = {
        "last_refreshed": datetime.now().strftime("%Y-%m-%d"),
        "problems": DEFAULT_PROBLEMS
    }
    
    if not os.path.exists(file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_structure, f, indent=4, ensure_ascii=False)
            return default_structure
        except Exception:
            return default_structure
            
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure it has the correct keys
            if "last_refreshed" not in data or "problems" not in data:
                return default_structure
            return data
    except Exception:
        return default_structure

def save_problem_solving(data):
    import json
    file_path = "problem_solving.json"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False

def generate_new_problem_with_groq(api_key):
    """
    Calls Groq to generate a new high-quality LeetCode problem or Production/Scaling bug
    with complete Python code and detailed explanation using the Groq SDK.
    """
    import random
    import json
    
    if not api_key:
        api_key = DEFAULT_GROQ_KEY
        
    client = Groq(api_key=api_key)
    
    # Randomly select a problem type to ensure variety
    choices = [
        "a classic LeetCode coding problem in Python (e.g. dynamic programming, trees, graphs, sorting/searching, sliding window, heaps, binary search, two pointers)",
        "a real-world production bug or scaling issue (e.g. database connection pool exhaustion, caching stampede, memory leaks, distributed lock issues, thread starvation, async I/O bottlenecks, message queue failures, Kafka/Redis consumer issues)",
        "a Generative AI / LLM system scaling or design challenge (e.g. rate limit queue handling, prompt token window overflow, vector database index tuning, hybrid retrieval issues, prompt injection guardrails)"
    ]
    selected_choice = random.choice(choices)
    
    prompt = f"""
    You are an expert Principal Software Engineer and a competitive programmer.
    Generate a highly educational problem-solving item focusing on {selected_choice}.
    
    Provide complete Python solution code, problem statement, summary, and in-depth explanation/root-cause-mitigation.
    
    Return a JSON object matching this schema exactly. Do not add any markdown wrapper around the JSON:
    {{
      "title": "Short title, e.g. 'LeetCode 236: Lowest Common Ancestor of a Binary Tree' or 'Production Bug: Thread Pool Starvation in Django REST Framework'",
      "category": "Must be one of: 'LeetCode Python', 'Production Scaling & Systems', or 'Generative AI & LLMs'",
      "difficulty": "Must be one of: 'Easy', 'Medium', or 'Hard'",
      "summary": "A 1-sentence quick summary of the problem and key fix.",
      "problem_description": "Clear statement of the problem / bug. Use markdown formatting if helpful.",
      "solution_code": "Complete, correct, and readable Python code showing the optimal solution or mitigation class/function.",
      "explanation": "Markdown text. For LeetCode, provide Time/Space complexity analysis and step-by-step logic. For Production bugs, provide Root Cause Analysis (RCA) and Mitigation/Prevention guide.",
      "tags": ["List of 2-3 relevant tags, e.g. 'Binary Tree', 'RCA', 'SQL', 'FastAPI', 'Redis'"]
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.85,
            timeout=20.0
        )
        content = completion.choices[0].message.content
        new_prob = json.loads(content)
        return new_prob
    except Exception as e:
        raise RuntimeError(f"Groq API Error: {str(e)}")

