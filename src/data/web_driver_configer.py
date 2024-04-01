from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from termcolor import colored
import yaml
import re


class WebDriverConfiger:
    """
    Read configuration files, verify the validity of user-input parameters (browser, user-agent, tracked products, URLs), and create a web driver according to the browser.
    """

    def __init__(self):
        # Read YAML config files
        raw_browser_parameters, raw_tracked_products_list = self.read_config_files() 

        # Get browser name that will be used and set all characters to lowercase
        self.browser_name = raw_browser_parameters['browser'].lower()

        # Get user agent
        self.user_agent = raw_browser_parameters['user_agent']

        # Check if the parameters set by the user for monitored products are valid
        if self.check_monitored_product_list(raw_tracked_products_list):
            self.tracked_products_list = raw_tracked_products_list
            
            # Create web driver corresponding to the chosen browser
            self.driver= self.set_browser_driver()
            
            
    def read_config_files(self) -> tuple[dict, list[dict]]:
        with open('config/browser.yaml', 'r') as file:
            raw_browser_name: dict = yaml.safe_load(file)

        with open('config/tracked_products.yaml', 'r') as file:
            raw_tracked_products_list: list[dict] = yaml.safe_load(file)
    
        return raw_browser_name, raw_tracked_products_list


    def check_monitored_product_list(self, raw_tracked_products_list: list[dict]) -> bool:
        _valid_parameters_list = ['name', 'keywords', 'url_kabum', 'url_amazon', 'url_pichau', 'url_terabyte', 'url_mercado_livre']
        success_bool = True

        for product in raw_tracked_products_list:
            for parameter, value in product.items():
                # Check if it is a valid parameter
                if (parameter not in _valid_parameters_list):
                    success_bool = False
                    print(colored(f"Error: Wrong parameter name '{parameter}' for product '{product['name']}' in config/tracked_products.yaml", "red"))

                # Check if the user set a name for product
                elif (parameter == 'name') and (value is None):
                    success_bool = False
                    print(colored(f"Error: No name was set for a product in config/tracked_products.yaml", "red"))
                    
                # Check if the URLs are valid
                elif (re.search("url_", parameter)):
                    if not (self.is_valid_url(parameter, value)):
                        success_bool = False
                        print(colored(f"Error: Invalid '{parameter}' was set for product '{product['name']}' in config/tracked_products.yaml", "red"))

            # Return warning if a product doesn't have at least one valid URL
            _bool_have_url = [True for parameter in product if parameter.startswith("url_")]
            if not _bool_have_url: 
                print(colored(f"Warning: No valid URL was set for product '{product['name']}' in config/tracked_products.yaml", "yellow"))
                
        if success_bool:
            print("Successfully processed the list of tracked products")

        return success_bool

    
    def is_valid_url(self, site_name: str, site_url: str | None) -> bool:
        # Check if the user has set a blank URL
        if site_url is None:
            return False
        
        # Auxiliary variable to identify the site name in URL check
        _site_name_adjusted = site_name.replace('url', '').replace('_', '')

        # Check if URL correspond to the site
        _match = re.search(f'.*{_site_name_adjusted}.*\.com', site_url, re.IGNORECASE)

        if _match is None:
            return False
        else:
            return True
        

    def set_browser_driver(self) -> webdriver.ChromeOptions | webdriver.EdgeOptions:
        _success_bool = True

        match self.browser_name:
            case 'chrome':
                driver = self.webDriverChrome()
            case 'edge':
                driver = self.webDriverEdge()
            case _:
                _success_bool = False
                
        if (_success_bool):
            print(colored(f"Successfully configured web scraping settings for {self.browser_name} browser", "green"))
        else:
            print(colored(f"Error: Invalid browser name '{self.browser_name}' in config/browser.yaml", "red"))

        return driver
    

    def webDriverChrome(self) -> webdriver.ChromeOptions:
        _options = webdriver.ChromeOptions()
        _options.add_argument('--headless') # Doesn't open the browser during the process
        _options.add_argument('log-level=3') # Suppress warning messages
        _options.add_argument(f'user-agent={self.user_agent}')
        #_options.add_experimental_option("detach", True) # Keeps browser open
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=_options)

        return driver


    def webDriverEdge(self) -> webdriver.EdgeOptions:
        _options = webdriver.EdgeOptions()
        _options.add_argument('--headless')
        _options.add_argument('log-level=3')
        _options.add_argument(f'user-agent={self.user_agent}')
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=_options)

        return driver