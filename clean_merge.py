import os
import json
from bs4 import BeautifulSoup

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"

def clean_html(html):
    """Convert HTML to plain text using BeautifulSoup."""
    return BeautifulSoup(html, "html.parser").get_text().strip()

def load_all_json_files(folder):
    """Recursively load all JSON files from folder and extract cleaned text and source URLs."""
    chunks = []
    skipped = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)

                        # Case 1: plain list of posts
                        if isinstance(data, list):
                            posts = data

                        # Case 2: Discourse structure with post_stream.posts
                        elif isinstance(data, dict) and "post_stream" in data:
                            posts = data["post_stream"].get("posts", [])

                        else:
                            print(f"⚠️ Skipped (unexpected structure): {path}")
                            skipped += 1
                            continue

                        for post in posts:
                            raw = post.get("cooked") or post.get("content") or ""
                            text = clean_html(raw)
                            post_url = BASE_URL + post.get("post_url", "")
                            if text:
                                chunks.append({"text": text, "url": post_url})

                except Exception as e:
                    print(f"❌ Error reading {path}: {e}")
                    skipped += 1
    print(f"✅ Processed {len(chunks)} chunks. Skipped {skipped} files.")
    return chunks

if __name__ == "__main__":
    INPUT_FOLDER = input("Enter your scraped data folder path: ").strip()
    output_file = "cleaned_chunks.json"

    chunks = load_all_json_files(INPUT_FOLDER)

    with open(output_file, "w") as f:
        json.dump(chunks, f, indent=2)

    print(f"📄 Saved cleaned data to {output_file}")
