# =============================================================================
# RETAIL SALES ANALYSIS — STREAMLIT WEB APP
# Dataset : Superstore Sales Dataset (Kaggle)
# Tools   : Python, Pandas, Plotly, Streamlit
# =============================================================================
# HOW TO RUN:
#   1. pip install streamlit plotly pandas
#   2. Place 'Sample - Superstore.csv' in the same folder
#   3. Run: streamlit run streamlit_app.py
#   4. Browser opens automatically at localhost:8501
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 1rem;
        color: #6B7280;
        margin-top: 0;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background-color: #F0F9FF;
        border-left: 4px solid #2563EB;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
    }
    div[data-testid="metric-container"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# LOAD & CACHE DATA
# =============================================================================

@st.cache_data
def load_data():
    # Try both common filename formats
    try:
        df = pd.read_csv("Sample - Superstore.csv", encoding="latin-1")
    except FileNotFoundError:
        try:
            df = pd.read_csv("superstore.csv", encoding="latin-1")
        except FileNotFoundError:
            st.error("❌ Dataset not found! Place 'Sample - Superstore.csv' in the same folder.")
            st.stop()

    df["Order Date"]      = pd.to_datetime(df["Order Date"])
    df["Ship Date"]       = pd.to_datetime(df["Ship Date"])
    df["Year"]            = df["Order Date"].dt.year
    df["Month"]           = df["Order Date"].dt.month
    df["Month Name"]      = df["Order Date"].dt.strftime("%b")
    df["Quarter"]         = "Q" + df["Order Date"].dt.quarter.astype(str)
    df["YearMonth"]       = df["Order Date"].dt.to_period("M").astype(str)
    df["Profit Margin %"] = (df["Profit"] / df["Sales"] * 100).round(2)
    df["Shipping Days"]   = (df["Ship Date"] - df["Order Date"]).dt.days

    bins   = [-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0]
    labels = ["No Discount","1-10%","11-20%","21-30%","31-50%","51%+"]
    df["Discount Bucket"] = pd.cut(df["Discount"], bins=bins, labels=labels)
    return df

df = load_data()


# =============================================================================
# SIDEBAR — FILTERS
# =============================================================================

st.sidebar.image("https://img.icons8.com/color/96/combo-chart--v1.png", width=60)
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

# Year filter
years = sorted(df["Year"].unique())
selected_years = st.sidebar.multiselect(
    "📅 Select Year(s)", years, default=years
)

# Region filter
regions = sorted(df["Region"].unique())
selected_regions = st.sidebar.multiselect(
    "🗺️ Select Region(s)", regions, default=regions
)

# Category filter
categories = sorted(df["Category"].unique())
selected_categories = st.sidebar.multiselect(
    "📦 Select Category", categories, default=categories
)

# Segment filter
segments = sorted(df["Segment"].unique())
selected_segments = st.sidebar.multiselect(
    "👤 Select Segment(s)", segments, default=segments
)

st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Retail Sales Dashboard**")
st.sidebar.markdown("Built with Python + Streamlit")
st.sidebar.markdown("Dataset: Superstore (Kaggle)")

# Apply filters
filtered_df = df[
    (df["Year"].isin(selected_years)) &
    (df["Region"].isin(selected_regions)) &
    (df["Category"].isin(selected_categories)) &
    (df["Segment"].isin(selected_segments))
]

if filtered_df.empty:
    st.warning("⚠️ No data found for selected filters. Please adjust your selections.")
    st.stop()


# =============================================================================
# HEADER
# =============================================================================

st.markdown('<p class="main-title">📊 Retail Sales Performance Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Business Analysis Project | Superstore Dataset | Python + Streamlit</p>', unsafe_allow_html=True)
st.markdown("---")


# =============================================================================
# ROW 1 — KPI METRICS
# =============================================================================

col1, col2, col3, col4, col5 = st.columns(5)

total_sales     = filtered_df["Sales"].sum()
total_profit    = filtered_df["Profit"].sum()
total_orders    = filtered_df["Order ID"].nunique()
avg_margin      = filtered_df["Profit Margin %"].mean()
total_customers = filtered_df["Customer ID"].nunique()

col1.metric("💰 Total Sales",     f"${total_sales:,.0f}")
col2.metric("📈 Total Profit",    f"${total_profit:,.0f}")
col3.metric("🧾 Total Orders",    f"{total_orders:,}")
col4.metric("👥 Customers",       f"{total_customers:,}")
col5.metric("📊 Avg Margin",      f"{avg_margin:.1f}%")

st.markdown("---")


# =============================================================================
# ROW 2 — SALES TREND + CATEGORY SPLIT
# =============================================================================

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📅 Monthly Sales & Profit Trend")
    monthly = filtered_df.groupby("YearMonth").agg(
        Sales  = ("Sales",  "sum"),
        Profit = ("Profit", "sum")
    ).reset_index().sort_values("YearMonth")

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(
        go.Scatter(x=monthly["YearMonth"], y=monthly["Sales"],
                   name="Sales", line=dict(color="#2563EB", width=2.5),
                   fill="tozeroy", fillcolor="rgba(37,99,235,0.08)"),
        secondary_y=False
    )
    fig_trend.add_trace(
        go.Scatter(x=monthly["YearMonth"], y=monthly["Profit"],
                   name="Profit", line=dict(color="#16A34A", width=2, dash="dot")),
        secondary_y=True
    )
    fig_trend.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=1.1),
        plot_bgcolor="white", paper_bgcolor="white"
    )
    fig_trend.update_xaxes(tickangle=45, tickfont=dict(size=9))
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.subheader("📦 Sales by Category")
    cat = filtered_df.groupby("Category")["Sales"].sum().reset_index()
    fig_cat = px.pie(cat, names="Category", values="Sales",
                     color_discrete_sequence=["#2563EB", "#16A34A", "#EA580C"],
                     hole=0.45)
    fig_cat.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0),
                          showlegend=True,
                          legend=dict(orientation="h", y=-0.1))
    fig_cat.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(fig_cat, use_container_width=True)


# =============================================================================
# ROW 3 — REGIONAL + SUB-CATEGORY
# =============================================================================

col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("🗺️ Regional Performance")
    region = filtered_df.groupby("Region").agg(
        Sales  = ("Sales",  "sum"),
        Profit = ("Profit", "sum")
    ).reset_index().melt(id_vars="Region", var_name="Metric", value_name="Value")

    fig_region = px.bar(region, x="Region", y="Value", color="Metric",
                        barmode="group",
                        color_discrete_map={"Sales": "#2563EB", "Profit": "#16A34A"})
    fig_region.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0),
                             plot_bgcolor="white", paper_bgcolor="white",
                             legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_region, use_container_width=True)

with col_right2:
    st.subheader("🏷️ Sub-Category Profit (Top & Bottom)")
    subcat = filtered_df.groupby("Sub-Category")["Profit"].sum().reset_index()
    subcat = subcat.sort_values("Profit", ascending=True)
    subcat["Color"] = subcat["Profit"].apply(lambda x: "Loss" if x < 0 else "Profit")

    fig_sub = px.bar(subcat, x="Profit", y="Sub-Category",
                     orientation="h", color="Color",
                     color_discrete_map={"Profit": "#16A34A", "Loss": "#DC2626"})
    fig_sub.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0),
                          plot_bgcolor="white", paper_bgcolor="white",
                          showlegend=True,
                          legend=dict(orientation="h", y=1.1))
    fig_sub.add_vline(x=0, line_color="black", line_width=1)
    st.plotly_chart(fig_sub, use_container_width=True)


# =============================================================================
# ROW 4 — DISCOUNT IMPACT + SEGMENT ANALYSIS
# =============================================================================

col_left3, col_right3 = st.columns(2)

with col_left3:
    st.subheader("💸 Discount Impact on Profit")
    disc = filtered_df.groupby("Discount Bucket", observed=True).agg(
        Avg_Profit = ("Profit", "mean"),
        Orders     = ("Order ID", "count")
    ).reset_index()
    disc["Color"] = disc["Avg_Profit"].apply(lambda x: "Loss" if x < 0 else "Profit")

    fig_disc = px.bar(disc, x="Discount Bucket", y="Avg_Profit", color="Color",
                      color_discrete_map={"Profit": "#16A34A", "Loss": "#DC2626"},
                      text="Avg_Profit")
    fig_disc.update_traces(texttemplate="$%{text:.0f}", textposition="outside")
    fig_disc.add_hline(y=0, line_color="black", line_width=1)
    fig_disc.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0),
                           plot_bgcolor="white", paper_bgcolor="white",
                           showlegend=False)
    st.plotly_chart(fig_disc, use_container_width=True)

with col_right3:
    st.subheader("👤 Customer Segment Breakdown")
    seg = filtered_df.groupby("Segment").agg(
        Sales  = ("Sales",  "sum"),
        Profit = ("Profit", "sum"),
        Orders = ("Order ID", "nunique")
    ).reset_index()

    fig_seg = px.bar(seg, x="Segment", y=["Sales", "Profit"],
                     barmode="group",
                     color_discrete_map={"Sales": "#7C3AED", "Profit": "#16A34A"})
    fig_seg.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0),
                          plot_bgcolor="white", paper_bgcolor="white",
                          legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_seg, use_container_width=True)


# =============================================================================
# ROW 5 — QUARTERLY HEATMAP + SHIP MODE
# =============================================================================

col_left4, col_right4 = st.columns(2)

with col_left4:
    st.subheader("📆 Quarterly Sales Heatmap")
    quarterly = filtered_df.groupby(["Year", "Quarter"])["Sales"].sum().unstack(fill_value=0)
    fig_heat = px.imshow(quarterly,
                         color_continuous_scale="Blues",
                         text_auto=".0f",
                         aspect="auto")
    fig_heat.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_heat, use_container_width=True)

with col_right4:
    st.subheader("🚚 Shipping Mode Analysis")
    ship = filtered_df.groupby("Ship Mode").agg(
        Orders    = ("Order ID", "count"),
        Avg_Days  = ("Shipping Days", "mean")
    ).reset_index()

    fig_ship = make_subplots(specs=[[{"secondary_y": True}]])
    fig_ship.add_trace(
        go.Bar(x=ship["Ship Mode"], y=ship["Orders"],
               name="Orders", marker_color="#2563EB"), secondary_y=False
    )
    fig_ship.add_trace(
        go.Scatter(x=ship["Ship Mode"], y=ship["Avg_Days"],
                   name="Avg Days", mode="markers+lines",
                   marker=dict(color="#EA580C", size=10),
                   line=dict(color="#EA580C")), secondary_y=True
    )
    fig_ship.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                           plot_bgcolor="white", paper_bgcolor="white",
                           legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_ship, use_container_width=True)


# =============================================================================
# ROW 6 — TOP CUSTOMERS TABLE
# =============================================================================

st.markdown("---")
col_t1, col_t2 = st.columns(2)

with col_t1:
    st.subheader("🏆 Top 10 Profitable Customers")
    top_cust = filtered_df.groupby("Customer Name").agg(
        Sales  = ("Sales",  "sum"),
        Profit = ("Profit", "sum"),
        Orders = ("Order ID", "nunique")
    ).nlargest(10, "Profit").reset_index()
    top_cust["Sales"]  = top_cust["Sales"].map("${:,.0f}".format)
    top_cust["Profit"] = top_cust["Profit"].map("${:,.0f}".format)
    st.dataframe(top_cust, use_container_width=True, hide_index=True)

with col_t2:
    st.subheader("⚠️ Top 10 Loss-Making Customers")
    bot_cust = filtered_df.groupby("Customer Name").agg(
        Sales  = ("Sales",  "sum"),
        Profit = ("Profit", "sum"),
        Orders = ("Order ID", "nunique")
    ).nsmallest(10, "Profit").reset_index()
    bot_cust["Sales"]  = bot_cust["Sales"].map("${:,.0f}".format)
    bot_cust["Profit"] = bot_cust["Profit"].map("${:,.0f}".format)
    st.dataframe(bot_cust, use_container_width=True, hide_index=True)


# =============================================================================
# ROW 7 — BUSINESS INSIGHTS
# =============================================================================

st.markdown("---")
st.subheader("💡 Key Business Insights")

# Dynamic insights based on filtered data
top_cat    = filtered_df.groupby("Category")["Profit"].sum().idxmax()
worst_cat  = filtered_df.groupby("Category")["Profit"].sum().idxmin()
top_region = filtered_df.groupby("Region")["Profit"].sum().idxmax()
loss_subcat= filtered_df.groupby("Sub-Category")["Profit"].sum()
loss_list  = loss_subcat[loss_subcat < 0].index.tolist()

ins1, ins2, ins3 = st.columns(3)

with ins1:
    st.markdown(f"""
    <div class="insight-box">
    <b>📦 Product Mix</b><br>
    <b>{top_cat}</b> is the most profitable category.<br>
    <b>{worst_cat}</b> needs pricing review.<br>
    Loss-making sub-categories: <b>{', '.join(loss_list) if loss_list else 'None'}</b>
    </div>
    """, unsafe_allow_html=True)

with ins2:
    st.markdown(f"""
    <div class="insight-box">
    <b>🗺️ Regional Focus</b><br>
    <b>{top_region}</b> is the top-performing region.<br>
    Focus retention efforts on high-margin regions.<br>
    Investigate underperforming regions for discount overuse.
    </div>
    """, unsafe_allow_html=True)

with ins3:
    st.markdown(f"""
    <div class="insight-box">
    <b>💸 Discount Strategy</b><br>
    Orders with <b>&gt;30% discount</b> generate negative profit.<br>
    Recommended cap: <b>20% maximum discount</b>.<br>
    Use high discounts only as a seasonal lever.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# ROW 8 — RAW DATA EXPLORER (optional)
# =============================================================================

st.markdown("---")
with st.expander("🔎 Explore Raw Data"):
    st.write(f"Showing {len(filtered_df):,} rows based on your filters")
    st.dataframe(
        filtered_df[[
            "Order Date","Category","Sub-Category","Region",
            "Segment","Sales","Profit","Discount","Profit Margin %","Ship Mode"
        ]].sort_values("Order Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9CA3AF;font-size:0.85rem;'>"
    "Built by [Vidit Basera] | Business Analyst Portfolio | Python + Streamlit + Plotly"
    "</div>",
    unsafe_allow_html=True
)