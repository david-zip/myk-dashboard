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
        logging.debug("Line chart created successfully")
        return fig
    except Exception as e:
        logging.error(f"Error creating plot: {e}")
        raise


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
        titlefont=dict(family="Calibri", size=12, color="black"),
        title_text=title_text,
        legend_title_text="",
        showlegend=False,
        hovermode="y unified",
        plot_bgcolor="white",
        legend=dict(
            font=dict(family="Calibri", size=10, color="black"),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=-0,
        ),
    )

    fig_.update_xaxes(
        title_text=x_text,
        titlefont=dict(family="Calibri", size=12, color="black"),
        tickfont=dict(family="Calibri", size=10, color="black"),
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
        titlefont=dict(family="Calibri", size=12, color="black"),
        tickfont=dict(family="Calibri", size=10, color="black"),
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