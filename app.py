from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    results = []

    if query:
        try:
            url = f"https://archive.org/advancedsearch.php?q={query}&fl[]=identifier,title&output=json"
            response = requests.get(url)
            data = response.json()

            for item in data['response']['docs'][:5]:
                identifier = item.get('identifier')
                title = item.get('title')
                link = f"https://archive.org/details/{identifier}"
                results.append({'title': title, 'source': 'Internet Archive', 'link': link})
        except Exception as e:
            results.append({'title': 'Error fetching results', 'source': 'Internet Archive', 'link': '#'})

    return render_template('index.html', results=results, query=query)