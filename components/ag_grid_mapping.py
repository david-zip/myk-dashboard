ag_grid_map = [
    { 'field': 'clean_product_name', 'headerName': 'Product','filter': True},
    { 'field': 'product_type', 'headerName': 'Category','filter': True },
    { 'field': 'total_revenue', 'headerName': 'Total Revenue','filter': True },
    { 'field': 'current_quarter_revenue', 'headerName': 'Current Quarter Revenue','filter': True },
    { 'field': 'last_quarter_revenue', 'headerName': 'Last Quarter Revenue','filter': True },
    { 'field': 'current_month_revenue', 'headerName': 'Current Month Revenue','filter': True },
    { 'field': 'last_month_revenue', 'headerName': 'Last Month Revenue','filter': True },
    { 'field': 'quarter_Growth(%)', 'headerName': 'Quarterly Growth(%)', 'filter': True
     ,'cellStyle': {  "function": "params.value > 0 ? {'color': 'green'} : {'color': 'red'}" } },
    { 'field': 'Monthly_Growth(%)', 'headerName': 'Monthly Growth(%)', 'filter': True, 'cellStyle': {  "function": "params.value > 0 ? {'color': 'green'} : {'color': 'red'}" }},

]