import pandas as pd
import numpy as np
from datetime import date
from termcolor import colored


class PriceHistoryUpdater:
    """
    Identify the daily and historical best prices for products, and then update the price history CSV files
    """

    def __init__(self, best_offers: list[dict]):
        self.today = date.today().strftime("%d-%m-%Y")

        self.best_offers_df = self.process_best_offers(best_offers)
        
        self.product_df_list = self.create_df_for_each_product()


    def process_best_offers(self, best_offers: list[dict]) -> pd.DataFrame:
        # Transform from dict to dataframe
        best_offers_df = pd.DataFrame(best_offers)

        # Add a date column
        best_offers_df['Date'] = self.today

        # Add flag best daily price column
        # True for the first occurence of the minimum price today, False for the rest
        index_daily_best_price = best_offers_df.groupby(['Product Name']).Price.idxmin()
        best_offers_df['Flag Daily Best Price'] = np.where(best_offers_df.index.isin(index_daily_best_price), True, False)

        # Save the most recently scraped offers in order to facilitate debugging
        best_offers_df.to_csv("data/latest_scraped_offers.csv", sep=';', index=False)

        return best_offers_df


    def create_df_for_each_product(self) -> list[pd.DataFrame]:
        # Separate best offers dataframe in a dataframe for each product in order to organize history update
        product_df_list = [product_df for _, product_df in self.best_offers_df.groupby(['Product Name'])]

        return product_df_list


    def update_all_products_price_history(self) -> list[pd.DataFrame]:
        updated_price_history_list_df: list[pd.DataFrame] = []

        for product_df in self.product_df_list:
            # Load price history of a specific product by CSV file
            price_history_path, product_name = self.get_product_price_history_path(product_df)
            price_history_df: pd.DataFrame = self.read_price_history_csv(price_history_path)
    
            updated_price_history_df = self.update_single_product_price_history(product_df, price_history_df, product_name)

            # Save updated price history of a product
            updated_price_history_df.to_csv(price_history_path, sep=';', index=False)
                 
            updated_price_history_list_df.append(updated_price_history_df)

        return updated_price_history_list_df
    

    def get_product_price_history_path(self, product_df: pd.DataFrame) -> tuple[str, str]:
        product_name: str = product_df['Product Name'].unique()[0]
        adjusted_product_name = product_name.replace(' ', '_')
        price_history_path = f"data/{adjusted_product_name}.csv"

        return price_history_path, adjusted_product_name
    

    def read_price_history_csv(self, price_history_path: str) -> pd.DataFrame:
        try:
            # Read csv file for price history of a product
            return pd.read_csv(price_history_path, sep=';', index_col=False)
        
        except FileNotFoundError:
            # Create empty dataframe if csv file doesn't already exist
            return pd.DataFrame()
        

    def update_single_product_price_history(self, product_df: pd.DataFrame, price_history_df: pd.DataFrame, product_name: str) -> pd.DataFrame:
        # Check if the CSV file for price history exists
        if price_history_df.empty:
            updated_price_history_df = product_df
            print(colored(f"A new CSV file for the price history of {product_name} has been created", 'green'))
        
        else:
            # Split price history df in two parts: current prices and past prices
            is_today_price = (price_history_df.Date == self.today)
            current_prices_df = price_history_df[is_today_price]
            past_prices_df = price_history_df[~is_today_price]

            # Check if prices for today already exist
            if current_prices_df.empty:
                # Concatenate today df with history df along index axis 
                updated_price_history_df = pd.concat(objs=[past_prices_df, product_df], axis=0, ignore_index=True)
                
            else:
                # Concatenate today df with history df along index axis 
                concated_daily_prices_df = pd.concat(objs=[current_prices_df, product_df], axis=0, ignore_index=True)

                # Remove duplicate rows based on store and date, retaining the minimum daily price for each store
                _index_min_store_daily_price = concated_daily_prices_df.groupby(['Store', 'Date']).Price.idxmin()
                min_current_prices_df = concated_daily_prices_df.loc[_index_min_store_daily_price]
                updated_price_history_df = pd.concat(objs=[past_prices_df, min_current_prices_df], axis=0, ignore_index=True)

            print(colored(f"Successfully updated price history of {product_name} with prices of {self.today}", 'green'))

        # Add flag historical best price 
        # If the historical best price occurs more than one time, consider the most recent
        masked_df = updated_price_history_df[updated_price_history_df['Flag Daily Best Price'] == True]
        masked_df = masked_df.sort_values(by='Date', ascending=True)
        historical_price = masked_df.Price.min()
        index_historical_best_price = masked_df.where(masked_df['Price'] == historical_price).last_valid_index()
        updated_price_history_df['Flag Historical Best Price'] = np.where(updated_price_history_df.index == index_historical_best_price, True, False)

        return updated_price_history_df