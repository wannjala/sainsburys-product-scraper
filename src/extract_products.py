from typing import Dict, Any, List
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time
import logging
import re
import random


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def setup_driver() -> webdriver.Chrome:
    """
    Set up and return a configured Chrome WebDriver
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")

    # Add user agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    )

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def construct_page_url(base_url: str, page_num: int) -> str:
    """
    Construct the correct URL for pagination
    """
    # If the URL already contains '/opt/page:', remove it
    base_url = re.sub(r"/opt/page:\d+", "", base_url)

    # Remove trailing slash if present
    base_url = base_url.rstrip("/")

    # Add page number
    return f"{base_url}/opt/page:{page_num}"


def extract_products_from_page_source(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extract products from the parsed HTML
    """
    products = {}
    product_desc_box = soup.find_all("div", class_="product-description-box")

    for product in product_desc_box:
        title_elem = product.find("h2", class_="pt__info__description")
        if title_elem and title_elem.find("a"):
            link = title_elem.find("a")
            title = link.get("title", "").strip()
            url = link.get("href", "").strip()

            # If URL is relative, make it absolute
            if url and not url.startswith("http"):
                url = f"https://www.sainsburys.co.uk{url}"

            if title and url:
                products[title] = url

    return products


def get_last_page_number(soup: BeautifulSoup) -> int:
    """
    Extract the last page number from pagination
    """
    try:
        # Look for the link with aria-label containing "3rd page" or similar
        last_page_link = soup.find(
            "a", {"class": "ln-c-pagination__link", "rel": "last"}
        )
        if last_page_link and "href" in last_page_link.attrs:
            return int(last_page_link["href"].strip("#"))

        # If no "last" link, find all page links and get the highest number
        page_links = soup.find_all("a", class_="ln-c-pagination__link")
        page_numbers = []
        for link in page_links:
            try:
                href = link.get("href", "")
                if href and href.startswith("#"):
                    page_numbers.append(int(href[1:]))
            except ValueError:
                continue

        return max(page_numbers) if page_numbers else 1
    except Exception as e:
        logging.error(f"\nError getting last page number: {str(e)}")
        return 1


def get_products_from_category(url: str) -> Dict[str, str]:
    """
    Get all products from a category, handling pagination
    """
    all_products = {}
    driver = setup_driver()

    try:
        # Get first page to determine total pages
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[class*="product-description-box"]')
            )
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        total_pages = get_last_page_number(soup)
        logging.info(f"\nTotal pages found: {total_pages}")

        # Process each page
        for page_num in range(1, total_pages + 1):
            page_url = construct_page_url(url, page_num)
            logging.info(f"\nProcessing page {page_num} of {total_pages}: {page_url}")

            if page_num > 1:  # We already have page 1 loaded
                driver.get(page_url)
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div[class*="product-description-box"]')
                    )
                )

            # Scroll to bottom for lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Get products from current page
            soup = BeautifulSoup(driver.page_source, "html.parser")
            page_products = extract_products_from_page_source(soup)

            if page_products:
                all_products.update(page_products)
                logging.info(
                    f"\nFound {len(page_products)} products on page {page_num}"
                )
            else:
                logging.warning(f"\nNo products found on page {page_num}")

            # Add a random delay between pages (between 1.5 and 7 seconds)
            delay = random.uniform(1.5, 7)
            logging.info(f"\nWaiting {delay:.2f} seconds before next page")
            time.sleep(delay)

    except Exception as e:
        logging.error(f"\nError processing category: {str(e)}")

    finally:
        driver.quit()

    return all_products


def load_categories() -> Dict[str, Any]:
    """
    Load the meat and fish categories from the JSON file
    """
    try:
        with open("meat_fish_categories.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("\nCategories file not found")
        return {}


def save_to_json(
    data: Dict[str, Dict[str, str]],
    filename: str = "all_products.json",
):
    """
    Save the data to a JSON file
    The data dictionary should have category names as keys
    and their corresponding product dictionaries as values
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"\nData successfully saved to {filename}")
    except Exception as e:
        logging.error(f"\nError saving data to {filename}: {str(e)}")


def load_existing_progress(
    filename: str = "all_products.json",
) -> Dict[str, Dict[str, str]]:
    """
    Load existing progress from JSON file if it exists
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        logging.info(f"\nLoaded existing progress from {filename}")
        logging.info(f"\nFound {len(existing_data)} categories already processed")
        return existing_data
    except FileNotFoundError:
        logging.info("\nNo existing progress found. Starting fresh.")
        return {}
    except Exception as e:
        logging.error(f"\nError loading existing progress: {str(e)}")
        return {}


def main():
    # Load categories
    categories = load_categories()
    if not categories:
        logging.error("\nUnable to load categories")
        return

    all_products = load_existing_progress()
    total_categories = len(categories["Meat & Fish"])

    # Process each category
    for index, (category_name, category_url) in enumerate(
        categories["Meat & Fish"].items(), 1
    ):
        try:
            print("=" * 50)

            # Skip if category already processed
            if category_name in all_products:
                logging.info(
                    f"\nSkipping category {index}/{total_categories}: {category_name} (already processed)"
                )
                continue

            logging.info(
                f"\nProcessing category {index}/{total_categories}: {category_name}"
            )
            logging.info(f"URL: {category_url}")

            # Get products for this category
            products = get_products_from_category(category_url)

            if products:
                all_products[category_name] = products
                logging.info(
                    f"\nTotal products found in {category_name}: {len(products)}"
                )

                # Save progress after each category
                save_to_json(all_products, "all_products.json")

                # Add a longer delay between categories (between 10 and 20 seconds)
                delay = random.uniform(5, 20)
                logging.info(f"\nWaiting {delay:.2f} seconds before next category...")
                print("=" * 50)
                time.sleep(delay)
            else:
                logging.warning(f"\nNo products found in {category_name}")

        except Exception as e:
            logging.error(f"\nError processing category {category_name}: {str(e)}")

            # Save progress even if there's an error
            save_to_json(all_products, "all_products.json")
            continue
    logging.info("\nAll categories processed!")
    logging.info(f"\nTotal categories processed: {len(all_products)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\nScript interrupted by user. Progress has been saved.")
        logging.info("Run the script again to continue from where you left off.")
