from bs4 import BeautifulSoup
from data.web_scraper import WebScraper
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from termcolor import colored
import re

class StoreBestOfferFinder:
    """
    Retrieve offers with titles matching the desired product keywords and prices that are available, then identify the best offer on the site
    """

    def __init__(self, driver, tracked_products_list): 
        self.driver = driver
        self.tracked_products_list = tracked_products_list

        # Auxiliary attributes to avoid pass arguments in methods
        self.product_info = {}
        self.site_info = {}


    def get_store_best_offers_for_all_products(self) -> list[dict]:
        ''' Get the name and price information from each best store offer '''
        best_offers = []

        # Sweep products list to get prices from each one
        for product in self.tracked_products_list:
            self.product_info = {'name': product['name'], 'keywords': product['keywords']}

            # Sweep product key and value to get the respective URLs set by the user
            for site_name, site_url in product.items():
                if site_name not in ['name', 'keywords']:
                    # Remove prefix "url_" from key in product dict
                    adjusted_site_name = site_name.replace('url_', '')
                    self.site_info = {'name': adjusted_site_name, 'url': site_url}
                    
                    # Get the name and price information from each available product ad that matches the desired product in the given URL
                    store_offers: dict[str, int] = self.get_available_matching_offers()

                    if self.check_web_scrapping_results(store_offers):
                        # Get the minimum price from store
                        best_store_offer = self.get_best_store_offer(store_offers)

                        # Add the best offer of each store in a list
                        best_offers.append(best_store_offer)

        # Close the WebDriver after completing the web scraping
        self.driver.quit()

        return best_offers
    

    def get_available_matching_offers(self) -> dict[str, int]:
        store_offers_dict = {}
        _delay = 60

        # Set URL to scrap
        self.driver.get(self.site_info['url'])

        # Wait for all span elements that contains prices loading
        wait = WebDriverWait(self.driver, _delay)
        wait.until(ec.presence_of_all_elements_located((By.TAG_NAME,'span'))) 

        # Get HTML from url
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Instance responsible for gathering data from different store sites
        web_scraper = WebScraper(soup, self.site_info['name'])

        # Find all product elements from HTML
        _product_elements = web_scraper.get_products()
        
        for element in _product_elements:
            # Get title and price from ads
            ad_title = web_scraper.get_title(element)
            ad_price = web_scraper.get_price(element)

            # Check if ad title correspond to desired product name by means of keywords
            if not self.check_ad_title(ad_title):
                continue

            # Check if ad price is non-zero
            if not self.check_ad_price(ad_price):
                continue
                
            # Add ad title and price in offers dictionary
            store_offers_dict[ad_title] = ad_price
    
        return store_offers_dict
    

    def check_ad_title(self, ad_title: str) -> bool:
        if self.product_info['keywords'] is None:
            return True

        for keyword in self.product_info['keywords']:
            _match = re.search(fr'{keyword}', ad_title, re.IGNORECASE)
            if _match is None:
                return False

        return True


    def check_ad_price(self, ad_price: int) -> bool:
        return (ad_price != 0)


    def check_web_scrapping_results(self, store_offers: dict[str, int]) -> bool:
        if store_offers:
            print(colored(f"Successfully took the prices of product '{self.product_info['name']}' from {self.site_info['name']}'s site", 'green'))
            return True
        else:
            print(colored(f"Error: No price for product '{self.product_info['name']}' was found in {self.site_info['name']}'s site. Check if the URL is correct: {self.site_info['url']}", "red"))
            print(colored("Otherwise, the HTML of the site may have been changed and the code needs maintenance", "red"))
            return False
       

    def get_best_store_offer(self, store_offers: dict[str,int]) -> dict:
        best_name = min(store_offers, key=store_offers.get)
        best_price = store_offers[best_name]
        
        best_store_offer = {'Product Name': self.product_info['name'], 'Store': self.site_info['name'], 'Price': best_price, 'Title': best_name}

        return best_store_offer