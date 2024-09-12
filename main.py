from flask import Flask, render_template, request, jsonify
from langchain_groq import ChatGroq
import logging
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize ChatGroq client
client = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name='mixtral-8x7b-32768'
)

# Load custom styles
with open('styles.json', 'r') as f:
    styles = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', styles=styles)

@app.route('/generate', methods=['POST'])
def generate_blog():
    try:
        data = request.json
        topic = data.get('topic')
        style = data.get('style')
        blog_type = data.get('type')

        # Generate content
        content = generate_content(topic, style, blog_type)

        # Apply terminology if provided
        # You may want to add functionality to process custom terminology here
        content = apply_terminology(content)
        
        # Optimize for SEO
        content, meta = optimize_seo(content)
        
        return jsonify({
            'content': content,
            'meta_description': meta['description'],
            'title': meta['title']
        })
    except Exception as e:
        logging.error(f"Error generating blog: {str(e)}")
        return jsonify({'error': 'An error occurred while generating the blog'}), 500

def generate_content(topic, style, blog_type):
    prompt = f"""
    Task: Write a {style} {blog_type} blog post about {topic}.
    """
    try:
        # Use the invoke method of the ChatGroq client
        response = client.invoke(prompt)
        
        # Log the response to understand its structure
        logging.info(f"Response: {response}")

        if isinstance(response, dict) and 'content' in response:
            content = response['content']
        else:
            # Adjust this line based on the actual response structure if it's different
            content = response['content'].strip()

        return content
    except Exception as e:
        logging.error(f"Error in content generation: {str(e)}")
        raise

def apply_terminology(content):
    # Add functionality to apply custom terminology here if needed
    return content

def optimize_seo(content):
    from collections import Counter
    import re

    words = re.findall(r'\w+', content.lower())
    word_count = Counter(words)
    top_keywords = [word for word, count in word_count.most_common(10) if len(word) > 5]
    
    meta_description = f"Discover insights on {', '.join(top_keywords[:3])} in this comprehensive {top_keywords[0]} guide."
    title = f"{top_keywords[0].capitalize()}: A Deep Dive into {' and '.join(top_keywords[1:3]).capitalize()}"

    return content, {'description': meta_description, 'title': title}

if __name__ == '__main__':
    app.run(debug=True)
