from datetime import datetime
from typing import Optional, Dict, Any

import requests
import json
import os


def get_category_tree() -> Optional[Dict[str, Any]]:
    """
    Fetch the category tree from Sainsbury's API

    Returns:
        Optional[Dict[str, Any]]: JSON response containing category tree or None if request fails
    """
    url = "https://www.sainsburys.co.uk/groceries-api/gol-services/product/categories/tree"

    cookies = {
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

    headers = {
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

    try:
        response = requests.get(
            url,
            cookies=cookies,  # cookies dictionary would be imported from a separate file
            headers=headers,
            timeout=10,  # Added timeout for safety
        )

        # Check if request was successful
        response.raise_for_status()

        # Try to parse JSON response
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"\nError making request: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"\nError decoding JSON response: {str(e)}")
        return None


def save_json_data(data: Dict[str, Any], filename: str) -> bool:
    """
    Save data to a JSON file

    Args:
        data: Dictionary containing the data to save
        filename: Name of the file to save to

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"\nData successfully saved to {filename}")
        return True
    except Exception as e:
        print(f"\nError saving data to {filename}: {str(e)}")
        return False


def load_json_data(filename: str) -> Optional[Dict[str, Any]]:
    """
    Load data from a JSON file

    Args:
        filename: Name of the file to load from

    Returns:
        Optional[Dict[str, Any]]: Loaded JSON data or None if load fails
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"\nData successfully loaded from {filename}")
        return data
    except FileNotFoundError:
        print(f"\nFile not found: {filename}")
        return None
    except json.JSONDecodeError as e:
        print(f"\nError decoding JSON from {filename}: {str(e)}")
        return None


def extract_meat_fish_categories(data):
    """
    Extract leaf subcategories from the Meat & fish category

    Args:
        data (dict): The loaded JSON data

    Returns:
        dict: Dictionary with Meat & Fish as main key and subcategories as nested dictionary
    """
    BASE_URL = "https://www.sainsburys.co.uk"

    # Initialize the structure
    meat_fish_data = {"Meat & Fish": {}}

    def traverse_categories(category):
        """
        Recursively traverse category tree to find leaf nodes

        Args:
            category (dict): Category dictionary containing 'n', 's' and optionally 'c' keys
        """
        # If category has subcategories, traverse them
        if "c" in category:
            for subcategory in category["c"]:
                traverse_categories(subcategory)
        else:
            # If no subcategories, this is a leaf node - add it to our list
            if "gol-ui" in category["s"]:
                complete_url = f"{BASE_URL}/{category['s']}"
                meat_fish_data["Meat & Fish"][category["n"]] = complete_url

    # Find the Meat & fish category and traverse its subcategories
    for category in data["category_hierarchy"]["c"]:
        if category["n"] == "Meat & fish":
            for subcategory in category["c"]:
                traverse_categories(subcategory)

    return meat_fish_data


def save_categories_to_json(data, filename="meat_fish_categories.json"):
    """
    Save the categories data to a JSON file

    Args:
        data (dict): The categories data to save
        filename (str): Name of the file to save to
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"\nData successfully saved to {filename}")
    except Exception as e:
        print(f"\nError saving data to {filename}: {str(e)}")


def main():
    """
    Main function to drive the script
    """
    # Configuration
    data_file = "category_tree.json"
    data_max_age_days = 7  # Maximum age of the data file in days

    # Check if we have a recent enough data file
    need_fresh_data = True
    if os.path.exists(data_file):
        file_age = datetime.now().timestamp() - os.path.getmtime(data_file)
        if file_age < (data_max_age_days * 24 * 60 * 60):  # Convert days to seconds
            print(f"\nFound recent data file (age: {file_age/3600:.1f} hours)")
            data = load_json_data(data_file)
            need_fresh_data = False
            print("\nUsing cached data")
        else:
            print(f"\nData file is too old (age: {file_age/3600:.1f} hours)")

    # Fetch fresh data if needed
    if need_fresh_data:
        print("\nFetching fresh data from API...")
        data = get_category_tree()
        if data:
            save_json_data(data, data_file)
        else:
            print("\nFailed to fetch fresh data")
            return

    if data:
        categories = extract_meat_fish_categories(data)
        save_categories_to_json(categories)
        print("\nExample of saved structure:")
        print(json.dumps(categories, indent=2))
    else:
        print("\nFailed to load or fetch data.")


if __name__ == "__main__":
    main()
