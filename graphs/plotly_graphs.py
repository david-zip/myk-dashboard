import plotly.express as px
import logging
import plotly.io as pio

pio.templates.default = "plotly"
logging.basicConfig(level=logging.DEBUG)


COLOR_DISCRETE_MAP={'Operating': '#1E3B63', 'FID reached': '#FFC000', 'Announced': '#A5A5A5'}

def plot_barchart(df, col, num_products):
    df = df.head(num_products)
    fig = px.bar(df, x=str(col), y='quantity', color=str(col),
                 labels={
                 str(col) :  str(col),
                 "quantity": "Quantity",
              
             })
    fig.update_layout(showlegend=False)
    return fig


def plot_line_chart(df
                    , group_by="hour"
                    , x="None"
                    , y="None"
                    , title=None
                    , sort_by=None
                    , ascending=False):
    try:
        if sort_by:
            agg_df = df.groupby(group_by)['quantity'].sum().reset_index().sort_values(by=sort_by, ascending=ascending)
        else:
            agg_df = df.groupby(group_by)['quantity'].sum().reset_index()

        fig = px.line(agg_df, x=x, y=y, title=title, template="plotly")
        # logging.debug("Line chart created successfully")
        return fig
    except Exception as e:
        # logging.error(f"Error creating plot: {e}")
        raise


def plot_pie_chart(df, group_by="category", values="quantity", title=None, sort_by=None, ascending=False):
    """
    Creates a pie chart using Plotly.

    Parameters:
    - df: pandas DataFrame containing the data
    - group_by: column name to group the data by (default is "category")
    - values: column name for the values (default is "quantity")
    - title: title of the chart (default is None)
    - sort_by: column name to sort the data by (default is None)
    - ascending: boolean to sort in ascending order (default is False)

    Returns:
    - fig: Plotly figure object
    """
    try:
        if sort_by:
            agg_df = df.groupby(group_by)[values].sum().reset_index().sort_values(by=sort_by, ascending=ascending)
        else:
            agg_df = df.groupby(group_by)[values].sum().reset_index()

        fig = px.pie(agg_df, names=group_by, values=values, title=title, template="plotly")
        return fig
    except Exception as e:
        raise e


def bar_chart_vertical(
    data,
    x,
    y,
    color,
    color_discrete_map=COLOR_DISCRETE_MAP,
    x_text=None,
    y_text=None,
    title_text=None,
    text=None,
    facet_row=None,
):
    fig_ = px.bar(
        data,
        x=x,
        y=y,
        facet_row=facet_row,
        color=color,
        color_discrete_map=color_discrete_map,
        orientation="h",
        text=text,
        #sort=False,
    )

    fig_.update_layout(
        titlefont=dict(size=12, color="black"),
        title_text=title_text,
        legend_title_text="",
        showlegend=False,
        hovermode="y unified",
        plot_bgcolor="white",
        legend=dict(
            font=dict(size=10, color="black"),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=-0,
        ),
    )

    fig_.update_xaxes(
        title_text=x_text,
        titlefont=dict(size=12, color="black"),
        tickfont=dict(size=10, color="black"),
        title_standoff=3,
        showspikes=False,
        spikemode="across",
        spikesnap="data",
        showline=True,
        showgrid=True,
        fixedrange=True,
        linewidth=1,
        linecolor="grey",
    )

    fig_.update_yaxes(
        title_text=y_text,
        titlefont=dict(size=12, color="black"),
        tickfont=dict(size=10, color="black"),
        title_standoff=3,
        fixedrange=True,
        linewidth=1,
        linecolor="grey",
        showgrid=True,
        gridwidth=1,
        gridcolor="whitesmoke",
        rangemode="tozero",
        showspikes=False,
        categoryorder="total ascending",
    )
    fig_.update_traces(texttemplate="%{x:,.0f}", textposition="inside")
    fig_.update_layout(uniformtext_minsize=8, uniformtext_mode="hide" )
    fig_.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig_


def plot_chart(
              data
             ,chart_type
             ,x=None
             ,y=None
             ,group_by=None
             ,sort_by=None
             ,ascending=True
             ):

    if chart_type == "pie":
        return plot_pie_chart(data, group_by="category", values="quantity", title=None, sort_by=None, ascending=False)
    
    elif chart_type == "line":
        return plot_line_chart(df=data, group_by=group_by, x=x
                         ,y=y, sort_by=sort_by, ascending=True)
    
    else:
        return bar_chart_vertical(data=data, x=x, y=y, color=x)