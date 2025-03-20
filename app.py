import os
import logging
from flask import Flask, render_template, request, redirect, json
import re
from markupsafe import Markup

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Load content data
with open('content.json') as f:
    posts = json.load(f)

# Simple Markdown to HTML converter
def convert_markdown(text):
    # Convert bold text
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    
    # Convert italic text
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
    
    # Convert headers
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    # Convert ordered lists
    text = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ol>\g<0></ol>', text, flags=re.MULTILINE | re.DOTALL)
    
    # Convert images with proper path handling
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" class="content-image">', text)
    
    # Convert paragraphs - split by double newlines and wrap in <p> tags
    paragraphs = text.split('\n\n')
    for i, p in enumerate(paragraphs):
        if not (p.startswith('<h') or p.startswith('<ol') or p.startswith('<img') or p.startswith('<iframe')) and p.strip() != '':
            paragraphs[i] = f'<p>{p}</p>'
    text = '\n'.join(paragraphs)
    
    # Convert single newlines to <br>
    text = re.sub(r'(?<!\n)\n(?!\n)(?!<)(?!.*>)', '<br>', text)
    
    return text

@app.route('/')
def home():
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = next((post for post in posts if post['id'] == post_id), None)
    if not post:
        return "Post not found", 404
    
    # Convert markdown content to HTML
    html_content = convert_markdown(post['content'])
    
    # Mark as safe HTML
    html_content = Markup(html_content)
    
    return render_template('post.html', post=post, content=html_content)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
