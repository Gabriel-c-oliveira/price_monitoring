import pandas as pd

'''
Helper functions to prepare price history data for visualization in the web application
'''

def concat_price_history_dfs(list_df: list[pd.DataFrame]) -> pd.DataFrame:
    concatenated_df = pd.DataFrame()

    for df in list_df:
        concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)

    return concatenated_df


def process_price_history(price_history_df: pd.DataFrame) -> pd.DataFrame:
    # Process store names
    price_history_df['Store'] = price_history_df['Store'].str.title().replace('_', ' ', regex=True)

    # Convert date values from str to datetime
    price_history_df['Date'] = pd.to_datetime(price_history_df['Date'], format='%d-%m-%Y')

    # Order by date and product
    price_history_df = price_history_df.sort_values(['Date', 'Product Name'])

    # Create dataref column in format month-year
    price_history_df['Dateref'] = price_history_df['Date'].apply(lambda x: str(x.month) + "/" + str(x.year))
    price_history_df['Dateref Datetime'] = pd.to_datetime(price_history_df['Dateref'], format="%m/%Y")

    return price_history_df