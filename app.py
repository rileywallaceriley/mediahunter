from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

def get_spotify_token(client_id, client_secret):
    token_url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    res = requests.post(token_url, headers=headers, data=data)
    return res.json().get("access_token")

SPOTIFY_CLIENT_ID = "fa347236d6da48d6881d909b4bbd4858"
SPOTIFY_CLIENT_SECRET = "5ff148a6bf594e1fa7399007a3d03022"
YOUTUBE_API_KEY = "AIzaSyBtjRHCHffqpOqwvWNf0oxJXpcrdU4QbuQ"

JACKETT_API_URL = "https://jackett-render-dwvc.onrender.com/api/v2.0/indexers/all/results/torznab/api"
JACKETT_API_KEY = "01eg3ignc2bi4j4ovr2o2q9svfhzi6nc"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search')
def search():
    query = request.args.get('query')
    selected_sources = request.args.getlist("source")
    results = []

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # Spotify Search
    if "spotify" in selected_sources:
        try:
            token = get_spotify_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
            spotify_headers = {"Authorization": f"Bearer {token}"}
            url = f"https://api.spotify.com/v1/search?q={urllib.parse.quote(query)}&type=track,album&limit=5"
            res = requests.get(url, headers=spotify_headers)
            items = res.json().get("tracks", {}).get("items", [])
            for item in items:
                results.append({
                    "title": f"{item['name']} — {item['artists'][0]['name']}",
                    "source": "Spotify",
                    "link": item['external_urls']['spotify']
                })
        except Exception as e:
            print("Spotify error:", e)

    # YouTube Search
    if "youtube" in selected_sources:
        try:
            yt_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 5,
                "key": YOUTUBE_API_KEY
            }
            res = requests.get(yt_url, params=params)
            for item in res.json().get("items", []):
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                link = f"https://www.youtube.com/watch?v={video_id}"
                results.append({
                    "title": title,
                    "source": "YouTube",
                    "link": link
                })
        except Exception as e:
            print("YouTube error:", e)

    # Archive.org Search
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

    # Jackett Torrent Search — Debug version
    if "torrents" in selected_sources:
        try:
            url = f"{JACKETT_API_URL}?apikey={JACKETT_API_KEY}&q={urllib.parse.quote(query)}"
            res = requests.get(url, headers=headers)

            # Debug: print the raw XML response from Jackett
            print("Jackett XML preview:")
            print(res.content[:1000])  # log first 1000 characters

            soup = BeautifulSoup(res.content, "xml")
            items = soup.find_all("item")[:5]

            if not items:
                print("No torrent items found in the XML.")

            for item in items:
                title = item.find("title").text
                link = item.find("link").text
                tracker = item.find("jackettindexer").text if item.find("jackettindexer") else "Jackett"
                results.append({
                    "title": title,
                    "source": tracker,
                    "link": link
                })
        except Exception as e:
            print("Jackett error:", e)

    return render_template("index.html", results=results, query=query)