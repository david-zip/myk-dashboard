import pandas as pd
from pandas.tseries.offsets import QuarterBegin, QuarterEnd

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

def generate_quarter_dict(start_year, end_year):
    quarter_dict = {}
    for year in range(start_year, end_year + 1):
        for quarter in range(1, 5):
            quarter_label = f"Q{quarter}-{year}"
            start_date = pd.Timestamp(f"{year}-01-01") + QuarterBegin(startingMonth=1) * (quarter - 1)
            end_date = start_date + QuarterEnd()
            quarter_dict[quarter_label] = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
    return quarter_dict

start_year = 2017
end_year = 2025
quarter_dates = generate_quarter_dict(start_year, end_year)
