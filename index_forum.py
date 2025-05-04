import requests
from bs4 import BeautifulSoup

BASE = "https://panzersim.forumotion.com"
path = "/f1-t34-vs-tiger"
topics = []

while path:
    r = requests.get(BASE+path, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    # grab each thread link
    for a in soup.select("a.topictitle"):
        title = a.text.strip().replace('"', '""')
        href  = a["href"]
        url   = href if href.startswith("http") else BASE+href
        topics.append((title,url))

    # next page?
    nxt = soup.select_one("a[rel=next]")
    path = nxt["href"] if nxt else None

# write CSV
with open("forum_topics.csv","w",encoding="utf-8") as f:
    f.write('Title,URL\n')
    for t,u in topics:
        f.write(f'"{t}",{u}\n')

print(f"Done: found {len(topics)} topics")
