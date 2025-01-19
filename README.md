# Universal Review Extractor API

The Universal Review Extractor API is a web application that dynamically extracts reviews from any product page URL. It uses browser automation and machine learning to identify CSS selectors for reviews and retrieve review data.

# Features
Dynamic Review Extraction: Automatically identifies CSS selectors for reviews using a machine learning model (Hugging Face pipeline).
Pagination Handling: Supports multiple pages of reviews to fetch complete review data.
User-Friendly API: Provides a simple API endpoint to fetch reviews from any product URL.
Fallback Mechanism: Default CSS selectors are used if the model fails to generate selectors.

# Technologies Used
Backend: Flask
Web Scraping: Playwright, BeautifulSoup
Machine Learning: Hugging Face transformers pipeline
Programming Language: Python

# Endpoints
## 1. Home
URL: /
Method: GET
Description: Displays a welcome message.
## 2. Reviews Extraction
URL: /api/reviews
Method: GET
Query Parameter:
url (required): The product page URL to extract reviews from.
Response:
reviews_count: Total number of reviews extracted.
reviews: A list of review details (title, body, rating, reviewer).

# Future Enhancements
Add authentication for API usage.
Build a detailed frontend interface for user-friendly interactions.
Support additional ML models for improved CSS selector generation.

