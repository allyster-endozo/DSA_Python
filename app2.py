from pathlib import Path
import html

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Retail Analytics Command Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BLUE = "#0247B7"
ORANGE = "#F47A2A"

PALETTE = [
    "#0247B7",
    "#38A3FF",
    "#5B6CFF",
    "#00A6A6",
    "#F47A2A",
    "#8B5CF6",
    "#22C55E",
    "#EAB308",
    "#64748B",
]


# ============================================================
# 2. MODERN DASHBOARD STYLING
# ============================================================

st.markdown(
    f"""
    <style>
        .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }}

        .hero {{
            border: 1px solid #DCE5F1;
            border-radius: 20px;
            padding: 1.35rem 1.55rem;
            background:
                linear-gradient(
                    135deg,
                    rgba(2,71,183,0.10),
                    rgba(56,163,255,0.03)
                );
            margin-bottom: .9rem;
        }}

        .hero-kicker {{
            color: {BLUE};
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .09em;
            text-transform: uppercase;
        }}

        .hero-title {{
            color: #172033;
            font-size: 2.15rem;
            font-weight: 800;
            margin-top: .15rem;
            margin-bottom: .2rem;
        }}

        .hero-sub {{
            color: #667085;
            font-size: .98rem;
        }}

        .chips {{
            display: flex;
            flex-wrap: wrap;
            gap: .4rem;
            margin: .25rem 0 1rem 0;
        }}

        .chip {{
            background: #EEF4FF;
            border: 1px solid #D8E6FF;
            color: {BLUE};
            border-radius: 999px;
            padding: .28rem .62rem;
            font-size: .8rem;
            font-weight: 650;
        }}

        div[data-testid="stMetric"] {{
            padding-top: .25rem;
            padding-bottom: .25rem;
        }}

        .section-note {{
            color: #667085;
            font-size: .86rem;
            margin-top: -.4rem;
            margin-bottom: .8rem;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. HELPERS
# ============================================================

def compact_number(value, decimals=2):
    if pd.isna(value):
        return "0"

    value = float(value)
    absolute = abs(value)

    if absolute >= 1_000_000_000:
        number = value / 1_000_000_000
        suffix = "B"
    elif absolute >= 1_000_000:
        number = value / 1_000_000
        suffix = "M"
    elif absolute >= 1_000:
        number = value / 1_000
        suffix = "K"
    else:
        return f"{value:,.0f}"

    text = f"{number:.{decimals}f}".rstrip("0").rstrip(".")
    return f"{text}{suffix}"


def clean_money(series):
    return pd.to_numeric(
        series.astype("string")
        .str.replace("₱", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip(),
        errors="coerce",
    )


def find_data_file(candidates):
    roots = [
        Path("data"),
        Path("."),
        Path("/mnt/data"),
    ]

    for root in roots:
        for name in candidates:
            path = root / name
            if path.exists():
                return path

    raise FileNotFoundError(
        "Could not find: " + ", ".join(candidates)
    )


def style_figure(fig, height=410):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(
            l=20,
            r=20,
            t=62,
            b=30,
        ),
        font=dict(
            family="Inter, Arial, sans-serif",
            size=12,
            color="#334155",
        ),
        title=dict(
            font=dict(
                size=17,
                color="#172033",
            ),
            x=.01,
            xanchor="left",
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
        ),
    )
    return fig


def chart_card(fig):
    with st.container(border=True):
        st.plotly_chart(
            fig,
            width="stretch",
        )


def filter_sales(
    dataframe,
    start_date,
    end_date,
    regions,
    channels,
    categories,
    shipping_methods,
):
    result = dataframe[
        dataframe["order_date"].notna()
    ].copy()

    result = result[
        result["order_date"].dt.date.between(
            start_date,
            end_date,
        )
    ]

    if regions:
        result = result[
            result["region_name"].isin(regions)
        ]

    if channels:
        result = result[
            result["sales_channel"].isin(channels)
        ]

    if categories:
        result = result[
            result["category_clean"].isin(categories)
        ]

    if shipping_methods:
        result = result[
            result["shipping_method"].isin(shipping_methods)
        ]

    return result.copy()


def make_filter_chips(
    start_date,
    end_date,
    regions,
    channels,
    categories,
):
    values = [
        f"{start_date:%d %b %Y} – {end_date:%d %b %Y}",
        f"Regions: {len(regions)}",
        f"Channels: {len(channels)}",
        f"Categories: {len(categories)}",
    ]

    tags = "".join(
        (
            '<span class="chip">'
            f"{html.escape(v)}"
            "</span>"
        )
        for v in values
    )

    st.markdown(
        f'<div class="chips">{tags}</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# 4. LOAD + CLEAN ALL SEVEN DATASETS
# ============================================================

@st.cache_data
def load_data():
    customer_file = find_data_file(
        [
            "customers.csv",
            "customers(20261017-082937).csv",
        ]
    )

    product_file = find_data_file(
        [
            "products.csv",
            "products(1).csv",
        ]
    )

    order_file = find_data_file(
        [
            "orders.csv",
            "orders(1).csv",
        ]
    )

    item_file = find_data_file(
        [
            "order_items.csv",
            "order_items(1).csv",
        ]
    )

    payment_file = find_data_file(
        [
            "payments.csv",
            "payments(1).csv",
        ]
    )

    shipment_file = find_data_file(
        [
            "shipments.csv",
            "shipments(1).csv",
        ]
    )

    return_file = find_data_file(
        [
            "returns.csv",
            "returns(1).csv",
        ]
    )

    # --------------------------------------------------------
    # READ RAW FILES
    # --------------------------------------------------------

    customers_raw = pd.read_csv(customer_file)
    products_raw = pd.read_csv(product_file)
    orders_raw = pd.read_csv(order_file)
    items_raw = pd.read_csv(item_file)
    payments_raw = pd.read_csv(payment_file)
    shipments_raw = pd.read_csv(shipment_file)
    returns_raw = pd.read_csv(return_file)

    raw_counts = {
        "Customers": len(customers_raw),
        "Products": len(products_raw),
        "Orders": len(orders_raw),
        "Order Items": len(items_raw),
        "Payments": len(payments_raw),
        "Shipments": len(shipments_raw),
        "Returns": len(returns_raw),
    }

    # --------------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------------

    customers = customers_raw.drop_duplicates().copy()
    products = products_raw.drop_duplicates().copy()
    orders = orders_raw.drop_duplicates().copy()
    items = items_raw.drop_duplicates().copy()
    payments = payments_raw.drop_duplicates().copy()
    shipments = shipments_raw.drop_duplicates().copy()
    returns = returns_raw.drop_duplicates().copy()

    # --------------------------------------------------------
    # CUSTOMERS
    # --------------------------------------------------------

    customers["customer_name"] = (
        customers["first_name"]
        .fillna("")
        .astype(str)
        .str.strip()
        + " "
        + customers["last_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    ).str.strip()

    gender_map = {
        "m": "Male",
        "male": "Male",
        "f": "Female",
        "female": "Female",
    }

    customers["gender_clean"] = (
        customers["gender"]
        .astype("string")
        .str.strip()
        .str.lower()
        .replace(gender_map)
        .fillna("Unknown")
    )

    customers["age_clean"] = pd.to_numeric(
        customers["age"],
        errors="coerce",
    )

    customers.loc[
        ~customers["age_clean"].between(
            18,
            100,
        ),
        "age_clean",
    ] = pd.NA

    customers["signup_date_clean"] = pd.to_datetime(
        customers["signup_date"],
        format="mixed",
        errors="coerce",
    )

    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    category_map = {
        "electronics": "Electronics",
        "elec": "Electronics",
        "home & kitchen": "Home & Kitchen",
        "home and kitchen": "Home & Kitchen",
        "books": "Books",
        "book": "Books",
        "groceries": "Groceries",
        "grocery": "Groceries",
        "toys": "Toys",
        "toy": "Toys",
        "beauty": "Beauty",
        "beauty & care": "Beauty",
        "fashion": "Fashion",
        "fashon": "Fashion",
        "sports": "Sports",
        "sports & outdoor": "Sports",
    }

    products["category_clean"] = (
        products["category"]
        .astype("string")
        .str.strip()
        .str.lower()
        .replace(category_map)
        .fillna("Unknown")
    )

    products["unit_cost_clean"] = clean_money(
        products["unit_cost"]
    )

    products["list_price_clean"] = clean_money(
        products["unit_price"]
    )

    products["stock_qty_clean"] = pd.to_numeric(
        products["stock_qty"],
        errors="coerce",
    )

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    orders["order_date"] = pd.to_datetime(
        orders["order_datetime"],
        format="mixed",
        errors="coerce",
    )

    orders["discount_pct_clean"] = pd.to_numeric(
        orders["discount_pct"],
        errors="coerce",
    ).fillna(0)

    orders.loc[
        ~orders["discount_pct_clean"].between(
            0,
            1,
        ),
        "discount_pct_clean",
    ] = 0

    orders["shipping_fee_clean"] = clean_money(
        orders["shipping_fee"]
    ).fillna(0)

    # Referential integrity: valid customer
    orders = orders[
        orders["customer_id"].isin(
            customers["customer_id"]
        )
    ].copy()

    # --------------------------------------------------------
    # ORDER ITEMS
    # --------------------------------------------------------

    items["quantity_clean"] = pd.to_numeric(
        items["quantity"],
        errors="coerce",
    )

    items["unit_price_clean"] = clean_money(
        items["unit_price_at_purchase"]
    )

    items = items[
        (items["quantity_clean"] > 0)
        & items["unit_price_clean"].notna()
        & items["product_id"].isin(
            products["product_id"]
        )
        & items["order_id"].isin(
            orders["order_id"]
        )
    ].copy()

    # --------------------------------------------------------
    # SALES ANALYSIS - ITEM LEVEL
    # --------------------------------------------------------

    sales_all = (
        items
        .merge(
            orders[
                [
                    "order_id",
                    "customer_id",
                    "order_date",
                    "order_status",
                    "sales_channel",
                    "shipping_method",
                    "discount_pct_clean",
                    "shipping_fee_clean",
                ]
            ],
            on="order_id",
            how="inner",
            validate="many_to_one",
        )
        .merge(
            products[
                [
                    "product_id",
                    "product_name",
                    "brand",
                    "category_clean",
                    "unit_cost_clean",
                    "list_price_clean",
                    "stock_qty_clean",
                ]
            ],
            on="product_id",
            how="inner",
            validate="many_to_one",
        )
        .merge(
            customers[
                [
                    "customer_id",
                    "customer_name",
                    "gender_clean",
                    "age_clean",
                    "region_name",
                    "city",
                    "barangay",
                    "loyalty_tier",
                ]
            ],
            on="customer_id",
            how="left",
            validate="many_to_one",
        )
    )

    sales_all["gross_sales"] = (
        sales_all["quantity_clean"]
        * sales_all["unit_price_clean"]
    )

    sales_all["net_sales"] = (
        sales_all["gross_sales"]
        * (
            1
            - sales_all["discount_pct_clean"]
        )
    )

    sales_all["discount_amount"] = (
        sales_all["gross_sales"]
        - sales_all["net_sales"]
    )

    sales_all["estimated_cost"] = (
        sales_all["quantity_clean"]
        * sales_all["unit_cost_clean"]
    )

    sales_all["estimated_profit"] = (
        sales_all["net_sales"]
        - sales_all["estimated_cost"]
    )

    sales_all["month"] = (
        sales_all["order_date"]
        .dt.to_period("M")
        .astype("string")
    )

    sales_all["weekday"] = (
        sales_all["order_date"]
        .dt.day_name()
    )

    sales_all["hour"] = (
        sales_all["order_date"]
        .dt.hour
    )

    # --------------------------------------------------------
    # PAYMENTS
    # --------------------------------------------------------

    payments["amount_paid_clean"] = clean_money(
        payments["amount_paid"]
    )

    payments["payment_date_clean"] = pd.to_datetime(
        payments["payment_date"],
        format="mixed",
        errors="coerce",
    )

    # --------------------------------------------------------
    # SHIPMENTS
    # --------------------------------------------------------

    shipments["ship_date_clean"] = pd.to_datetime(
        shipments["ship_date"],
        format="mixed",
        errors="coerce",
    )

    shipments["delivered_date_clean"] = pd.to_datetime(
        shipments["delivered_date"],
        format="mixed",
        errors="coerce",
    )

    shipments["delivery_days"] = (
        shipments["delivered_date_clean"]
        - shipments["ship_date_clean"]
    ).dt.days

    shipments.loc[
        shipments["delivery_days"] < 0,
        "delivery_days",
    ] = pd.NA

    # --------------------------------------------------------
    # RETURNS
    # --------------------------------------------------------

    returns["return_request_date_clean"] = pd.to_datetime(
        returns["return_request_date"],
        format="mixed",
        errors="coerce",
    )

    returns["refund_amount_clean"] = clean_money(
        returns["refund_amount"]
    ).fillna(0)

    returns["refunded_flag_clean"] = (
        returns["refunded_flag"]
        .astype("string")
        .str.strip()
        .str.title()
        .fillna("Unknown")
    )

    # --------------------------------------------------------
    # ORDER-LEVEL SUMMARY
    # --------------------------------------------------------

    order_summary = (
        sales_all
        .groupby(
            "order_id",
            as_index=False,
        )
        .agg(
            customer_id=("customer_id", "first"),
            customer_name=("customer_name", "first"),
            order_date=("order_date", "first"),
            order_status=("order_status", "first"),
            sales_channel=("sales_channel", "first"),
            shipping_method=("shipping_method", "first"),
            region_name=("region_name", "first"),
            city=("city", "first"),
            loyalty_tier=("loyalty_tier", "first"),
            discount_pct=(
                "discount_pct_clean",
                "first",
            ),
            shipping_fee=(
                "shipping_fee_clean",
                "first",
            ),
            gross_order_value=(
                "gross_sales",
                "sum",
            ),
            net_order_value=(
                "net_sales",
                "sum",
            ),
            discount_amount=(
                "discount_amount",
                "sum",
            ),
            estimated_cost=(
                "estimated_cost",
                "sum",
            ),
            estimated_profit=(
                "estimated_profit",
                "sum",
            ),
            units=("quantity_clean", "sum"),
            line_items=("order_item_id", "nunique"),
        )
    )

    order_summary["profit_margin_pct"] = (
        order_summary["estimated_profit"]
        / order_summary["net_order_value"]
        * 100
    )

    order_summary["month"] = (
        order_summary["order_date"]
        .dt.to_period("M")
        .astype("string")
    )

    order_summary["weekday"] = (
        order_summary["order_date"]
        .dt.day_name()
    )

    order_summary["hour"] = (
        order_summary["order_date"]
        .dt.hour
    )

    clean_counts = {
        "Customers": len(customers),
        "Products": len(products),
        "Orders": len(orders),
        "Order Items": len(items),
        "Payments": len(payments),
        "Shipments": len(shipments),
        "Returns": len(returns),
    }

    return {
        "customers": customers,
        "products": products,
        "sales_all": sales_all,
        "order_summary": order_summary,
        "payments": payments,
        "shipments": shipments,
        "returns": returns,
        "raw_counts": raw_counts,
        "clean_counts": clean_counts,
    }


# ============================================================
# 5. LOAD DATA
# ============================================================

try:
    data = load_data()

except FileNotFoundError as error:
    st.error(
        "One or more retail CSV files could not be found."
    )
    st.exception(error)
    st.stop()


customers = data["customers"]
products = data["products"]
sales_all = data["sales_all"]
order_summary = data["order_summary"]
payments = data["payments"]
shipments = data["shipments"]
returns = data["returns"]
raw_counts = data["raw_counts"]
clean_counts = data["clean_counts"]


# ============================================================
# 6. FILTER STATE
# ============================================================

date_series = sales_all["order_date"].dropna()

min_date = date_series.min().date()
max_date = date_series.max().date()

all_regions = sorted(
    sales_all["region_name"]
    .dropna()
    .unique()
    .tolist()
)

all_channels = sorted(
    sales_all["sales_channel"]
    .dropna()
    .unique()
    .tolist()
)

all_categories = sorted(
    sales_all["category_clean"]
    .dropna()
    .unique()
    .tolist()
)

all_shipping_methods = sorted(
    sales_all["shipping_method"]
    .dropna()
    .unique()
    .tolist()
)


def reset_filters():
    st.session_state["date_range"] = (
        min_date,
        max_date,
    )
    st.session_state["regions"] = all_regions
    st.session_state["channels"] = all_channels
    st.session_state["categories"] = all_categories
    st.session_state["shipping_methods"] = all_shipping_methods


if "date_range" not in st.session_state:
    reset_filters()


# ============================================================
# 7. SIDEBAR
# ============================================================

with st.sidebar:
    st.header("Dashboard Filters")
    st.caption(
        "Filters apply across all analytical sections."
    )

    selected_dates = st.date_input(
        "Order date range",
        min_value=min_date,
        max_value=max_date,
        key="date_range",
    )

    if isinstance(selected_dates, (tuple, list)):
        if len(selected_dates) == 2:
            start_date = selected_dates[0]
            end_date = selected_dates[1]
        else:
            start_date = min_date
            end_date = max_date
    else:
        start_date = selected_dates
        end_date = selected_dates

    selected_regions = st.multiselect(
        "Region",
        all_regions,
        key="regions",
    )

    selected_channels = st.multiselect(
        "Sales Channel",
        all_channels,
        key="channels",
    )

    selected_categories = st.multiselect(
        "Product Category",
        all_categories,
        key="categories",
    )

    selected_shipping = st.multiselect(
        "Shipping Method",
        all_shipping_methods,
        key="shipping_methods",
    )

    st.button(
        "Reset Filters",
        width="stretch",
        type="primary",
        on_click=reset_filters,
    )

    st.divider()

    st.caption(
        "Sales KPIs use fulfilled orders: Completed + Shipped."
    )


# ============================================================
# 8. FILTER ANALYTICAL DATA
# ============================================================

filtered_all = filter_sales(
    sales_all,
    start_date,
    end_date,
    selected_regions,
    selected_channels,
    selected_categories,
    selected_shipping,
)

if filtered_all.empty:
    st.warning(
        "No records match the selected filters."
    )
    st.stop()


filtered_fulfilled = filtered_all[
    filtered_all["order_status"].isin(
        [
            "Completed",
            "Shipped",
        ]
    )
].copy()

matching_all_order_ids = (
    filtered_all["order_id"]
    .drop_duplicates()
    .tolist()
)

matching_fulfilled_order_ids = (
    filtered_fulfilled["order_id"]
    .drop_duplicates()
    .tolist()
)

filtered_orders_all = order_summary[
    order_summary["order_id"].isin(
        matching_all_order_ids
    )
].copy()

filtered_orders_fulfilled = order_summary[
    order_summary["order_id"].isin(
        matching_fulfilled_order_ids
    )
].copy()

payment_scope = payments[
    payments["order_id"].isin(
        matching_all_order_ids
    )
].copy()

shipment_scope = shipments[
    shipments["order_id"].isin(
        matching_all_order_ids
    )
].copy()

return_scope = returns[
    returns["order_id"].isin(
        matching_all_order_ids
    )
].copy()


# ============================================================
# 9. HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">DataSense Analytics</div>
        <div class="hero-title">
            Retail Analytics Command Center
        </div>
        <div class="hero-sub">
            A comprehensive view of sales, customers, products,
            profitability, payments, logistics, and returns
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

make_filter_chips(
    start_date,
    end_date,
    selected_regions,
    selected_channels,
    selected_categories,
)


# ============================================================
# 10. EXECUTIVE KPI STRIP
# ============================================================

gross_sales = filtered_fulfilled["gross_sales"].sum()
net_sales = filtered_fulfilled["net_sales"].sum()
discount_value = filtered_fulfilled["discount_amount"].sum()
estimated_profit = filtered_fulfilled["estimated_profit"].sum()
units_sold = filtered_fulfilled["quantity_clean"].sum()
fulfilled_orders = filtered_fulfilled["order_id"].nunique()
unique_customers = filtered_fulfilled["customer_id"].nunique()

aov = (
    filtered_orders_fulfilled["net_order_value"].mean()
    if not filtered_orders_fulfilled.empty
    else 0
)

profit_margin = (
    estimated_profit / net_sales * 100
    if net_sales != 0
    else 0
)

k1, k2, k3, k4 = st.columns(
    4,
    border=True,
)

k1.metric(
    "Gross Sales",
    f"₱{compact_number(gross_sales)}",
)

k2.metric(
    "Net Sales",
    f"₱{compact_number(net_sales)}",
)

k3.metric(
    "Fulfilled Orders",
    f"{fulfilled_orders:,}",
)

k4.metric(
    "Average Order Value",
    f"₱{aov:,.2f}",
)

k5, k6, k7, k8 = st.columns(
    4,
    border=True,
)

k5.metric(
    "Units Sold",
    f"{units_sold:,.0f}",
)

k6.metric(
    "Unique Customers",
    f"{unique_customers:,}",
)

k7.metric(
    "Estimated Profit",
    f"₱{compact_number(estimated_profit)}",
)

k8.metric(
    "Estimated Margin",
    f"{profit_margin:.1f}%",
)


# ============================================================
# 11. DASHBOARD TABS
# ============================================================

(
    executive_tab,
    sales_tab,
    products_tab,
    customers_tab,
    profitability_tab,
    payments_tab,
    logistics_tab,
    data_tab,
) = st.tabs(
    [
        "Executive",
        "Sales",
        "Products",
        "Customers",
        "Profit & Discounts",
        "Payments",
        "Logistics & Returns",
        "Data Explorer",
    ]
)


# ============================================================
# 12. EXECUTIVE TAB
# ============================================================

with executive_tab:
    st.subheader("Executive Overview")
    st.markdown(
        '<div class="section-note">'
        'High-level indicators for fulfilled sales plus operational order mix.'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Monthly gross vs net sales
    # --------------------------------------------------------

    monthly_revenue = (
        filtered_fulfilled
        .groupby(
            "month",
            as_index=False,
        )
        .agg(
            Gross_Sales=("gross_sales", "sum"),
            Net_Sales=("net_sales", "sum"),
        )
        .sort_values("month")
    )

    fig = px.line(
        monthly_revenue,
        x="month",
        y=[
            "Gross_Sales",
            "Net_Sales",
        ],
        markers=True,
        title="Monthly Gross vs Net Sales",
        labels={
            "month": "Month",
            "value": "Sales (PHP)",
            "variable": "Measure",
        },
        color_discrete_sequence=[
            BLUE,
            ORANGE,
        ],
    )

    fig.update_layout(
        hovermode="x unified",
        yaxis_tickprefix="₱",
        yaxis_tickformat=",.0f",
    )

    chart_card(
        style_figure(
            fig,
            height=440,
        )
    )

    left, right = st.columns(
        2,
        gap="medium",
    )

    # Order status
    status_df = (
        filtered_orders_all[
            "order_status"
        ]
        .value_counts()
        .rename_axis("order_status")
        .reset_index(name="orders")
    )

    fig_status = px.pie(
        status_df,
        names="order_status",
        values="orders",
        hole=.58,
        title="Order Status Mix",
        color_discrete_sequence=PALETTE,
    )

    fig_status = style_figure(
        fig_status,
        height=420,
    )

    with left:
        chart_card(fig_status)

    # Sales channel
    channel_df = (
        filtered_fulfilled
        .groupby(
            "sales_channel",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values(
            "gross_sales",
            ascending=False,
        )
    )

    fig_channel = px.pie(
        channel_df,
        names="sales_channel",
        values="gross_sales",
        hole=.58,
        title="Gross Sales Share by Channel",
        color_discrete_sequence=PALETTE,
    )

    fig_channel = style_figure(
        fig_channel,
        height=420,
    )

    with right:
        chart_card(fig_channel)

    left2, right2 = st.columns(
        2,
        gap="medium",
    )

    category_df = (
        filtered_fulfilled
        .groupby(
            "category_clean",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values("gross_sales")
    )

    fig_category = px.bar(
        category_df,
        x="gross_sales",
        y="category_clean",
        orientation="h",
        title="Gross Sales by Category",
        labels={
            "gross_sales": "Gross Sales (PHP)",
            "category_clean": "Category",
        },
        color="gross_sales",
        color_continuous_scale=[
            "#DBEAFE",
            BLUE,
        ],
    )

    fig_category.update_layout(
        coloraxis_showscale=False,
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
    )

    with left2:
        chart_card(
            style_figure(
                fig_category,
                height=450,
            )
        )

    region_df = (
        filtered_fulfilled
        .groupby(
            "region_name",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values("gross_sales")
    )

    fig_region = px.bar(
        region_df,
        x="gross_sales",
        y="region_name",
        orientation="h",
        title="Gross Sales by Region",
        labels={
            "gross_sales": "Gross Sales (PHP)",
            "region_name": "Region",
        },
        color="gross_sales",
        color_continuous_scale=[
            "#E0F2FE",
            BLUE,
        ],
    )

    fig_region.update_layout(
        coloraxis_showscale=False,
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
    )

    with right2:
        chart_card(
            style_figure(
                fig_region,
                height=450,
            )
        )


# ============================================================
# 13. SALES TAB
# ============================================================

with sales_tab:
    st.subheader("Sales Performance")

    row1a, row1b = st.columns(
        2,
        gap="medium",
    )

    # Orders by month
    monthly_orders = (
        filtered_orders_fulfilled
        .groupby(
            "month",
            as_index=False,
        )["order_id"]
        .nunique()
        .rename(
            columns={
                "order_id": "orders"
            }
        )
        .sort_values("month")
    )

    fig = px.line(
        monthly_orders,
        x="month",
        y="orders",
        markers=True,
        title="Fulfilled Orders by Month",
        labels={
            "month": "Month",
            "orders": "Orders",
        },
        color_discrete_sequence=[
            BLUE
        ],
    )

    with row1a:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    # AOV by month
    monthly_aov = (
        filtered_orders_fulfilled
        .groupby(
            "month",
            as_index=False,
        )["net_order_value"]
        .mean()
        .rename(
            columns={
                "net_order_value": "aov"
            }
        )
        .sort_values("month")
    )

    fig = px.line(
        monthly_aov,
        x="month",
        y="aov",
        markers=True,
        title="Average Order Value by Month",
        labels={
            "month": "Month",
            "aov": "AOV (PHP)",
        },
        color_discrete_sequence=[
            ORANGE
        ],
    )

    fig.update_layout(
        yaxis_tickprefix="₱",
        yaxis_tickformat=",.0f",
    )

    with row1b:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    row2a, row2b = st.columns(
        2,
        gap="medium",
    )

    # Sales by weekday
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    weekday_df = (
        filtered_fulfilled
        .groupby(
            "weekday",
            as_index=False,
        )["gross_sales"]
        .sum()
    )

    weekday_df["weekday"] = pd.Categorical(
        weekday_df["weekday"],
        categories=weekday_order,
        ordered=True,
    )

    weekday_df = weekday_df.sort_values(
        "weekday"
    )

    fig = px.bar(
        weekday_df,
        x="weekday",
        y="gross_sales",
        title="Gross Sales by Day of Week",
        labels={
            "weekday": "Day",
            "gross_sales": "Gross Sales (PHP)",
        },
        color="gross_sales",
        color_continuous_scale=[
            "#DBEAFE",
            BLUE,
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
        yaxis_tickprefix="₱",
        yaxis_tickformat=",.0f",
    )

    with row2a:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    # Sales by hour
    hourly_df = (
        filtered_fulfilled
        .groupby(
            "hour",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values("hour")
    )

    fig = px.line(
        hourly_df,
        x="hour",
        y="gross_sales",
        markers=True,
        title="Gross Sales by Hour of Day",
        labels={
            "hour": "Hour",
            "gross_sales": "Gross Sales (PHP)",
        },
        color_discrete_sequence=[
            BLUE
        ],
    )

    fig.update_layout(
        yaxis_tickprefix="₱",
        yaxis_tickformat=",.0f",
    )

    with row2b:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    row3a, row3b = st.columns(
        2,
        gap="medium",
    )

    # Order value distribution
    fig = px.histogram(
        filtered_orders_fulfilled,
        x="net_order_value",
        nbins=35,
        title="Net Order Value Distribution",
        labels={
            "net_order_value": "Net Order Value (PHP)",
        },
        color_discrete_sequence=[
            BLUE
        ],
    )

    fig.update_layout(
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
        yaxis_title="Orders",
    )

    with row3a:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    # Shipping method sales
    ship_method_df = (
        filtered_fulfilled
        .groupby(
            "shipping_method",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values(
            "gross_sales",
            ascending=False,
        )
    )

    fig = px.bar(
        ship_method_df,
        x="shipping_method",
        y="gross_sales",
        title="Gross Sales by Shipping Method",
        labels={
            "shipping_method": "Shipping Method",
            "gross_sales": "Gross Sales (PHP)",
        },
        color="shipping_method",
        color_discrete_sequence=PALETTE,
    )

    fig.update_layout(
        showlegend=False,
        yaxis_tickprefix="₱",
        yaxis_tickformat=",.0f",
    )

    with row3b:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )


# ============================================================
# 14. PRODUCTS TAB
# ============================================================

with products_tab:
    st.subheader("Product & Category Analytics")

    p1, p2 = st.columns(
        2,
        gap="medium",
    )

    top_products = (
        filtered_fulfilled
        .groupby(
            "product_name",
            as_index=False,
        )
        .agg(
            gross_sales=("gross_sales", "sum"),
            units=("quantity_clean", "sum"),
        )
        .sort_values(
            "gross_sales",
            ascending=False,
        )
        .head(15)
        .sort_values("gross_sales")
    )

    fig = px.bar(
        top_products,
        x="gross_sales",
        y="product_name",
        orientation="h",
        title="Top 15 Products by Gross Sales",
        labels={
            "gross_sales": "Gross Sales (PHP)",
            "product_name": "Product",
        },
        color="gross_sales",
        color_continuous_scale=[
            "#DBEAFE",
            BLUE,
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
    )

    with p1:
        chart_card(
            style_figure(
                fig,
                height=540,
            )
        )

    top_brands = (
        filtered_fulfilled
        .groupby(
            "brand",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values(
            "gross_sales",
            ascending=False,
        )
        .head(12)
        .sort_values("gross_sales")
    )

    fig = px.bar(
        top_brands,
        x="gross_sales",
        y="brand",
        orientation="h",
        title="Top Brands by Gross Sales",
        labels={
            "gross_sales": "Gross Sales (PHP)",
            "brand": "Brand",
        },
        color="gross_sales",
        color_continuous_scale=[
            "#DFF8F3",
            "#00A6A6",
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
    )

    with p2:
        chart_card(
            style_figure(
                fig,
                height=540,
            )
        )

    p3, p4 = st.columns(
        2,
        gap="medium",
    )

    category_units = (
        filtered_fulfilled
        .groupby(
            "category_clean",
            as_index=False,
        )["quantity_clean"]
        .sum()
        .sort_values("quantity_clean")
    )

    fig = px.bar(
        category_units,
        x="quantity_clean",
        y="category_clean",
        orientation="h",
        title="Units Sold by Category",
        labels={
            "quantity_clean": "Units",
            "category_clean": "Category",
        },
        color="quantity_clean",
        color_continuous_scale=[
            "#EDE9FE",
            "#5B6CFF",
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    with p3:
        chart_card(
            style_figure(
                fig,
                height=430,
            )
        )

    product_relationship = (
        filtered_fulfilled
        .groupby(
            [
                "product_name",
                "category_clean",
            ],
            as_index=False,
        )
        .agg(
            units=("quantity_clean", "sum"),
            average_price=(
                "unit_price_clean",
                "mean",
            ),
            gross_sales=("gross_sales", "sum"),
        )
    )

    fig = px.scatter(
        product_relationship,
        x="average_price",
        y="units",
        size="gross_sales",
        color="category_clean",
        hover_name="product_name",
        title="Product Price vs Units Sold",
        labels={
            "average_price": "Average Selling Price (PHP)",
            "units": "Units Sold",
            "category_clean": "Category",
        },
        color_discrete_sequence=PALETTE,
    )

    fig.update_layout(
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
    )

    with p4:
        chart_card(
            style_figure(
                fig,
                height=430,
            )
        )

    with st.container(border=True):
        st.subheader("Product Performance Table")

        product_table = (
            filtered_fulfilled
            .groupby(
                [
                    "product_name",
                    "brand",
                    "category_clean",
                ],
                as_index=False,
            )
            .agg(
                Units=("quantity_clean", "sum"),
                Orders=("order_id", "nunique"),
                Gross_Sales=("gross_sales", "sum"),
                Net_Sales=("net_sales", "sum"),
                Estimated_Profit=(
                    "estimated_profit",
                    "sum",
                ),
            )
            .sort_values(
                "Gross_Sales",
                ascending=False,
            )
        )

        st.dataframe(
            product_table,
            width="stretch",
            hide_index=True,
            column_config={
                "product_name": st.column_config.TextColumn(
                    "Product",
                    width="large",
                ),
                "brand": "Brand",
                "category_clean": "Category",
                "Units": st.column_config.NumberColumn(
                    "Units",
                    format="%d",
                ),
                "Orders": st.column_config.NumberColumn(
                    "Orders",
                    format="%d",
                ),
                "Gross_Sales": st.column_config.NumberColumn(
                    "Gross Sales",
                    format="₱ %.2f",
                ),
                "Net_Sales": st.column_config.NumberColumn(
                    "Net Sales",
                    format="₱ %.2f",
                ),
                "Estimated_Profit": st.column_config.NumberColumn(
                    "Est. Profit",
                    format="₱ %.2f",
                ),
            },
        )


# ============================================================
# 15. CUSTOMERS TAB
# ============================================================

with customers_tab:
    st.subheader("Customer Analytics")

    unique_customer_scope = (
        filtered_fulfilled[
            [
                "customer_id",
                "customer_name",
                "gender_clean",
                "age_clean",
                "region_name",
                "city",
                "loyalty_tier",
            ]
        ]
        .drop_duplicates(
            "customer_id"
        )
    )

    c1, c2 = st.columns(
        2,
        gap="medium",
    )

    loyalty_df = (
        unique_customer_scope[
            "loyalty_tier"
        ]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("loyalty_tier")
        .reset_index(name="customers")
    )

    fig = px.pie(
        loyalty_df,
        names="loyalty_tier",
        values="customers",
        hole=.58,
        title="Customer Mix by Loyalty Tier",
        color_discrete_sequence=PALETTE,
    )

    with c1:
        chart_card(
            style_figure(
                fig,
                height=420,
            )
        )

    loyalty_sales = (
        filtered_fulfilled
        .groupby(
            "loyalty_tier",
            as_index=False,
            dropna=False,
        )["net_sales"]
        .sum()
        .sort_values(
            "net_sales",
            ascending=False,
        )
    )

    loyalty_sales["loyalty_tier"] = (
        loyalty_sales["loyalty_tier"]
        .fillna("Unknown")
    )

    fig = px.bar(
        loyalty_sales,
        x="loyalty_tier",
        y="net_sales",
        title="Net Sales by Loyalty Tier",
        labels={
            "loyalty_tier": "Loyalty Tier",
            "net_sales": "Net Sales (PHP)",
        },
        color="loyalty_tier",
        color_discrete_sequence=PALETTE,
    )

    fig.update_layout(
        showlegend=False,
        yaxis_tickprefix="₱",
        yaxis_tickformat=",.0f",
    )

    with c2:
        chart_card(
            style_figure(
                fig,
                height=420,
            )
        )

    c3, c4 = st.columns(
        2,
        gap="medium",
    )

    city_df = (
        filtered_fulfilled
        .groupby(
            "city",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values(
            "gross_sales",
            ascending=False,
        )
        .head(12)
        .sort_values("gross_sales")
    )

    fig = px.bar(
        city_df,
        x="gross_sales",
        y="city",
        orientation="h",
        title="Top Cities by Gross Sales",
        labels={
            "gross_sales": "Gross Sales (PHP)",
            "city": "City",
        },
        color="gross_sales",
        color_continuous_scale=[
            "#DBEAFE",
            BLUE,
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
    )

    with c3:
        chart_card(
            style_figure(
                fig,
                height=470,
            )
        )

    region_customers = (
        unique_customer_scope
        .groupby(
            "region_name",
            as_index=False,
        )["customer_id"]
        .nunique()
        .rename(
            columns={
                "customer_id": "customers"
            }
        )
        .sort_values("customers")
    )

    fig = px.bar(
        region_customers,
        x="customers",
        y="region_name",
        orientation="h",
        title="Unique Customers by Region",
        labels={
            "customers": "Customers",
            "region_name": "Region",
        },
        color="customers",
        color_continuous_scale=[
            "#E0F2FE",
            BLUE,
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    with c4:
        chart_card(
            style_figure(
                fig,
                height=470,
            )
        )

    c5, c6 = st.columns(
        2,
        gap="medium",
    )

    customer_summary = (
        filtered_fulfilled
        .groupby(
            [
                "customer_id",
                "customer_name",
                "loyalty_tier",
                "region_name",
            ],
            as_index=False,
        )
        .agg(
            Orders=("order_id", "nunique"),
            Spend=("net_sales", "sum"),
        )
    )

    fig = px.histogram(
        customer_summary,
        x="Spend",
        nbins=30,
        title="Customer Spend Distribution",
        labels={
            "Spend": "Net Customer Spend (PHP)",
        },
        color_discrete_sequence=[
            BLUE
        ],
    )

    fig.update_layout(
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
        yaxis_title="Customers",
    )

    with c5:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    fig = px.histogram(
        customer_summary,
        x="Orders",
        nbins=20,
        title="Customer Order Frequency",
        labels={
            "Orders": "Number of Orders",
        },
        color_discrete_sequence=[
            ORANGE
        ],
    )

    fig.update_layout(
        yaxis_title="Customers",
    )

    with c6:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    with st.container(border=True):
        st.subheader("Top Customers")

        top_customers = (
            customer_summary
            .sort_values(
                "Spend",
                ascending=False,
            )
            .head(25)
        )

        st.dataframe(
            top_customers,
            width="stretch",
            hide_index=True,
            column_config={
                "customer_id": "Customer ID",
                "customer_name": st.column_config.TextColumn(
                    "Customer",
                    width="large",
                ),
                "loyalty_tier": "Loyalty Tier",
                "region_name": "Region",
                "Orders": st.column_config.NumberColumn(
                    "Orders",
                    format="%d",
                ),
                "Spend": st.column_config.NumberColumn(
                    "Net Spend",
                    format="₱ %.2f",
                ),
            },
        )


# ============================================================
# 16. PROFITABILITY + DISCOUNTS TAB
# ============================================================

with profitability_tab:
    st.subheader("Profitability & Discount Analytics")

    d1, d2, d3, d4 = st.columns(
        4,
        border=True,
    )

    avg_discount = (
        filtered_orders_fulfilled[
            "discount_pct"
        ].mean() * 100
        if not filtered_orders_fulfilled.empty
        else 0
    )

    median_order = (
        filtered_orders_fulfilled[
            "net_order_value"
        ].median()
        if not filtered_orders_fulfilled.empty
        else 0
    )

    d1.metric(
        "Discount Value",
        f"₱{compact_number(discount_value)}",
    )

    d2.metric(
        "Average Discount",
        f"{avg_discount:.1f}%",
    )

    d3.metric(
        "Median Order Value",
        f"₱{median_order:,.2f}",
    )

    d4.metric(
        "Estimated Margin",
        f"{profit_margin:.1f}%",
    )

    pr1, pr2 = st.columns(
        2,
        gap="medium",
    )

    # Profit by category
    profit_category = (
        filtered_fulfilled
        .groupby(
            "category_clean",
            as_index=False,
        )
        .agg(
            estimated_profit=(
                "estimated_profit",
                "sum",
            ),
            net_sales=("net_sales", "sum"),
        )
    )

    profit_category["margin_pct"] = (
        profit_category["estimated_profit"]
        / profit_category["net_sales"]
        * 100
    )

    profit_category = profit_category.sort_values(
        "estimated_profit"
    )

    fig = px.bar(
        profit_category,
        x="estimated_profit",
        y="category_clean",
        orientation="h",
        title="Estimated Profit by Category",
        labels={
            "estimated_profit": "Estimated Profit (PHP)",
            "category_clean": "Category",
        },
        color="estimated_profit",
        color_continuous_scale=[
            "#DCFCE7",
            "#16A34A",
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
    )

    with pr1:
        chart_card(
            style_figure(
                fig,
                height=440,
            )
        )

    margin_df = profit_category.sort_values(
        "margin_pct"
    )

    fig = px.bar(
        margin_df,
        x="margin_pct",
        y="category_clean",
        orientation="h",
        title="Estimated Profit Margin by Category",
        labels={
            "margin_pct": "Estimated Margin (%)",
            "category_clean": "Category",
        },
        color="margin_pct",
        color_continuous_scale=[
            "#EDE9FE",
            "#7C3AED",
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    with pr2:
        chart_card(
            style_figure(
                fig,
                height=440,
            )
        )

    pr3, pr4 = st.columns(
        2,
        gap="medium",
    )

    fig = px.histogram(
        filtered_orders_fulfilled,
        x="discount_pct",
        nbins=25,
        title="Order Discount Distribution",
        labels={
            "discount_pct": "Discount Rate",
        },
        color_discrete_sequence=[
            ORANGE
        ],
    )

    fig.update_layout(
        xaxis_tickformat=".0%",
        yaxis_title="Orders",
    )

    with pr3:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    fig = px.scatter(
        filtered_orders_fulfilled,
        x="discount_pct",
        y="net_order_value",
        color="sales_channel",
        hover_data=[
            "order_id",
            "region_name",
        ],
        title="Discount Rate vs Net Order Value",
        labels={
            "discount_pct": "Discount Rate",
            "net_order_value": "Net Order Value (PHP)",
            "sales_channel": "Channel",
        },
        color_discrete_sequence=PALETTE,
    )

    fig.update_layout(
        xaxis_tickformat=".0%",
        yaxis_tickprefix="₱",
        yaxis_tickformat=",.0f",
    )

    with pr4:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    monthly_profit = (
        filtered_orders_fulfilled
        .groupby(
            "month",
            as_index=False,
        )
        .agg(
            Net_Sales=(
                "net_order_value",
                "sum",
            ),
            Estimated_Profit=(
                "estimated_profit",
                "sum",
            ),
            Discount_Value=(
                "discount_amount",
                "sum",
            ),
        )
        .sort_values("month")
    )

    fig = px.line(
        monthly_profit,
        x="month",
        y=[
            "Net_Sales",
            "Estimated_Profit",
            "Discount_Value",
        ],
        markers=True,
        title="Monthly Net Sales, Profit and Discount Value",
        labels={
            "month": "Month",
            "value": "Amount (PHP)",
            "variable": "Measure",
        },
        color_discrete_sequence=[
            BLUE,
            "#16A34A",
            ORANGE,
        ],
    )

    fig.update_layout(
        hovermode="x unified",
        yaxis_tickprefix="₱",
        yaxis_tickformat=",.0f",
    )

    chart_card(
        style_figure(
            fig,
            height=440,
        )
    )


# ============================================================
# 17. PAYMENTS TAB
# ============================================================

with payments_tab:
    st.subheader("Payment Analytics")

    paid_rows = payment_scope[
        payment_scope["payment_status"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("paid")
    ]

    total_paid = paid_rows[
        "amount_paid_clean"
    ].sum()

    failed_payments = (
        payment_scope["payment_status"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("failed")
        .sum()
    )

    refunded_payments = (
        payment_scope["payment_status"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("refunded")
        .sum()
    )

    pay1, pay2, pay3, pay4 = st.columns(
        4,
        border=True,
    )

    pay1.metric(
        "Payment Records",
        f"{len(payment_scope):,}",
    )

    pay2.metric(
        "Paid Amount",
        f"₱{compact_number(total_paid)}",
    )

    pay3.metric(
        "Failed Payments",
        f"{failed_payments:,}",
    )

    pay4.metric(
        "Refunded Payments",
        f"{refunded_payments:,}",
    )

    py1, py2 = st.columns(
        2,
        gap="medium",
    )

    payment_status_df = (
        payment_scope[
            "payment_status"
        ]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("payment_status")
        .reset_index(name="count")
    )

    fig = px.pie(
        payment_status_df,
        names="payment_status",
        values="count",
        hole=.58,
        title="Payment Status",
        color_discrete_sequence=PALETTE,
    )

    with py1:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    payment_method_df = (
        payment_scope[
            "payment_method"
        ]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("payment_method")
        .reset_index(name="count")
        .sort_values("count")
    )

    fig = px.bar(
        payment_method_df,
        x="count",
        y="payment_method",
        orientation="h",
        title="Payment Method Usage",
        labels={
            "count": "Payments",
            "payment_method": "Payment Method",
        },
        color="count",
        color_continuous_scale=[
            "#DBEAFE",
            BLUE,
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    with py2:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    py3, py4 = st.columns(
        2,
        gap="medium",
    )

    amount_method = (
        payment_scope
        .groupby(
            "payment_method",
            as_index=False,
        )["amount_paid_clean"]
        .sum()
        .sort_values("amount_paid_clean")
    )

    fig = px.bar(
        amount_method,
        x="amount_paid_clean",
        y="payment_method",
        orientation="h",
        title="Recorded Payment Amount by Method",
        labels={
            "amount_paid_clean": "Amount (PHP)",
            "payment_method": "Payment Method",
        },
        color="amount_paid_clean",
        color_continuous_scale=[
            "#DFF8F3",
            "#00A6A6",
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
    )

    with py3:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    method_status = (
        payment_scope
        .groupby(
            [
                "payment_method",
                "payment_status",
            ],
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "size": "count"
            }
        )
    )

    fig = px.bar(
        method_status,
        x="payment_method",
        y="count",
        color="payment_status",
        barmode="stack",
        title="Payment Status by Method",
        labels={
            "payment_method": "Payment Method",
            "count": "Payments",
            "payment_status": "Status",
        },
        color_discrete_sequence=PALETTE,
    )

    with py4:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )


# ============================================================
# 18. LOGISTICS + RETURNS TAB
# ============================================================

with logistics_tab:
    st.subheader("Logistics & Returns")

    delivered_days = shipment_scope[
        "delivery_days"
    ].dropna()

    median_delivery = (
        delivered_days.median()
        if not delivered_days.empty
        else pd.NA
    )

    returned_orders = (
        return_scope["order_id"]
        .nunique()
    )

    return_rate = (
        returned_orders
        / len(filtered_orders_all)
        * 100
        if len(filtered_orders_all) > 0
        else 0
    )

    total_refunds = (
        return_scope[
            "refund_amount_clean"
        ].sum()
    )

    lost_shipments = (
        shipment_scope["shipment_status"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("lost")
        .sum()
    )

    lg1, lg2, lg3, lg4 = st.columns(
        4,
        border=True,
    )

    lg1.metric(
        "Median Delivery",
        (
            f"{median_delivery:.0f} days"
            if pd.notna(median_delivery)
            else "—"
        ),
    )

    lg2.metric(
        "Return Rate",
        f"{return_rate:.1f}%",
    )

    lg3.metric(
        "Refund Amount",
        f"₱{compact_number(total_refunds)}",
    )

    lg4.metric(
        "Lost Shipments",
        f"{lost_shipments:,}",
    )

    lgrow1a, lgrow1b = st.columns(
        2,
        gap="medium",
    )

    shipment_status_df = (
        shipment_scope[
            "shipment_status"
        ]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("shipment_status")
        .reset_index(name="count")
    )

    fig = px.pie(
        shipment_status_df,
        names="shipment_status",
        values="count",
        hole=.58,
        title="Shipment Status",
        color_discrete_sequence=PALETTE,
    )

    with lgrow1a:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    courier_df = (
        shipment_scope[
            "courier"
        ]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("courier")
        .reset_index(name="shipments")
        .sort_values("shipments")
    )

    fig = px.bar(
        courier_df,
        x="shipments",
        y="courier",
        orientation="h",
        title="Shipment Volume by Courier",
        labels={
            "shipments": "Shipments",
            "courier": "Courier",
        },
        color="shipments",
        color_continuous_scale=[
            "#DBEAFE",
            BLUE,
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    with lgrow1b:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    lgrow2a, lgrow2b = st.columns(
        2,
        gap="medium",
    )

    delivery_by_courier = (
        shipment_scope
        .groupby(
            "courier",
            as_index=False,
        )["delivery_days"]
        .median()
        .dropna()
        .sort_values("delivery_days")
    )

    fig = px.bar(
        delivery_by_courier,
        x="delivery_days",
        y="courier",
        orientation="h",
        title="Median Delivery Days by Courier",
        labels={
            "delivery_days": "Median Delivery Days",
            "courier": "Courier",
        },
        color="delivery_days",
        color_continuous_scale=[
            "#ECFDF5",
            "#16A34A",
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    with lgrow2a:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    fig = px.histogram(
        shipment_scope.dropna(
            subset=[
                "delivery_days"
            ]
        ),
        x="delivery_days",
        nbins=20,
        title="Delivery Time Distribution",
        labels={
            "delivery_days": "Delivery Days",
        },
        color_discrete_sequence=[
            BLUE
        ],
    )

    fig.update_layout(
        yaxis_title="Shipments",
    )

    with lgrow2b:
        chart_card(
            style_figure(
                fig,
                height=410,
            )
        )

    lgrow3a, lgrow3b = st.columns(
        2,
        gap="medium",
    )

    return_reason_df = (
        return_scope[
            "reason"
        ]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("reason")
        .reset_index(name="returns")
        .sort_values("returns")
    )

    fig = px.bar(
        return_reason_df,
        x="returns",
        y="reason",
        orientation="h",
        title="Return Reasons",
        labels={
            "returns": "Return Requests",
            "reason": "Reason",
        },
        color="returns",
        color_continuous_scale=[
            "#FFEDD5",
            ORANGE,
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    with lgrow3a:
        chart_card(
            style_figure(
                fig,
                height=430,
            )
        )

    refund_flag_df = (
        return_scope[
            "refunded_flag_clean"
        ]
        .value_counts()
        .rename_axis("refund_status")
        .reset_index(name="count")
    )

    fig = px.pie(
        refund_flag_df,
        names="refund_status",
        values="count",
        hole=.58,
        title="Return Refund Status",
        color_discrete_sequence=PALETTE,
    )

    with lgrow3b:
        chart_card(
            style_figure(
                fig,
                height=430,
            )
        )

    refund_reason_df = (
        return_scope
        .groupby(
            "reason",
            as_index=False,
        )["refund_amount_clean"]
        .sum()
        .sort_values("refund_amount_clean")
    )

    fig = px.bar(
        refund_reason_df,
        x="refund_amount_clean",
        y="reason",
        orientation="h",
        title="Refund Amount by Return Reason",
        labels={
            "refund_amount_clean": "Refund Amount (PHP)",
            "reason": "Return Reason",
        },
        color="refund_amount_clean",
        color_continuous_scale=[
            "#FFE4E6",
            "#E11D48",
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickprefix="₱",
        xaxis_tickformat=",.0f",
    )

    chart_card(
        style_figure(
            fig,
            height=430,
        )
    )


# ============================================================
# 19. DATA EXPLORER + QUALITY TAB
# ============================================================

with data_tab:
    st.subheader("Data Explorer & Quality Checks")

    dq1, dq2 = st.columns(
        2,
        gap="medium",
    )

    count_rows = []

    for dataset_name in raw_counts:
        count_rows.append(
            {
                "Dataset": dataset_name,
                "Raw Rows": raw_counts[
                    dataset_name
                ],
                "Clean Rows": clean_counts[
                    dataset_name
                ],
            }
        )

    count_df = pd.DataFrame(
        count_rows
    )

    count_long = count_df.melt(
        id_vars="Dataset",
        var_name="Stage",
        value_name="Rows",
    )

    fig = px.bar(
        count_long,
        x="Dataset",
        y="Rows",
        color="Stage",
        barmode="group",
        title="Raw vs Clean Row Counts",
        color_discrete_sequence=[
            "#94A3B8",
            BLUE,
        ],
    )

    with dq1:
        chart_card(
            style_figure(
                fig,
                height=430,
            )
        )

    quality_summary = pd.DataFrame(
        {
            "Metric": [
                "Filtered item rows",
                "Filtered all orders",
                "Filtered fulfilled orders",
                "Payment records",
                "Shipment records",
                "Return records",
            ],
            "Value": [
                len(filtered_all),
                len(filtered_orders_all),
                len(
                    filtered_orders_fulfilled
                ),
                len(payment_scope),
                len(shipment_scope),
                len(return_scope),
            ],
        }
    )

    with dq2:
        with st.container(border=True):
            st.markdown(
                "#### Current Filter Scope"
            )
            st.dataframe(
                quality_summary,
                width="stretch",
                hide_index=True,
                column_config={
                    "Metric": "Metric",
                    "Value": st.column_config.NumberColumn(
                        "Records",
                        format="%d",
                    ),
                },
            )

    with st.container(border=True):
        st.subheader(
            "Filtered Transaction Details"
        )

        detail_columns = [
            "order_id",
            "order_date",
            "customer_name",
            "product_name",
            "brand",
            "category_clean",
            "quantity_clean",
            "unit_price_clean",
            "sales_channel",
            "shipping_method",
            "region_name",
            "city",
            "discount_pct_clean",
            "gross_sales",
            "net_sales",
            "estimated_profit",
        ]

        detail = (
            filtered_all[
                detail_columns
            ]
            .sort_values(
                "order_date",
                ascending=False,
            )
            .copy()
        )

        detail[
            "discount_percent"
        ] = (
            detail[
                "discount_pct_clean"
            ]
            * 100
        )

        detail = detail.drop(
            columns=[
                "discount_pct_clean"
            ]
        )

        st.dataframe(
            detail,
            width="stretch",
            hide_index=True,
            column_config={
                "order_id": st.column_config.TextColumn(
                    "Order ID",
                    pinned=True,
                ),
                "order_date": st.column_config.DatetimeColumn(
                    "Order Date",
                    format="DD MMM YYYY, hh:mm a",
                ),
                "customer_name": st.column_config.TextColumn(
                    "Customer",
                    width="medium",
                ),
                "product_name": st.column_config.TextColumn(
                    "Product",
                    width="large",
                ),
                "brand": "Brand",
                "category_clean": "Category",
                "quantity_clean": st.column_config.NumberColumn(
                    "Qty",
                    format="%d",
                ),
                "unit_price_clean": st.column_config.NumberColumn(
                    "Unit Price",
                    format="₱ %.2f",
                ),
                "sales_channel": "Channel",
                "shipping_method": "Shipping",
                "region_name": "Region",
                "city": "City",
                "discount_percent": st.column_config.NumberColumn(
                    "Discount",
                    format="%.1f%%",
                ),
                "gross_sales": st.column_config.NumberColumn(
                    "Gross Sales",
                    format="₱ %.2f",
                ),
                "net_sales": st.column_config.NumberColumn(
                    "Net Sales",
                    format="₱ %.2f",
                ),
                "estimated_profit": st.column_config.NumberColumn(
                    "Est. Profit",
                    format="₱ %.2f",
                ),
            },
        )

        st.download_button(
            "Download Filtered Transactions",
            data=detail.to_csv(
                index=False
            ).encode("utf-8"),
            file_name=(
                "retail_filtered_transactions.csv"
            ),
            mime="text/csv",
            width="stretch",
        )

    with st.expander(
        "Cleaning rules used by this dashboard"
    ):
        st.markdown(
            """
            - Exact duplicate rows are removed.
            - Product category variants are standardized.
            - Currency-like values are converted to numeric.
            - Non-positive item quantities are excluded.
            - Mixed date formats are parsed with `format="mixed"`.
            - Missing order discounts are treated as zero.
            - Invalid discount rates are reset to zero.
            - Orders must reference an existing customer.
            - Order items must reference existing orders and products.
            - Sales KPIs use **Completed** and **Shipped** orders.
            - Estimated profit is `net sales - estimated product cost`.
            - Shipping fee is not included in net sales.
            """
        )
