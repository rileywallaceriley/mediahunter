from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    results = []

    # Internet Archive Search
    ia_url = f"https://archive.org/advancedsearch.php?q={query}&fl[]=identifier,title&output=json"
    ia_res = requests.get(ia_url).json()
    for item in ia_res['response']['docs'][:5]:
        identifier = item.get('identifier')
        title = item.get('title')
        link = f"https://archive.org/details/{identifier}"
        results.append({'title': title, 'source': 'Internet Archive', 'link': link})

    # YouTube Mobile Search via DuckDuckGo
    yt_url = f"https://html.duckduckgo.com/html/?q={query}+site:youtube.com"
    yt_res = requests.get(yt_url).text
    soup = BeautifulSoup(yt_res, 'html.parser')
    links = soup.select('a.result__a[href*="youtube.com"]')[:5]
    for a in links:
        title = a.text
        link = a['href']
        results.append({'title': title, 'source': 'YouTube', 'link': link})

    return render_template('index.html', results=results, query=query)
