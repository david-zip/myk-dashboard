from http import server
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components.standard_components import create_card, get_growth, get_icon
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Output, Input, State, Serverside, html, dcc, \
    ServersideOutputTransform, callback
from data_proccessing.utils import *
from io import StringIO
import boto3



app = DashProxy(__name__,
                use_pages=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                transforms=[ServersideOutputTransform()])
server = app.server

app.config.suppress_callback_exceptions=True

df = pd.read_excel("data/full_iseller_data.xlsx")
df = df.sample(10000)

# will remove 
df['closed_date'] = pd.to_datetime(df['closed_date'])
df['date'] = df['closed_date'] .dt.date
df['day_of_week_num'] = df['closed_date'].dt.dayofweek
df['day_name'] = df['closed_date'].dt.day_name()




product_categories = df['product_type'].unique().tolist()
product_names = df['clean_product_name'].unique().tolist()
branches = df['outlet_name'].unique().tolist()
quarter_year = df['quarter_year'].unique().tolist()

# df = df.sample(10000)





############ Navbar #########################

navlinks = html.Div(
    [
        dmc.NavLink(
            label="Home",
            icon=get_icon(icon="bi:house-door-fill"),
            href='/'
        ),
        dmc.NavLink(
            label="Sales Performance",
            icon=get_icon(icon="carbon:sales-ops"),
            href='/sales'
            # rightSection=get_icon(icon="tabler-chevron-right"),
        ),
        dmc.NavLink(
            label="Time Series Analysis",
            icon=get_icon(icon="mdi:graph-line"),
            # rightSection=get_icon(icon="tabler-chevron-right"),
        ),
        
    ],
    style={"width": 260},
)

burger = html.Div(
    [
        dmc.Burger(id="burger-button", opened=False, style={"margin-right": "40px"}),
    ],
    style={"display": "flex", "justify-content": "flex-start", "align-items": "center", "padding-right": "20px"}
)


########## Filters
product_multi_select = dmc.MultiSelect(
            label="Product",
            description="Select Product Name",
            placeholder="Select all you like!",
            id="product-select",
            # value=["ng", "vue"],
            data=[{"label": names, "value": names} for names in product_names],
            w=240,
            mb=10,
        ),

category_multi_select = dmc.MultiSelect(
            label="Category",
            description="Select Product Category",
            placeholder="Select all you like!",
            id="category-select",
            # value=["ng", "vue"],
            data=[{"label": category, "value": category} for category in product_categories],
            w=240,
            mb=10,
        ),


location_multi_select = dmc.MultiSelect(
            label="Location",
            description="Select Branch Location",
            placeholder="Select all you like!",
            id="location-select",
            # value=["ng", "vue"],
            data=[{"label": branch, "value": branch} for branch in branches],
            w=240,
            mb=10,
        ),


select_start_date = dmc.DateInput(
            id="start-date",
            label="Enter the Start Date",
            description="Select start date",
            style={"width": 240},
            clearable=True
        )

select_end_date = dmc.DateInput(
            id="end-date",
            label="Enter the End Date",
            description="Select end date",
            style={"width": 230},
            clearable=True

        )

select_quarter = dmc.MultiSelect(
            label="Quarter",
            description="Select quarter",
            placeholder="Select all you like!",
            id="quarter-select",
            # value=["ng", "vue"],
            data=[{"label": quarter, "value": quarter} for quarter in quarter_year],
            w=240,
            mb=10,
        ),
#
# Arrange the components side by side

filter_rows = dbc.Col([
    dbc.Row([
        dbc.Col(select_start_date, width=2),
        dbc.Col(select_end_date, width=2),
        dbc.Col(select_quarter, width=2),
        dbc.Col(category_multi_select, width=2),
        dbc.Col(product_multi_select, width=2),
    ], className="custom-gutter"),
], width={"size": 12, "offset": 1})

filter_row_2 = dbc.Col([
    dbc.Row([
        dbc.Col(location_multi_select, width=2)], className="custom-gutter"),
], width={"size": 12, "offset": 1})

#### Indicators 
indicator_row_1 =dbc.Col([
    dbc.Row([
    ], id="indicator-row-1")]
    ,width={"size": 12, "offset": 1})

indicator_row_2 =dbc.Col([
    dbc.Row([
    ], id="indicator-row-2")]
    ,width={"size": 12, "offset": 1})

# indicator_row_2= dbc.Row([
#     dbc.Col(create_card("Current  Revenue Monthly Growth", "Content for card 3"), width=2)
# ])



app.layout =html.Div(
    [
         dbc.Row([
            dbc.Col([burger],width=1),
            dbc.Col([dmc.Title("MYK Dashboard") ], width=10 )]),
            dmc.Space(h=20),
            filter_rows,
            filter_row_2,
            dmc.Space(h=20),
            indicator_row_1,
            indicator_row_2,
            dmc.Drawer(title="Navigation Bar",id="drawer-simple",  padding="md"
                       , size=280,zIndex=10000,children=[navlinks]),
           dash.page_container,
           dcc.Store(id='intermediate-value'),
           dcc.Store(id='sales-data-value')
    ]


)


@callback(Output("drawer-simple", "opened"),
         Input("burger-button", "opened"))
def open_burger(opened):
    return str(opened), True

@callback(
    Output(component_id='intermediate-value' , component_property='data'),
    Input(component_id='start-date', component_property='value'),
    Input(component_id='end-date', component_property='value'),
    Input(component_id='product-select', component_property='value'),
    Input(component_id='category-select', component_property='value'),
    Input(component_id='location-select', component_property='value'),
    Input(component_id='quarter-select', component_property='value'),

)
def filter_dataframe(date_start=None, date_end=None
                     , product_name=None, product_category=None
                     , location=None, quarter_year=None):
    filtered_df = df.copy()  # Create a copy to avoid modifying the original DataFrame

    # Ensure the date columns in the DataFrame are in datetime format
    if 'date' in filtered_df.columns:
        filtered_df['date'] = pd.to_datetime(filtered_df['date'])

    # Apply filters based on the provided parameters
    if date_start is not None:
        date_start = pd.to_datetime(date_start)
        filtered_df = filtered_df[filtered_df['date'] >= date_start]

    if date_end is not None:
        date_end = pd.to_datetime(date_end)
        filtered_df = filtered_df[filtered_df['date'] <= date_end]

    if product_category is not None and len(product_category) > 0:
        filtered_df = filtered_df[filtered_df['product_type'].isin(product_category)]

    if product_name is not None and len(product_name) > 0:
        filtered_df = filtered_df[filtered_df['clean_product_name'].isin(product_name)]

    if location is not None and len(location) > 0:
        filtered_df = filtered_df[filtered_df['outlet_name'].isin(location)]

    if quarter_year is not None and len(quarter_year) > 0:
        filtered_df = filtered_df[filtered_df['quarter_year'].isin(quarter_year)]

    return Serverside(filtered_df)  # no JSON serialization here


@callback(
    Output(component_id='sales-data-value' , component_property='data'),
    Input(component_id='intermediate-value', component_property='data'),

)
def generate_sales_table(data):
    # Calculate current and last periods
    # df = pd.DataFrame(data)
    df = data.copy()

    current_quarter = df["quarter"].max()
    last_quarter = current_quarter - 1
    current_month = df["month"].max()
    last_month = current_month - 1

    # Filter dataframe once for each period
    df_current_quarter = df[df['quarter'] == current_quarter]
    df_last_quarter = df[df['quarter'] == last_quarter]
    df_current_month = df[df['month'] == current_month]
    df_last_month = df[df['month'] == last_month]

    # Groupby operation for each period
    total_revenue_df = df.groupby(['clean_product_name', 'product_type'])['total_order_amount'].sum().reset_index()
    total_revenue_df = total_revenue_df.rename(columns={'total_order_amount': 'total_revenue'})

    current_quarter_revenue = df_current_quarter.groupby(['clean_product_name', 'product_type'])['total_order_amount']\
        .sum().reset_index().rename(columns={'total_order_amount': 'current_quarter_revenue'})

    last_quarter_revenue = df_last_quarter.groupby(['clean_product_name', 'product_type'])['total_order_amount']\
        .sum().reset_index().rename(columns={'total_order_amount': 'last_quarter_revenue'})

    current_month_revenue = df_current_month.groupby(['clean_product_name', 'product_type'])['total_order_amount']\
        .sum().reset_index().rename(columns={'total_order_amount': 'current_month_revenue'})

    last_month_revenue = df_last_month.groupby(['clean_product_name', 'product_type'])['total_order_amount']\
        .sum().reset_index().rename(columns={'total_order_amount': 'last_month_revenue'})

    # Profit

    # Merge all dataframes into a single dataframe
    sales_performance_df = total_revenue_df.merge(current_quarter_revenue, on=["clean_product_name", "product_type"], how='left')\
        .merge(last_quarter_revenue, on=["clean_product_name", "product_type"], how='left')\
        .merge(current_month_revenue, on=["clean_product_name", "product_type"], how='left')\
        .merge(last_month_revenue, on=["clean_product_name", "product_type"], how='left')

    # Fill NaN values with 0 (if appropriate for your context)
    sales_performance_df = sales_performance_df.fillna(0)

    # Revenue growth
    sales_performance_df['quarterly_growth'] = (sales_performance_df['current_quarter_revenue'] - sales_performance_df['last_quarter_revenue']) / sales_performance_df['last_quarter_revenue'] * 100
    sales_performance_df['monthly_growth'] = (sales_performance_df['current_month_revenue'] - sales_performance_df['last_month_revenue']) / sales_performance_df['last_month_revenue'] * 100
    
    # Calc growth Revenue
    sales_performance_df['quarter_Growth(%)'] = ((sales_performance_df['current_quarter_revenue'] - \
                                         sales_performance_df['last_quarter_revenue']) / (sales_performance_df['current_quarter_revenue'] +  sales_performance_df['last_quarter_revenue'])).round(2)
    sales_performance_df['Monthly_Growth(%)'] = ((sales_performance_df['current_month_revenue'] - \
                                            sales_performance_df['last_month_revenue']) / (sales_performance_df['current_month_revenue'] + sales_performance_df['last_month_revenue'])).round(2)
    return sales_performance_df.to_dict(orient='records')


@callback(
    Output('indicator-row-1', 'children'),
    Output('indicator-row-2', 'children'),
    Input('intermediate-value', 'data'),
)
def update_indicators(data):
    if data is None:
        raise PreventUpdate
    df = data.copy()

    # Get Current Metrics
    total_unit_sold = df['quantity'].sum()
    total_revenue = df['total_order_amount'].sum()
    total_profit = df['profit'].sum()
    total_unique_customers = df["customer_id"].nunique()
    total_orders = df.groupby('order_id').size().count()
    total_unique_customers = df.groupby('customer_id').size().count()
    avg_spending = df["total_order_amount"].mean().round(2)

    # fixed the formatting
    formatted_total_unit_sold = f"{total_unit_sold:,}"
    formatted_total_revenue = f"IDR {total_revenue:,.2f}"
    formatted_total_profit = f"IDR {total_profit:,.2f}"
    formatted_total_unique_customers = f"{total_unique_customers:,}"
    formatted_total_orders = f"{total_orders:,}"
    formatted_avg_spending = f"IDR {avg_spending:,.2f}"

    # Get Growth 
    # replace curr_period with current month from datetime

    unit_growth = get_growth(df, "month", 3, "quantity")
    rev_growth = get_growth(df, "month", 3, "total_order_amount")
    profit_growth = get_growth(df, "month", 3, "profit")
    cust_growth = get_growth(df, "month", 3, "quantity")
    order_growth = get_growth(df, "month", 3, "order_id" , "count")
    avg_spending_growth = get_growth(df, "month", 3, "total_order_amount", "mean")
    
    # Create Cards for the metrics along side with the growth rate
    cols = [
        dbc.Col(create_card("Total Units Sold", formatted_total_unit_sold, unit_growth, "mdi:cart-outline"), width=3, style={"padding": "10px"}),  # Adjust width and padding
        dbc.Col(create_card("Total Orders", formatted_total_orders, order_growth, "mdi:account-group-outline"), width=3, style={"padding": "10px"}),  # Adjust width and padding
        dbc.Col(create_card("Total Revenue", formatted_total_revenue, rev_growth, "mdi:currency-usd"), width=3, style={"padding": "10px"}),  # Adjust width and padding
        dbc.Col(create_card("Total Profit", formatted_total_profit, profit_growth, "mdi:cash-multiple"), width=3, style={"padding": "10px"})  # Adjust width and padding
    ]

    col_2 = [
            dbc.Col(create_card("Average Spending", formatted_avg_spending, avg_spending_growth, "mdi:cash-multiple"), width=3, style={"padding": "10px"}),  # Adjust width and padding
            dbc.Col(create_card("Total Number of Customers", formatted_total_unique_customers, cust_growth, "mdi:account-group-outline"), width=3, style={"padding": "10px"}),  # Adjust width and padding

    ]

    return cols, col_2

if __name__ == '__main__':
    app.run(debug=False)
