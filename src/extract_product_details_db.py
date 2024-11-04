from typing import Dict, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from contextlib import contextmanager

import json
import time
import random
import logging
import re
import unicodedata
import sqlite3


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nutrition_scraper_test.log"),
        logging.StreamHandler(),
    ],
)

# Constant definitions
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "dnt": "1",
    "if-none-match": 'W/"17c4-kstrrGLbPLVZ7rQNCdTRnKlSWvM"',
    "priority": "u=0, i",
    "referer": "https://www.sainsburys.co.uk/",
    "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
}

COOKIES = {
    "Apache": "10.8.240.5.1729494399763019",
    "SESSION_COOKIEACCEPT": "true",
    "WC_SESSION_ESTABLISHED": "true",
    "WC_PERSISTENT": "aRRaZSvuVEhLp6mNpTl1LgHCsDM%3D%0A%3B2024-10-21+08%3A06%3A39.765_1729494399764-419486_0",
    "WC_AUTHENTICATION_-1002": "-1002%2C3jIiHU%2F3lFc4jalpGDAhYOztAdQ%3D",
    "WC_ACTIVEPOINTER": "44%2C0",
    "WC_USERACTIVITY_-1002": "-1002%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2CKMrJ5CfMSypIHoRY9%2Fm%2Ffj67GuRhV00RVsmkAZdr0I%2FPbWN%2FgSgQH72aXdQWCPbX3tq%2B6yRwJgVzAgiMPB43jM%2BeEUpdR3PbVD9goSH7PCgTaIuM59aoBEeHzGFUNnsH9gW%2B69n5RfLjUzyrcYKSwJGIJb0TwE7a2cAuu0W7MYb1yf%2BHxzRDkbUK2JuHHIauiJ6JgOZ%2F4lVp27dq8cmLcw%3D%3D",
    "WC_GENERIC_ACTIVITYDATA": "[97046593216%3Atrue%3Afalse%3A0%3Aps3WwGx49lFnMn1EVnAylEnH2jo%3D][com.ibm.commerce.context.entitlement.EntitlementContext|null%26null%26null%26-2000%26null%26null%26null][com.sol.commerce.context.SolBusinessContext|null%26null%26null%26null%26null%26null%26null%26null%26false%26false%26false%26null%26false%26null%26false%26false%26null%26false%26false%26false%26null%26false%26false%26false%26null%26null%26null%26null%260%260%26null][com.ibm.commerce.context.audit.AuditContext|1729494399764-419486][com.ibm.commerce.context.globalization.GlobalizationContext|44%26null%2644%26null][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|null%26null%26false%26false%26false][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.context.preview.PreviewContext|null%26null%26false][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|0%26-1002%26-1002%26-1][com.sol.commerce.catalog.businesscontext.SolCatalogContext|10241%26null%26false%26false%26false%26null%26null]",
    "last_button_track": "false",
    "OptanonAlertBoxClosed": "2024-10-21T07:07:21.855Z",
    "search_redirect_flag": "0",
    "GOLVI": "75f63482ed6f411bbaae6dee67744188",
    "espot_click": "false",
    "topnav_click": "false",
    "prizeDrawPopUp_customer1In20Chance": "false",
    "ak_bmsc": "21317C6675EB915AB10886C7E6636937~000000000000000000000000000000~YAAQjawwFxw7auqSAQAAXWLm9Rm1oJVggiZXCk1e8c338fl5UY+AAWIm5IW4V9QNIoWf95qNnNeyUr29F/drZObvGbCEeSDj68+3B0m9MhjuAUGxagXbDqjOEGXGP4be3wv9kg9FAfBqogq6yTpyPT96bDM1ICPZUgB5J8J1/Wol0s4taxFe7fG6ugYMJ+vyMa8++hQhRVe0RVjq55lkZRSpO3XIf9TrTdXKMyap++sryNzpBhGdc9dof1FlgOZUABJW0/A22At63yURGBtr75w4tNH6PMtoUSUc+RcpDRuOnpHlX5xrE3Pli1ncifDEAAYM2hact3qGfv/rUpIghXoid0bR1wTLm6wOFxuIPpplv4myzD8yRba6dYVgQVkjWLAshXs+MXx0FNfx/cWKLwIx",
    "JSESSIONID": "0000g6ULhx9666awKR45mEtmE-A:1ibbsugik",
    "_abck": "06050ACD75ADFA15AFCBEAEFF0B10981~0~YAAQjawwFxH4auqSAQAA+uvs9QxRbcON7FOiHXuyvaEwv0lZgvdxTC0o7CSMx/RSljKLkdoHesmeOR8onRiwvioZdMlZ1Ab1oX3i27Ei8Gd+qCHM+bGKaQN3F+/YdxDG+DfRKbOq1P72gDiMDQVLETI26LAijkjYkXi0xcL5+JW83M8NNDdNTsrBSkldAYmxGnEqSoJEje8yAoWRG/XDnYiRe8kmn58clOzqy4Tg03ckEiSxziFPq3H/viRVDhynmtU8fjpaRW5BjUvfsVnbfmAAlfOrEbgMHYccDQtR99y3Xwt7niH9DBQijo5mkRxyP0jRGhc4KiVh2eyFoxlUESPUfYYMrFI1JRT92/vf6rfPFKfMcyJ+ZAYTfaN471FX/G+2TGkKNhRrTobzOhAjDZG5JCAp5qdFzH5DmCnLWirp81e2qRWE3+QMEuU8q7Z02Clf9XQuiKOhPx7Q3Mcq/XUFbE48f4MJU0gdfuQFQC/s5bzyUwnBSCc/aAiNMkbI0KY7+x9RQbE2VSmIIr+/Fydo7ESztJizkVjUMrm2vfJiDkQmL7gm+csbGEkwrHizquo17wvzV4S+XkhJd5qAA4E301SLAnc9fH63mLm65gy2mpD/mC9eDNM346x72EBl5rm8uggDJLLwtfZ9o9KcuO63Nqk=~-1~-1~-1",
    "bm_sz": "1F90C94602A36947F1F871125E106D4A~YAAQm6wwF6TKuKuSAQAAALjz9RmHVTRF4GENn1LAsPFGXpHz5CysaEBbWM1WyITT6PeUgIZdsJ0ZPLv4FAoe9ujyM2bX1fffd1xd7Qd3UTkEgDS//ytUitm8xVQnNPjLy7JOW3QTz8g46Tvea67nC5J/QMVL9Vr7xdnf9RkPA0l9uM+WCXOkI7+nX2MKDQhafywrPFtd82uJurTBHyPe0+T7/+urCxGKAat07R0aKNkt46ruE4D9xMjbIC8Z+DUMTrzSd7RSYjdraU05tOEF0zISBi228FtayiVMmwAXerLahT9P0a+CH0yWn6KAtZVL15VzN3DsMjaLPsWeMl2+IcYBTTUhIEt6f/JtpDacSs/2kgrR2LBbHxhc258GNPt6wMpmLWLfLwOr9eb4NFMvJvoPEToOTBAyQOvZeAZkSifnJFQwq1dOPip+oJcFdQ==~3684162~3158585",
    "OptanonConsent": "isGpcEnabled=0&datestamp=Mon+Nov+04+2024+10%3A06%3A47+GMT%2B0300+(East+Africa+Time)&version=202408.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=c1ba8c6f-5dcf-49e6-aa75-c9ad93a23759&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=1%3A1%2C2%3A0%2C3%3A0%2C4%3A0&intType=6&geolocation=KE%3B30&AwaitingReconsent=false",
    "bm_sv": "5476BFB1B05E7197876A420BA2C4DCE0~YAAQjawwF0oubeqSAQAA23P/9Rn9flrnIFTjYD70KOxUL+8BZatDPKmlhvzfqaffKGPelUTBIxxU6wg/xeNtFpsnrHOXmiH2lmT/HCGecVw2WKRPStk8VJpKZjrY8WkOkeVpLfHNhYhSa7xWl4E0oOuRXFjaGvI8uvb1PbzTiniQw/XaiaoFpSjWh5PsQQNxiGf95l4vJ6cFsoGBASPPWNsYXwO5udbtLFZZmyL3os1MilTWlWURaV8tMBBnhpu9bFeWCgwYXg==~1",
    "utag_main": "v_id:0192ade688e500157879700912150507d002d07500978$_sn:49$_ss:0$_st:1730705816263$dc_visit:2$ses_id:1730702370817%3Bexp-session$_pn:5%3Bexp-session$previousPageName:web%3Ahomepage%3Bexp-session$previousSiteSection:homepage%3Bexp-session$previousPagePath:%2F%3Bexp-session",
    "akavpau_vpc_gol_default": "1730704319~id=ba336f387a5fcce157f20bb1accfd236",
    "AWSALB": "+dZy80gO6buMfRcfYypo8/WNOrRxDc27/ac3nJNXxy/u7YL/vMgf7QYYMT5oI685nQCpq7Vv50+WgZyxByz/Sr9vg6LAWo0zdKeSyt1JG0efqW2TDRtvV+IYpCYO",
    "AWSALBCORS": "+dZy80gO6buMfRcfYypo8/WNOrRxDc27/ac3nJNXxy/u7YL/vMgf7QYYMT5oI685nQCpq7Vv50+WgZyxByz/Sr9vg6LAWo0zdKeSyt1JG0efqW2TDRtvV+IYpCYO",
}


@dataclass
class NutritionInfo:
    """Data class to store nutrition information"""

    energy_kj: Optional[str] = None
    energy_kcal: Optional[str] = None
    fat: Optional[str] = None
    saturates: Optional[str] = None
    mono_unsaturates: Optional[str] = None
    polyunsaturates: Optional[str] = None
    carbohydrate: Optional[str] = None
    sugars: Optional[str] = None
    fibre: Optional[str] = None
    protein: Optional[str] = None
    salt: Optional[str] = None
    reference_intake: Optional[str] = None


@dataclass
class Product:
    """Data class to store product information"""

    name: str
    url: str
    item_code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    review_count: Optional[int] = None
    average_rating: Optional[float] = None
    ingredients: Optional[str] = None
    nutrition: Optional[NutritionInfo] = None


@dataclass
class ScrapingStats:
    """Class to track scraping statistics"""

    total_attempts: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    failed_saves: int = 0
    missing_item_codes: int = 0
    missing_nutrition: int = 0

    def log_stats(self):
        """Log current statistics"""
        success_rate = (
            (self.successful_scrapes / self.total_attempts * 100)
            if self.total_attempts > 0
            else 0
        )
        logging.info("\n=== Scraping Statistics ===\n")
        logging.info(f"Total Attempts: {self.total_attempts}")
        logging.info(f"Successful Scrapes: {self.successful_scrapes}")
        logging.info(f"Failed Scrapes: {self.failed_scrapes}")
        logging.info(f"Failed Database Saves: {self.failed_saves}")
        logging.info(f"Missing Item Codes: {self.missing_item_codes}")
        logging.info(f"Missing Nutrition Info: {self.missing_nutrition}")
        logging.info(f"Success Rate: {success_rate:.1f}%")
        logging.info("==========================\n")


class DatabaseManager:
    def __init__(self, db_file: str = "sainsburys_products.db"):
        self.db_file = db_file
        self.setup_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
        finally:
            conn.close()

    def setup_database(self):
        """Create necessary tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create products table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    item_code TEXT NOT NULL PRIMARY KEY,  -- Text for product codes like "AB123"
                    name TEXT NOT NULL,                   -- Text for product names
                    url TEXT UNIQUE,                      -- Text for web URLs
                    description TEXT,                     -- Text for longer product descriptions
                    price DECIMAL(10,2),                  -- Money values like £2.50
                    review_count INTEGER,                 -- Whole numbers for counting reviews
                    average_rating DECIMAL(3,1),          -- Ratings like 4.5 (1-5 scale)
                    ingredients TEXT,                     -- Text for ingredient lists
                    category TEXT,                        -- Text for category names
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create nutrition table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS nutrition (
                    item_code TEXT NOT NULL PRIMARY KEY,
                    energy_kj DECIMAL(10,2),  
                    energy_kcal DECIMAL(10,2),
                    fat DECIMAL(10,2),
                    saturates DECIMAL(10,2),
                    mono_unsaturates DECIMAL(10,2), 
                    polyunsaturates DECIMAL(10,2),
                    carbohydrate DECIMAL(10,2),
                    sugars DECIMAL(10,2),
                    fibre DECIMAL(10,2),
                    protein DECIMAL(10,2),
                    salt DECIMAL(10,2),
                    FOREIGN KEY (item_code) REFERENCES products(item_code) ON DELETE CASCADE
                )
            """
            )

            conn.commit()

    def clear_database(self):
        """Delete all records from both tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM nutrition")
                cursor.execute("DELETE FROM products")
                conn.commit()
                logging.info("All existing records deleted from database")
                return True
        except Exception as e:
            logging.error(f"Error clearing database: {str(e)}")
            return False

    def _insert_product(self, cursor, product: Product, category: str) -> None:
        """Insert product data into products table"""
        cursor.execute(
            """
            INSERT OR REPLACE INTO products (
                item_code, name, url, description, price, 
                review_count, average_rating, ingredients, category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                product.item_code,
                product.name,
                product.url,
                product.description,
                float(product.price) if product.price else None,
                int(product.review_count) if product.review_count else None,
                float(product.average_rating) if product.average_rating else None,
                product.ingredients,
                category,
            ),
        )

    def _insert_nutrition(self, cursor, product: Product) -> None:
        """Insert nutrition data into nutrition table"""
        if not product.nutrition:
            return

        cursor.execute(
            """
            INSERT OR REPLACE INTO nutrition (
                item_code, energy_kj, energy_kcal, fat, saturates,
                mono_unsaturates, polyunsaturates, carbohydrate,
                sugars, fibre, protein, salt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                product.item_code,
                (
                    float(product.nutrition.energy_kj)
                    if product.nutrition.energy_kj
                    else None
                ),
                (
                    float(product.nutrition.energy_kcal)
                    if product.nutrition.energy_kcal
                    else None
                ),
                float(product.nutrition.fat) if product.nutrition.fat else None,
                (
                    float(product.nutrition.saturates)
                    if product.nutrition.saturates
                    else None
                ),
                (
                    float(product.nutrition.mono_unsaturates)
                    if product.nutrition.mono_unsaturates
                    else None
                ),
                (
                    float(product.nutrition.polyunsaturates)
                    if product.nutrition.polyunsaturates
                    else None
                ),
                (
                    float(product.nutrition.carbohydrate)
                    if product.nutrition.carbohydrate
                    else None
                ),
                float(product.nutrition.sugars) if product.nutrition.sugars else None,
                float(product.nutrition.fibre) if product.nutrition.fibre else None,
                float(product.nutrition.protein) if product.nutrition.protein else None,
                float(product.nutrition.salt) if product.nutrition.salt else None,
            ),
        )

    def save_product(self, product: Product, category: str) -> bool:
        """Save product and nutrition information to database"""
        if not product.item_code:
            logging.warning(f"No item_code for product {product.name}, skipping")
            return False

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                self._insert_product(cursor, product, category)
                self._insert_nutrition(cursor, product)
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error saving to database: {str(e)}")
            return False

    def get_processed_urls(self) -> set:
        """Get all processed product URLs from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM products")
            return {row[0] for row in cursor.fetchall()}

    def get_product_count(self) -> int:
        """Get total number of products in database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            return cursor.fetchone()[0]

    def get_products_by_category(self, category: str) -> list:
        """Get all products in a specific category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
            return cursor.fetchall()

    def get_product_with_nutrition(self, item_code: str) -> tuple:
        """Get product and its nutrition information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, n.*
                FROM products p
                LEFT JOIN nutrition n ON p.item_code = n.item_code
                WHERE p.item_code = ?
            """,
                (item_code,),
            )
            return cursor.fetchone()


# Helper/Utility functions
def clean_text(text: str) -> str:
    """Clean text by normalizing Unicode characters and removing unwanted characters"""
    if not text:
        return ""

    # Log each character and its Unicode code point
    logging.info("Character analysis:")
    for char in text:
        if ord(char) > 127:  # Non-ASCII characters
            logging.info(
                f"Found special character: {char} (Unicode: \\u{ord(char):04x})"
            )

    # Original normalization code
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ASCII", "ignore").decode("ASCII")
    cleaned = " ".join(ascii_text.split())

    return cleaned.strip()


def clean_nutrition_value(value: str) -> Optional[str]:
    """Clean and standardize nutrition values"""
    if not value or value.strip() == "":
        return None

    value = value.strip()

    if value.lower() in ["trace", "traces"]:
        return "0.01"  # Represent trace amounts as 0.01

    # Remove units and other non-numeric characters
    value = value.replace("g", "")  # Remove 'g' unit
    value = value.replace("kJ", "")  # Remove 'kJ' unit
    value = value.replace("kcal", "")  # Remove 'kcal' unit

    # Handle '<' values
    if "<" in value:
        # For values like '<0.1', take the number without '<'
        return value.replace("<", "")

    if "of which" in value.lower():
        return value

    # Remove any remaining non-numeric characters except decimal points
    value = re.sub(r"[^\d\.]", "", value)

    # Return None if we end up with empty string
    if not value:
        return None

    return value


def setup_driver():
    """Set up and configure Chrome WebDriver with headers and cookies"""
    try:
        service = Service(ChromeDriverManager().install())

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--enable-unsafe-swiftshader")

        # Add headers
        for key, value in HEADERS.items():
            chrome_options.add_argument(f"--header={key}:{value}")

        # Set user agent
        chrome_options.add_argument(f'user-agent={HEADERS["user-agent"]}')

        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Load domain first
        driver.get(
            "https://www.sainsburys.co.uk/groceries-api/gol-services/product/categories/tree"
        )

        # Add cookies
        for name, value in COOKIES.items():
            driver.add_cookie({"name": name, "value": value})

        logging.info("WebDriver successfully initialized with headers and cookies")
        return driver

    except WebDriverException as e:
        logging.error(f"WebDriver initialization failed: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during WebDriver setup: {str(e)}")
        raise


# Extraction helper functions
def _process_energy_row(row: BeautifulSoup) -> dict:
    """Extract energy values from a table row"""
    values = {}
    cells = row.find_all("td")

    if cells:
        values["energy_kj"] = clean_nutrition_value(cells[0].text.strip())
        next_row = row.find_next_sibling("tr", class_="tableRow0")
        if next_row and (kcal_cell := next_row.find("td")):
            values["energy_kcal"] = clean_nutrition_value(kcal_cell.text.strip())
    return values


def _extract_basic_nutrients(nutrition_table: BeautifulSoup) -> dict:
    """Extract basic nutrient values from nutrition table"""
    nutrient_values = {}
    nutrient_mapping = {
        "Fat": "fat",
        "Saturates": "saturates",
        "Mono-unsaturates": "mono_unsaturates",
        "Polyunsaturates": "polyunsaturates",
        "Carbohydrate": "carbohydrate",
        "Sugars": "sugars",
        "Fibre": "fibre",
        "Protein": "protein",
        "Salt": "salt",
    }

    try:
        for row in nutrition_table.find_all("tr"):
            header = row.find("th")
            if not header:
                continue

            nutrient = header.text.strip()
            if nutrient == "Energy":
                nutrient_values.update(_process_energy_row(row))
            elif nutrient in nutrient_mapping and (cells := row.find_all("td")):
                field_name = nutrient_mapping[nutrient]
                nutrient_values[field_name] = clean_nutrition_value(
                    cells[0].text.strip()
                )

    except Exception as e:
        logging.error(f"Error in _extract_basic_nutrients: {str(e)}")

    return nutrient_values


def extract_nutrition_info(soup: BeautifulSoup) -> NutritionInfo:
    """Extract nutrition information from the product page"""
    nutrition_info = NutritionInfo()

    try:
        nutrition_table = soup.find("table", class_="nutritionTable")
        if not nutrition_table:
            logging.warning("No nutrition table found")
            return nutrition_info

        # Extract nutrients
        nutrients = _extract_basic_nutrients(nutrition_table)
        for field, value in nutrients.items():
            setattr(nutrition_info, field, value)

        # Get reference intake
        table_wrapper = soup.find("div", class_="tableWrapper")
        reference_ps = table_wrapper.find_next_siblings("p")
        for p in reference_ps:
            if "reference intake" in p.text.lower():
                nutrition_info.reference_intake = p.text.strip()
                break

    except Exception as e:
        logging.error(f"Error extracting nutrition info: {str(e)}")

    return nutrition_info


def extract_rating(soup: BeautifulSoup) -> Optional[float]:
    """Extract product rating"""
    try:
        rating_elem = soup.select_one("div.ds-c-rating__stars")
        if rating_elem and (title := rating_elem.get("title")):
            return float(title.split()[1])
        return None
    except Exception as e:
        logging.error(f"Error extracting rating: {str(e)}")
        return None


def extract_review_count(soup: BeautifulSoup) -> Optional[int]:
    """Extract number of reviews"""
    try:
        review_elem = soup.select_one('span[data-testid="review-count"]')
        if review_elem and (count_match := re.search(r"\d+", review_elem.text)):
            return int(count_match.group())
        return None
    except Exception as e:
        logging.error(f"Error extracting review count: {str(e)}")
        return None


def extract_ingredients(soup: BeautifulSoup) -> Optional[str]:
    """Extract product ingredients"""
    try:
        # Look for the ingredients header
        ingredients_header = soup.find(
            "h3", class_="productDataItemHeader", string="Ingredients"
        )

        if ingredients_header:
            # Find the next div with class 'productText'
            product_text_div = ingredients_header.find_next("div", class_="productText")
            if product_text_div:
                # Combine all p tags within the productText div
                ingredients_text = " ".join(
                    p.text.strip() for p in product_text_div.find_all("p")
                )
                # Remove "INGREDIENTS:" if present (case insensitive)
                ingredients_text = re.sub(
                    r"INGREDIENTS:\s*", "", ingredients_text, flags=re.IGNORECASE
                )
                return clean_text(ingredients_text)

        return None
    except Exception as e:
        logging.error(f"Error extracting ingredients: {str(e)}")
        return None


def extract_product_info(soup: BeautifulSoup, url: str) -> Product:
    """Extract all product information"""
    try:
        name_elem = soup.find("h1", class_="pd__header")
        name = name_elem.text.strip() if name_elem else "Unknown Product"

        # Create product with mandatory fields
        product = Product(name=name, url=url)

        # Extract all information using helper functions
        product.nutrition = extract_nutrition_info(soup)
        product.average_rating = extract_rating(soup)
        product.review_count = extract_review_count(soup)
        product.ingredients = extract_ingredients(soup)

        # Extract price
        price_elem = soup.find("span", class_="pd__cost__retail-price")
        if price_elem:
            price_text = price_elem.text.strip()
            # Clean the price text (remove '£' and extra spaces)
            product.price = re.sub(r"[^\d.]", "", price_text)

        # Extract item code (if available)
        item_code_elem = soup.find("span", id="productSKU")
        if item_code_elem:
            product.item_code = item_code_elem.text.strip()

        # Extract description
        desc_elem = soup.find("div", class_="productText")
        if desc_elem:
            description_parts = [
                p.text.strip() for p in desc_elem.find_all("p") if p.text.strip()
            ]
            product.description = " ".join(description_parts)

        return product

    except Exception as e:
        logging.error(f"Error extracting product info: {str(e)}")
        return Product(name="Error", url=url)


# Progress handling functions
def load_existing_progress(db_manager: DatabaseManager) -> set:
    """Load URLs of already processed products from database"""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM products")
        processed_urls = {row[0] for row in cursor.fetchall()}

        logging.info(f"Found {len(processed_urls)} previously processed products")
        return processed_urls


# Main scraping functions
def get_all_products(filename: str) -> Dict[str, Dict[str, str]]:
    """Load all products from each category"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            all_products = json.load(f)

        logging.info(f"Found {len(all_products)} categories")
        total_products = sum(len(products) for products in all_products.values())
        logging.info(f"Total products to process: {total_products}")

        return all_products

    except Exception as e:
        logging.error(f"Error loading products: {str(e)}")
        return {}


def scrape_product(url: str, driver: webdriver.Chrome) -> Optional[Product]:
    """Scrape information from a single product page"""
    try:

        logging.info(f"Scraping product: {url}")
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "nutritionTable")))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        product = extract_product_info(soup, url)

        return product

    except Exception as e:
        logging.error(f"Error scraping product {url}: {str(e)}")
        return None


def scrape_categories(
    categories: Dict[str, Dict[str, str]],
    driver: webdriver.Chrome,
    db_manager: DatabaseManager,
    stats: ScrapingStats,
) -> None:
    """Scrape categories and save to database"""

    # Get already processed URLs

    processed_urls = load_existing_progress(db_manager)

    # Calculate totals
    total_products = sum(len(products) for products in categories.values())
    total_processed = len(processed_urls)

    logging.info(
        f"Starting scraping: {total_processed}/{total_products} products already processed"
    )

    for category_index, (category, products) in enumerate(categories.items(), 1):

        print("=" * 100)

        logging.info(
            f"\nProcessing category {category_index}/{len(categories)}: {category}"
        )

        category_total = len(products)
        category_processed = sum(
            1 for url in products.values() if url in processed_urls
        )

        logging.info(f"Category progress: {category_processed}/{category_total}")

        try:
            for product_index, (product_name, product_url) in enumerate(
                products.items(), 1
            ):
                if product_url in processed_urls:
                    logging.info(f"Skipping already processed product: {product_name}")
                    continue

                stats.total_attempts += 1  # Increment attempt counter
                print("*" * 100)
                logging.info(
                    f"\nProcessing product {product_index}/{category_total}: {product_name}"
                )

                product = scrape_product(product_url, driver)
                if product:
                    # Track missing data
                    if not product.item_code:
                        stats.missing_item_codes += 1
                    if not product.nutrition:
                        stats.missing_nutrition += 1

                    # Save to database
                    if db_manager.save_product(product, category):
                        stats.successful_scrapes += 1
                        processed_urls.add(product_url)
                        total_processed += 1

                        # Log progress
                        completion_percentage = (total_processed / total_products) * 100
                        logging.info(
                            f"Overall progress: {total_processed}/{total_products} ({completion_percentage:.1f}%)"
                        )
                        logging.info("Successfully processed product")
                        print("*" * 100)
                    else:
                        stats.failed_saves += 1
                        logging.error(
                            f"Failed to save product to database: {product_name}"
                        )
                else:
                    stats.failed_scrapes += 1

                # Log statistics every 10 products
                if stats.total_attempts % 10 == 0:
                    stats.log_stats()

                # Random delay
                delay = random.uniform(5, 20)
                logging.info(f"Waiting {delay:.2f} seconds before next request...")
                time.sleep(delay)

        except Exception as e:
            logging.error(f"Error processing category {category}: {str(e)}")
            continue

        print("=" * 100)


# Function that drives the program
# This main function is for testing purposes
def main():
    """Main function that drives the program"""
    driver = None
    start_time = datetime.now()
    db_manager = DatabaseManager("sainsburys_products.db")
    stats = ScrapingStats()

    # Clear existing records
    if not db_manager.clear_database():
        logging.error("Failed to clear database. Exiting...")
        return

    # Test products for controlled scraping
    test_products = {
        "Meat & fish essentials": {
            "Sainsbury's British or Irish 5% Fat Beef Mince 500g": "https://www.sainsburys.co.uk/gol-ui/product/sainsburys-beef-mince-5-fat-500g",
            "Sainsbury's British Fresh Chicken Breast Fillets Skinless & Boneless 640g": "https://www.sainsburys.co.uk/gol-ui/product/sainsburys-whole-chicken-breast-fillets-640g",
            "Sainsbury's Skin on ASC Scottish Salmon Fillets x2 240g": "https://www.sainsburys.co.uk/gol-ui/product/sainsburys-responsibly-sourced-scottish-salmon-fillet-x2-240g",
            "Sainsbury's British Fresh Chicken Breast Fillets Skinless & Boneless 1kg": "https://www.sainsburys.co.uk/gol-ui/product/sainsburys-chicken-fillets-1kg",
            "Sainsbury's British Fresh Chicken Breast Fillets Skinless & Boneless 320g": "https://www.sainsburys.co.uk/gol-ui/product/sainsburys-chicken-breast-fillets-300g",
        }
    }

    try:
        logging.info("Starting scraping process...")
        total_products = sum(len(products) for products in test_products.values())
        logging.info(f"Total products to process: {total_products}")

        logging.info("Initializing WebDriver...")
        driver = setup_driver()

        try:
            scrape_categories(test_products, driver, db_manager, stats)

            end_time = datetime.now()
            execution_time = end_time - start_time
            hours, remainder = divmod(execution_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            logging.info("\nScraping completed:")
            logging.info(f"Total execution time: {hours}h {minutes}m {seconds}s")
            stats.log_stats()

        except KeyboardInterrupt:
            interrupt_time = datetime.now()
            execution_time = interrupt_time - start_time
            hours, remainder = divmod(execution_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            logging.info("\nScraping interrupted:")
            logging.info(f"Time elapsed: {hours}h {minutes}m {seconds}s")
            stats.log_stats()
            return

    except Exception as e:
        error_time = datetime.now()
        execution_time = error_time - start_time
        hours, remainder = divmod(execution_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        logging.error(
            f"Main execution error after {hours}h {minutes}m {seconds}s: {str(e)}"
        )
        stats.log_stats()
        logging.error("Check the log file for details")

    finally:
        if driver:
            try:
                driver.quit()
                logging.info("WebDriver closed")
            except Exception as e:
                logging.error(f"Error closing WebDriver: {str(e)}")


# Use this main() function when you do not want to test,
# but you want to scrape the details for all products
# def main():
#     """Main function that drives the program"""
#     driver = None
#     start_time = datetime.now()
#     db_manager = DatabaseManager("sainsburys_products.db")
#     stats = ScrapingStats()

#     try:
#         logging.info("Loading all products...")
#         all_products = get_all_products("all_products.json")

#         if not all_products:
#             logging.error("Failed to load products. Exiting...")
#             return

#         # Clear existing records
#         if not db_manager.clear_database():
#             logging.error("Failed to clear database. Exiting...")
#             return

#         total_categories = len(all_products)
#         total_products = sum(len(products) for products in all_products.values())
#         logging.info(
#             f"Found {total_categories} categories with {total_products} total products"
#         )

#         logging.info("Initializing WebDriver...")
#         driver = setup_driver()

#         try:
#             scrape_categories(all_products, driver, db_manager, stats)

#             end_time = datetime.now()
#             execution_time = end_time - start_time
#             hours, remainder = divmod(execution_time.seconds, 3600)
#             minutes, seconds = divmod(remainder, 60)

#             logging.info("\nScraping completed:")
#             logging.info(f"Total execution time: {hours}h {minutes}m {seconds}s")
#             stats.log_stats()

#         except KeyboardInterrupt:
#             interrupt_time = datetime.now()
#             execution_time = interrupt_time - start_time
#             hours, remainder = divmod(execution_time.seconds, 3600)
#             minutes, seconds = divmod(remainder, 60)

#             logging.info("\nScraping interrupted:")
#             logging.info(f"Time elapsed: {hours}h {minutes}m {seconds}s")
#             stats.log_stats()
#             return

#     except Exception as e:
#         error_time = datetime.now()
#         execution_time = error_time - start_time
#         hours, remainder = divmod(execution_time.seconds, 3600)
#         minutes, seconds = divmod(remainder, 60)

#         logging.error(
#             f"Main execution error after {hours}h {minutes}m {seconds}s: {str(e)}"
#         )
#         stats.log_stats()
#         logging.error("Check the log file for details")

#     finally:
#         if driver:
#             try:
#                 driver.quit()
#                 logging.info("WebDriver closed")
#             except Exception as e:
#                 logging.error(f"Error closing WebDriver: {str(e)}")


if __name__ == "__main__":
    main()
