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
            html.H6([get_icon(icon), " ", title] if icon else title, className="card-title"),
            html.H4(curr_metric),
            dmc.Text(f"{growth}%", c=c),
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
