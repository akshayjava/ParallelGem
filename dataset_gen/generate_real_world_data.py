import os
import json
import time
import random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 2.0 Flash for high-quality synthetic generation
model = genai.GenerativeModel('models/gemini-2.0-flash-exp')

CATEGORIES = ["self-harm", "suicide", "violence", "abuse", "overdose"]

def generate_synthetic_post(category):
    """Generate a realistic social media post using Gemini."""
    prompt = f"""
    Generate a realistic, short social media post or forum comment (max 300 chars) that discusses {category}.
    It should sound authentic, like a real person sharing a personal story, seeking help, or raising awareness.
    Do NOT include hashtags.
    """
    retries = 3
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                wait_time = (attempt + 1) * 60
                print(f"Rate limit hit. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error generating post: {e}")
                return None
    return None

def analyze_severity(text):
    """Analyze severity using Gemini."""
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
    
    # Load existing data
    real_world_data = []
    if os.path.exists(output_path):
        try:
            with open(output_path, "r") as f:
                real_world_data = json.load(f)
                print(f"Loaded {len(real_world_data)} existing examples.")
        except Exception as e:
            print(f"Error loading existing data: {e}")

    print("Starting synthetic data generation using Gemini 2.0 Flash Exp...")
    
    new_items_count = 0
    target_new_items = 10 # Generate 10 new items per run
    
    for _ in range(target_new_items):
        category = random.choice(CATEGORIES)
        print(f"Generating post for: {category}")
        
        content = generate_synthetic_post(category)
        if not content:
            continue
            
        analysis = analyze_severity(content)
        
        new_item = {
            "title": f"User Story: {category.title()}",
            "content": content,
            "url": "https://example.com/synthetic-post", 
            "original_query": "synthetic_generation",
            "severity": analysis.get('severity', 'medium'),
            "reason": analysis.get('reason', 'Synthetic generation'),
            "detected_category": analysis.get('category', category),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add to beginning of list (newest first)
        real_world_data.insert(0, new_item)
        new_items_count += 1
        
        print("Waiting 60s to respect API rate limits...")
        time.sleep(60) # Increased to 60s to handle rate limits

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
