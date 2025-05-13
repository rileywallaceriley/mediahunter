from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    selected_sources = request.args.getlist("source")
    results = []

    if not query:
        return render_template("index.html", results=[], query="")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # Archive.org
    if "archive" in selected_sources:
        try:
            archive_url = "https://archive.org/advancedsearch.php"
            params = {
                "q": f"{query} AND (mediatype:(texts) OR mediatype:(audio) OR collection:(comics))",
                "fl[]": "identifier,title",
                "rows": 10,
                "page": 1,
                "output": "json"
            }
            res = requests.get(archive_url, params=params, timeout=10)
            for doc in res.json()['response']['docs']:
                results.append({
                    "title": doc.get("title"),
                    "source": "Internet Archive",
                    "link": f"https://archive.org/details/{doc.get('identifier')}"
                })
        except Exception as e:
            print("Archive error:", e)

    # YouTube via Bing
    if "youtube" in selected_sources:
        try:
            encoded = urllib.parse.quote(query + " site:youtube.com")
            bing_url = f"https://www.bing.com/search?q={encoded}"
            res = requests.get(bing_url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.select("li.b_algo h2 a")[:5]
            for a in links:
                results.append({
                    "title": a.text,
                    "source": "YouTube",
                    "link": a['href']
                })
        except Exception as e:
            print("YouTube error:", e)

    # Spotify
    if "spotify" in selected_sources:
        try:
            encoded = urllib.parse.quote(query)
            results.append({
                "title": f"Search Spotify for: {query}",
                "source": "Spotify",
                "link": f"https://open.spotify.com/search/{encoded}"
            })
        except Exception as e:
            print("Spotify error:", e)

    # 1337x.to
    if "torrents" in selected_sources:
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://1337x.to/search/{encoded}/1/"
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.select("tr")[:5]
            for row in rows:
                a = row.find("a", href=True)
                if a and "/torrent/" in a['href']:
                    title = a.text.strip()
                    page_link = "https://1337x.to" + a['href']
                    torrent_page = requests.get(page_link, headers=headers)
                    sub_soup = BeautifulSoup(torrent_page.text, "html.parser")
                    magnet = sub_soup.find("a", href=True, title="Magnet Download")
                    if magnet:
                        results.append({
                            "title": title,
                            "source": "1337x",
                            "link": magnet['href']
                        })
        except Exception as e:
            print("1337x error:", e)

    # Pirate Bay
    if "torrents" in selected_sources:
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://thepiratebay0.org/search/{encoded}/1/99/0"
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.select("div.detName a")[:5]
            for a in rows:
                parent = a.find_parent("div", class_="detName").find_next_sibling("a", title="Download this torrent using magnet")
                if parent:
                    results.append({
                        "title": a.text.strip(),
                        "source": "Pirate Bay",
                        "link": parent['href']
                    })
        except Exception as e:
            print("Pirate Bay error:", e)

    # GetComics
    if "comics" in selected_sources:
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://getcomics.org/?s={encoded}"
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            posts = soup.select("h3.post-title a")[:5]
            for a in posts:
                results.append({
                    "title": a.text.strip(),
                    "source": "GetComics",
                    "link": a['href']
                })
        except Exception as e:
            print("GetComics error:", e)

    # Comics.codes
    if "comics" in selected_sources:
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://comics.codes/?s={encoded}"
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            posts = soup.select("h2.entry-title a")[:5]
            for a in posts:
                results.append({
                    "title": a.text.strip(),
                    "source": "Comics.codes",
                    "link": a['href']
                })
        except Exception as e:
            print("Comics.codes error:", e)

    return render_template("index.html", results=results, query=query)