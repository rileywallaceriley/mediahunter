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
JACKETT_API_KEY = "ha4czkrot1v1v0qblrlk0lwem58iyigw"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search')
def search():
    query = request.args.get('query')
    selected_sources = request.args.getlist("source")
    selected_categories = request.args.getlist("cat")
    torrent_limit = request.args.get("limit", "5")
    yt_limit = request.args.get("yt_limit", "5")
    sp_limit = request.args.get("sp_limit", "5")
    results = []

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    if "spotify" in selected_sources:
        try:
            token = get_spotify_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
            spotify_headers = {"Authorization": f"Bearer {token}"}
            limit_val = 50 if sp_limit == "all" else int(sp_limit)
            url = f"https://api.spotify.com/v1/search?q={urllib.parse.quote(query)}&type=track,album&limit={limit_val}"
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

    if "youtube" in selected_sources:
        try:
            yt_url = "https://www.googleapis.com/youtube/v3/search"
            max_val = 50 if yt_limit == "all" else int(yt_limit)
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": max_val,
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

    if "torrents" in selected_sources:
        try:
            category_param = ",".join(selected_categories) if selected_categories else None
            limit_val = None if torrent_limit == "all" else int(torrent_limit)
            url = f"{JACKETT_API_URL}?apikey={JACKETT_API_KEY}&q={urllib.parse.quote(query)}"
            if category_param:
                url += f"&cat={category_param}"
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.content, "xml")
            items = soup.find_all("item")
            if limit_val:
                items = items[:limit_val]
            for item in items:
                title = item.find("title").text
                public_link = item.find("comments").text if item.find("comments") else item.find("link").text
                magnet_link = item.find("link").text if "magnet:?" in item.find("link").text else None
                tracker = item.find("jackettindexer").text if item.find("jackettindexer") else "Jackett"
                results.append({
                    "title": title,
                    "source": tracker,
                    "link": public_link,
                    "magnet": magnet_link
                })
        except Exception as e:
            print("Jackett error:", e)

    return render_template("index.html", results=results, query=query)