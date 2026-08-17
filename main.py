import asyncio
import time
import feedparser
import httpx
import os
import json
from datetime import datetime
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

SOURCES = [
    # 1. General News
    {"category": "general", "name": "ENA", "url": "https://www.ena.et/web/eng/rss"},
    {"category": "general", "name": "Addis Standard", "url": "https://addisstandard.com/feed/"},
    {"category": "general", "name": "BBC News", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"category": "general", "name": "Reuters", "url": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best"},
    {"category": "general", "name": "FBC", "url": "https://rsshub.app/telegram/channel/fana_broadcast"},

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
        response = await http_client.get(source["url"], timeout=4.5)
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
You are the Chief Editor for an automated international news blog.
Below is a raw list of news items collected from global and local sources across 6 categories:

{combined_raw_text}

TASK:
Select the top 1 most important story for EACH of the 6 categories (general, sports, tech, business, lifestyle, oddities).
For EACH selected story, write complete long-form blog posts in THREE languages: Amharic (AM), Afaan Oromoo (OM), and English (EN).

Return ONLY a strict JSON array of objects with no Markdown backticks or surrounding text. Format exact schema:

[
  {{
    "category": "general|sports|tech|business|lifestyle|oddities",
    "source_name": "Name of Source",
    "amharic": {{
      "title": "Amharic Blog Title",
      "content": "<p>Detailed paragraph 1 in Amharic...</p><p>Detailed paragraph 2 in Amharic...</p>"
    }},
    "afaan_oromoo": {{
      "title": "Afaan Oromoo Blog Title",
      "content": "<p>Detailed paragraph 1 in Afaan Oromoo...</p><p>Detailed paragraph 2 in Afaan Oromoo...</p>"
    }},
    "english": {{
      "title": "English Blog Title",
      "content": "<p>Detailed paragraph 1 in English...</p><p>Detailed paragraph 2 in English...</p>"
    }}
  }}
]
"""

    models_to_try = ["gemini-3.7-flash", "gemini-3.6-flash"]

    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            clean_json = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Error with {model}: {e}")
            time.sleep(1)

    return []

def save_markdown_posts(articles):
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    for idx, article in enumerate(articles):
        cat = article["category"]
        source = article["source_name"]

        # 1. Save Amharic Post
        am_dir = "_posts/am"
        os.makedirs(am_dir, exist_ok=True)
        am_file = f"{am_dir}/{today}-{cat}-{timestamp}-{idx}.md"
        am_meta = f"---\nlayout: post\ntitle: \"{article['amharic']['title']}\"\ncategories: {cat}\nlang: am\nsource: \"{source}\"\n---\n\n{article['amharic']['content']}\n\n<p><strong>📌 ምንጭ:</strong> {source}</p>"
        with open(am_file, "w", encoding="utf-8") as f:
            f.write(am_meta)

        # 2. Save Afaan Oromoo Post
        om_dir = "_posts/om"
        os.makedirs(om_dir, exist_ok=True)
        om_file = f"{om_dir}/{today}-{cat}-{timestamp}-{idx}.md"
        om_meta = f"---\nlayout: post\ntitle: \"{article['afaan_oromoo']['title']}\"\ncategories: {cat}\nlang: om\nsource: \"{source}\"\n---\n\n{article['afaan_oromoo']['content']}\n\n<p><strong>📌 Madda:</strong> {source}</p>"
        with open(om_file, "w", encoding="utf-8") as f:
            f.write(om_meta)

        # 3. Save English Post
        en_dir = "_posts/en"
        os.makedirs(en_dir, exist_ok=True)
        en_file = f"{en_dir}/{today}-{cat}-{timestamp}-{idx}.md"
        en_meta = f"---\nlayout: post\ntitle: \"{article['english']['title']}\"\ncategories: {cat}\nlang: en\nsource: \"{source}\"\n---\n\n{article['english']['content']}\n\n<p><strong>📌 Source:</strong> {source}</p>"
        with open(en_file, "w", encoding="utf-8") as f:
            f.write(en_meta)

    print(f"✅ Saved {len(articles) * 3} multi-lingual blog post files!")

async def main():
    raw_news = await fetch_all_feeds()
    if not raw_news:
        return
    
    articles = generate_tri_lingual_articles(raw_news)
    if articles:
        save_markdown_posts(articles)

if __name__ == "__main__":
    asyncio.run(main())
