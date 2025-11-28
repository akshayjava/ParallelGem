import os
import json
import requests
import google.generativeai as genai
import time

# API Keys
PARALLEL_API_KEY = "Hon7rLk0I2Gc56SvYnszXN5OW710jxb0kXujnmKt"
GEMINI_API_KEY = "AIzaSyDbP7ZYEreKdUCUjW1Jbk4fCrJgBmyUwSY"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
# Using confirmed model name from list
model = genai.GenerativeModel('models/gemini-flash-latest')

CATEGORIES = [
    "self-harm",
    "suicide",
    "violence",
    "abuse",
    "overdose"
]

def search_parallel(query):
    """Search Parallel Web for context."""
    # Parallel API integration paused due to endpoint/key issues.
    # Returning empty context to proceed with synthetic generation.
    print(f"  [Skipping Parallel Search for '{query}' - API configuration pending]")
    return None

def generate_synthetic_data(category, context_results):
    """Generate synthetic posts using Gemini based on context."""
    
    context_text = ""
    if context_results and 'results' in context_results:
        for res in context_results['results']:
            context_text += f"- {res.get('title', '')}: {res.get('content', '')[:200]}...\n"
            
    prompt = f"""
    You are helping to build a safety benchmark dataset to train AI models to DETECT and PREVENT self-harm, violence, and abuse.
    
    Please generate 5 realistic but SYNTHETIC social media posts or short text messages related to the category: "{category}".
    
    The posts should be realistic examples of what a user might write if they were struggling with this issue, so that we can train models to flag them.
    
    Format the output as a JSON list of strings.
    Example: ["I feel so alone and I don't know what to do anymore.", "I'm scared of him when he drinks."]
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean up markdown code blocks if present
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"Error generating data for {category}: {e}")
        return []

def main():
    dataset = []
    
    print("Starting dataset generation...")
    
    for category in CATEGORIES:
        print(f"Processing category: {category}")
        
        # 1. Get context from Parallel (Skipped for now)
        search_query = f"signs of {category} help support stories"
        parallel_results = search_parallel(search_query)
        
        # 2. Generate synthetic data
        print(f"  Generating synthetic data with Gemini...")
        posts = generate_synthetic_data(category, parallel_results)
        
        for post in posts:
            dataset.append({
                "text": post,
                "label": category,
                "is_sensitive": True,
                "source": "synthetic_gemini"
            })
            
        # Add safe examples
        safe_prompt = f"Generate 2 neutral/positive social media posts that might use similar keywords to '{category}' but are NOT sensitive/harmful. Return JSON list of strings."
        try:
            safe_resp = model.generate_content(safe_prompt)
            safe_text = safe_resp.text.replace("```json", "").replace("```", "").strip()
            try:
                safe_posts = json.loads(safe_text)
            except:
                safe_posts = []
                
            for post in safe_posts:
                dataset.append({
                    "text": post,
                    "label": "safe",
                    "related_category": category,
                    "is_sensitive": False,
                    "source": "synthetic_gemini_safe_contrast"
                })
        except Exception as e:
            print(f"Error generating safe data: {e}")

        time.sleep(1) 

    # Save dataset
    output_path = "benchmark.json"
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Dataset generated with {len(dataset)} items. Saved to {output_path}")

if __name__ == "__main__":
    main()
