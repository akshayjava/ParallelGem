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
    real_world_data = []
    
    print("Starting real-world data collection...")
    
    for category in CATEGORIES:
        print(f"Searching for: {category}")
        
        # Search for social media and personal stories as requested.
        # We iterate through a few variations to get diverse sources.
        queries = [
            f"site:reddit.com {category} personal story",
            f"site:twitter.com {category} help",
            f"site:instagram.com {category} awareness",
            f"personal blog about living with {category}",
            f"forum discussion {category} support"
        ]
        
        for query in queries:
            if len(real_world_data) >= 500:
                break
                
            print(f"  Querying: {query}")
            try:
                # Using the beta search method with correct arguments.
                # Aiming for 500 total items across 25 queries (5 cats * 5 templates) -> 20 per query
                response = client.beta.search(search_queries=[query], max_results=20, mode="agentic")
                
                if response.results:
                    for res in response.results:
                        if len(real_world_data) >= 500:
                            break
                            
                        # Access attributes of the result object
                        title = getattr(res, 'title', 'No Title')
                        url = getattr(res, 'url', '')
                        # Content is in 'excerpts'
                        excerpts = getattr(res, 'excerpts', [])
                        if isinstance(excerpts, list):
                            content = " ".join([str(e) for e in excerpts])
                        else:
                            content = str(excerpts)
                        
                        if not content or content == "[]":
                            print(f"  [DEBUG] Content/Excerpts missing for {title}")
                            continue
                            
                        print(f"  Found: {title[:50]}...")
                        
                        # Analyze severity
                        analysis = analyze_severity(content[:500]) # Analyze first 500 chars
                        
                        real_world_data.append({
                            "title": title,
                            "content": content[:300] + "...", # Truncate for display
                            "url": url,
                            "original_query": query,
                            "severity": analysis.get('severity', 'unknown'),
                            "reason": analysis.get('reason', ''),
                            "detected_category": analysis.get('category', category),
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        if len(real_world_data) % 10 == 0:
                            print(f"  Collected {len(real_world_data)} examples so far...")
                else:
                    print(f"  No results found for {query}")
                    
            except Exception as e:
                print(f"  Error searching for {category}: {e}")
                # If method name is wrong, we might see it here.
        
        if len(real_world_data) >= 500:
            print("Reached 500 examples limit.")
            break
        
        time.sleep(1)

    # Save data
    output_path = "real_world_data.json"
    with open(output_path, "w") as f:
        json.dump(real_world_data, f, indent=2)
        
    print(f"Collection complete. Saved {len(real_world_data)} items to {output_path}")

if __name__ == "__main__":
    main()
