def generate_tri_lingual_articles(raw_items):
    combined_raw_text = json.dumps(raw_items, ensure_ascii=False, indent=2)
    
    prompt = f"""
You are the Chief Editor for an automated international news blog.
Below is a raw list of news items collected from global and local sources across 6 categories:

{combined_raw_text}

TASK:
Select the top 1 most important story for EACH of the 6 categories (general, sports, tech, business, lifestyle, oddities).
For EACH selected story, write complete long-form blog posts in THREE languages: Amharic (AM), Afaan Oromoo (OM), and English (EN).

Return ONLY a valid JSON array of objects without backticks or Markdown tags. Format exact schema:

[
  {{
    "category": "general",
    "source_name": "Source Name",
    "amharic": {{
      "title": "Title in Amharic",
      "content": "<p>Paragraph 1...</p><p>Paragraph 2...</p>"
    }},
    "afaan_oromoo": {{
      "title": "Title in Afaan Oromoo",
      "content": "<p>Paragraph 1...</p><p>Paragraph 2...</p>"
    }},
    "english": {{
      "title": "Title in English",
      "content": "<p>Paragraph 1...</p><p>Paragraph 2...</p>"
    }}
  }}
]
"""

    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]

    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            raw_response = response.text.strip()
            
            # Clean Markdown formatting wrappers if present
            if raw_response.startswith("```"):
                raw_response = raw_response.split("```")[1]
                if raw_response.startswith("json"):
                    raw_response = raw_response[4:]
            
            clean_json = raw_response.strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"⚠️ Generation attempt with {model} failed: {e}")
            time.sleep(2)

    print("❌ All model generation attempts failed.")
    return []
