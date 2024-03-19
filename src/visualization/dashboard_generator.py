import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re

# Web application to visualize products price history data

def set_up_init_configurations():
    st.set_page_config(layout="wide")

    price_history_df = pd.read_csv('data/processed_price_histories.csv', sep=';', index_col=False)
    best_prices_df = price_history_df[price_history_df['Flag Daily Best Price'] == True].sort_values(by='Date', ascending=True)
    best_prices_df['Date'] = pd.to_datetime(best_prices_df['Date'], format='%Y-%m-%d')
    best_prices_df['Dateref Datetime'] = pd.to_datetime(best_prices_df['Dateref Datetime'], format='%Y-%m-%d')
    st.session_state['best_prices_df'] = best_prices_df

    st.markdown("# Price Monitoring")


def implement_sidebar_filters():
    # Filters in sidebar
    st.sidebar.title("Filters")

    best_prices_df = st.session_state['best_prices_df']

    # Multi Select Products to display prices
    selected_products = st.sidebar.multiselect(label = "Select products to display prices",
                                               options = best_prices_df['Product Name'].unique())

    product_mask = best_prices_df['Product Name'].isin(selected_products)
    filtered_products_df = best_prices_df[product_mask]
    st.session_state['selected_products'] = selected_products

    st.sidebar.write("#")

    if selected_products:
        # Select Slider to select month interval to display prices
        monthYear_list = filtered_products_df['Dateref'].unique().tolist()
        min_date = monthYear_list[0]
        max_date = monthYear_list[-1]

        # If there is data for only one month, include the next month for selection in the slider to prevent errors during iteration
        if (min_date == max_date):
            # Convert string to datetime in order to add one month
            formatted_max_date = datetime.strptime(max_date, "%m/%Y").date()
            correct_max_date = formatted_max_date + relativedelta(months=1)

            # Convert back to string
            correct_max_date_str = correct_max_date.strftime('%m/%Y')
            max_date = re.sub('^0', '', correct_max_date_str) # Remove the leading zero from the month to standardize the patterns
            monthYear_list.append(max_date)

        min_selected, max_selected = st.sidebar.select_slider(label = "Move sliders to select month interval",
                                                              options = monthYear_list,
                                                              value = (min_date, max_date))

        # Convert string to datetime in order to filter dataframe by selected month interval
        min_selected_datetime = datetime.strptime(min_selected, "%m/%Y")
        max_selected_datetime = datetime.strptime(max_selected, "%m/%Y")

        dataref_mask = (filtered_products_df['Dateref Datetime'] >= min_selected_datetime) & (filtered_products_df['Dateref Datetime'] <= max_selected_datetime)
        filtered_products_dateref_df = filtered_products_df[dataref_mask]
        st.session_state['filtered_products_dateref_df'] = filtered_products_dateref_df
    
    else:
        st.session_state['filtered_products_dateref_df'] = pd.DataFrame()

    for i in range(11):
        st.sidebar.write("#")

    st.sidebar.markdown("Develop by Gabriel Corrêa de Oliveira")
    st.sidebar.markdown("Contact: [LinkedIn](https://www.linkedin.com/in/gabriel-correa-de-oliveira/) | [GitHub](https://github.com/Gabriel-c-oliveira)")


def get_price_metrics():
    selected_products = st.session_state['selected_products']
    filtered_products_dateref_df = st.session_state['filtered_products_dateref_df']
    product_infos: list[dict] = []

    for count, product in enumerate(selected_products):
        # Limit of two product infos to show in app
        if (count >= 2):
            continue

        product_dict: dict = {}
        
        # Current price information
        product_df = filtered_products_dateref_df[filtered_products_dateref_df['Product Name'] == product]
        product_df = product_df.sort_values(by='Date', ascending=True)
        index_current_price = product_df['Date'].idxmax()
        product_dict['Current Name'] = product_df.loc[index_current_price, 'Product Name']
        product_dict['Current Price'] = product_df.loc[index_current_price, 'Price']
        product_dict['Current Store'] = product_df.loc[index_current_price, 'Store']
        product_dict['Current Title'] = product_df.loc[index_current_price, 'Title']
        product_dict['Current Date'] = product_df.loc[index_current_price, 'Date']

        # Yesterday price information
        yesterday = product_dict['Current Date'] - timedelta(days=1)
        if yesterday in product_df['Date'].values:
            yesterday_price = product_df.loc[product_df['Date'] == yesterday, 'Price'].item()
            product_dict['Delta Day'] = round(100*(product_dict['Current Price']/yesterday_price - 1))
        else:
            product_dict['Delta Day'] = 0

        # Historical price information
        historical_price = product_df['Price'].min()
        index_historical_price = product_df.where(product_df['Price'] == historical_price).last_valid_index()
        product_dict['Historical Price'] = product_df.loc[index_historical_price, 'Price']
        product_dict['Historical Store'] = product_df.loc[index_historical_price, 'Store']
        product_dict['Historical Title'] = product_df.loc[index_historical_price, 'Title']
        product_dict['Historical Date'] = product_df.loc[index_historical_price, 'Date'] 

        product_infos.append(product_dict)

    st.session_state['product_infos'] = product_infos


def plot_graphs_and_metrics():
    col1, col2, col3 = st.columns([5,2,2])
    product_infos = st.session_state['product_infos']
    number_products_selected = len(product_infos)
    filtered_products_dateref_df = st.session_state['filtered_products_dateref_df']

    with col1:
        st.header('Best Price History per Product')
        con_graph1 = st.container(border=True)
        fig_date = px.line(data_frame=filtered_products_dateref_df, x='Date', y='Price', color='Product Name')
        con_graph1.plotly_chart(fig_date, use_container_width=True)
    
    if (number_products_selected >= 1):
        with col2:
            product_1: dict = product_infos[0]
            st.header(f'{product_1["Current Name"]}')
            con_info1 = st.container(border=True)
            con_info1.metric(label='Current Price', value=f'R$ {product_1["Current Price"]}', delta=f'{product_1["Delta Day"]}%', delta_color="inverse")
            con_info1.metric(label='Store', value=product_1["Current Store"])
            con_info1.metric(label='Date', value=product_1["Current Date"].strftime("%d/%m/%y"))
            con_info1.caption(f'Title: {product_1["Current Title"]}')

            con_info1.divider()

            con_info1.markdown(f'Historical Price: **R$ {product_1["Historical Price"]}**')
            con_info1.markdown(f'Store: **{product_1["Historical Store"]}**')
            con_info1.markdown(f'Date: **{product_1["Historical Date"].strftime("%d/%m/%y")}**')
            con_info1.caption(f'Title: {product_1["Historical Title"]}')
            
    if (number_products_selected >= 2):
        with col3:
            product_2: dict = product_infos[1]
            st.header(f'{product_2["Current Name"]}')
            con_info2 = st.container(border=True)
            con_info2.metric(label='Current Price', value=f'R$ {product_2["Current Price"]}', delta=f'{product_2["Delta Day"]}%', delta_color="inverse")
            con_info2.metric(label='Store', value=product_2["Current Store"])
            con_info2.metric(label='Date', value=product_2["Current Date"].strftime("%d/%m/%y"))
            con_info2.caption(f'Title: {product_2["Current Title"]}')

            con_info2.divider()

            con_info2.markdown(f'Historical Price: **R$ {product_2["Historical Price"]}**')
            con_info2.markdown(f'Store: **{product_2["Historical Store"]}**')
            con_info2.markdown(f'Date: **{product_2["Historical Date"].strftime("%d/%m/%y")}**')
            con_info2.caption(f'Title: {product_2["Historical Title"]}')


def plot_filtered_dataframe():
    filtered_products_dateref_df = st.session_state['filtered_products_dateref_df']
    filtered_products_dateref_df['Date'] = filtered_products_dateref_df['Date'].dt.strftime('%d/%m/%Y')
    filtered_products_dateref_df = filtered_products_dateref_df.drop('Dateref Datetime', axis=1)
    df_expander = st.expander("Price History DataFrame", expanded=False)

    with df_expander:
        st.dataframe(filtered_products_dateref_df, use_container_width=True)


def execute_dashboard():
    set_up_init_configurations()

    implement_sidebar_filters()

    if not st.session_state['filtered_products_dateref_df'].empty:
        get_price_metrics()
        
        plot_graphs_and_metrics()
        
        plot_filtered_dataframe()

    else:
        st.warning("Select at least one product and a month interval with available price data")


if __name__ == '__main__':
    execute_dashboard()