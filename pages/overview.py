import dash
import dash_bootstrap_components as dbc
import pandas as pd
import dash_mantine_components as dmc
import plotly.express as px
from dash import html, ctx
from dash_extensions.enrich import Output, Input, State, html, dcc, callback
from dash.exceptions import PreventUpdate
from components.standard_components import create_card_dmc, create_accordion_label, create_accordion_content
from graphs.plotly_graphs import bar_chart_vertical, plot_barchart, plot_line_chart
import boto3


dash.register_page(
    __name__,
    path='/',
    title='Our Analytics Dashboard',
    name='Our Analytics Dashboard'
)
 
df = pd.read_excel("data/full_iseller_data.xlsx")

product_quantity = df.groupby('product_name')['quantity'].sum().reset_index()\
    .sort_values(by='quantity', ascending=False)

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
            create_card_dmc("Top Selling Product by Quantity", dcc.Loading(dcc.Graph(id='top-product-bar')), "bar-button"),
            width=6,  # Width set to 6 to allow two columns in a row
            style={"padding": "8px"}  # Adjust padding as needed
        ),
        dbc.Col(
            create_card_dmc("Top Selling Category by Quantity", dcc.Loading(dcc.Graph(id='top-category-bar')), "monthly-category-button"),
            width=6,  # Width set to 6 to allow two columns in a row
            style={"padding": "10px"}  # Adjust padding as needed
        )
    ]),
    dbc.Row([
        dbc.Col(
            create_card_dmc("Monthly Sales by Quantity", dcc.Loading(dcc.Graph(id='month-line-graph')), "monthly-q-button"),
            width=6,  # Adjust width as needed
            style={"padding": "8px"}  # Adjust padding as needed
        ),
        dbc.Col(
            create_card_dmc("Daily Sales by Quantity", dcc.Loading(dcc.Graph(id='daily-line-graph')), "daily-q-button"),
            width=6,  # Adjust width as needed
            style={"padding": "10px"}  # Adjust padding as needed
        )
    ]),
 
], width=12)



# Create a Dash app layout
layout = html.Div([
        dbc.Row([
            dbc.Col([
                dmc.Space(h=20),
                graphs,
            ],  width={"size": 12, "offset": 1},)
        ], className="m-0"),
         dmc.Modal(
            title="Generate Insight with AI!",
            id="modal-simple",
            zIndex=10000,
            size="55%",
            children=[
                html.H4("AI Generated Weekly Insights!"),
                html.H6(id="modal-title"),
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
    Output(component_id='daily-line-graph' , component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
)
def plot_daily_sales(data):
    if data is None:
        raise PreventUpdate
    # df = pd.DataFrame(data)
    df = data.copy()
    # print("DATA", dff.head())
    fig = plot_line_chart(df=df, group_by=['day_name', 'day_of_week_num'], x="day_name"
                                       , y="quantity"
                                       , sort_by="day_of_week_num", ascending=True)
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig

@callback(
    Output(component_id='top-product-bar' , component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
)
def plot_top_product_quant(data):
    if data is None:
        raise PreventUpdate
    # df = pd.DataFrame(data)
    df = data.copy()
    product_quantity = df.groupby('product_name')['quantity'].sum().reset_index()\
        .sort_values(by='quantity', ascending=False)
    
    return bar_chart_vertical(product_quantity.head(10), x="quantity", y="product_name", color="product_name")


# top-product-bar, top-category-bar
@callback(
    Output(component_id='top-category-bar' , component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
)
def plot_top_product_category(data):
    if data is None:
        raise PreventUpdate
    # df = pd.DataFrame(data)
    df = data.copy()
    product_quantity = df.groupby('product_type')['quantity'].sum().reset_index()\
        .sort_values(by='quantity', ascending=False)
    
    fig = plot_barchart(product_quantity, 'product_type', 10)
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig

@callback(
    Output(component_id='month-line-graph' , component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
)
def plot_monthly_sales(data):
    if data is None:
        raise PreventUpdate
    # df = pd.DataFrame(data)
    df = data.copy()

    # print("DATA", dff.head())
    fig = plot_line_chart(df, group_by='month', x='month', y='quantity')
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig

@callback(
    Output("modal-simple", "opened"),
    Output("modal-title", "children"),

    Input("bar-button", "n_clicks"),
    Input("monthly-category-button", "n_clicks"),
    Input("monthly-q-button", "n_clicks"),
    Input("daily-q-button", "n_clicks"),
    Input("modal-close-button", "n_clicks"),
    Input("modal-submit-button", "n_clicks"),
    State("modal-simple", "opened"),
    prevent_initial_call=True,
)
def modal_demo(nc1, nc2, nc3, nc4, nc5, nc6, opened):
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    print(button_id)
    if button_id == "bar-button":
        title = "Bar graph Insights"
        return not opened, title
    
    elif button_id == "monthly-category-button":
        title = "Monthly Category Insights"
        return not opened, title
    
    elif button_id == "monthly-q-button":
        title = "Pie Chart Insights"
        return not opened, title
    
    elif button_id == "daily-q-button":
        title = "Daily Quanity Insights"
        return not opened, title
    return not opened
