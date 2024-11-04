# Sainsbury's Product Scraper

This is a comprehensive data collection system that I designed to extract and organize detailed nutrition information of products listed on the [Sainsbury's online shop](https://www.sainsburys.co.uk/). Sainsbury's is one of the largest supermarket chains in the United Kingdom. I made this scraping solution modular to handle the complexities of the target page. It handles product hierarchies, detailed product attributes, and nutritional information, storing data in both structured database format and JSON for flexible analysis and usage.

## Project Background

The main objective for this project was to crawl the online shop and extract nutrition details for products listed in the Meat & Fish zone. 

The idea for this project came from a book by Gábor László Hajba titled ["Website Scraping with Python Using BeautifulSoup and Scrapy"](https://link.springer.com/book/10.1007/978-1-4842-3925-4). Reading the book was hard at first because the information is dated, so I decided to dig into the project to take on the challenge by the horns. 

Notably, this project doesn't use Scrapy yet but I will repeat the data extraction later after I have made myself comfortable with the library.

## Project Structure

This project consists of four Python scripts working together in sequence:

1. `extract_categories.py`
  * Connects to Sainsbury's API (I chose to target the backend API because it made it easier to obtain the product categories in the format that I wanted).
  * Extracts the category hierarchy
  * Focuses on the Meat & Fish section
  * Generates `meat_fish_categories.json`

2. `extract_products.py`
  * Uses the generated categories file
  * Collects product listings from each category
  * Handles pagination
  * Creates `all_products.json`

3. `extract_product_details_db.py`
  * Processes URLs from the products file
  * Extracts detailed product information including nutrition data
  * Stores information in SQLite database

4. `extract_product_details_json.py`
  * Alternative to the DB version
  * Same extraction capabilities
  * Stores data in JSON format
  * Creates `processed_products.json`

### Data Flow
Categories API → `meat_fish_categories.json` → `all_products.json` → Detailed Product Data (DB/JSON)

### System Architecture

```mermaid
flowchart TD
    subgraph Data Collection Flow
        A[extract_categories.py] -->|Generates| B[meat_fish_categories.json]
        B -->|Input for| C[extract_products.py]
        C -->|Generates| D[all_products.json]
        D -->|Input for| E1[extract_product_details_db.py]
        D -->|Input for| E2[extract_product_details_json.py]
    end

    subgraph Storage Options
        E1 -->|Stores in| F1[(SQLite Database)]
        E2 -->|Stores in| F2[processed_products.json]
    end

    subgraph Key Features
        G1[Pagination Handling]
        G2[Rate Limiting]
        G3[Error Recovery]
        G4[Progress Tracking]
        G5[Data Cleaning]
    end

## Final Thoughts

This project was incredibly enriching, although it took many days of trial and error to get right. The journey taught me several valuable lessons in web scraping and API interaction:

### Challenge 1: Category Extraction
Initially, I attempted to use graph algorithms (Depth-First Search and Breadth-First Search) to traverse the website's category structure. While these are powerful algorithms, they couldn't yield the product categories in the structured manner I needed. This led me to explore the backend API, accessible through the Network tab in the browser's Developer Tools, which provided a much cleaner and more reliable solution.

### Challenge 2: Server Etiquette
The most significant challenge was learning proper "web scraping etiquette." This involved:
* Understanding how to use cookies and headers from DevTools to access the website respectfully
* Implementing appropriate delays between requests to avoid overwhelming the server
* Managing sessions effectively to maintain stable connections
* Handling errors gracefully when the server was under load

These challenges transformed what seemed like a straightforward scraping project into a comprehensive learning experience about web technologies, API interactions, and responsible data collection practices.

### Note
If you want to use this scraper, you should consider fine-tuning it, especially the delay parameters, to achieve faster execution while avoiding being blocked by the server. The current settings prioritize reliability over speed.