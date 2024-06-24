import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import  html
from dash_iconify import DashIconify
import pandas as pd
from datetime import datetime, timedelta

def calculate_growth(current, initial):
    growth_rate = ((current - initial) / initial) * 100
    return round(growth_rate,2)

def get_growth(df, period, curr_period, metric, agg="sum"):
    # replace curr_period with current month from datetime
    """Get growth rate from df
    df: dataframe
    period: Month, Quarter, Week
    curr_period: Growth rate from curr period vs previous period (example Feb growth vs Jan)
    metric: total_profit, total_rev etc
    agg: aggregation function ('sum' or 'mean')
    """
    dff = df.copy()
    
    # Define aggregation functions dictionary
    agg_func = {'sum': 'sum', 'mean': 'mean', 'count': 'count'}

    try:
        # Group by period and apply aggregation function
        grouped_df = dff.groupby([period])[metric].agg(agg_func[agg]).reset_index().sort_values(by=period)
        
        # Pivot the DataFrame
        pivot_df = grouped_df.pivot_table(index=None, columns=period, values=metric, aggfunc=agg_func[agg]).reset_index(drop=True)
        
        current_month_value = pivot_df[curr_period].max()
        previous_month_value = pivot_df[curr_period - 1].max()
        
        return round(calculate_growth(current_month_value, previous_month_value), 1)
    except:
        return "Time period difference less than 30 days"

def calculate_transaction_stats(df):
    # Ensure the date column is in datetime format
    df['date'] = pd.to_datetime(df['date'])

    earliest_date = df.date.min()
    latest_date = df.date.max()

    
    # Calculate the sum and mean of transactions for the current date
    total_rev_sum = df.groupby('order_id')['total_order_amount'].sum().sum()
    total_profit = df['profit'].sum()
    total_avg_spening = df.groupby('order_id')['total_order_amount'].mean().mean()
    total_unique_customers = df["customer_id"].nunique()
    total_orders = df.groupby('order_id').size().count()
    total_unit_sold = df['quantity'].sum()
    
    if (latest_date - earliest_date).days < 30:
        return "Time period less than 30 days"

    # Define the date range for the last 30 days
    last_30_date = latest_date - timedelta(days=30)
    
    # Filter transactions for the last 30 days
    transaction_30_days_before = df[(df['date'] <= last_30_date)]

   
    # Calculate the sum and mean of transactions for the last 30 days
    last_30_days_rev = transaction_30_days_before.groupby('order_id')['total_order_amount'].sum().sum()
    last_30_days_profit = transaction_30_days_before['profit'].sum()
    last_30_days_avg_spening = transaction_30_days_before.groupby('order_id')['total_order_amount'].mean().mean()
    last_30_days_unique_customers = transaction_30_days_before["customer_id"].nunique()
    last_30_days_total_orders = transaction_30_days_before.groupby('order_id').size().count()
    last_30_days_total_unit_sold = transaction_30_days_before['quantity'].sum()

    rev_growth = calculate_growth(total_rev_sum, last_30_days_rev)
    profit_growth = calculate_growth(total_profit, last_30_days_profit)
    avg_spending_growth = calculate_growth(total_avg_spening, last_30_days_avg_spening)
    customer_growth = calculate_growth(total_unique_customers, last_30_days_unique_customers)
    total_orders_growth = calculate_growth(total_orders, last_30_days_total_orders)
    unit_sold_growth = calculate_growth(total_unit_sold, last_30_days_total_unit_sold)

    
    # Return the calculated values
    return {
        'rev_growth': rev_growth,
        'profit_growth': profit_growth,
        'avg_spending_growth': avg_spending_growth,
        'customer_growth': customer_growth,
        'total_orders_growth': total_orders_growth,
        'unit_sold_growth': unit_sold_growth
    }


def get_icon(icon):
    return DashIconify(icon=icon, height=16)

def create_card(title, curr_metric, prev_metric=None, icon=None):
    c = "black"  # Default color
    if prev_metric:
        growth = prev_metric
        if isinstance(growth, str):
            c = "gray"
        elif growth > 0:
            c = "green"
        else:
            c = "red"
    else:
        growth = ""


    # Create card layout
    card = dmc.Card(
        children=[
            html.H6([get_icon(icon), " ", title] if icon else title, className="card-title", style={"textAlign": "center"}),
            html.H4(curr_metric, style={"textAlign": "center"}),
            dmc.Text(f"{growth}%" if growth != "Time period less than 30 days" else f"{growth}", size="sm", c=c, align="center"),
            dmc.Text("vs previous 30 days", size="xs", c="gray", align="center")

        ],
        withBorder=True,
        w=300,
        h=120
    )

    # Add spacing between cards
    card_with_spacing = html.Div([card, html.Div(style={'margin-bottom': '10px'})])
    return card_with_spacing



def create_card_dmc(title, content, button_id, w=700, h=600, add_graph_options=False):
    # Add id for each button
    graph_options = dmc.Group(
        [
            dmc.ActionIcon(
                DashIconify(icon="oui:vis-pie"),
                variant="outline",
                color="blue",
                id="pie_" + button_id
            ),
            dmc.ActionIcon(
                DashIconify(icon="mdi:chart-line"),
                variant="outline",
                color="blue",
                id="line_" + button_id
            ),
            dmc.ActionIcon(
                DashIconify(icon="raphael:barchart"),
                variant="outline",
                color="blue",
                id="bar_" + button_id
            ),
        ]
    )

    button_with_options = html.Div(
        [
            dmc.Button(
                "Generate Insights",
                id=button_id,
                mt="md",
                radius="md",
                variant="gradient",
                gradient={"from": "indigo", "to": "cyan"},
            ),
            html.Div(
                graph_options,
                style={
                    'display': 'inline-block',
                    'verticalAlign': 'bottom',
                    'marginLeft': 'auto',
                    'marginTop': '20px',  # Adjust this value to position the icons lower
                    'float': 'right',
                }
            )
        ],
        style={'display': 'flex', 'justifyContent': 'space-between'}
    )

    card = dmc.Card(
        children=[
            dmc.Text(title, fw=500),
            html.P(content),
            button_with_options
        ],
        withBorder=True,
        ml="sm",
        shadow="sm",
        radius="sm",
        w=w,
        h=h
    )

    card_with_spacing = html.Div([card, html.Div(style={'margin-bottom': '40px'})])
    return card_with_spacing



def create_accordion_label(label, image, description):
    return dmc.AccordionControl(
        dmc.Group(
            [
                dmc.Avatar(src=image, radius="xl", size="lg"),
                html.Div(
                    [
                        dmc.Text(label),
                        dmc.Text(description, size="sm", weight=400, color="dimmed"),
                    ]
                ),
            ]
        )
    )


def create_accordion_content(content):
    return dmc.AccordionPanel(dmc.Text(content, size="sm"))
