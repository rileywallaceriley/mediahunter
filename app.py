from flask import Flask, render_template, request
import requests
import urllib.parse

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    results = []

    if query:
        encoded_query = urllib.parse.quote(query)
        url = f"https://archive.org/advancedsearch.php?q={encoded_query}&fl[]=identifier,title&rows=10&page=1&output=json"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data['response']['docs']:
                identifier = item.get('identifier')
                title = item.get('title')
                link = f"https://archive.org/details/{identifier}"
                results.append({'title': title, 'source': 'Internet Archive', 'link': link})

        except Exception as e:
            results.append({'title': f'Error: {str(e)}', 'source': 'Archive.org', 'link': '#'})

    return render_template('index.html', results=results, query=query)