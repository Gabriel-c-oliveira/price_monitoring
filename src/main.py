from data.web_driver_configer import WebDriverConfiger
from data.store_best_offer_finder import StoreBestOfferFinder
from features.price_history_updater import PriceHistoryUpdater
import features.process_price_history as process

def main():
    # Instance responsable to provide the web driver and the tracked products list set by the user
    web_driver_configer = WebDriverConfiger()
    driver = web_driver_configer.driver
    tracked_products_list: list[dict] = web_driver_configer.tracked_products_list

    # Instance responsable to provide the best offer from each store for tracked products list
    store_best_offer_finder = StoreBestOfferFinder(driver, tracked_products_list)
    best_offers: list[dict] = store_best_offer_finder.get_store_best_offers_for_all_products()

    # Update the price history csv file of tracked products with newly scraped data and create a dataframe for each product
    # If there is already a store price today, save the lowest price
    price_history_updater = PriceHistoryUpdater(best_offers)
    updated_price_history_list_df = price_history_updater.update_all_products_price_history()

    # Concat and process all price history dfs for visualization in dashboard
    concatenated_df = process.concat_price_history_dfs(updated_price_history_list_df)
    processed_price_history_df = process.process_price_history(concatenated_df)

    # Save final price history dataframe
    processed_price_history_df.to_csv('data/processed_price_histories.csv', sep=';', index=False)


if __name__ == "__main__":
    main()