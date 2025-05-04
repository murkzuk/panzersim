# export_threads.py
import os, requests, zipfile, re
from bs4 import BeautifulSoup

BASE = "https://panzersim.forumotion.com"
FORUM_PATH = "/f1-t34-vs-tiger"
OUTPUT_DIR = "threads_text"
ZIP_NAME = "threads_text.zip"

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)[:200]

def get_topics():
    topics = []
    path = FORUM_PATH
    while path:
        r = requests.get(BASE + path, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a.topictitle"):
            topics.append((a.text.strip(), BASE + a["href"]))
        nxt = soup.select_one("a[rel=next]")
        path = nxt["href"] if nxt else None
    return topics

def scrape_thread(title, url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = sanitize_filename(title) + ".txt"
    with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as f:
        page = url
        while page:
            r = requests.get(page, headers={"User-Agent":"Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            for post in soup.select("div.postbody div.content"):
                f.write(post.get_text("\n", strip=True) + "\n\n")
            nxt = soup.select_one("a[rel=next]")
            page = BASE + nxt["href"] if nxt else None

def zip_threads():
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in os.listdir(OUTPUT_DIR):
            z.write(os.path.join(OUTPUT_DIR, fn), arcname=fn)

def main():
    for title, url in get_topics():
        scrape_thread(title, url)
    zip_threads()
    print(f"Export complete: {ZIP_NAME}")

if __name__ == "__main__":
    main()
