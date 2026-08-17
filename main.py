import asyncio
import time
import feedparser
import httpx
import os
import json
from datetime import datetime
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

SOURCES = [
    # 1. General News
    {"category": "general", "name": "ENA", "url": "https://www.ena.et/web/eng/rss"},
    {"category": "general", "name": "Addis Standard", "url": "https://addisstandard.com/feed/"},
    {"category": "general", "name": "BBC News", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"category": "general", "name": "Reuters", "url": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best"},

    # 2. Sports
    {"category": "sports", "name": "Soccer Ethiopia", "url": "https://soccerethiopia.net/feed/"},
    {"category": "sports", "name": "CAF Online", "url": "https://news.google.com/rss/search?q=site:cafonline.com"},
    {"category": "sports", "name": "BBC Sport Africa", "url": "https://feeds.bbci.co.uk/sport/africa/rss.xml"},

    # 3. Tech & Innovation
    {"category": "tech", "name": "Shega.co", "url": "https://shega.co/feed/"},
    {"category": "tech", "name": "TechCabal", "url": "https://techcabal.com/feed/"},
    {"category": "tech", "name": "TechCrunch", "url": "https://techcrunch.com/feed/"},

    # 4. Business & Economy
    {"category": "business", "name": "Addis Fortune", "url": "https://addisfortune.news/feed/"},
    {"category": "business", "name": "Business Daily Africa", "url": "https://www.businessdailyafrica.com/service/rss/bda/2046/feed.rss"},

    # 5. Lifestyle & Entertainment
    {"category": "lifestyle", "name": "LinkUp Addis", "url": "https://rsshub.app/telegram/channel/linkupaddis"},
    {"category": "lifestyle", "name": "BellaNaija", "url": "https://www.bellanaija.com/feed/"},

    # 6. Odd & Offbeat News
    {"category": "oddities", "name": "Oddity Central", "url": "https://www.odditycentral.com/feed"},
    {"category": "oddities", "name": "Reddit r/NotTheOnion", "url": "https://www.reddit.com/r/nottheonion/top/.rss?sort=top&t=day"}
]

async def fetch_single_feed(http_client, source):
    try:
        response = await http_client.get(source["url"], timeout=5.0)
        feed = feedparser.parse(response.content)
        items = []
        for entry in feed.entries[:2]:
            items.append({
                "category": source["category"],
                "source": source["name"],
                "headline": getattr(entry, 'title', ''),
                "context": getattr(entry, 'summary', '')
            })
        return items
    except Exception:
        return []

async def fetch_all_feeds():
    async with httpx.AsyncClient(follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as http_client:
        tasks = [fetch_single_feed(http_client, src) for src in SOURCES]
        results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]

def generate_tri_lingual_articles(raw_items):
    combined_raw_text = json.dumps(raw_items, ensure_ascii=False, indent=2)
    
    prompt = f"""
You are the Chief Editor for a tri-lingual news platform.
Select the top 1 news event for EACH category (general, sports, tech, business, lifestyle, oddities) from the raw data below:

{combined_raw_text}

For each selected story, write complete long-form news reports in Amharic, Afaan Oromoo, and English.
Return structured output adhering strictly to the JSON Schema provided.
"""

    response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "category": {"type": "STRING"},
                "source_name": {"type": "STRING"},
                "amharic": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING"},
                        "content": {"type": "STRING"}
                    },
                    "required": ["title", "content"]
                },
                "afaan_oromoo": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING"},
                        "content": {"type": "STRING"}
                    },
                    "required": ["title", "content"]
                },
                "english": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING"},
                        "content": {"type": "STRING"}
                    },
                    "required": ["title", "content"]
                }
            },
            "required": ["category", "source_name", "amharic", "afaan_oromoo", "english"]
        }
    }

    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]

    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"⚠️ Generation failed using {model}: {e}")
            time.sleep(2)

    return []

def save_markdown_posts(articles):
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H%M%S")

    for idx, article in enumerate(articles):
        cat = article["category"]
        source = article["source_name"]

        # 1. Save Amharic Article
        am_dir = "_posts/am"
        os.makedirs(am_dir, exist_ok=True)
        am_file = f"{am_dir}/{today}-{cat}-{timestamp}-{idx}.md"
        am_meta = f"---\nlayout: post\ntitle: \"{article['amharic']['title']}\"\ncategories: {cat}\nlang: am\nsource: \"{source}\"\n---\n\n{article['amharic']['content']}\n\n<p><strong>📌 ምንጭ:</strong> {source}</p>"
        with open(am_file, "w", encoding="utf-8") as f:
            f.write(am_meta)

        # 2. Save Afaan Oromoo Article
        om_dir = "_posts/om"
        os.makedirs(om_dir, exist_ok=True)
        om_file = f"{om_dir}/{today}-{cat}-{timestamp}-{idx}.md"
        om_meta = f"---\nlayout: post\ntitle: \"{article['afaan_oromoo']['title']}\"\ncategories: {cat}\nlang: om\nsource: \"{source}\"\n---\n\n{article['afaan_oromoo']['content']}\n\n<p><strong>📌 Madda:</strong> {source}</p>"
        with open(om_file, "w", encoding="utf-8") as f:
            f.write(om_meta)

        # 3. Save English Article
        en_dir = "_posts/en"
        os.makedirs(en_dir, exist_ok=True)
        en_file = f"{en_dir}/{today}-{cat}-{timestamp}-{idx}.md"
        en_meta = f"---\nlayout: post\ntitle: \"{article['english']['title']}\"\ncategories: {cat}\nlang: en\nsource: \"{source}\"\n---\n\n{article['english']['content']}\n\n<p><strong>📌 Source:</strong> {source}</p>"
        with open(en_file, "w", encoding="utf-8") as f:
            f.write(en_meta)

    print(f"✅ Generated and saved {len(articles) * 3} post files!")

async def main():
    raw_news = await fetch_all_feeds()
    if not raw_news:
        print("❌ No raw news items retrieved.")
        return
    
    articles = generate_tri_lingual_articles(raw_news)
    if articles:
        save_markdown_posts(articles)
    else:
        print("❌ Generation failed or returned empty payload.")

if __name__ == "__main__":
    asyncio.run(main())
