import pandas as pd

def WeekOfMonth(date):
    first_day_of_month = date.replace(day=1)
    day_of_week_first_day = first_day_of_month.weekday()
    week_number = (date.day + day_of_week_first_day - 1) // 7 + 1
    return week_number

def generate_location_df(data):
    df = data.copy()
    # df = df[df['outlet_name'].isin(['Bekasi', 'Jaksel', 'Cibubur', 'Jakut', 'Tangerang', 'Bandung' ])]
    sales_loc_df = df.groupby(["outlet_name", "month_name", "month"])["quantity"].sum().reset_index()
    sales_loc_df = sales_loc_df.sort_values(by=["month", "quantity"], ascending=[True, False])
    sales_loc_df = sales_loc_df.sort_values(by=['outlet_name', 'month'])

    # Step 2: Calculate the difference in quantity between consecutive months for each location
    sales_loc_df['quantity_diff'] = sales_loc_df.groupby('outlet_name')['quantity'].diff()

    # Step 3: Calculate the growth rate
    sales_loc_df['growth_rate'] = (sales_loc_df['quantity_diff'] / sales_loc_df['quantity'].shift()) * 100
    return sales_loc_df