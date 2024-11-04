from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
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

import json
import time
import random
import logging
import re
import unicodedata

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
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "dnt": "1",
    "enabled-feature-flags": "add_to_favourites,occasions,use_food_basket_service,ads_conditionals,findability_v5,show_static_cnc_messaging,fetch_future_slot_weeks,click_and_collect_promo_banner,cookie_law_link,citrus_banners,citrus_favourites_trio_banners,offers_trio_banners_single_call,special_logo,custom_product_messaging,promotional_link,findability_search,findability_autosuggest,findability_orchestrator,fto_header_flag,recurring_slot_skip_opt_out,first_favourite_oauth_entry_point,seasonal_favourites,cnc_start_amend_order_modal,favourites_product_cta_alt,get_favourites_from_v2,offers_config,alternatives_modal,relevancy_rank,changes_to_trolley,nectar_destination_page,nectar_card_associated,meal_deal_live,browse_pills_nav_type,zone_featured,use_cached_findability_results,event_zone_list,cms_carousel_zone_list,show_ynp_change_slot_banner,recipe_scrapbooks_enabled,event_carousel_skus,trolley_nectar_card,golui_payment_cards,favourites_magnolia,homepage,meal_deal_cms_template_ids,food_to_order,food_to_order_trial_modal,pdp_meta_desc_template,grouped_meal_deals,new_filters,ynp_np_zonalpage,enable_favourites_priority,xmas_slot_guide_enabled,occasions_navigation,slots_event_banner_config,rokt,sales_window,compare_seasonal_favourites,call_bcs,catchweight_dropdown,citrus_preview_new,citrus_search_trio_banners,citrus_xsell,constant_commerce_v2,desktop_interstitial_variant,disable_product_cache_validation,event_dates,favourites_pill_nav,favourites_whole_service,first_favourites_static,foodmaestro_modal,hfss_restricted,interstitial_variant,kg_price_label,krang_recommendations,meal_planner,mobile_interstitial_variant,nectar_prices,new_favourites_service,ni_brexit_banner,promo_lister_page,recipes_ingredients_modal,review_syndication,sale_january,show_hd_xmas_slots_banner,similar_products,use_food_basket_service_v3,xmas_dummy_skus,your_nectar_prices",
    "priority": "u=1, i",
    "referer": "https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/c:1020388?langId=44&storeId=10151",
    "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "traceparent": "00-10a9450995b383a1388157bf66aabc10-34b5073c060dd725-01",
    "tracestate": "2092320@nr=0-1-1782819-181742266-34b5073c060dd725----1730098192493",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "wcauthtoken": "-1002%2C3jIiHU%2F3lFc4jalpGDAhYOztAdQ%3D",
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
    "ak_bmsc": "5A5F9A63A548B1E333BDF9CC9B901152~000000000000000000000000000000~YAAQt8cQAk02MMiSAQAAd7ji0RnVZK17cxr+Y1J3sdLoYwsioBUoY7IDFOnLzi6SzYjoZ+OoFWzf3Dq7APs0uWNAcsBjeB4ZGv5XalXh4NwdJ5LwjYUoQBPF7npSAo+2Ao4Mu8NGWUpqr8xszBXEqmYUEeiE/fHxlhznvnxCelbP4LDFa6wa7C+zFojkm688WdJOjEejSj3k/JIIo620aBOtCUwRKBTDgzQe66VvPlmGSaVyZjbwrOH2jqOQVQRO+zXKgBiX3ThrmKgG8wd+lmtrISr+NsOCbe6LqEUWe4TENyIlIundZdxn8BFfW/sXppRgs/8duZ0RtoG18JXF4YSZrIf6TJV1h1CqGLI4OA8P+L2omKUso+LNM7Kg9k+8YTnVg9pZbLI0sbPPVUXTvOpP",
    "OptanonConsent": "isGpcEnabled=0&datestamp=Mon+Oct+28+2024+09%3A49%3A21+GMT%2B0300+(East+Africa+Time)&version=202408.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=c1ba8c6f-5dcf-49e6-aa75-c9ad93a23759&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=1%3A1%2C2%3A0%2C3%3A0%2C4%3A0&intType=6&geolocation=KE%3B30&AwaitingReconsent=false",
    "JSESSIONID": "0000VXL4-it_iu_p6qwB2P74MDJ:1i4oiilh4",
    "AWSALB": "yL44yekBbcfqBqt9FYaCjV9H/2EgbLgBOW4uTRTqrhsiSjVhpY9MiDWs9AclwHQ9ss2ZwIgCtPpvJaJ+T1LFmOgCbUgUaPTWmd1BgoiNwhHrnMU42l1AeQKFS0iR",
    "AWSALBCORS": "yL44yekBbcfqBqt9FYaCjV9H/2EgbLgBOW4uTRTqrhsiSjVhpY9MiDWs9AclwHQ9ss2ZwIgCtPpvJaJ+T1LFmOgCbUgUaPTWmd1BgoiNwhHrnMU42l1AeQKFS0iR",
    "akavpau_vpc_gol_default": "1730098492~id=592bfbca8b53ae208445f46a215e40aa",
    "_abck": "06050ACD75ADFA15AFCBEAEFF0B10981~0~YAAQbccQApFhwr+SAQAAoF/j0Qz8yVJtINDBh+WErJLzQVLCAmXb79xWYxpxzx/v/r75l8PNHe/07oOqJpUlW3I9aLJ8W/x2ZyweGpmdjYI7zHBrk09PyDBZ5mwjKhPhzGmQ/sjz4Z2ZSaS09+FQ2WCeJWtQuH/5jp4aSscRyhaY9slgdHwPl8yTbMeKCN/cESbQqWvTVCnje/Fl1xxiCZ2IaTzgOofKfwhA6us3DMWhkd2ZvZVAnSCzU+igFBtp3Uj6LWgQl82lnT8vU5/EQXTcO/s1yQH2hxj7uXFDj7U+HLEIQE6bTBPMkQbHp0TTMqleVTvStqf+wdjwLMCfINkcgFY175ICg1+pxPkdIrxTfEsi+MDgBsvjmsuwNCREvLethCzgIw6fuRJcOU+1yOj77zrYxbT04kjMeh6g1HswDEOyHCsrR+lLyyxFWQuEOMpVbMiFRq+hkyGFR/EX0RyW/5QDf+FTo4xzKacsGon6CJYif9UOkRSO11LENbRXrWExL2jSN+Ckvza5k2PtPZ9X6CbXVlRgUySqZqA7qaU8gJ0ZknD8ReAT1WJ3h+7vkWp66ZmuALoh4Uo4BBZDyRrTOeo9cFIZ9zGBzyqsHUsJPtlN/Sf6Oak=~-1~-1~-1",
    "bm_sv": "934D2E61E34E0550F12783511AD26ED9~YAAQbccQApJhwr+SAQAAoF/j0Rmx8LWhymSqBCX7DcwnlPgVgvjZL/ZzCuEuF1aVwROn6akiYX5kxm2OX5v6XN+bDUCMt13AFVhQHWIfngJntrBSna+WtKDgMo4znSwINTATPjEB3X6xtHpnBCsAE3i1hw6f0HIJS6zOIziWSbIBI68oSAWqS42WGN4vLuyBsFwtxaGZHPwBjMi+IIenRJTAJc6YPd4wzTBJXbazCS/khN9UNN5iPQZqIBf2MmAhO2npjYjd~1",
    "bm_sz": "E0D03929979BE87E73795EF0269ECA85~YAAQbccQApNhwr+SAQAAoF/j0Rm5OEhkUinnfY6ib1e7U0XTk14T4edjG7D56/7nXUB+RcOOzc22y0MCGaE/JTktz+zaEX9bXK0W6nEZ5n4Hz9fAN2jv4+phK2bc9sSZlMqbVjrN1NIfUueo4RccStq4Pg5MIHerSdX2CkWojpPPtXVN+aiLAjft+vHvZSWd2KgwQs/uvDQGNdqMV/Fh1twUYYJ0jUW90A9Un1H9umEYq+cHQTDE/fpks8JPakJSVqDfRyVQQqn5N/ZHTaRiYU6PtHbNUqIRzm+g2LDII6Dqd4Dmw3xwTFQETY86vYFYkO1S5dEG4kK8QD/j8QRjMt40dTFPpo6qXNlfcM4XRWorjfXOiUIZ5plRdV75wy5RONWgxSdYT5xKhkidaXGq2JyLf7o2j66GG7g3ynPjVc7Mqy66B+X/PpQOOiBCvkucWls482t6ktL1PwZOhA==~3224390~3227959",
    "utag_main": "v_id:0192ade688e500157879700912150507d002d07500978$_sn:26$_ss:0$_st:1730099992255$dc_visit:1$ses_id:1730098160419%3Bexp-session$_pn:2%3Bexp-session$previousPageName:web%3Agroceries%3Aproduct%3A6850577%3Bexp-session$previousSiteSection:product%20detail%3Bexp-session$previousPagePath:%2Fgol-ui%2Fproduct%2Fsainsburys-wilthsire-smoked-back-bacon--taste-the-difference-240g%3Bexp-session",
}

INGREDIENTS_LABEL = "INGREDIENTS:"
TEST_PRODUCT_DATA_FILE = "test_product_data.json"
HTML_CLASSES = {
    "NUTRITION_TABLE": "nutritionTable",
    "PRODUCT_HEADER": "pd__header",
    "PRODUCT_PRICE": "pd__cost",
    "PRODUCT_TEXT": "productText",
    "ITEM_CODE": "pd__item-code",
}
PROCESSED_PRODUCTS_FILE = "processed_products.json"


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
        return "Trace"

    if "of which" in value.lower():
        return value

    value = value.replace("g/td>", "g")
    value = re.sub(r"[^\d\.\/<]+", "", value)

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
        ingredients_label = soup.find(
            "strong", string=lambda text: text and "INGREDIENTS:" in text.upper()
        )

        if ingredients_label:
            ingredients_p = ingredients_label.parent
            if ingredients_p:
                text = ingredients_p.text.strip()
                if ":" in text:
                    text = text.split(":", 1)[1].strip()
                return clean_text(text)

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
def load_existing_progress() -> dict:
    """Load existing progress from processed_products.json if it exists"""
    try:
        with open(PROCESSED_PRODUCTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            logging.info("Loaded existing progress from processed_products.json")
            return data
    except FileNotFoundError:
        logging.info("No existing progress found. Starting fresh scraping session.")
        return {}
    except json.JSONDecodeError:
        logging.warning(
            "Existing progress file is corrupted. Starting fresh scraping session."
        )
        return {}


def save_progress(processed_products: dict):
    """Save current progress to processed_products.json"""
    with open(PROCESSED_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(processed_products, f, indent=2)
    logging.info(f"Progress saved to {PROCESSED_PRODUCTS_FILE}")


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
    categories: Dict[str, Dict[str, str]], driver: webdriver.Chrome
) -> dict:
    """Scrape all categories and their products"""
    # Load progress once at the start
    processed_products = load_existing_progress()

    # Calculate total products for progress tracking
    total_products = sum(len(products) for products in categories.values())
    processed_count = sum(len(products) for products in processed_products.values())

    logging.info(
        f"Starting with {processed_count}/{total_products} products already processed"
    )

    for category_index, (category, products) in enumerate(categories.items(), 1):
        print("=" * 100)
        logging.info(
            f"\nProcessing category {category_index}/{len(categories)}: {category}"
        )

        # Initialize category if it doesn't exist
        if category not in processed_products:
            processed_products[category] = []

        processed_urls = {p["url"] for p in processed_products[category]}
        category_total = len(products)
        category_processed = len(processed_urls)
        logging.info(
            f"Category progress: {category_processed}/{category_total} products already processed"
        )

        try:
            for product_index, (product_name, product_url) in enumerate(
                products.items(), 1
            ):
                if product_url in processed_urls:
                    logging.info(f"Skipping already processed product: {product_name}")
                    continue

                logging.info(
                    f"\nProcessing product {product_index}/{category_total}: {product_name}"
                )
                logging.info(f"URL: {product_url}")

                product = scrape_product(product_url, driver)
                if product:
                    processed_products[category].append(asdict(product))
                    save_progress(processed_products)

                    # Update progress counts
                    processed_count += 1
                    completion_percentage = (processed_count / total_products) * 100
                    logging.info(
                        f"Overall progress: {processed_count}/{total_products} ({completion_percentage:.1f}%)"
                    )
                    logging.info("Successfully processed product")

                # Random delay between requests
                delay = random.uniform(5, 20)
                logging.info(f"Waiting {delay:.2f} seconds before next request...")
                time.sleep(delay)

        except Exception as e:
            logging.error(f"Error processing category {category}: {str(e)}")
            continue

        print("=" * 100)

    return processed_products


# Function that drives the program
def main():
    driver = None
    start_time = datetime.now()

    try:
        logging.info("Loading all products...")
        all_products = get_all_products("all_products.json")

        if not all_products:
            logging.error("Failed to load products")
            return

        # Load existing progress
        existing_progress = load_existing_progress()
        total_categories = len(all_products)
        processed_categories = len(existing_progress) if existing_progress else 0
        total_products = sum(len(products) for products in all_products.values())

        logging.info(
            f"Found {total_categories} categories with {total_products} total products"
        )
        if processed_categories > 0:
            processed_count = sum(
                len(products) for products in existing_progress.values()
            )
            completion_percentage = (processed_count / total_products) * 100
            logging.info("Resuming from previous session:")
            logging.info(
                f"- Categories processed: {processed_categories}/{total_categories}"
            )
            logging.info(
                f"- Products processed: {processed_count}/{total_products} ({completion_percentage:.1f}%)"
            )

        logging.info("Initializing WebDriver...")
        driver = setup_driver()

        try:
            processed_products = scrape_categories(all_products, driver)

            end_time = datetime.now()
            execution_time = end_time - start_time
            hours, remainder = divmod(execution_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            final_count = sum(len(products) for products in processed_products.values())
            final_percentage = (final_count / total_products) * 100

            logging.info("\nProcessing completed:")
            logging.info(
                f"- Categories processed: {len(processed_products)}/{total_categories}"
            )
            logging.info(
                f"- Products scraped: {final_count}/{total_products} ({final_percentage:.1f}%)"
            )
            logging.info(f"- Total execution time: {hours}h {minutes}m {seconds}s")

            # Save with comprehensive metadata
            final_data = {
                "metadata": {
                    "start_time": start_time.isoformat(),
                    "completed_at": end_time.isoformat(),
                    "execution_time_seconds": execution_time.total_seconds(),
                    "execution_time_formatted": f"{hours}h {minutes}m {seconds}s",
                    "total_categories": total_categories,
                    "processed_categories": len(processed_products),
                    "total_products": total_products,
                    "processed_products": final_count,
                    "completion_percentage": final_percentage,
                    "average_time_per_product": (
                        execution_time.total_seconds() / final_count
                        if final_count > 0
                        else 0
                    ),
                },
                "products": processed_products,
            }

            with open(PROCESSED_PRODUCTS_FILE, "w", encoding="utf-8") as f:
                json.dump(final_data, f, indent=2)
            logging.info(f"\nAll data saved to {PROCESSED_PRODUCTS_FILE}")

        except KeyboardInterrupt:
            interrupt_time = datetime.now()
            execution_time = interrupt_time - start_time
            hours, remainder = divmod(execution_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            current_count = sum(
                len(products) for products in processed_products.values()
            )
            current_percentage = (current_count / total_products) * 100

            logging.info("\nScraping interrupted:")
            logging.info(f"- Progress: {current_percentage:.1f}% complete")
            logging.info(f"- Products processed: {current_count}/{total_products}")
            logging.info(f"- Time elapsed: {hours}h {minutes}m {seconds}s")
            logging.info("Progress has been saved. Run the script again to continue.")
            return

    except Exception as e:
        error_time = datetime.now()
        execution_time = error_time - start_time
        hours, remainder = divmod(execution_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        logging.error(
            f"Main execution error after {hours}h {minutes}m {seconds}s: {str(e)}"
        )
        logging.error("Check the log file for details")

    finally:
        if driver:
            try:
                driver.quit()
                logging.info("WebDriver successfully closed")
            except Exception as e:
                logging.error(f"Error closing WebDriver: {str(e)}")


if __name__ == "__main__":
    main()
