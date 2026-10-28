# [Option A] Sales Performance and Customer Insights

import pandas as pd
import plotly.express as px
import streamlit as st


# [Checkpoint 1] Page Configuration

st.set_page_config(
    page_title = 'Retail Sales Dashboard',
    page_icon = '📈',
    layout = 'wide',
)

st.title('📈 Retail Sales Dashboard')

st.caption(
    'Interactive analysis of fulfilled retail orders '
    '(completed and shipped)'
)


# [Checkpoint 2] Helper Function for Numeric Cleaning

def clean_money(series):
    """
    Convert values such as:

        1,250.50
        ₱1,250.50
        1250.50

    into numeric values.

    Invalid values become NaN.
    """

    return pd.to_numeric(
        series.astype('string')
        .str.replace('₱', '', regex = False)
        .str.replace(',', '', regex = False)
        .str.strip(),
        errors = 'coerce',
    )


# [Checkpoint 3] Load and Prepare the Original Retail Data

@st.cache_data
def load_and_prepare_data():

    # [Checkpoint 3A] Read the Original CSV Files

    customers = pd.read_csv(
        'data/customers.csv'
    )

    products = pd.read_csv(
        'data/products.csv'
    )

    orders = pd.read_csv(
        'data/orders.csv'
    )

    items = pd.read_csv(
        'data/order_items.csv'
    )

    returns = pd.read_csv(
        'data/returns.csv'
    )


    # [Checkpoint 3B] Remove Exact Duplicates

    customers = (
        customers
        .drop_duplicates()
        .copy()
    )

    products = (
        products
        .drop_duplicates()
        .copy()
    )

    orders = (
        orders
        .drop_duplicates()
        .copy()
    )

    items = (
        items
        .drop_duplicates()
        .copy()
    )

    returns = (
        returns
        .drop_duplicates()
        .copy()
    )


    # [Checkpoint 3C] Clean Product Categories

    category_map = {

        'electronics': 'Electronics',
        'elec': 'Electronics',

        'home & kitchen': 'Home & Kitchen',
        'home and kitchen': 'Home & Kitchen',

        'books': 'Books',
        'book': 'Books',

        'groceries': 'Groceries',
        'grocery': 'Groceries',

        'toys': 'Toys',
        'toy': 'Toys',

        'beauty': 'Beauty',
        'beauty & care': 'Beauty',

        'fashion': 'Fashion',
        'fashon': 'Fashion',

        'sports': 'Sports',
        'sports & outdoor': 'Sports',
    }


    products['category_clean'] = (

        products['category']

        .astype('string')

        .str.strip()

        .str.lower()

        .replace(category_map)

        .fillna('Unknown')
    )


    # [Checkpoint 3D] Clean Order Item Values

    items['quantity'] = pd.to_numeric(
        items['quantity'],
        errors = 'coerce',
    )


    items['unit_price_clean'] = clean_money(
        items['unit_price_at_purchase']
    )


    # Keep valid quantity and price rows only

    items = items[
        (items['quantity'] > 0)
        &
        items['unit_price_clean'].notna()
    ].copy()


    # [Checkpoint 3E] Clean Orders

    # Your dataset contains several date formats.
    # format = 'mixed' allows Pandas to interpret them.

    orders['order_date'] = pd.to_datetime(
        orders['order_datetime'],
        format = 'mixed',
        errors = 'coerce',
    )


    # Convert discount to numeric

    orders['discount_pct'] = pd.to_numeric(
        orders['discount_pct'],
        errors = 'coerce',
    )


    # Missing discount means no discount

    orders['discount_pct'] = (
        orders['discount_pct']
        .fillna(0)
    )


    # Convert shipping fee

    orders['shipping_fee'] = pd.to_numeric(
        orders['shipping_fee'],
        errors = 'coerce',
    )


    # Keep valid discount percentages only
    # Example:
    # 0.10 = 10%
    # 0.25 = 25%

    orders.loc[
        ~orders['discount_pct'].between(
            0,
            1
        ),
        'discount_pct'
    ] = 0


    # [Checkpoint 3F] Referential Integrity

    # Remove orders whose customer_id does not exist
    # in the customer master file.

    orders = orders[
        orders['customer_id'].isin(
            customers['customer_id']
        )
    ].copy()


    # Remove order items whose product does not exist

    items = items[
        items['product_id'].isin(
            products['product_id']
        )
    ].copy()


    # Remove order items whose order does not exist

    items = items[
        items['order_id'].isin(
            orders['order_id']
        )
    ].copy()


    # [Checkpoint 3G] Build Item-level Analytical Dataframe

    sales = (

        items

        .merge(
            orders,
            on = 'order_id',
            how = 'inner',
            validate = 'many_to_one',
        )

        .merge(
            products[
                [
                    'product_id',
                    'product_name',
                    'brand',
                    'category_clean',
                ]
            ],
            on = 'product_id',
            how = 'inner',
            validate = 'many_to_one',
        )

        .merge(
            customers[
                [
                    'customer_id',
                    'region_name',
                    'city',
                    'loyalty_tier',
                ]
            ],
            on = 'customer_id',
            how = 'left',
            validate = 'many_to_one',
        )

        .merge(
            returns,
            on = 'order_id',
            how = 'left',
            validate = 'many_to_one',
        )
    )


    # [Checkpoint 3H] Create Analytical Fields

    # Gross Sales
    #
    # Quantity × Unit Price

    sales['gross_sales'] = (

        sales['quantity']

        *

        sales['unit_price_clean']
    )


    # Net Sales
    #
    # Gross Sales after Discount

    sales['net_sales'] = (

        sales['gross_sales']

        *

        (
            1
            -
            sales['discount_pct']
        )
    )


    # Create Month Column

    sales['month'] = (

        sales['order_date']

        .dt.to_period('M')

        .astype('string')
    )


    # [Checkpoint 3I] Keep Only Fulfilled Orders

    fulfilled_sales = sales[

        sales['order_status'].isin(
            [
                'Completed',
                'Shipped',
            ]
        )

    ].copy()


    # Remove rows with unparseable dates

    fulfilled_sales = fulfilled_sales[

        fulfilled_sales[
            'order_date'
        ].notna()

    ].copy()


    return fulfilled_sales


# [Checkpoint 4] Load Data

try:

    sales = load_and_prepare_data()

except FileNotFoundError as error:

    st.error(
        'A required CSV file was not found. '
        'Check your data folder and filenames.'
    )

    st.code(
        """
data/
├── customers.csv
├── products.csv
├── orders.csv
├── order_items.csv
└── returns.csv
        """
    )

    st.exception(error)

    st.stop()


# [Checkpoint 5] Sidebar Filters

st.markdown("""
    <style>
    [data-testid = 'stSidebar'] {
        color: white;
    }

    [data-testid = 'stSidebar'] h1,
    [data-testid = 'stSidebar'] h2,
    [data-testid = 'stSidebar'] h3,
    [data-testid = 'stSidebar'] label,
    [data-testid = 'stSidebar'] p,
    [data-testid = 'stSidebar'] span {
        color: white;
    }
    </style>
    """, unsafe_allow_html = True)

st.sidebar.header(
    'Dashboard Filters'
)


# Month

month_options = [

    'All'

] + sorted(

    sales['month']

    .dropna()

    .astype(str)

    .unique()

    .tolist()
)


# Region

region_options = [

    'All'

] + sorted(

    sales['region_name']

    .dropna()

    .astype(str)

    .unique()

    .tolist()
)


# Sales Channel

channel_options = [

    'All'

] + sorted(

    sales['sales_channel']

    .dropna()

    .astype(str)

    .unique()

    .tolist()
)


# Product Category

category_options = [

    'All'

] + sorted(

    sales['category_clean']

    .dropna()

    .astype(str)

    .unique()

    .tolist()
)


# Display filters

st.markdown("""
    <style>
        [data-testid = stSidebar] {
            background-color: #008080;
        }
    </style>
""", unsafe_allow_html = True)

selected_month = st.sidebar.selectbox(
    'Month',
    month_options,
)


selected_region = st.sidebar.selectbox(
    'Region',
    region_options,
)


selected_channel = st.sidebar.selectbox(
    'Sales Channel',
    channel_options,
)


selected_category = st.sidebar.selectbox(
    'Product Category',
    category_options,
)


# [Checkpoint 6] Apply Filters

filtered = sales.copy()


if selected_month != 'All':

    filtered = filtered[
        filtered['month']
        ==
        selected_month
    ]


if selected_region != 'All':

    filtered = filtered[
        filtered['region_name']
        ==
        selected_region
    ]


if selected_channel != 'All':

    filtered = filtered[
        filtered['sales_channel']
        ==
        selected_channel
    ]


if selected_category != 'All':

    filtered = filtered[
        filtered['category_clean']
        ==
        selected_category
    ]


# [Checkpoint 7] Handle Empty Filter Results

if filtered.empty:

    st.warning(
        'No records match the selected filters. '
        'Please change one or more filters.'
    )

    st.stop()


# [Checkpoint 8] KPI Calculations


# Gross Sales

total_gross_sales = (
    filtered['gross_sales']
    .sum()
)


# Net Sales

total_net_sales = (
    filtered['net_sales']
    .sum()
)


# Number of Unique Orders

order_count = (

    filtered['order_id']

    .nunique()
)


# Average Order Value

order_values = (

    filtered

    .groupby(
        'order_id',
        as_index = False,
    )['net_sales']

    .sum()

    .rename(
        columns = {
            'net_sales':
            'order_value'
        }
    )
)


aov = (
    order_values[
        'order_value'
    ]
    .mean()
)


# Top Category

top_category = (

    filtered

    .groupby(
        'category_clean'
    )['gross_sales']

    .sum()

    .idxmax()
)


# Repeat and New Customers

repeat_customers = (
    filtered['customer_id'].duplicated().sum()
)

new_customers = (
    filtered['customer_id'].nunique()
)


# [Checkpoint 9] KPI Cards

st.markdown("""
    <style>
    div[data-testid = 'stMetric'] {
        background-color: teal;
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: white;
    }
    </style>
    """, unsafe_allow_html = True)

st.subheader(
    'Key Performance Indicators'
)


kpi1, kpi2, kpi3, kpi4 = (
    st.columns(4)
)


kpi1.metric(
    'Gross Sales',
    f'🪙 PHP {total_gross_sales:,.2f}',
)


kpi2.metric(
    'Fulfilled Orders',
    f'📦 {order_count:,}',
)


kpi3.metric(
    'Average Order Value',
    f'🏷️ PHP {aov:,.2f}',
)


kpi4.metric(
    'Top Category',
    f'👑 {top_category}',
)


st.caption(
    f'Net Sales after Order Discounts: '
    f'PHP {total_net_sales:,.2f}'
)

st.caption(
    f'Customer Count: '
    f'{repeat_customers:,} Repeat vs. '
    f'{new_customers:,} New'
)


# [Checkpoint 10] Monthly Sales Trend

st.subheader(
    'Sales Trend'
)


monthly_sales = (

    filtered

    .groupby(
        'month',
        as_index = False,
    )['gross_sales']

    .sum()

    .sort_values(
        'month'
    )
)


fig_month_sales = px.line(

    monthly_sales,

    x = 'month',

    y = 'gross_sales',

    markers = True,

    title = '📅 Monthly Gross Sales',

    labels = {
        'month':
        'Month',

        'gross_sales':
        'Gross Sales',
    },
)


fig_month_sales.update_layout(

    yaxis_tickprefix = 'PHP ',

    yaxis_tickformat = ',.0f',
)


fig_month_sales.update_traces(
    
    line_color = 'teal',

    marker = dict(symbol = 'diamond', size = 10)

)


with st.container(border = True):
    st.plotly_chart(
        fig_month_sales,
        width = 'stretch',
    )


# [Checkpoint 11] Category and Region Comparison

left, right = st.columns(2)


# Product Category Sales

category_sales = (

    filtered

    .groupby(
        'category_clean',
        as_index = False,
    )['gross_sales']

    .sum()

    .sort_values(
        'gross_sales'
    )
)


fig_category = px.bar(

    category_sales,

    x = 'gross_sales',

    y = 'category_clean',

    orientation = 'h',

    title = (
        '🛍️ Gross Sales '
        'by Product Category'
    ),

    labels = {
        'gross_sales':
        'Gross Sales',

        'category_clean':
        'Product Category',
    },
)


fig_category.update_layout(

    xaxis_tickprefix = 'PHP ',

    xaxis_tickformat = ',.0f',
)


fig_category.update_traces(marker_color = 'teal')


with left:
    with st.container(border = True):
        st.plotly_chart(
            fig_category,
            width = 'stretch',
        )


# Region Sales

region_sales = (

    filtered

    .groupby(
        'region_name',
        as_index = False,
    )['gross_sales']

    .sum()

    .sort_values(
        'gross_sales'
    )
)


fig_region = px.bar(

    region_sales,

    x = 'gross_sales',

    y = 'region_name',

    orientation = 'h',

    title = '📌 Gross Sales by Region',

    labels = {
        'gross_sales':
        'Gross Sales',

        'region_name':
        'Region',
    },
)


fig_region.update_layout(

    xaxis_tickprefix = 'PHP ',

    xaxis_tickformat = ',.0f',
)


fig_region.update_traces(marker_color = 'teal')


with right:
    with st.container(border = True):
        st.plotly_chart(
            fig_region,
            width = 'stretch',
        )


# [Checkpoint 12] Order Value Distribution

left2, right2 = st.columns(2)


fig_distribution = px.histogram(

    order_values,

    x = 'order_value',

    nbins = 30,

    title = '🔔 Order Value Distribution',

    labels = {
        'order_value':
        'Net Order Value (PHP)',
    },
)


fig_distribution.update_layout(

    xaxis_tickprefix = 'PHP ',

    xaxis_tickformat = ',.0f',

    yaxis_title = (
        'Number of Orders'
    ),
)


fig_distribution.update_traces(
    
    marker_color = 'teal',

    marker_line_color = 'white',
    
    marker_line_width = 1.5
    
)


with left2:
    with st.container(border = True):
        st.plotly_chart(
            fig_distribution,
            width = 'stretch',
        )


# [Checkpoint 13] Sales Channel Comparison

channel_sales = (

    filtered

    .groupby(
        'sales_channel',
        as_index = False,
    )['gross_sales']

    .sum()

    .sort_values(
        'gross_sales',
        ascending = False,
    )
)


fig_channel = px.pie(

    channel_sales,

    names = 'sales_channel',

    values = 'gross_sales',

    hole = 0.5,

    title = (
        '🛒 Gross Sales '
        'by Sales Channel'
    ),

    labels = {
        'sales_channel':
        'Sales Channel',

        'gross_sales':
        'Gross Sales',
    },

)


fig_channel.update_traces(

    marker_colors = [
        'teal',
        'lightseagreen',
        'turquoise',
        'cadetblue',
    ],

    textinfo = 'percent+label',

    hovertemplate = (
        '<b>%{label}</b><br>'
        'Gross Sales: PHP %{value:,.2f}<br>'
        'Share: %{percent}'
        '<extra></extra>'
    ),

)


with right2:
    with st.container(border = True):
        st.plotly_chart(
            fig_channel,
            width = 'stretch',
        )


# [Checkpoint 14] Monthly Returns Trend

st.subheader(
    'Returns Trend'
)


monthly_returns = (

    filtered

    .groupby(
        'month',
        as_index = False,
    )['return_id']

    .count()

    .sort_values(
        'month'
    )
)


fig_month_returns = px.line(

    monthly_returns,

    x = 'month',

    y = 'return_id',

    markers = True,

    title = '📅 Monthly Return Count',

    labels = {
        'month':
        'Month',

        'return_id':
        'Return Count',
    },
)


fig_month_returns.update_layout(

    yaxis_tickformat = ',.0f',
)


fig_month_returns.update_traces(
    
    line_color = '#800000',

    marker = dict(symbol = 'cross', size = 10)

)


with st.container(border = True):
    st.plotly_chart(
        fig_month_returns,
        width = 'stretch',
    )


# [Checkpoint 15] Top Products

st.subheader(
    'Top Products'
)


top_products = (

    filtered

    .groupby(
        'product_name',
        as_index = False,
    )['gross_sales']

    .sum()

    .sort_values(
        'gross_sales',
        ascending = False,
    )

    .head(10)

    .sort_values(
        'gross_sales'
    )
)


fig_products = px.bar(

    top_products,

    x = 'gross_sales',

    y = 'product_name',

    orientation = 'h',

    title = (
        '🔝 Top 10 Products '
        'by Gross Sales'
    ),

    labels = {
        'gross_sales':
        'Gross Sales',

        'product_name':
        'Product',
    },
)


fig_products.update_layout(

    xaxis_tickprefix = 'PHP ',

    xaxis_tickformat = ',.0f',
)


fig_products.update_traces(marker_color = 'teal')


with st.container(border = True):
    st.plotly_chart(
        fig_products,
        width = 'stretch',
    )


# [Checkpoint 16] Filtered Transaction Table

with st.expander(
    'Filtered Transaction Details'
):

    detail_columns = [
        'order_id',
        'order_date',
        'product_name',
        'category_clean',
        'quantity',
        'unit_price_clean',
        'region_name',
        'city',
        'sales_channel',
        'discount_pct',
        'gross_sales',
        'net_sales',
    ]

    detail = (
        filtered[detail_columns]
        .sort_values(
            'order_date',
            ascending = False,
        )
        .copy()
    )

    with st.container(border = True):
        st.dataframe(
            detail,
            width = 'stretch',
            hide_index = True,
        )


# [Checkpoint X] Insights and Recommendations

with st.expander(
    'Insights and Recommendations'
):

    st.write(
        """
        - Insight 1: monthly gross sales fluctuated significantly from January 2024 to January 2026, peaking at approximately PHP 239,000 in August 2025 before declining to around PHP 200,000 by January 2026, which suggests inconsistent sales performance and a weakening trend toward the end of the period. Recommendation 1: analyze the factors behind peak-sales months and replicate successful strategies such as effective promotions or seasonal campaigns – while investigating the late-2025 decline; moreover, implement targeted marketing and sales initiatives to stabilize monthly revenue and sustain growth.
        - Insight 2: Toys generate the highest gross sales at approximately PHP 740,000, followed by Electronics at PHP 720,000; Sports has the lowest sales at around PHP 570,000, indicating differences in customer demand across product categories. Recommendation 2: prioritize inventory and marketing for high-performing categories like Toys and Electronics to sustain revenue – while reviewing the performance of Sports and other lower-selling categories to identify opportunities for improvement through targeted promotions and product assortment adjustments.
        - Insight 3: Central Luzon generates the highest gross sales at approximately PHP 950,000, followed by Central Visayas at PHP 925,000; CALABARZON records the lowest sales at around PHP 830,000, indicating opportunities to improve regional performance. Recommendation 3: maintain strong sales strategies in Central Luzon and Central Visayas – while investigating the factors behind CALABARZON’s lower sales; moreover, implement targeted regional promotions and strengthen distribution efforts to increase revenue and reduce performance gaps across regions.
        - Insight 4: order values are heavily concentrated below PHP 500, with the highest frequency around PHP 200–300; the distribution is right-skewed, meaning high-value orders are relatively rare. Recommendation 4: focus on increasing average order value through targeted upselling, product bundles, and free-shipping incentives for orders above PHP 500 – while maintaining affordable options that appeal to the majority of customers.
        - Insight 5: the Web channel generates the highest gross sales, whereas the Marketplace has the lowest; however, sales across all three channels are relatively similar at approximately PHP 1.75–1.80 million. Recommendation 5: maintain strong performance across all channels – while analyzing the Web channel’s successful strategies and applying them to the Marketplace to help close the sales gap and increase overall revenue.
        - Insight 6: monthly returns fluctuate significantly, ranging from approximately 67 to 119 — with notable peaks in June 2024, November 2024, and July 2025; despite these spikes, returns declined toward the end of 2025 before recovering in January 2026. Recommendation 6: investigate the factors driving peak-return months and the sharp declines, then use these insights to develop targeted strategies to stabilize monthly returns and replicate successful performance patterns.
        - Insight 7: KidJoy Toys 607 is the top-selling product by gross sales, significantly outperforming the other products, whereas BookNest Groceries 219 ranks lowest among the top 10; this indicates stronger sales performance in certain product categories, particularly toys. Recommendation 7: prioritize inventory and marketing for high-performing products like KidJoy Toys 607 to sustain sales momentum – while reviewing the pricing, promotions, and customer demand for lower-performing products to identify opportunities for improvement.
        """
    )


# [Checkpoint 17] About the Dashboard

with st.expander(
    'About This Dashboard'
):

    st.write(
        """
        This dashboard uses the original retail CSV files.

        The application performs basic cleaning before analysis:
        - removes exact duplicate records
        - standardizes product categories
        - converts unit prices to numeric values 
        - removes zero or negative quantities
        - parses mixed order-date formats
        - fills missing discounts with zero
        - validates customer, order, and product references
        - keeps completed and shipped orders for sales analysis

        Gross Sales = Quantity × Unit Price

        Net Sales = Gross Sales × (1 − Discount Percentage)

        The average order value is calculated at the order level,
        not at the order-item level.
        
        """
    )


    st.write(
        'Filtered item rows:',
        f'{len(filtered):,}',
    )


    st.write(
        'Filtered unique orders:',
        f'{order_count:,}',
    )