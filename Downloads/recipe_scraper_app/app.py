from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_recipe():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
        
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Basic extraction attempt
        title = soup.find('h1')
        title_text = title.get_text().strip() if title else 'Untitled Recipe'
        
        ingredients = []
        for li in soup.find_all(['li']):
            text = li.get_text().strip()
            if 'cup' in text.lower() or 'tbsp' in text.lower() or 'tsp' in text.lower() or 'ingredient' in li.get('class', [''])[0].lower():
                ingredients.append(text)
                
        return jsonify({
            'title': title_text,
            'ingredients': ingredients[:15], # limit for safety/cleanliness
            'source': url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
