from pathlib import Path
from io import BytesIO
import base64
import html

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    PageBreak,
    KeepTogether,
)


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Retail Analytics Studio",
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
# 2. PREMIUM ANIMATED DASHBOARD STYLING
# ============================================================

st.markdown(
    f"""
    <style>
        :root {{
            --brand-blue: {BLUE};
            --brand-cyan: #38A3FF;
            --brand-violet: #6D5DFB;
            --brand-teal: #00A6A6;
            --brand-orange: {ORANGE};
            --brand-green: #22C55E;
            --ink: #172033;
            --muted: #667085;
        }}

        @keyframes fadeUp {{
            from {{
                opacity: 0;
                transform: translateY(18px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes gradientFlow {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        @keyframes floatOrb {{
            0%, 100% {{
                transform: translate3d(0, 0, 0) scale(1);
            }}
            50% {{
                transform: translate3d(10px, -14px, 0) scale(1.08);
            }}
        }}

        @keyframes pulseDot {{
            0% {{
                box-shadow: 0 0 0 0 rgba(34,197,94,.55);
            }}
            70% {{
                box-shadow: 0 0 0 9px rgba(34,197,94,0);
            }}
            100% {{
                box-shadow: 0 0 0 0 rgba(34,197,94,0);
            }}
        }}

        @keyframes shine {{
            0% {{ transform: translateX(-140%); }}
            100% {{ transform: translateX(220%); }}
        }}

        html {{
            scroll-behavior: smooth;
        }}

        .stApp {{
            background:
                radial-gradient(
                    circle at 8% 0%,
                    rgba(56,163,255,.10),
                    transparent 25%
                ),
                radial-gradient(
                    circle at 95% 12%,
                    rgba(109,93,251,.09),
                    transparent 22%
                ),
                linear-gradient(
                    180deg,
                    #F8FAFF 0%,
                    #F7F9FC 55%,
                    #FBFCFE 100%
                );
        }}

        .block-container {{
            max-width: 1540px;
            padding-top: 1.25rem;
            padding-bottom: 2.6rem;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background:
                linear-gradient(
                    180deg,
                    #061C48 0%,
                    #082A68 48%,
                    #0A377C 100%
                );
            border-right: 1px solid rgba(255,255,255,.08);
        }}

        section[data-testid="stSidebar"] * {{
            color: #F8FBFF;
        }}

        section[data-testid="stSidebar"] label {{
            font-weight: 650;
        }}

        section[data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,.14);
        }}

        /* Hero */
        .hero {{
            position: relative;
            overflow: hidden;
            border-radius: 26px;
            padding: 1.65rem 1.8rem 1.55rem 1.8rem;
            margin-bottom: .95rem;
            color: white;
            background:
                linear-gradient(
                    120deg,
                    #061C48,
                    #0247B7,
                    #635BFF,
                    #0E7490
                );
            background-size: 300% 300%;
            animation:
                gradientFlow 12s ease infinite,
                fadeUp .55s ease both;
            box-shadow:
                0 20px 55px rgba(2,71,183,.20);
            isolation: isolate;
        }}

        .hero::before {{
            content: "";
            position: absolute;
            width: 230px;
            height: 230px;
            border-radius: 50%;
            right: -55px;
            top: -100px;
            background:
                radial-gradient(
                    circle,
                    rgba(255,255,255,.30),
                    rgba(255,255,255,.02) 70%
                );
            animation: floatOrb 7s ease-in-out infinite;
            z-index: -1;
        }}

        .hero::after {{
            content: "";
            position: absolute;
            width: 160px;
            height: 160px;
            border-radius: 50%;
            right: 180px;
            bottom: -115px;
            background:
                radial-gradient(
                    circle,
                    rgba(244,122,42,.45),
                    rgba(244,122,42,.02) 72%
                );
            animation: floatOrb 9s ease-in-out infinite reverse;
            z-index: -1;
        }}

        .hero-topline {{
            display: flex;
            align-items: center;
            gap: .65rem;
            margin-bottom: .65rem;
        }}

        .live-dot {{
            width: 9px;
            height: 9px;
            background: #22C55E;
            border-radius: 50%;
            animation: pulseDot 1.8s infinite;
        }}

        .hero-kicker {{
            color: #DDEAFF;
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .10em;
            text-transform: uppercase;
        }}

        .hero-title {{
            color: #FFFFFF;
            font-size: clamp(2rem, 3.2vw, 3.05rem);
            font-weight: 850;
            line-height: 1.06;
            letter-spacing: -.035em;
            margin-bottom: .45rem;
        }}

        .hero-sub {{
            max-width: 850px;
            color: rgba(255,255,255,.84);
            font-size: 1rem;
            line-height: 1.55;
        }}

        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            margin-top: .95rem;
            padding: .42rem .72rem;
            border-radius: 999px;
            background: rgba(255,255,255,.12);
            border: 1px solid rgba(255,255,255,.18);
            color: white;
            font-size: .80rem;
            font-weight: 650;
        }}

        /* Filter pills */
        .chips {{
            display: flex;
            flex-wrap: wrap;
            gap: .5rem;
            margin: .35rem 0 1.1rem 0;
            animation: fadeUp .55s .08s ease both;
        }}

        .chip {{
            background:
                linear-gradient(
                    135deg,
                    rgba(255,255,255,.96),
                    rgba(238,244,255,.95)
                );
            border: 1px solid rgba(2,71,183,.15);
            color: var(--brand-blue);
            border-radius: 999px;
            padding: .36rem .72rem;
            font-size: .80rem;
            font-weight: 700;
            box-shadow: 0 5px 18px rgba(15,23,42,.05);
            transition:
                transform .20s ease,
                box-shadow .20s ease;
        }}

        .chip:hover {{
            transform: translateY(-2px);
            box-shadow: 0 9px 22px rgba(2,71,183,.12);
        }}

        /* Animated metric cards */
        div[data-testid="stMetric"] {{
            position: relative;
            overflow: hidden;
            min-height: 116px;
            padding: 1rem 1rem .88rem 1rem;
            border: 1px solid rgba(148,163,184,.24);
            border-radius: 18px;
            background:
                linear-gradient(
                    145deg,
                    rgba(255,255,255,.98),
                    rgba(242,247,255,.92)
                );
            box-shadow:
                0 10px 28px rgba(15,23,42,.07);
            animation: fadeUp .5s ease both;
            transition:
                transform .22s ease,
                box-shadow .22s ease,
                border-color .22s ease;
        }}

        div[data-testid="stMetric"]::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            width: 5px;
            height: 100%;
            background:
                linear-gradient(
                    180deg,
                    #38A3FF,
                    #0247B7,
                    #6D5DFB
                );
        }}

        div[data-testid="stMetric"]::after {{
            content: "";
            position: absolute;
            width: 80px;
            height: 180%;
            top: -35%;
            left: -120px;
            transform: rotate(18deg);
            background:
                linear-gradient(
                    90deg,
                    transparent,
                    rgba(255,255,255,.65),
                    transparent
                );
            animation: shine 6.5s ease-in-out infinite;
            pointer-events: none;
        }}

        div[data-testid="stMetric"]:hover {{
            transform: translateY(-5px);
            border-color: rgba(2,71,183,.32);
            box-shadow:
                0 18px 40px rgba(2,71,183,.13);
        }}

        div[data-testid="stMetricLabel"] {{
            color: #64748B;
            font-weight: 700;
        }}

        div[data-testid="stMetricValue"] {{
            color: #102A56;
            font-weight: 850;
            letter-spacing: -.025em;
        }}

        /* Bordered containers / chart cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 20px !important;
            background:
                linear-gradient(
                    145deg,
                    rgba(255,255,255,.96),
                    rgba(248,250,255,.91)
                ) !important;
            border: 1px solid rgba(148,163,184,.22) !important;
            box-shadow: 0 9px 26px rgba(15,23,42,.055);
            animation: fadeUp .48s ease both;
            transition:
                transform .20s ease,
                box-shadow .20s ease,
                border-color .20s ease;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            transform: translateY(-2px);
            border-color: rgba(56,163,255,.34) !important;
            box-shadow: 0 16px 34px rgba(2,71,183,.09);
        }}

        div[data-testid="stPlotlyChart"] {{
            animation: fadeUp .52s ease both;
        }}

        /* Headings */
        h1, h2, h3 {{
            color: var(--ink);
            letter-spacing: -.02em;
        }}

        h2 {{
            position: relative;
            padding-left: .75rem;
        }}

        h2::before {{
            content: "";
            position: absolute;
            width: 4px;
            height: 72%;
            left: 0;
            top: 15%;
            border-radius: 99px;
            background:
                linear-gradient(
                    180deg,
                    #38A3FF,
                    #6D5DFB
                );
        }}

        .section-note {{
            color: var(--muted);
            font-size: .86rem;
            margin-top: -.4rem;
            margin-bottom: .85rem;
        }}

        /* Tabs */
        div[data-baseweb="tab-list"] {{
            gap: .35rem;
            padding: .32rem;
            border-radius: 16px;
            background: rgba(232,238,248,.76);
            margin-bottom: .7rem;
        }}

        button[data-baseweb="tab"] {{
            border-radius: 12px;
            padding-left: .9rem;
            padding-right: .9rem;
            transition:
                background .20s ease,
                transform .20s ease,
                color .20s ease;
        }}

        button[data-baseweb="tab"]:hover {{
            transform: translateY(-1px);
            background: rgba(255,255,255,.75);
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            background:
                linear-gradient(
                    135deg,
                    #0247B7,
                    #5B6CFF
                );
            color: white !important;
            box-shadow: 0 7px 18px rgba(2,71,183,.20);
        }}

        button[data-baseweb="tab"][aria-selected="true"] * {{
            color: white !important;
        }}

        /* Buttons */
        div[data-testid="stButton"] button,
        div[data-testid="stDownloadButton"] button {{
            border-radius: 12px;
            font-weight: 750;
            transition:
                transform .18s ease,
                box-shadow .18s ease;
        }}

        div[data-testid="stButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(2,71,183,.15);
        }}

        /* Tables */
        div[data-testid="stDataFrame"] {{
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 22px rgba(15,23,42,.055);
        }}

        /* Expanders */
        details {{
            border-radius: 15px !important;
            border-color: rgba(148,163,184,.24) !important;
            background: rgba(255,255,255,.76);
        }}

        @media (max-width: 900px) {{
            .hero {{
                padding: 1.3rem;
            }}

            .hero-title {{
                font-size: 2rem;
            }}

            div[data-testid="stMetric"] {{
                min-height: 100px;
            }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            *,
            *::before,
            *::after {{
                animation-duration: .01ms !important;
                animation-iteration-count: 1 !important;
                scroll-behavior: auto !important;
                transition-duration: .01ms !important;
            }}
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
            l=18,
            r=18,
            t=62,
            b=28,
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
        plot_bgcolor="rgba(255,255,255,0)",
        paper_bgcolor="rgba(255,255,255,0)",
        hoverlabel=dict(
            bgcolor="#0F2A56",
            bordercolor="#0F2A56",
            font_color="white",
            font_size=12,
        ),
        transition=dict(
            duration=420,
            easing="cubic-in-out",
        ),
        uirevision="retail-dashboard",
    )

    fig.update_xaxes(
        gridcolor="rgba(148,163,184,.18)",
        zerolinecolor="rgba(148,163,184,.24)",
        linecolor="rgba(148,163,184,.18)",
    )

    fig.update_yaxes(
        gridcolor="rgba(148,163,184,.18)",
        zerolinecolor="rgba(148,163,184,.24)",
        linecolor="rgba(148,163,184,.18)",
    )

    return fig


def chart_card(fig):
    with st.container(border=True):
        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displaylogo": False,
                "responsive": True,
                "scrollZoom": False,
                "modeBarButtonsToRemove": [
                    "lasso2d",
                    "select2d",
                ],
            },
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
# 4. REPORT / PRINT HELPERS
# ============================================================

PDF_BLUE = "#0247B7"
PDF_ORANGE = "#F47A2A"
PDF_TEAL = "#00A6A6"
PDF_GREEN = "#16A34A"
PDF_PURPLE = "#6D5DFB"
PDF_GRAY = "#64748B"


def _currency(value):
    if pd.isna(value):
        return "PHP 0.00"
    return f"PHP {float(value):,.2f}"


def _percent(value):
    if pd.isna(value):
        return "0.0%"
    return f"{float(value):.1f}%"


def _matplotlib_bytes(fig):
    """
    Convert a Matplotlib figure to PNG bytes for PDF/HTML reporting.
    """
    buffer = BytesIO()

    fig.savefig(
        buffer,
        format="png",
        dpi=170,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)

    buffer.seek(0)
    return buffer


def _base_axes(title):
    fig, ax = plt.subplots(
        figsize=(9.2, 4.8)
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.set_title(
        title,
        loc="left",
        fontsize=14,
        fontweight="bold",
        color="#172033",
        pad=14,
    )

    ax.spines[
        [
            "top",
            "right",
        ]
    ].set_visible(False)

    ax.grid(
        axis="y",
        alpha=.17,
        linewidth=.8,
    )

    return fig, ax


def report_monthly_sales_chart(filtered_fulfilled):
    monthly = (
        filtered_fulfilled
        .groupby(
            "month",
            as_index=False,
        )
        .agg(
            gross_sales=("gross_sales", "sum"),
            net_sales=("net_sales", "sum"),
        )
        .sort_values("month")
    )

    fig, ax = _base_axes(
        "Monthly Gross vs Net Sales"
    )

    ax.plot(
        monthly["month"],
        monthly["gross_sales"],
        marker="o",
        linewidth=2.4,
        label="Gross Sales",
        color=PDF_BLUE,
    )

    ax.plot(
        monthly["month"],
        monthly["net_sales"],
        marker="o",
        linewidth=2.4,
        label="Net Sales",
        color=PDF_ORANGE,
    )

    ax.set_ylabel("Sales (PHP)")
    ax.tick_params(
        axis="x",
        rotation=35,
    )
    ax.legend(
        frameon=False,
        loc="upper left",
    )

    return _matplotlib_bytes(fig)


def report_category_chart(filtered_fulfilled):
    data = (
        filtered_fulfilled
        .groupby(
            "category_clean",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values("gross_sales")
    )

    fig, ax = _base_axes(
        "Gross Sales by Category"
    )

    ax.barh(
        data["category_clean"],
        data["gross_sales"],
        color=PDF_BLUE,
        alpha=.88,
    )

    ax.set_xlabel("Gross Sales (PHP)")
    ax.grid(
        axis="x",
        alpha=.17,
    )
    ax.grid(
        axis="y",
        visible=False,
    )

    return _matplotlib_bytes(fig)


def report_region_chart(filtered_fulfilled):
    data = (
        filtered_fulfilled
        .groupby(
            "region_name",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values("gross_sales")
    )

    fig, ax = _base_axes(
        "Gross Sales by Region"
    )

    ax.barh(
        data["region_name"],
        data["gross_sales"],
        color=PDF_TEAL,
        alpha=.88,
    )

    ax.set_xlabel("Gross Sales (PHP)")
    ax.grid(
        axis="x",
        alpha=.17,
    )
    ax.grid(
        axis="y",
        visible=False,
    )

    return _matplotlib_bytes(fig)


def report_order_status_chart(filtered_orders_all):
    data = (
        filtered_orders_all[
            "order_status"
        ]
        .fillna("Unknown")
        .value_counts()
    )

    fig, ax = plt.subplots(
        figsize=(8.2, 4.8)
    )

    ax.pie(
        data.values,
        labels=data.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=[
            PDF_BLUE,
            PDF_ORANGE,
            PDF_TEAL,
            PDF_PURPLE,
            PDF_GREEN,
            "#94A3B8",
        ][:len(data)],
        textprops={
            "fontsize": 9
        },
    )

    ax.set_title(
        "Order Status Mix",
        loc="left",
        fontsize=14,
        fontweight="bold",
        color="#172033",
    )

    return _matplotlib_bytes(fig)


def report_top_products_chart(filtered_fulfilled):
    data = (
        filtered_fulfilled
        .groupby(
            "product_name",
            as_index=False,
        )["gross_sales"]
        .sum()
        .sort_values(
            "gross_sales",
            ascending=False,
        )
        .head(10)
        .sort_values("gross_sales")
    )

    fig, ax = _base_axes(
        "Top 10 Products by Gross Sales"
    )

    ax.barh(
        data["product_name"],
        data["gross_sales"],
        color=PDF_PURPLE,
        alpha=.88,
    )

    ax.set_xlabel("Gross Sales (PHP)")
    ax.grid(
        axis="x",
        alpha=.17,
    )
    ax.grid(
        axis="y",
        visible=False,
    )

    return _matplotlib_bytes(fig)


def report_loyalty_chart(filtered_fulfilled):
    data = (
        filtered_fulfilled
        .groupby(
            "loyalty_tier",
            as_index=False,
            dropna=False,
        )["net_sales"]
        .sum()
    )

    data["loyalty_tier"] = (
        data["loyalty_tier"]
        .fillna("Unknown")
    )

    data = data.sort_values(
        "net_sales",
        ascending=False,
    )

    fig, ax = _base_axes(
        "Net Sales by Loyalty Tier"
    )

    ax.bar(
        data["loyalty_tier"],
        data["net_sales"],
        color=PDF_BLUE,
        alpha=.88,
    )

    ax.set_ylabel("Net Sales (PHP)")
    ax.tick_params(
        axis="x",
        rotation=20,
    )

    return _matplotlib_bytes(fig)


def report_profit_chart(filtered_fulfilled):
    data = (
        filtered_fulfilled
        .groupby(
            "category_clean",
            as_index=False,
        )["estimated_profit"]
        .sum()
        .sort_values("estimated_profit")
    )

    fig, ax = _base_axes(
        "Estimated Profit by Category"
    )

    ax.barh(
        data["category_clean"],
        data["estimated_profit"],
        color=PDF_GREEN,
        alpha=.88,
    )

    ax.set_xlabel("Estimated Profit (PHP)")
    ax.grid(
        axis="x",
        alpha=.17,
    )
    ax.grid(
        axis="y",
        visible=False,
    )

    return _matplotlib_bytes(fig)


def report_discount_chart(filtered_orders_fulfilled):
    fig, ax = _base_axes(
        "Order Discount Distribution"
    )

    discounts = (
        filtered_orders_fulfilled[
            "discount_pct"
        ]
        .dropna()
        * 100
    )

    ax.hist(
        discounts,
        bins=20,
        color=PDF_ORANGE,
        alpha=.88,
        edgecolor="white",
    )

    ax.set_xlabel("Discount (%)")
    ax.set_ylabel("Orders")

    return _matplotlib_bytes(fig)


def report_payment_chart(payment_scope):
    data = (
        payment_scope[
            "payment_method"
        ]
        .fillna("Unknown")
        .value_counts()
        .sort_values()
    )

    fig, ax = _base_axes(
        "Payment Method Usage"
    )

    ax.barh(
        data.index,
        data.values,
        color=PDF_BLUE,
        alpha=.88,
    )

    ax.set_xlabel("Payment Records")
    ax.grid(
        axis="x",
        alpha=.17,
    )
    ax.grid(
        axis="y",
        visible=False,
    )

    return _matplotlib_bytes(fig)


def report_shipment_chart(shipment_scope):
    data = (
        shipment_scope[
            "shipment_status"
        ]
        .fillna("Unknown")
        .value_counts()
    )

    fig, ax = plt.subplots(
        figsize=(8.2, 4.8)
    )

    ax.pie(
        data.values,
        labels=data.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=[
            PDF_BLUE,
            PDF_TEAL,
            PDF_ORANGE,
            PDF_PURPLE,
            "#94A3B8",
        ][:len(data)],
        textprops={
            "fontsize": 9
        },
    )

    ax.set_title(
        "Shipment Status",
        loc="left",
        fontsize=14,
        fontweight="bold",
        color="#172033",
    )

    return _matplotlib_bytes(fig)


def report_delivery_chart(shipment_scope):
    data = (
        shipment_scope
        .groupby(
            "courier",
            as_index=False,
        )["delivery_days"]
        .median()
        .dropna()
        .sort_values("delivery_days")
    )

    fig, ax = _base_axes(
        "Median Delivery Days by Courier"
    )

    ax.barh(
        data["courier"],
        data["delivery_days"],
        color=PDF_TEAL,
        alpha=.88,
    )

    ax.set_xlabel("Median Delivery Days")
    ax.grid(
        axis="x",
        alpha=.17,
    )
    ax.grid(
        axis="y",
        visible=False,
    )

    return _matplotlib_bytes(fig)


def report_return_chart(return_scope):
    data = (
        return_scope[
            "reason"
        ]
        .fillna("Unknown")
        .value_counts()
        .sort_values()
    )

    fig, ax = _base_axes(
        "Return Reasons"
    )

    ax.barh(
        data.index,
        data.values,
        color=PDF_ORANGE,
        alpha=.88,
    )

    ax.set_xlabel("Return Requests")
    ax.grid(
        axis="x",
        alpha=.17,
    )
    ax.grid(
        axis="y",
        visible=False,
    )

    return _matplotlib_bytes(fig)


def _pdf_header_footer(canvas, doc):
    canvas.saveState()

    width, height = landscape(A4)

    canvas.setFillColor(
        colors.HexColor(PDF_BLUE)
    )

    canvas.rect(
        0,
        height - 9 * mm,
        width,
        9 * mm,
        fill=1,
        stroke=0,
    )

    canvas.setFillColor(
        colors.HexColor("#FFFFFF")
    )

    canvas.setFont(
        "Helvetica-Bold",
        8.5,
    )

    canvas.drawString(
        12 * mm,
        height - 6 * mm,
        "DataSense Analytics · Retail Analytics Report",
    )

    canvas.setFillColor(
        colors.HexColor("#64748B")
    )

    canvas.setFont(
        "Helvetica",
        8,
    )

    canvas.drawString(
        12 * mm,
        7 * mm,
        "Generated from the current dashboard filters",
    )

    canvas.drawRightString(
        width - 12 * mm,
        7 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


def _pdf_chart_pair(
    left_buffer,
    right_buffer,
    width=121 * mm,
    height=65 * mm,
):
    left = RLImage(
        left_buffer,
        width=width,
        height=height,
    )

    right = RLImage(
        right_buffer,
        width=width,
        height=height,
    )

    table = Table(
        [
            [
                left,
                right,
            ]
        ],
        colWidths=[
            width + 2 * mm,
            width + 2 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    return table


def build_pdf_report(
    filtered_fulfilled,
    filtered_orders_all,
    filtered_orders_fulfilled,
    payment_scope,
    shipment_scope,
    return_scope,
    filter_text,
    raw_counts,
    clean_counts,
):
    """
    Build a multi-page PDF report from the current dashboard filters.

    Plotly remains the interactive dashboard engine.
    Matplotlib is used here for reliable report rendering.
    """
    output = BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=16 * mm,
        bottomMargin=13 * mm,
        title="Retail Analytics Report",
        author="DataSense Analytics",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=29,
        textColor=colors.HexColor(
            "#102A56"
        ),
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor(
            PDF_BLUE
        ),
        spaceBefore=5,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor(
            "#475569"
        ),
    )

    small_style = ParagraphStyle(
        "SmallBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor(
            "#64748B"
        ),
    )

    story = []

    gross_sales = (
        filtered_fulfilled[
            "gross_sales"
        ].sum()
    )

    net_sales = (
        filtered_fulfilled[
            "net_sales"
        ].sum()
    )

    estimated_profit = (
        filtered_fulfilled[
            "estimated_profit"
        ].sum()
    )

    discount_value = (
        filtered_fulfilled[
            "discount_amount"
        ].sum()
    )

    units_sold = (
        filtered_fulfilled[
            "quantity_clean"
        ].sum()
    )

    fulfilled_orders = (
        filtered_fulfilled[
            "order_id"
        ].nunique()
    )

    unique_customers = (
        filtered_fulfilled[
            "customer_id"
        ].nunique()
    )

    aov = (
        filtered_orders_fulfilled[
            "net_order_value"
        ].mean()
        if not filtered_orders_fulfilled.empty
        else 0
    )

    margin = (
        estimated_profit
        / net_sales
        * 100
        if net_sales
        else 0
    )

    returned_orders = (
        return_scope[
            "order_id"
        ].nunique()
    )

    return_rate = (
        returned_orders
        / len(filtered_orders_all)
        * 100
        if len(filtered_orders_all)
        else 0
    )

    delivery_median = (
        shipment_scope[
            "delivery_days"
        ]
        .dropna()
        .median()
    )

    # --------------------------------------------------------
    # Cover / executive page
    # --------------------------------------------------------

    story.append(
        Spacer(
            1,
            8 * mm,
        )
    )

    story.append(
        Paragraph(
            "Retail Analytics Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Sales, product, customer, profitability, payment, "
            "logistics and returns performance",
            body_style,
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    filter_box = Table(
        [
            [
                Paragraph(
                    "<b>Report scope</b>",
                    body_style,
                ),
                Paragraph(
                    filter_text,
                    body_style,
                ),
            ]
        ],
        colWidths=[
            36 * mm,
            210 * mm,
        ],
    )

    filter_box.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        "#EEF4FF"
                    ),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    .6,
                    colors.HexColor(
                        "#D8E6FF"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(filter_box)

    story.append(
        Spacer(
            1,
            6 * mm,
        )
    )

    kpi_data = [
        [
            "Gross Sales",
            "Net Sales",
            "Fulfilled Orders",
            "Average Order Value",
        ],
        [
            _currency(gross_sales),
            _currency(net_sales),
            f"{fulfilled_orders:,}",
            _currency(aov),
        ],
        [
            "Units Sold",
            "Unique Customers",
            "Estimated Profit",
            "Estimated Margin",
        ],
        [
            f"{units_sold:,.0f}",
            f"{unique_customers:,}",
            _currency(
                estimated_profit
            ),
            _percent(margin),
        ],
    ]

    kpi_table = Table(
        kpi_data,
        colWidths=[
            61 * mm,
            61 * mm,
            61 * mm,
            61 * mm,
        ],
        rowHeights=[
            9 * mm,
            14 * mm,
            9 * mm,
            14 * mm,
        ],
    )

    kpi_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.white,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#EAF2FF"
                    ),
                ),
                (
                    "BACKGROUND",
                    (0, 2),
                    (-1, 2),
                    colors.HexColor(
                        "#EAF2FF"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#475569"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 2),
                    (-1, 2),
                    colors.HexColor(
                        "#475569"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 1),
                    (-1, 1),
                    colors.HexColor(
                        "#102A56"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 3),
                    (-1, 3),
                    colors.HexColor(
                        "#102A56"
                    ),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 2),
                    (-1, 2),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, 1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 3),
                    (-1, 3),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, 1),
                    15,
                ),
                (
                    "FONTSIZE",
                    (0, 3),
                    (-1, 3),
                    15,
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    .4,
                    colors.HexColor(
                        "#DCE5F1"
                    ),
                ),
            ]
        )
    )

    story.append(kpi_table)

    story.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    additional = Table(
        [
            [
                "Discount Value",
                _currency(discount_value),
                "Return Rate",
                _percent(return_rate),
                "Median Delivery",
                (
                    f"{delivery_median:.0f} days"
                    if pd.notna(
                        delivery_median
                    )
                    else "N/A"
                ),
            ]
        ],
        colWidths=[
            28 * mm,
            42 * mm,
            25 * mm,
            28 * mm,
            30 * mm,
            34 * mm,
        ],
    )

    additional.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        "#F8FAFC"
                    ),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    .4,
                    colors.HexColor(
                        "#E2E8F0"
                    ),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (2, 0),
                    (2, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (4, 0),
                    (4, -1),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8.5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(additional)

    story.append(PageBreak())

    # --------------------------------------------------------
    # Executive charts
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Executive Performance",
            section_style,
        )
    )

    story.append(
        _pdf_chart_pair(
            report_monthly_sales_chart(
                filtered_fulfilled
            ),
            report_order_status_chart(
                filtered_orders_all
            ),
        )
    )

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    story.append(
        _pdf_chart_pair(
            report_category_chart(
                filtered_fulfilled
            ),
            report_region_chart(
                filtered_fulfilled
            ),
        )
    )

    story.append(PageBreak())

    # --------------------------------------------------------
    # Product + customer
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Products & Customers",
            section_style,
        )
    )

    story.append(
        _pdf_chart_pair(
            report_top_products_chart(
                filtered_fulfilled
            ),
            report_loyalty_chart(
                filtered_fulfilled
            ),
        )
    )

    top_customers = (
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
            Net_Spend=("net_sales", "sum"),
        )
        .sort_values(
            "Net_Spend",
            ascending=False,
        )
        .head(12)
    )

    customer_rows = [
        [
            "Customer",
            "Tier",
            "Region",
            "Orders",
            "Net Spend",
        ]
    ]

    for _, row in top_customers.iterrows():
        customer_rows.append(
            [
                str(
                    row[
                        "customer_name"
                    ]
                )[:32],
                str(
                    row[
                        "loyalty_tier"
                    ]
                ),
                str(
                    row[
                        "region_name"
                    ]
                )[:24],
                f"{int(row['Orders']):,}",
                _currency(
                    row[
                        "Net_Spend"
                    ]
                ),
            ]
        )

    customer_table = Table(
        customer_rows,
        colWidths=[
            70 * mm,
            35 * mm,
            54 * mm,
            25 * mm,
            45 * mm,
        ],
        repeatRows=1,
    )

    customer_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        PDF_BLUE
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    .35,
                    colors.HexColor(
                        "#DCE5F1"
                    ),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor(
                            "#F8FAFC"
                        ),
                    ],
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    story.append(
        KeepTogether(
            [
                Paragraph(
                    "Top Customers",
                    section_style,
                ),
                customer_table,
            ]
        )
    )

    story.append(PageBreak())

    # --------------------------------------------------------
    # Profitability + payments
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Profitability & Payments",
            section_style,
        )
    )

    story.append(
        _pdf_chart_pair(
            report_profit_chart(
                filtered_fulfilled
            ),
            report_discount_chart(
                filtered_orders_fulfilled
            ),
        )
    )

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    payment_status_data = (
        payment_scope[
            "payment_status"
        ]
        .fillna("Unknown")
        .value_counts()
        .rename_axis(
            "Payment Status"
        )
        .reset_index(
            name="Records"
        )
    )

    payment_rows = [
        [
            "Payment Status",
            "Records",
        ]
    ]

    for _, row in payment_status_data.iterrows():
        payment_rows.append(
            [
                str(
                    row[
                        "Payment Status"
                    ]
                ),
                f"{int(row['Records']):,}",
            ]
        )

    payment_table = Table(
        payment_rows,
        colWidths=[
            80 * mm,
            35 * mm,
        ],
    )

    payment_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#EAF2FF"
                    ),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    .4,
                    colors.HexColor(
                        "#DCE5F1"
                    ),
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8.5,
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "RIGHT",
                ),
            ]
        )
    )

    lower = Table(
        [
            [
                RLImage(
                    report_payment_chart(
                        payment_scope
                    ),
                    width=122 * mm,
                    height=65 * mm,
                ),
                payment_table,
            ]
        ],
        colWidths=[
            130 * mm,
            115 * mm,
        ],
    )

    lower.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    story.append(lower)

    story.append(PageBreak())

    # --------------------------------------------------------
    # Logistics + returns
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Logistics & Returns",
            section_style,
        )
    )

    story.append(
        _pdf_chart_pair(
            report_shipment_chart(
                shipment_scope
            ),
            report_delivery_chart(
                shipment_scope
            ),
        )
    )

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    story.append(
        _pdf_chart_pair(
            report_return_chart(
                return_scope
            ),
            report_payment_chart(
                payment_scope
            ),
        )
    )

    story.append(PageBreak())

    # --------------------------------------------------------
    # Data quality
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Data Preparation Summary",
            section_style,
        )
    )

    data_quality_rows = [
        [
            "Dataset",
            "Raw Rows",
            "Clean Rows",
            "Change",
        ]
    ]

    for dataset_name in raw_counts:
        raw_value = raw_counts[
            dataset_name
        ]

        clean_value = clean_counts[
            dataset_name
        ]

        data_quality_rows.append(
            [
                dataset_name,
                f"{raw_value:,}",
                f"{clean_value:,}",
                f"{clean_value - raw_value:+,}",
            ]
        )

    quality_table = Table(
        data_quality_rows,
        colWidths=[
            70 * mm,
            45 * mm,
            45 * mm,
            45 * mm,
        ],
        repeatRows=1,
    )

    quality_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        PDF_BLUE
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    .4,
                    colors.HexColor(
                        "#DCE5F1"
                    ),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor(
                            "#F8FAFC"
                        ),
                    ],
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(quality_table)

    story.append(
        Spacer(
            1,
            7 * mm,
        )
    )

    story.append(
        Paragraph(
            "<b>Interpretation note:</b> Estimated profit uses "
            "net sales minus estimated product cost. Shipping fees "
            "are not included in net sales. Sales KPIs use Completed "
            "and Shipped orders.",
            body_style,
        )
    )

    doc.build(
        story,
        onFirstPage=_pdf_header_footer,
        onLaterPages=_pdf_header_footer,
    )

    output.seek(0)
    return output.getvalue()


def _png_data_uri(buffer):
    return (
        "data:image/png;base64,"
        + base64.b64encode(
            buffer.getvalue()
        ).decode("ascii")
    )


def build_printable_html(
    filtered_fulfilled,
    filtered_orders_all,
    filtered_orders_fulfilled,
    payment_scope,
    shipment_scope,
    return_scope,
    filter_text,
):
    """
    Build a printable HTML report.

    The report contains its own Print / Save as PDF button.
    It is rendered inside a Streamlit iframe with components.html().
    """
    gross_sales = filtered_fulfilled[
        "gross_sales"
    ].sum()

    net_sales = filtered_fulfilled[
        "net_sales"
    ].sum()

    estimated_profit = filtered_fulfilled[
        "estimated_profit"
    ].sum()

    orders = filtered_fulfilled[
        "order_id"
    ].nunique()

    customers = filtered_fulfilled[
        "customer_id"
    ].nunique()

    units = filtered_fulfilled[
        "quantity_clean"
    ].sum()

    aov = (
        filtered_orders_fulfilled[
            "net_order_value"
        ].mean()
        if not filtered_orders_fulfilled.empty
        else 0
    )

    margin = (
        estimated_profit
        / net_sales
        * 100
        if net_sales
        else 0
    )

    monthly_img = _png_data_uri(
        report_monthly_sales_chart(
            filtered_fulfilled
        )
    )

    category_img = _png_data_uri(
        report_category_chart(
            filtered_fulfilled
        )
    )

    region_img = _png_data_uri(
        report_region_chart(
            filtered_fulfilled
        )
    )

    status_img = _png_data_uri(
        report_order_status_chart(
            filtered_orders_all
        )
    )

    products_img = _png_data_uri(
        report_top_products_chart(
            filtered_fulfilled
        )
    )

    profit_img = _png_data_uri(
        report_profit_chart(
            filtered_fulfilled
        )
    )

    payment_img = _png_data_uri(
        report_payment_chart(
            payment_scope
        )
    )

    shipment_img = _png_data_uri(
        report_shipment_chart(
            shipment_scope
        )
    )

    returns_img = _png_data_uri(
        report_return_chart(
            return_scope
        )
    )

    top_customers = (
        filtered_fulfilled
        .groupby(
            [
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
        .sort_values(
            "Spend",
            ascending=False,
        )
        .head(10)
    )

    customer_rows = ""

    for _, row in top_customers.iterrows():
        customer_rows += f"""
            <tr>
                <td>{html.escape(str(row['customer_name']))}</td>
                <td>{html.escape(str(row['loyalty_tier']))}</td>
                <td>{html.escape(str(row['region_name']))}</td>
                <td>{int(row['Orders']):,}</td>
                <td>PHP {row['Spend']:,.2f}</td>
            </tr>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Retail Analytics Printable Report</title>

<style>
    @page {{
        size: A4 landscape;
        margin: 10mm;
    }}

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        font-family:
            Inter,
            Arial,
            sans-serif;
        color: #172033;
        background: #F4F7FB;
    }}

    .toolbar {{
        position: sticky;
        top: 0;
        z-index: 10;
        padding: 12px 18px;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        background: rgba(255,255,255,.95);
        border-bottom: 1px solid #DCE5F1;
    }}

    .toolbar button {{
        border: 0;
        border-radius: 9px;
        padding: 10px 16px;
        background: #0247B7;
        color: white;
        font-weight: 700;
        cursor: pointer;
    }}

    .report {{
        max-width: 1150px;
        margin: 18px auto;
    }}

    .page {{
        background: white;
        padding: 22px;
        margin-bottom: 18px;
        border: 1px solid #DCE5F1;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(15,23,42,.07);
        page-break-after: always;
    }}

    .hero {{
        padding: 24px;
        color: white;
        border-radius: 15px;
        background:
            linear-gradient(
                125deg,
                #061C48,
                #0247B7,
                #635BFF
            );
    }}

    .hero h1 {{
        margin: 4px 0 8px 0;
        font-size: 30px;
    }}

    .hero p {{
        margin: 0;
        color: rgba(255,255,255,.85);
    }}

    .filters {{
        margin-top: 14px;
        padding: 12px;
        border-radius: 10px;
        background: #EEF4FF;
        color: #334155;
        font-size: 13px;
    }}

    .kpis {{
        margin-top: 16px;
        display: grid;
        grid-template-columns:
            repeat(4, 1fr);
        gap: 10px;
    }}

    .kpi {{
        border: 1px solid #DCE5F1;
        border-radius: 12px;
        padding: 13px;
        background:
            linear-gradient(
                145deg,
                white,
                #F7FAFF
            );
    }}

    .kpi .label {{
        color: #64748B;
        font-size: 12px;
        font-weight: 700;
    }}

    .kpi .value {{
        margin-top: 5px;
        color: #102A56;
        font-size: 22px;
        font-weight: 800;
    }}

    h2 {{
        color: #0247B7;
        margin: 0 0 14px 0;
    }}

    .chart-grid {{
        display: grid;
        grid-template-columns:
            repeat(2, 1fr);
        gap: 14px;
    }}

    .chart {{
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 8px;
        background: white;
    }}

    .chart img {{
        width: 100%;
        height: auto;
        display: block;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }}

    th {{
        background: #0247B7;
        color: white;
        text-align: left;
        padding: 8px;
    }}

    td {{
        padding: 8px;
        border-bottom: 1px solid #E2E8F0;
    }}

    tr:nth-child(even) {{
        background: #F8FAFC;
    }}

    .footer-note {{
        margin-top: 14px;
        color: #64748B;
        font-size: 11px;
    }}

    @media print {{
        body {{
            background: white;
        }}

        .toolbar {{
            display: none;
        }}

        .report {{
            max-width: none;
            margin: 0;
        }}

        .page {{
            border: none;
            box-shadow: none;
            border-radius: 0;
            margin: 0;
            min-height: 180mm;
        }}

        .page:last-child {{
            page-break-after: auto;
        }}
    }}
</style>
</head>

<body>

<div class="toolbar">
    <button onclick="window.print()">
        Print / Save as PDF
    </button>
</div>

<div class="report">

    <section class="page">
        <div class="hero">
            <div>DataSense Analytics</div>
            <h1>Retail Analytics Report</h1>
            <p>
                Complete retail performance report generated
                from the current dashboard filters.
            </p>
        </div>

        <div class="filters">
            <strong>Report scope:</strong>
            {html.escape(filter_text)}
        </div>

        <div class="kpis">
            <div class="kpi">
                <div class="label">Gross Sales</div>
                <div class="value">PHP {gross_sales:,.2f}</div>
            </div>

            <div class="kpi">
                <div class="label">Net Sales</div>
                <div class="value">PHP {net_sales:,.2f}</div>
            </div>

            <div class="kpi">
                <div class="label">Fulfilled Orders</div>
                <div class="value">{orders:,}</div>
            </div>

            <div class="kpi">
                <div class="label">Average Order Value</div>
                <div class="value">PHP {aov:,.2f}</div>
            </div>

            <div class="kpi">
                <div class="label">Units Sold</div>
                <div class="value">{units:,.0f}</div>
            </div>

            <div class="kpi">
                <div class="label">Unique Customers</div>
                <div class="value">{customers:,}</div>
            </div>

            <div class="kpi">
                <div class="label">Estimated Profit</div>
                <div class="value">PHP {estimated_profit:,.2f}</div>
            </div>

            <div class="kpi">
                <div class="label">Estimated Margin</div>
                <div class="value">{margin:.1f}%</div>
            </div>
        </div>

        <div class="footer-note">
            Sales metrics use Completed and Shipped orders.
        </div>
    </section>

    <section class="page">
        <h2>Executive Performance</h2>

        <div class="chart-grid">
            <div class="chart">
                <img src="{monthly_img}">
            </div>

            <div class="chart">
                <img src="{status_img}">
            </div>

            <div class="chart">
                <img src="{category_img}">
            </div>

            <div class="chart">
                <img src="{region_img}">
            </div>
        </div>
    </section>

    <section class="page">
        <h2>Products & Profitability</h2>

        <div class="chart-grid">
            <div class="chart">
                <img src="{products_img}">
            </div>

            <div class="chart">
                <img src="{profit_img}">
            </div>
        </div>

        <h2 style="margin-top:18px;">
            Top Customers
        </h2>

        <table>
            <thead>
                <tr>
                    <th>Customer</th>
                    <th>Tier</th>
                    <th>Region</th>
                    <th>Orders</th>
                    <th>Net Spend</th>
                </tr>
            </thead>
            <tbody>
                {customer_rows}
            </tbody>
        </table>
    </section>

    <section class="page">
        <h2>Payments, Logistics & Returns</h2>

        <div class="chart-grid">
            <div class="chart">
                <img src="{payment_img}">
            </div>

            <div class="chart">
                <img src="{shipment_img}">
            </div>

            <div class="chart">
                <img src="{returns_img}">
            </div>
        </div>

        <div class="footer-note">
            Use the Print / Save as PDF button above or
            press Ctrl+P / Cmd+P in this report.
        </div>
    </section>

</div>

</body>
</html>
"""


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
    """<div class="hero"><div class="hero-topline"><span class="live-dot"></span><span class="hero-kicker">DataSense Analytics · Interactive Dashboard</span></div><div class="hero-title">Retail Analytics Studio</div><div class="hero-sub">Explore sales performance, customer behavior, product trends, estimated profitability, payments, logistics, and returns from one interactive analytics workspace.</div><div class="hero-badge">✦ Complete Retail Intelligence</div></div>""",
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



st.markdown(
    f"""<div style="display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;padding:.72rem .9rem;margin:.25rem 0 .85rem 0;border-radius:14px;border:1px solid rgba(2,71,183,.12);background:linear-gradient(90deg,rgba(2,71,183,.065),rgba(109,93,251,.055),rgba(0,166,166,.045));animation:fadeUp .55s .12s ease both;"><div style="font-size:.82rem;color:#334155;font-weight:650;">✦ Interactive view updated from your current filters</div><div style="font-size:.80rem;color:#64748B;">{len(filtered_all):,} item rows · {len(filtered_orders_all):,} orders · {len(payment_scope):,} payment records</div></div>""",
    unsafe_allow_html=True,
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
    report_tab,
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
        "Report & Export",
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


# ============================================================
# 20. REPORT & EXPORT TAB
# ============================================================

with report_tab:
    st.subheader(
        "Report & Export"
    )

    st.markdown(
        '<div class="section-note">'
        'Create a professional PDF report or open a print-ready '
        'version based on the current dashboard filters.'
        '</div>',
        unsafe_allow_html=True,
    )

    filter_text = (
        f"Order dates: {start_date:%d %b %Y} to "
        f"{end_date:%d %b %Y}; "
        f"Regions: "
        f"{', '.join(selected_regions) if selected_regions else 'All'}; "
        f"Channels: "
        f"{', '.join(selected_channels) if selected_channels else 'All'}; "
        f"Categories: "
        f"{', '.join(selected_categories) if selected_categories else 'All'}; "
        f"Shipping methods: "
        f"{', '.join(selected_shipping) if selected_shipping else 'All'}"
    )

    report_signature = (
        str(start_date),
        str(end_date),
        tuple(selected_regions),
        tuple(selected_channels),
        tuple(selected_categories),
        tuple(selected_shipping),
    )

    export_left, export_right = st.columns(
        [1, 1],
        gap="medium",
    )

    # --------------------------------------------------------
    # PDF EXPORT
    # --------------------------------------------------------

    with export_left:
        with st.container(
            border=True
        ):
            st.markdown(
                "### PDF Report"
            )

            st.write(
                "Generate a multi-page PDF with KPI summaries, "
                "charts, top customers, logistics, returns, "
                "payments, and data-quality information."
            )

            if st.button(
                "Generate PDF Report",
                type="primary",
                width="stretch",
                key="generate_pdf_report",
            ):
                with st.spinner(
                    "Building PDF report..."
                ):
                    pdf_bytes = build_pdf_report(
                        filtered_fulfilled=filtered_fulfilled,
                        filtered_orders_all=filtered_orders_all,
                        filtered_orders_fulfilled=filtered_orders_fulfilled,
                        payment_scope=payment_scope,
                        shipment_scope=shipment_scope,
                        return_scope=return_scope,
                        filter_text=filter_text,
                        raw_counts=raw_counts,
                        clean_counts=clean_counts,
                    )

                    st.session_state[
                        "retail_pdf_bytes"
                    ] = pdf_bytes

                    st.session_state[
                        "retail_pdf_signature"
                    ] = report_signature

            pdf_ready = (
                "retail_pdf_bytes"
                in st.session_state
                and st.session_state.get(
                    "retail_pdf_signature"
                )
                == report_signature
            )

            if pdf_ready:
                st.success(
                    "PDF report is ready."
                )

                st.download_button(
                    "Download PDF Report",
                    data=st.session_state[
                        "retail_pdf_bytes"
                    ],
                    file_name=(
                        "retail_analytics_report.pdf"
                    ),
                    mime="application/pdf",
                    width="stretch",
                    key="download_pdf_report",
                )

            elif (
                "retail_pdf_bytes"
                in st.session_state
            ):
                st.info(
                    "The filters changed. Generate the PDF "
                    "again so the report matches the current view."
                )

    # --------------------------------------------------------
    # PRINTABLE HTML
    # --------------------------------------------------------

    with export_right:
        with st.container(
            border=True
        ):
            st.markdown(
                "### Print / Save as PDF"
            )

            st.write(
                "Generate a print-ready report with its own "
                "Print / Save as PDF button. This is useful "
                "when you want to use the browser's print dialog."
            )

            if st.button(
                "Generate Printable Report",
                width="stretch",
                key="generate_print_report",
            ):
                with st.spinner(
                    "Preparing printable report..."
                ):
                    printable_html = (
                        build_printable_html(
                            filtered_fulfilled=filtered_fulfilled,
                            filtered_orders_all=filtered_orders_all,
                            filtered_orders_fulfilled=filtered_orders_fulfilled,
                            payment_scope=payment_scope,
                            shipment_scope=shipment_scope,
                            return_scope=return_scope,
                            filter_text=filter_text,
                        )
                    )

                    st.session_state[
                        "retail_print_html"
                    ] = printable_html

                    st.session_state[
                        "retail_print_signature"
                    ] = report_signature

            print_ready = (
                "retail_print_html"
                in st.session_state
                and st.session_state.get(
                    "retail_print_signature"
                )
                == report_signature
            )

            if print_ready:
                st.success(
                    "Printable report is ready below."
                )

                st.download_button(
                    "Download Printable HTML",
                    data=st.session_state[
                        "retail_print_html"
                    ],
                    file_name=(
                        "retail_analytics_print_report.html"
                    ),
                    mime="text/html",
                    width="stretch",
                    key="download_html_report",
                )

            elif (
                "retail_print_html"
                in st.session_state
            ):
                st.info(
                    "The filters changed. Generate the printable "
                    "report again to update it."
                )

    # --------------------------------------------------------
    # CURRENT FILTER SUMMARY
    # --------------------------------------------------------

    with st.container(
        border=True
    ):
        st.markdown(
            "### Current Report Scope"
        )

        st.write(
            filter_text
        )

        r1, r2, r3, r4 = st.columns(
            4,
            border=True,
        )

        r1.metric(
            "Item Rows",
            f"{len(filtered_all):,}",
        )

        r2.metric(
            "All Orders",
            f"{len(filtered_orders_all):,}",
        )

        r3.metric(
            "Fulfilled Orders",
            f"{len(filtered_orders_fulfilled):,}",
        )

        r4.metric(
            "Return Records",
            f"{len(return_scope):,}",
        )

    # --------------------------------------------------------
    # PRINTABLE REPORT PREVIEW
    # --------------------------------------------------------

    if (
        "retail_print_html"
        in st.session_state
        and st.session_state.get(
            "retail_print_signature"
        )
        == report_signature
    ):
        st.markdown(
            "### Printable Report Preview"
        )

        st.caption(
            "Use the Print / Save as PDF button inside the preview. "
            "The browser will open its print dialog."
        )

        components.html(
            st.session_state[
                "retail_print_html"
            ],
            height=980,
            scrolling=True,
        )

    # --------------------------------------------------------
    # CSV EXPORT
    # --------------------------------------------------------

    with st.container(
        border=True
    ):
        st.markdown(
            "### Data Export"
        )

        export_columns = [
            "order_id",
            "order_date",
            "customer_id",
            "customer_name",
            "product_id",
            "product_name",
            "brand",
            "category_clean",
            "quantity_clean",
            "unit_price_clean",
            "sales_channel",
            "shipping_method",
            "region_name",
            "city",
            "gross_sales",
            "net_sales",
            "discount_amount",
            "estimated_profit",
        ]

        export_df = (
            filtered_all[
                export_columns
            ]
            .sort_values(
                "order_date"
            )
            .copy()
        )

        st.download_button(
            "Download Filtered CSV",
            data=export_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name=(
                "retail_analytics_filtered_data.csv"
            ),
            mime="text/csv",
            width="stretch",
            key="report_csv_export",
        )

        st.caption(
            "The CSV contains the same transaction scope "
            "used by the current dashboard filters."
        )
