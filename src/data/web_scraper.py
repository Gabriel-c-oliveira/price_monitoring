from bs4 import BeautifulSoup, Tag
import re
from math import ceil


class WebScraper:
    """
    Set up web scraping parameters according to the store and then attempt to gather offer data from the site.
    """

    kabum = {'tag_products': 'article', 'attribute_products': 'class', 'value_products': 'productCard',
            'tag_title': 'span', 'attribute_title': 'class', 'value_title': 'nameCard',
            'tag_price': 'span', 'attribute_price': 'class', 'value_price': 'priceCard'}

    amazon = {'tag_products': 'div', 'attribute_products': 'class', 'value_products': 'a-section a-spacing-base',
            'tag_title': 'span', 'attribute_title': 'class', 'value_title': 'a-size-base-plus a-color-base a-text-normal',
            'tag_price': 'span', 'attribute_price': 'class', 'value_price': 'a-offscreen'}
    
    mercado_livre = {'tag_products': 'li', 'attribute_products': 'class', 'value_products': 'ui-search-layout__item',
            'tag_title': 'h2', 'attribute_title': 'class', 'value_title': 'ui-search-item__title',
            'tag_price': 'span', 'attribute_price': 'class', 'value_price': 'andes-money-amount__fraction'}
    
    terabyte = {'tag_products': 'div', 'attribute_products': 'class', 'value_products': 'commerce_columns_item_inner',
            'tag_title': 'a', 'attribute_title': 'class', 'value_title': 'prod-name',
            'tag_price': 'div', 'attribute_price': 'class', 'value_price': 'prod-new-price'}
        
    pichau = {'tag_products': 'div', 'attribute_products': 'class', 'value_products': 'MuiCardContent-root',
            'tag_title': 'h2', 'attribute_title': 'class', 'value_title': 'MuiTypography-root',
            'tag_price': 'div', 'attribute_price': 'class', 'value_price': ''}
    

    def __init__(self, soup: BeautifulSoup, store: str):
        self.soup = soup

        # Set web scraping parameters based on the store
        self.store = store
        store_parameters = self.set_up_store_parameters()
        
        self.tag_products = store_parameters['tag_products']
        self.attr_products = store_parameters['attribute_products']
        self.value_products = store_parameters['value_products']

        self.tag_title = store_parameters['tag_title']
        self.attr_title = store_parameters['attribute_title']
        self.value_title = store_parameters['value_title']

        self.tag_price = store_parameters['tag_price']
        self.attr_price = store_parameters['attribute_price']
        self.value_price = store_parameters['value_price']


    def set_up_store_parameters(self) -> dict[str, str]:
        match self.store:
            case 'kabum':
                store_parameters = WebScraper.kabum
            case 'amazon':
                store_parameters = WebScraper.amazon
            case 'mercado_livre':
                store_parameters = WebScraper.mercado_livre
            case 'terabyte':
                store_parameters = WebScraper.terabyte
            case 'pichau':
                store_parameters = WebScraper.pichau
            case _:
                store_parameters = {}

        return store_parameters
        

    def get_products(self) -> list | None:
        try:
            ad_products = self.soup.find_all(self.tag_products, attrs = {self.attr_products: re.compile(self.value_products)})
        
        except AttributeError:
            ad_products = None

        return ad_products


    def get_title(self, element: Tag) -> str | None:
        try:
            ad_title_tag = element.find(self.tag_title, attrs = {self.attr_title: re.compile(self.value_title)})
            ad_title = ad_title_tag.text.strip()
        
        except AttributeError:
            ad_title = None

        return ad_title


    def get_price(self, element: Tag) -> int:
        try:
            # Web scraping prices from the Pichau store requires a different approach
            if (self.store == 'pichau'):
                ad_price_tag = element.find_all(self.tag_price)[4]
            else:
                ad_price_tag = element.find(self.tag_price, attrs = {self.attr_price: re.compile(self.value_price)})
            
            raw_ad_price_str = ad_price_tag.text.strip()
            
            # Search for price pattern in ad
            ad_price_match = re.search(r"(\d{1,3}\.)+\d{1,3},{0,1}\d*", raw_ad_price_str)

            # Price data processing
            ad_price_str = ad_price_match.group()
            processed_ad_price_str = ad_price_str.translate({ord('.'): None, ord(','): ord('.')})
            ad_price = ceil(float(processed_ad_price_str))
        
        except (AttributeError, IndexError):
            ad_price = 0

        return ad_price