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
        url = f"https://archive.org/advancedsearch.php"
        params = {
            "q": query,
            "fl[]": "identifier,title",
            "rows": 10,
            "page": 1,
            "output": "json"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for doc in data['response']['docs']:
                identifier = doc.get('identifier')
                title = doc.get('title')
                link = f"https://archive.org/details/{identifier}"
                results.append({
                    "title": title,
                    "source": "Internet Archive",
                    "link": link
                })

        except Exception as e:
            results.append({
                "title": f"API error: {str(e)}",
                "source": "Archive.org",
                "link": "#"
            })

    return render_template("index.html", results=results, query=query)