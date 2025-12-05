import os
import json
import time
from parallel import Parallel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# API Keys
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-flash-latest')

# Configure Parallel
try:
    client = Parallel(api_key=PARALLEL_API_KEY)
except Exception as e:
    print(f"Error initializing Parallel client: {e}")
    exit(1)

CATEGORIES = [
    "self-harm",
    "suicide",
    "violence",
    "abuse",
    "overdose"
]

def analyze_severity(text):
    """Use Gemini to analyze severity of the content."""
    prompt = f"""
    Analyze the following text for safety risk severity.
    Text: "{text}"
    
    Return a JSON object with:
    - severity: "low", "medium", "high"
    - reason: short explanation
    - category: best matching category from [self-harm, suicide, violence, abuse, overdose] or "other"
    
    JSON:
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return {"severity": "unknown", "reason": str(e), "category": "unknown"}

def main():
    # Resolve paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "../web_app/src/real_world_data.json")
    backup_path = os.path.join(script_dir, "real_world_data.json")
    
    # Load existing data to implement rolling window
    real_world_data = []
    if os.path.exists(output_path):
        try:
            with open(output_path, "r") as f:
                real_world_data = json.load(f)
                print(f"Loaded {len(real_world_data)} existing examples.")
        except Exception as e:
            print(f"Error loading existing data: {e}")

    print("Starting real-world data collection...")
    
    new_items_count = 0
    target_new_items = 20 # Fetch 20 new items per run
    
    for category in CATEGORIES:
        if new_items_count >= target_new_items:
            break
            
        print(f"Searching for: {category}")
        
        queries = [
            f"site:reddit.com {category} personal story",
            f"site:twitter.com {category} help",
            f"site:instagram.com {category} awareness",
            f"personal blog about living with {category}",
            f"forum discussion {category} support"
        ]
        
        for query in queries:
            if new_items_count >= target_new_items:
                break
                
            print(f"  Querying: {query}")
            try:
                # Fetch fewer results per query since we run frequently
                response = client.beta.search(search_queries=[query], max_results=5, mode="agentic")
                
                if response.results:
                    for res in response.results:
                        if new_items_count >= target_new_items:
                            break
                            
                        title = getattr(res, 'title', 'No Title')
                        url = getattr(res, 'url', '')
                        
                        # Check for duplicates based on URL
                        if any(item['url'] == url for item in real_world_data):
                            print(f"  Skipping duplicate: {title[:30]}...")
                            continue

                        excerpts = getattr(res, 'excerpts', [])
                        if isinstance(excerpts, list):
                            content = " ".join([str(e) for e in excerpts])
                        else:
                            content = str(excerpts)
                        
                        if not content or content == "[]":
                            continue
                            
                        print(f"  Found: {title[:50]}...")
                        
                        analysis = analyze_severity(content[:500])
                        
                        new_item = {
                            "title": title,
                            "content": content[:300] + "...",
                            "url": url,
                            "original_query": query,
                            "severity": analysis.get('severity', 'unknown'),
                            "reason": analysis.get('reason', ''),
                            "detected_category": analysis.get('category', category),
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Add to beginning of list (newest first)
                        real_world_data.insert(0, new_item)
                        new_items_count += 1
                        
                else:
                    print(f"  No results found for {query}")
                    
            except Exception as e:
                print(f"  Error searching for {category}: {e}")
        
        time.sleep(1)

    # Keep only latest 100 items
    if len(real_world_data) > 100:
        real_world_data = real_world_data[:100]
        print(f"Trimmed dataset to latest 100 items.")

    # Save data
    try:
        with open(output_path, "w") as f:
            json.dump(real_world_data, f, indent=2)
        with open(backup_path, "w") as f:
            json.dump(real_world_data, f, indent=2)
        print(f"Collection complete. Saved {len(real_world_data)} items (added {new_items_count} new).")
    except Exception as e:
        print(f"Error saving data: {e}")

if __name__ == "__main__":
    main()
