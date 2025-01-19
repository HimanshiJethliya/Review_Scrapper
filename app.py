from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from transformers import pipeline

app = Flask(__name__)

# Load Hugging Face model for text generation
generator = pipeline("text-generation", model="distilgpt2")

def identify_css_selectors_with_llm(html_content):
    """
    Use a free Hugging Face LLM to identify CSS selectors for reviews.
    """
    try:
        prompt = f"""
        Analyze the following HTML content and identify the CSS selectors for reviews, review titles, review body text, ratings, and reviewer names.
        Provide the CSS selectors in the format:
        {{
            'review': '<CSS selector for review container>',
            'title': '<CSS selector for review title>',
            'body': '<CSS selector for review body>',
            'rating': '<CSS selector for review rating>',
            'reviewer': '<CSS selector for reviewer name>'
        }}
        HTML Content: {html_content[:1000]}  # Limit to 1000 characters to keep it concise
        """
        response = generator(prompt, max_length=150, num_return_sequences=1)
        print("LLM Output:", response[0]['generated_text'])
        selectors = eval(response[0]['generated_text'])
        return selectors
    except Exception as e:
        print(f"Error with LLM: {e}")
        return None

def identify_css_selectors_fallback():
    return {
        'review': 'div.target-review-class',
        'title': 'h3.target-title-class',
        'body': 'p.target-body-class',
        'rating': 'span.target-rating-class',
        'reviewer': 'span.target-reviewer-class'
    }


def get_reviews_from_page(url):
    """
    Extract reviews from the provided URL using Playwright for dynamic rendering.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        page.goto(url)
        
        # Wait for the page to load completely
        page.wait_for_timeout(5000)  # Adjust if necessary
        
        # Get the HTML content of the page
        page_html = page.content()
        print("Page HTML Loaded:", page_html[:500])  # Debug: Check loaded HTML

        # Use LLM to identify CSS selectors
        selectors = identify_css_selectors_with_llm(page_html)
        print("Generated Selectors:", selectors)  # Debug: Check generated selectors
        
        # Fallback to default selectors if LLM fails
        if not selectors:
            selectors = identify_css_selectors_fallback()
        
        soup = BeautifulSoup(page_html, 'html.parser')
        reviews = []
        review_elements = soup.select(selectors['review'])
        print("Review Elements Found:", len(review_elements))  # Debug: Check number of review elements
        
        for review in review_elements:
            try:
                print("Current Review HTML:", review)  # Debug: Check each review HTML
                title = review.select_one(selectors['title'])
                body = review.select_one(selectors['body'])
                rating = review.select_one(selectors['rating'])
                reviewer = review.select_one(selectors['reviewer'])
                
                reviews.append({
                    'title': title.text.strip() if title else None,
                    'body': body.text.strip() if body else None,
                    'rating': rating.text.strip() if rating else None,
                    'reviewer': reviewer.text.strip() if reviewer else None
                })
                next_page = page.query_selector('a.next-page')  # Replace with actual "next page" selector
                print("Next Page Found:", bool(next_page))  # Debug: Check if "next page" is found
                 
                if next_page:
                    print("Clicking next page...")
                    next_page.click()
                    page.wait_for_timeout(3000)  # Wait for the next page to load
                else:
                    print("No next page found. Exiting pagination.")
                    break      
            except Exception as e:
                print(f"Error extracting review details: {e}")
                continue
        
        browser.close()
        return reviews


@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Universal Review Extractor API!"

@app.route("/favicon.ico")
def favicon():
    return '', 204

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400

    try:
        reviews = get_reviews_from_page(url)
        return jsonify({
            'reviews_count': len(reviews),
            'reviews': reviews
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
