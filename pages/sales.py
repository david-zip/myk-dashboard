import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px
from dash_extensions.enrich import Output, Input, html, dcc, \
     callback, ctx, html, State
import json
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
from components.ag_grid_mapping import ag_grid_map
from components.standard_components import create_card_dmc, create_accordion_content, create_accordion_label
from data_proccessing.utils import *
from graphs.plotly_graphs import bar_chart_vertical




dash.register_page(
    __name__,
    path='/sales',
    title='Our Analytics Dashboard',
    name='Our Analytics Dashboard'
)

# TEMP
characters_list = [
    {
        "id": "bender",
        "image": "https://img.icons8.com/clouds/256/000000/futurama-bender.png",
        "label": "Prompt 1",
        "description": "Tell me what are the top 5 Selling Products",
        "content": "Bender Bending Rodríguez, (born September 4, 2996), designated Bending Unit 22, and commonly "
        "known as Bender, is a bending unit created by a division of MomCorp in Tijuana, Mexico, "
        "and his serial number is 2716057. His mugshot id number is 01473. He is Fry's best friend.",
    },
    {
        "id": "carol",
        "image": "https://img.icons8.com/clouds/256/000000/futurama-mom.png",
        "label": "Prompt 2",
        "description": "Based on this Data, which Cateory of Drinks should I prioritize",
        "content": "Carol Miller (born January 30, 2880), better known as Mom, is the evil chief executive officer "
        "and shareholder of 99.7% of Momcorp, one of the largest industrial conglomerates in the universe "
        "and the source of most of Earth's robots. She is also one of the main antagonists of the Futurama "
        "series.",
    },
    {
        "id": "homer",
        "image": "https://img.icons8.com/clouds/256/000000/homer-simpson.png",
        "label": "Prompt 3",
        "description": "Prompt 3 ",
        "content": "Homer Jay Simpson (born May 12) is the main protagonist and one of the five main characters of "
        "The Simpsons series(or show). He is the spouse of Marge Simpson and father of Bart, "
        "Lisa and Maggie Simpson.",
    },
]


graphs = dbc.Col([
    dbc.Row([
        dbc.Col(
            create_card_dmc("Top Products by Revenue", dcc.Loading(dcc.Graph(id="top-product-rev")), "product-rev-button"),
            width=6,  # Adjusted width to 6
            style={"padding": "10px"}  # Added padding for spacing
        ),
        dbc.Col(
            create_card_dmc("Top Category by Revenue", dcc.Loading(dcc.Graph(id="top-category-rev")), "category-rev-button"),
            width=6,  # Adjusted width to 6 to fit two columns in a row
            style={"padding": "10px"}  # Added padding for spacing
        )
    ]),
      dbc.Row([
        dbc.Col(
            create_card_dmc("Top Products by Profit", dcc.Loading(dcc.Graph(id="top-product-profit")), "product-profit-button"),
            width=6,  # Adjusted width to 6
            style={"padding": "10px"}  # Added padding for spacing
        ),
        dbc.Col(
            create_card_dmc("Top Category by Profit", dcc.Loading(dcc.Graph(id="top-category-profit")), "category-profit-button"),
            width=6,  # Adjusted width to 6 to fit two columns in a row
            style={"padding": "10px"}  # Added padding for spacing
        )
    ]),
    dbc.Row([
        dbc.Col(
            create_card_dmc("Outlet Performance", dcc.Loading(dcc.Graph(id="location-bar")), "outlet-button", h=1200),
            width=6,  # Adjusted width to 6
            style={"padding": "10px"}  # Added padding for spacing
        ),
        dbc.Col(
            create_card_dmc("Outlet Growth Performance", dcc.Loading(dcc.Graph(id="location-growth")), "outlet-growth-button", h=1200),
            width=6,  # Adjusted width to 6 to fit two columns in a row
            style={"padding": "10px"}  # Added padding for spacing
        )
    ]),
    dbc.Row([
        dbc.Col(
            create_card_dmc("Monthly Revenue Patterns", dcc.Loading(dcc.Graph(id="monthly-patterns")), "monthly-rev-button"),
            width=6,  # Adjusted width to 6
            style={"padding": "10px"}  # Added padding for spacing
        ),
        dbc.Col(
            create_card_dmc("Daily Sales Pattern", dcc.Loading(dcc.Graph(id='daily-patterns')), "daily-sales-button"),
            width=6,  # Adjusted width to 6 to fit two columns in a row
            style={"padding": "10px"}  # Added padding for spacing
        )
    ]),
    dbc.Row([
        dbc.Col(
            create_card_dmc("Monthly Revenue Patterns", dcc.Loading(dcc.Graph(id="monthly-growth")), "monthly-growth-button", w=1450),
            width=12,  # Adjusted width to 6
            style={"padding": "10px"} )]),
    dbc.Row([
        dbc.Col(
            create_card_dmc("Daily Average Spending", dcc.Loading(dcc.Graph(id="daily-avg")), "daily-avg-button", w=1450),
            width=12,  # Adjusted width to 6
            style={"padding": "10px"} )])
], width=12)



layout = html.Div([
        dbc.Row([
            dbc.Col([
                dmc.Space(h=40),
                dbc.Row(id='sales-table'),
                dmc.Space(h=40),
                graphs,
                dcc.Store('sales-loc-data'),
            ],  width={"size": 11.5, "offset": 1},)
        ], className="m-0"),
        dmc.Modal(
            title="Generate Insight with AI!",
            id="modal-sales",
            zIndex=10000,
            size="55%",
            children=[
                html.H4("AI Generated Weekly Insights!"),
                html.H6(id="modal-sales-title"),
                dmc.Space(h=20),   
                dmc.Accordion(
                chevronPosition="right",
                variant="contained",
                children=[
                    dmc.AccordionItem(
                        [
                            create_accordion_label(
                                character["label"], character["image"], character["description"]
                            ),
                            create_accordion_content(character["content"]),
                        ],
                        value=character["id"],
                    )
                    for character in characters_list
                ],
            ),
            dmc.Space(h=10),
            html.H4("Write your own prompts"),
            dmc.Textarea(
            label="Ask Questions about this Data",
            placeholder="Tell me about ...",
            style={"width": 800},
            autosize=True,
            minRows=2,
            ),
            dmc.Space(h=10),
            dmc.Group(
                    [
                        dmc.Button("Submit", id="modal-submit-button"),
                        dmc.Button(
                            "Close",
                            color="red",
                            variant="outline",
                            id="modal-close-button",
                        ),
                    ],
                    
                ),

            ],
        ),

])


@callback(
    Output('sales-table', 'children'),
    Input('sales-data-value', 'data')
)
def generate_sales_table(data):
    if data is None:
        raise PreventUpdate
    grid = dag.AgGrid(
        id="get-started-example-basic-df",
        rowData=data,
        columnDefs=ag_grid_map,
        dashGridOptions={'pagination':True},
        style={'width': '100%', 'height': '600px'},  # Adjust width and height as needed

    )
    return grid

@callback(
    Output(component_id='top-product-profit' , component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
)
def plot_top_product_profit(data):
    if data is None:
        raise PreventUpdate
    df = data.copy()
    product_quantity = df.groupby('product_name')['profit'].sum().reset_index()\
        .sort_values(by='profit', ascending=False)
    
    return bar_chart_vertical(product_quantity.head(10), x="profit", y="product_name", color="product_name")

@callback(
    Output(component_id='top-category-profit' , component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
)
def plot_top_cateogry_profit(data):
    if data is None:
        raise PreventUpdate
    # df = pd.DataFrame(data)
    df = data.copy()
    product_quantity = df.groupby('product_type')['profit'].sum().reset_index()\
        .sort_values(by='profit', ascending=False)
    
    return bar_chart_vertical(product_quantity.head(10), x="profit", y="product_type", color="product_type")

@callback(
    Output(component_id='top-product-rev' , component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
)
def plot_top_product_rev(data):
    if data is None:
        raise PreventUpdate
    df = data.copy()
    product_quantity = df.groupby('product_name')['total_amount'].sum().reset_index()\
        .sort_values(by='total_amount', ascending=False)
    return bar_chart_vertical(product_quantity.head(10), x="total_amount", y="product_name", color="product_name")

@callback(
    Output(component_id='top-category-rev' , component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
)
def plot_top_category_rev(data):
    if data is None:
        raise PreventUpdate
    df = data.copy()
    product_quantity = df.groupby('product_type')['total_amount'].sum().reset_index()\
        .sort_values(by='total_amount', ascending=False)
    
    return bar_chart_vertical(product_quantity.head(10), x="total_amount", y="product_type", color="product_type")


@callback(
    Output('location-bar', 'figure'),
    Input('intermediate-value', 'data')
)
def location_bar(data):
    if data is None:
        raise PreventUpdate
    dff = generate_location_df(data)
    fig = px.bar(dff, x="month_name", y="quantity", barmode="group"
                ,facet_col="outlet_name", facet_col_wrap=2
                , hover_data=dff.columns.to_list(), template='ggplot2'
                ,height=1000)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(plot_bgcolor='white')
    return fig

@callback(
    Output('location-growth', 'figure'),
    Input('intermediate-value', 'data')
)
def location_growth(data):
    if data is None:
        raise PreventUpdate
    dff = generate_location_df(data)
    fig = px.line(dff,  x="month", y='growth_rate'
                     , facet_col="outlet_name"
                     , facet_col_wrap=2, height=1000)
    fig.update_yaxes(range=[-100, 100])
    return fig

@callback(
    Output('monthly-patterns', 'figure'),
    Input('intermediate-value', 'data')
)
def monthly_patterns(data):
    if data is None:
        raise PreventUpdate
    dff =  data
    agg_df = dff.groupby(["month", "month_name", "week_of_month"])['quantity'].sum().reset_index()
    fig = px.line(agg_df, x="week_of_month"
                 , y='quantity', facet_col="month_name"
                 , facet_col_wrap=3)
    return fig

@callback(
    Output('daily-patterns', 'figure'),
    Input('intermediate-value', 'data')
)
def daily_patterns(data):
    if data is None:
        raise PreventUpdate
    dff = data
    agg_df = dff.groupby(["day_of_week_num", "day_name", "hour"])['quantity'].sum().reset_index()
    fig = px.line(agg_df, x="hour", y='quantity', facet_col="day_name", facet_col_wrap=3)
    return fig

@callback(
    Output('monthly-growth', 'figure'),
    Input('intermediate-value', 'data')
)
def monthly_growth(data):
    dff = data.copy()
    monthly_data = dff.groupby(['month']).agg({'total_amount': 'sum', 'profit': 'sum'}).reset_index().sort_values(by="month")
    monthly_data.dropna(inplace=True)
    
    monthly_data['revenue_growth_pct'] = monthly_data['total_amount'].pct_change() * 100
    monthly_data['profit_growth_pct'] = monthly_data['profit'].pct_change() * 100
    
    # Calculate month-over-month growth percentage for each product for both revenue and profit
    monthly_data.dropna(inplace=True)
    fig = px.line(monthly_data, x='month', y=["revenue_growth_pct", "profit_growth_pct"], width=1200)
    return fig

@callback(
    Output('daily-avg', 'figure'),
    Input('intermediate-value', 'data')
)
def daily_avg(data):
    dff = data.copy()
    daily_average = dff.groupby(['date', 'order_id'])['total_order_amount'].sum().reset_index()

    # Group by month to get the average of these summed amounts
    daily_avg = daily_average.groupby('date')['total_order_amount'].mean().reset_index()

    # Rename the columns for clarity
    daily_avg.columns = ['date', 'average_order_amount']
    fig = px.line(daily_avg, x='date', y=["average_order_amount"])
    return fig


@callback(
    Output("modal-sales", "opened"),
    Output("modal-sales-title", "children"),

    Input("outlet-button", "n_clicks"),
    Input("outlet-growth-button", "n_clicks"),
    Input("monthly-rev-button", "n_clicks"),
    Input("daily-sales-button", "n_clicks"),
    Input("modal-close-button", "n_clicks"),
    Input("modal-submit-button", "n_clicks"),
    State("modal-sales", "opened"),
    prevent_initial_call=True,
)
def modal_demo(nc1, nc2, nc3, nc4, nc5, nc6, opened):
    #outler-button, monthly-category-button, monthly-sales-pattern, daily-sales-button
    # # outlet-growth-button, monthly-rev-button", daily-sales-button


    button_id = ctx.triggered_id if not None else 'No clicks yet'
    print(button_id)
    if button_id == "outlet-button":
        title = "Outler Performance Insights"
        return not opened, title
    
    elif button_id == "outlet-growth-button":
        title = "Outler Growth Insights"
        return not opened, title
    
    
    elif button_id == "monthly-rev-button":
        title = "Monthly Revenue Insights"
        return not opened, title
    
    elif button_id == "daily-sales-button":
        title = "Daily Sales Insights"
        return not opened, title
    return not opened

