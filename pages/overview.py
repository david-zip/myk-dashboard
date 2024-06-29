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
 


llm_output_df = pd.read_csv("data/llm_output.csv")

def transform_prompt_output_to_accordion(data, graph_name):
    images = "/assets/png-transparent-honda-insight-customer-insight-management-service-service-industry-miscellaneous-company-building-thumbnail.png"
    prompt_list = []
    graph_name = graph_name
    filtered_df = data[data["graph_name"] == graph_name]
    i = 1
    for _, row in filtered_df.iterrows():
        prompt_output = {
            "id": "",
            "image": images,
            "label": f"Weekly Insight {i}",
            "description": row["prompt"],
            "response": row["response"]
        }
        prompt_list.append(prompt_output)
        i += 1

    accordion_items = []

    for index, prompt in enumerate(prompt_list):
        label = create_accordion_label(prompt["label"], prompt["image"], prompt["description"])
        content = create_accordion_content(prompt["response"])
        accordion_item = dmc.AccordionItem(
            children=[label, content],  # Combine label and content as children
            value=str(index + 1)  # Using the index as a unique value
        )
        accordion_items.append(accordion_item)

    return accordion_items

# TEMP
images= "/assets/png-transparent-honda-insight-customer-insight-management-service-service-industry-miscellaneous-company-building-thumbnail.png"


graphs = dbc.Col([
    dbc.Row([
        dbc.Col(
            create_card_dmc("Top Selling Product by Quantity", dcc.Loading(dcc.Graph(id='top-product-bar')), "product-bar-button"),
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
                id="accordion-item",
                children=[],
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
    [
        Output("modal-simple", "opened"),
        Output("modal-title", "children"),
        Output("accordion-item", "children"),
    ],
    [
        Input("product-bar-button", "n_clicks"),
        Input("monthly-category-button", "n_clicks"),
        Input("monthly-q-button", "n_clicks"),
        Input("daily-q-button", "n_clicks"),
        Input("modal-close-button", "n_clicks"),
        Input("modal-submit-button", "n_clicks"),
    ],
    [State("modal-simple", "opened")],
    prevent_initial_call=True,
)
def modal_demo(nc1, nc2, nc3, nc4, nc5, nc6, opened):
    button_id = ctx.triggered_id if ctx.triggered_id else 'No clicks yet'
    if button_id in ["product-bar-button", "monthly-category-button", "monthly-q-button", "daily-q-button"]:
        title_map = {
            "product-bar-button": "Bar graph Insights",
            "monthly-category-button": "Monthly Category Insights",
            "monthly-q-button": "Pie Chart Insights",
            "daily-q-button": "Daily Quantity Insights"
        }
        title = title_map.get(button_id)
        if title == "Bar graph Insights":
            graph_name = "top product by category sold"
       
        elif title == "Monthly Category Insight":
            graph_name = "top product by category sold"
        
        elif title == "Pie Chart Insights":
            graph_name = "top product by quantity sold"
        
        elif title == "Daily Quantity Insights":
            graph_name = "sales"

        accordion_child = transform_prompt_output_to_accordion(llm_output_df, graph_name)
        return not opened, title, accordion_child
    return not opened, dash.no_update, dash.no_update

# @callback(
#     Output("modal-simple", "opened"),
#     Output("modal-title", "children"),
#     Output("accordion-item", "children"),

#     Input("product-bar-button", "n_clicks"),
#     Input("monthly-category-button", "n_clicks"),
#     Input("monthly-q-button", "n_clicks"),
#     Input("daily-q-button", "n_clicks"),
#     Input("modal-close-button", "n_clicks"),
#     Input("modal-submit-button", "n_clicks"),
#     State("modal-simple", "opened"),
#     prevent_initial_call=True,
# )
# def modal_demo(nc1, nc2, nc3, nc4, nc5, nc6, opened):
#     button_id = ctx.triggered_id if not None else 'No clicks yet'
#     print(button_id)
#     if button_id == "product-bar-button":
        
#         title = "Bar graph Insights"
#         graph_name = "top product by category sold"
#         accordion_child = transform_prompt_output_to_accordion(llm_output_df, graph_name)
        
#         return not opened, title, accordion_child
    
#     elif button_id == "monthly-category-button":
        
#         title = "Monthly Category Insights"
#         graph_name = "top product by category sold"
#         accordion_child = transform_prompt_output_to_accordion(llm_output_df, graph_name)
        
#         return not opened, title, accordion_child
    
#     elif button_id == "monthly-q-button":
        
#         title = "Pie Chart Insights"
#         graph_name = "top product by category sold"
#         accordion_child = transform_prompt_output_to_accordion(llm_output_df, graph_name)
        
#         return not opened, title, accordion_child
    
#     elif button_id == "daily-q-button":
        
#         title = "Daily Quanity Insights"
#         graph_name = "top product by category sold"
#         accordion_child = transform_prompt_output_to_accordion(llm_output_df, graph_name)
        
#         return not opened, title, accordion_child
#     return not opened
