"""
Temp util files to test LLM invocations

** Finalise code
** Refactor
** Get LLM to create sample prompts based on db 

"""
import pandas as pd

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
    return sales_performance_df

def generate_location_df(data):
    df = data.copy()
    # df = df[df['outlet_name'].isin(['Bekasi', 'Jaksel', 'Cibubur', 'Jakut', 'Tangerang', 'Bandung' ])]
    sales_loc_df = df.groupby(["outlet_name", "year", "month_name", "month"])["quantity"].sum().reset_index()
    sales_loc_df = sales_loc_df.sort_values(by=["year", "month", "quantity"], ascending=[True, True, False])
    sales_loc_df = sales_loc_df.sort_values(by=['outlet_name', 'year', 'month'])

    # Step 2: Calculate the difference in quantity between consecutive months for each location
    sales_loc_df['quantity_diff'] = sales_loc_df.groupby('outlet_name')['quantity'].diff()

    # Step 3: Calculate the growth rate
    sales_loc_df['growth_rate'] = (sales_loc_df['quantity_diff'] / sales_loc_df['quantity'].shift()) * 100
    return sales_loc_df