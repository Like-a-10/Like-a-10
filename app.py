from flask import Flask, render_template, request, redirect, url_for
from transformers import pipeline
import wikipediaapi
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize the model for custom text explanation
model = pipeline("text2text-generation", model="google/flan-t5-base")

# Initialize Wikipedia API with proper user agent
user_agent = "EducationalExplainer/1.0 (https://github.com/SahilB2k/educational-explainer; sahilb2k@github.com) python-wikipediaapi"
wiki = wikipediaapi.Wikipedia(
    user_agent=user_agent,    # Your user agent string
    language='en'            # Language specification
)

def get_wiki_content(topic):
    """Get content from Wikipedia"""
    try:
        page = wiki.page(topic)
        if page.exists():
            return page.summary
        return "Topic not found on Wikipedia"
    except Exception as e:
        return f"Error fetching topic: {str(e)}"

# ... rest of your code remains the same ...
def get_wiki_content(topic):
    """Get content from Wikipedia"""
    try:
        page = wiki.page(topic)
        if page.exists():
            return page.summary
        return "Topic not found on Wikipedia"
    except Exception as e:
        return f"Error fetching topic: {str(e)}"

def generate_explanation(text, level):
    """Generate explanation based on level with more distinct differences"""
    prompts = {
        "child": (
            "Explain this to a 10-year-old child using:\n"
            "1. Very simple words\n"
            "2. Short sentences\n"
            "3. Familiar examples from daily life\n"
            "4. No technical terms\n"
            "5. Use analogies with toys or games\n"
            "Text to explain: " + text
        ),
        "teen": (
            "Explain this to a high school student using:\n"
            "1. Moderate complexity\n"
            "2. Some basic technical terms\n"
            "3. Real-world examples\n"
            "4. Clear step-by-step explanations\n"
            "Text to explain: " + text
        ),
        "expert": (
            "Explain this at an advanced college level using:\n"
            "1. Technical terminology\n"
            "2. Detailed theoretical concepts\n"
            "3. Scientific principles\n"
            "4. Complex relationships\n"
            "5. Reference to advanced topics\n"
            "Text to explain: " + text
        )
    }
    
    try:
        # Add temperature and top_p parameters for more varied outputs
        result = model(
            prompts[level],
            max_length=300,
            min_length=100,
            do_sample=True,
            temperature=0.7,  # Add randomness (0.0 to 1.0)
            top_p=0.9,       # Nucleus sampling
            no_repeat_ngram_size=2  # Avoid repetition
        )
        
        # Post-process the explanation based on level
        explanation = result[0]['generated_text']
        
        if level == "child":
            # For child level, break into shorter paragraphs
            sentences = explanation.split('. ')
            explanation = '\n\n'.join(['. '.join(sentences[i:i+2]) for i in range(0, len(sentences), 2)])
            explanation += "\n\nDo you understand? If not, feel free to ask questions!"
            
        elif level == "teen":
            # For teen level, add learning objectives
            explanation = "Key Points to Remember:\n\n" + explanation
            
        else:  # expert
            # For expert level, keep technical format
            explanation = "Technical Analysis:\n\n" + explanation
        
        return explanation
        
    except Exception as e:
        return f"Error generating explanation: {str(e)}"

@app.route('/')
def home():
    """Homepage with selection between topic and custom text"""
    return render_template('home.html')

@app.route('/topic', methods=['GET', 'POST'])
def topic_explain():
    """Page for topic explanation"""
    if request.method == 'POST':
        topic = request.form.get('topic')
        level = request.form.get('level')
        
        if topic:
            # Get content from Wikipedia
            wiki_content = get_wiki_content(topic)
            # Generate level-appropriate explanation
            explanation = generate_explanation(wiki_content, level)
            return render_template('topic_explain.html', 
                                explanation=explanation, 
                                topic=topic,
                                level=level)
    
    return render_template('topic_explain.html')

@app.route('/text', methods=['GET', 'POST'])
def text_explain():
    """Page for custom text explanation"""
    if request.method == 'POST':
        text = request.form.get('text')
        level = request.form.get('level')
        
        if text:
            explanation = generate_explanation(text, level)
            return render_template('text_explain.html', 
                                explanation=explanation,
                                original_text=text,
                                level=level)
    
    return render_template('text_explain.html')

if __name__ == '__main__':
    app.run(debug=True)