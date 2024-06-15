import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import  html
from dash_iconify import DashIconify


def calculate_growth(current, initial):
    growth_rate = ((current - initial) / initial) * 100
    return growth_rate

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

    # Group by period and apply aggregation function
    grouped_df = dff.groupby([period])[metric].agg(agg_func[agg]).reset_index().sort_values(by=period)
    
    # Pivot the DataFrame
    pivot_df = grouped_df.pivot_table(index=None, columns=period, values=metric, aggfunc=agg_func[agg]).reset_index(drop=True)
    
    current_month_value = pivot_df[curr_period].max()
    previous_month_value = pivot_df[curr_period - 1].max()
    
    return round(calculate_growth(current_month_value, previous_month_value), 1)

def get_growth_30_days(df, date_column, metric, agg="sum"):
    """Get growth rate from df for the last 30 days compared to the previous 30 days.
    
    df: DataFrame
    date_column: Date column in the DataFrame
    metric: Metric to calculate growth rate for (e.g., total_profit, total_rev)
    agg: Aggregation function ('sum' or 'mean')
    """
    # Ensure date column is in datetime format
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Define aggregation functions dictionary
    agg_func = {'sum': 'sum', 'mean': 'mean', 'count': 'count'}
    
    # Filter the last 60 days
    end_date = df[date_column].max()
    start_date = end_date - pd.Timedelta(days=60)
    recent_df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
    
    # Calculate the total or mean for the last 30 days and the previous 30 days
    last_30_days_end = end_date
    last_30_days_start = last_30_days_end - pd.Timedelta(days=30)
    prev_30_days_end = last_30_days_start - pd.Timedelta(days=1)
    prev_30_days_start = prev_30_days_end - pd.Timedelta(days=30)
    
    last_30_days_df = recent_df[(recent_df[date_column] > last_30_days_start) & (recent_df[date_column] <= last_30_days_end)]
    prev_30_days_df = recent_df[(recent_df[date_column] >= prev_30_days_start) & (recent_df[date_column] <= prev_30_days_end)]
    
    last_30_days_value = last_30_days_df[metric].agg(agg_func[agg])
    prev_30_days_value = prev_30_days_df[metric].agg(agg_func[agg])
    
    return round(calculate_growth(last_30_days_value, prev_30_days_value), 1)

def get_icon(icon):
    return DashIconify(icon=icon, height=16)

def create_card(title, curr_metric, prev_metric=None, icon=None):
    # Determine growth and color
    if prev_metric:
        growth = prev_metric
        if growth > 0:
            c = "green"
        else:
            c = "red"
    else:
        growth = ""
        c = "black"

    # Create card layout
    card = dmc.Card(
        children=[
            html.H6([get_icon(icon), " ", title] if icon else title, className="card-title", style={"textAlign": "center"}),
            html.H4(curr_metric, style={"textAlign": "center"}),
            dmc.Text(f"{growth}%", c=c, align="center"),
            dmc.Text("vs previous 30 days", size="xs", c="gray", align="center")

        ],
        withBorder=True,
        w=300,
        h=120
    )

    # Add spacing between cards
    card_with_spacing = html.Div([card, html.Div(style={'margin-bottom': '10px'})])
    return card_with_spacing



def create_card_dmc(title, content, button_id, w=700, h=600):
    # add id for each button
    card = dmc.Card(
    children=[
        dmc.Text(title, fw=500),
        html.P(content),
        dmc.Button(
            "Generate Insights",
            id=button_id,
            mt="md",
            radius="md",
            variant="gradient",
            gradient={"from": "indigo", "to": "cyan"},
        ),
    ],
    withBorder=True,
    ml="sm",
    shadow="sm",
    radius="sm",
    
    w=w, #780
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
