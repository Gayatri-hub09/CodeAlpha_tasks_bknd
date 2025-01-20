from flask import Flask, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy
import hashlib
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model to store the original and short URLs
class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, original_url, short_url):
        self.original_url = original_url
        self.short_url = short_url

# Initialize database
db.create_all()

# Function to generate a random short URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# Route to shorten URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form.get('url')
    if not original_url:
        return "URL is required", 400

    # Check if the URL is already shortened
    existing_mapping = URLMapping.query.filter_by(original_url=original_url).first()
    if existing_mapping:
        return f"Shortened URL: {request.host_url}{existing_mapping.short_url}"

    # Generate a unique short URL
    short_url = generate_short_url()
    
    # Save to the database
    new_mapping = URLMapping(original_url=original_url, short_url=short_url)
    db.session.add(new_mapping)
    db.session.commit()

    return f"Shortened URL: {request.host_url}{short_url}"

# Route to handle redirection
@app.route('/<short_url>')
def redirect_to_url(short_url):
    # Look up the original URL in the database
    mapping = URLMapping.query.filter_by(short_url=short_url).first()
    if mapping:
        return redirect(mapping.original_url)
    else:
        return "Short URL not found", 404

# Route to render the home page with a form to shorten URLs
@app.route('/')
def home():
    return render_template_string('''
    <form method="POST" action="/shorten">
        <label for="url">Enter URL to shorten:</label>
        <input type="text" id="url" name="url" required>
        <button type="submit">Shorten URL</button>
    </form>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
