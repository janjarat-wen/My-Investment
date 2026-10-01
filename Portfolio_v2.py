

import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Investment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# DARK THEME
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #0b1220;
    color: #e2e8f0;
}

[data-testid="stSidebar"] {
    background-color: #101d30;
    border-right: 1px solid #26364d;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

h1, h2, h3 {
    color: #f1f5f9;
}

[data-testid="stMetric"] {
    background-color: #111e32;
    border: 1px solid #26364d;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #94a3b8;
}

[data-testid="stMetricValue"] {
    color: #f8fafc;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #26364d;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# GOOGLE SHEETS
# ==========================================

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1JaAat1fG-JCgp5FigRCSx3HSrsqs4YvUAUVvhDuwWXA"


@st.cache_resource
def connect_google_sheets():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    return client


@st.cache_data(ttl=300)
def load_data():

    client = connect_google_sheets()

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # Read each worksheet
    portfolio = pd.DataFrame(
        spreadsheet.worksheet("Portfolio").get_all_records()
    )

    fund = pd.DataFrame(
        spreadsheet.worksheet("Fund").get_all_records()
    )

    bond = pd.DataFrame(
        spreadsheet.worksheet("Bond").get_all_records()
    )

    dividend = pd.DataFrame(
        spreadsheet.worksheet("Dividend").get_all_records()
    )

    # Remove extra spaces in column names
    for df in [portfolio, fund, bond, dividend]:
        df.columns = df.columns.str.strip()

    # Convert numeric columns
    for col in ["Total", "Yield Rate/Yr", "Yield Baht/Yr"]:
        if col in portfolio.columns:
            portfolio[col] = pd.to_numeric(
                portfolio[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("%", "", regex=False),
                errors="coerce"
            ).fillna(0)

    if "Total" in fund.columns:
        fund["Total"] = pd.to_numeric(
            fund["Total"]
            .astype(str)
            .str.replace(",", "", regex=False),
            errors="coerce"
        ).fillna(0)

    if "Mine" in bond.columns:
        bond["Mine"] = pd.to_numeric(
            bond["Mine"]
            .astype(str)
            .str.replace(",", "", regex=False),
            errors="coerce"
        ).fillna(0)

    if "Amount" in bond.columns:
        bond["Amount"] = pd.to_numeric(
            bond["Amount"]
            .astype(str)
            .str.replace(",", "", regex=False),
            errors="coerce"
        ).fillna(0)

    if "Yield" in bond.columns:
        bond["Yield"] = pd.to_numeric(
            bond["Yield"]
            .astype(str)
            .str.replace("%", "", regex=False),
            errors="coerce"
        ).fillna(0)

    for col in ["NETT", "เงินปันผล"]:
        if col in dividend.columns:
            dividend[col] = pd.to_numeric(
                dividend[col]
                .astype(str)
                .str.replace(",", "", regex=False),
                errors="coerce"
            ).fillna(0)

    if "วันที่จ่ายเงินปันผล" in dividend.columns:
        dividend["วันที่จ่ายเงินปันผล"] = pd.to_datetime(
            dividend["วันที่จ่ายเงินปันผล"],
            errors="coerce"
        )

    return portfolio, fund, bond, dividend


portfolio, fund, bond, dividend = load_data()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown(
        "<h2 style='text-align:center;'>📊 MY PORTFOLIO</h2>",
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "MENU",
        [
            "Portfolio",
            "Fund",
            "Bond",
            "Dividend",
            "Future 1",
            "Future 2"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.caption("Investment Dashboard")
    st.caption("Version 1.0")


# ==========================================
# CHART THEME
# ==========================================

def dark_chart(fig):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220",
        font=dict(color="#e2e8f0"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        )
    )

    return fig


# ==========================================
# PORTFOLIO PAGE
# ==========================================

if page == "Portfolio":

    st.title("🏠 Portfolio Overview")
    st.caption("Overall Asset Allocation and Performance")

    total = portfolio["Total"].sum()

    income = portfolio["Yield Baht/Yr"].sum()

# Calculate Weighted Yield from income-generating assets only


    yield_assets = portfolio[
    (portfolio["Yield Baht/Yr"] > 0) &
    (portfolio["Total"] > 0)
    ]

    yield_total = yield_assets["Total"].sum()

    avg_yield = (
    income / yield_total
    if yield_total > 0 else 0
    )    

    # KPI
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Assets",
        f"฿{total:,.0f}"
    )

    c2.metric(
        "Annual Income",
        f"฿{income:,.0f}"
    )

    c3.metric(
        "Weighted Yield",
        f"{avg_yield:.2%}"
    )

    st.divider()

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        selected_group = st.multiselect(
            "Group",
            portfolio["Group"].dropna().unique(),
            default=portfolio["Group"].dropna().unique()
        )

    with col2:
        selected_type = st.multiselect(
            "Asset Type",
            portfolio["Asset Type"].dropna().unique(),
            default=portfolio["Asset Type"].dropna().unique()
        )

    filtered = portfolio[
        portfolio["Group"].isin(selected_group)
        & portfolio["Asset Type"].isin(selected_type)
    ].copy()

    # Recalculate after filtering
    total_filtered = filtered["Total"].sum()
    income_filtered = filtered["Yield Baht/Yr"].sum()

    yield_filtered = (
        income_filtered / total_filtered
        if total_filtered else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Filtered Assets", f"฿{total_filtered:,.0f}")
    c2.metric("Annual Income", f"฿{income_filtered:,.0f}")
    c3.metric("Weighted Yield", f"{yield_filtered:.2%}")

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:

        asset_data = (
            filtered.groupby("Asset Type")["Total"]
            .sum()
            .reset_index()
            .sort_values("Total", ascending=False)
        )

        fig = px.pie(
            asset_data,
            names="Asset Type",
            values="Total",
            hole=0.65,
            title="Asset Allocation"
        )

        fig.update_traces(
            textinfo="label+percent",
            textposition="outside"
        )

        st.plotly_chart(
            dark_chart(fig),
            use_container_width=True
        )

    with col2:

        group_data = (
            filtered.groupby("Asset Type")["Total"]
            .sum()
            .reset_index()
            .sort_values("Total", ascending=True)
        )

        fig = px.bar(
            group_data,
            x="Total",
            y="Asset Type",
            orientation="h",
            text="Total",
            title="Asset Type"
        )

        fig.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Asset Type",
            yaxis_title="Value (฿)",
            yaxis_tickformat=",.0f",
            showlegend=False
        )

        st.plotly_chart(
            dark_chart(fig),
            use_container_width=True
        )
        
    st.subheader("Asset Allocation - Top 10")

    # Calculate allocation by asset name
    top10 = (
        filtered.groupby("Name", as_index=False)
        .agg({
            "Total": "sum",
            "Asset Type": "first"
        })
        .sort_values("Total", ascending=False)
        .head(10)
        .copy()
    )

    # Calculate allocation percentage
    total_filtered = filtered["Total"].sum()

    top10["Allocation (%)"] = (
        top10["Total"] / total_filtered * 100
        if total_filtered > 0 else 0
    )

    # Display Top 10 table
    st.dataframe(
        top10[
            [
                "Name",
                "Asset Type",
                "Total",
                "Allocation (%)"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn(
                "Asset"
            ),
            "Asset Type": st.column_config.TextColumn(
                "Asset Type"
            ),
            "Total": st.column_config.NumberColumn(
                "Value (฿)",
                format="฿%,.0f"
            ),
            "Allocation (%)": st.column_config.NumberColumn(
                "Allocation (%)",
                format="%.2f%%"
            )
        }
    )
    


# ==========================================
# FUND PAGE
# ==========================================

elif page == "Fund":

    st.title("📊 Fund Analysis")
    st.caption("Fund Allocation and Investment Strategy")

    col1, col2, col3 = st.columns(3)

    total_fund = fund["Total"].sum()

    core = fund.loc[
        fund["Group"] == "CORE", "Total"
    ].sum()

    sat = fund.loc[
        fund["Group"] == "SAT", "Total"
    ].sum()

    col1.metric("Total Fund", f"฿{total_fund:,.0f}")
    col2.metric("CORE", f"฿{core:,.0f}")
    col3.metric("SAT", f"฿{sat:,.0f}")

    st.divider()

    # Filters
    c1, c2, c3 = st.columns(3)

    with c1:
        types = st.multiselect(
            "Fund Type",
            fund["Type"].dropna().unique(),
            default=fund["Type"].dropna().unique()
        )

    with c2:
        groups = st.multiselect(
            "Group",
            fund["Group"].dropna().unique(),
            default=fund["Group"].dropna().unique()
        )

    with c3:
        brokers = st.multiselect(
            "Broker",
            fund["Broker"].dropna().unique(),
            default=fund["Broker"].dropna().unique()
        )

    filtered = fund[
        fund["Type"].isin(types)
        & fund["Group"].isin(groups)
        & fund["Broker"].isin(brokers)
    ].copy()

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        group_data = (
            filtered.groupby("Group")["Total"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            group_data,
            names="Group",
            values="Total",
            hole=0.6,
            title="CORE vs SAT"
        )

        fig.update_traces(
            textinfo="label+percent"
        )

        st.plotly_chart(
            dark_chart(fig),
            use_container_width=True
        )

    with col2:

        type_data = (
            filtered.groupby("Specific Type")["Total"]
            .sum()
            .reset_index()
            .sort_values("Total", ascending=True)
        )

        fig = px.bar(
            type_data,
            x="Total",
            y="Specific Type",
            orientation="h",
            text="Total",
            title="Fund Allocation by Type"
        )

        fig.update_traces(
            texttemplate="%{x:,.0f}",
            textposition="outside"
        )

        st.plotly_chart(
            dark_chart(fig),
            use_container_width=True
        )

    # Broker Chart
    broker_data = (
        filtered.groupby("Broker")["Total"]
        .sum()
        .reset_index()
        .sort_values("Total", ascending=True)
    )

    fig = px.bar(
        broker_data,
        x="Total",
        y="Broker",
        orientation="h",
        text="Total",
        title="Fund Allocation by Broker"
    )

    fig.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside"
    )

    st.plotly_chart(
        dark_chart(fig),
        use_container_width=True
    )

    st.subheader("Fund Details")

    st.dataframe(
        filtered.sort_values("Total", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total": st.column_config.NumberColumn(
                format="฿%,.0f"
            )
        }
    )


# ==========================================
# BOND PAGE
# ==========================================

elif page == "Bond":

    st.title("💰 Bond Portfolio")
    st.caption("Fixed Income and Bond Maturity Analysis")

    bond_total = bond["Mine"].sum()

    bond_income = (bond["Mine"] * bond["Yield"]).sum()

    bond_yield = (
        bond_income / bond_total
        if bond_total else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Bond Value", f"฿{bond_total:,.0f}")
    c2.metric("Estimated Annual Income", f"฿{bond_income:,.0f}")
    c3.metric("Weighted Yield", f"{bond_yield:.2%}")

    st.divider()

    # Filter
    brokers = st.multiselect(
        "Broker",
        bond["Broker"].dropna().unique(),
        default=bond["Broker"].dropna().unique()
    )

    filtered = bond[
        bond["Broker"].isin(brokers)
    ].copy()

    col1, col2 = st.columns(2)

    with col1:

        broker_data = (
            filtered.groupby("Broker")["Mine"]
            .sum()
            .reset_index()
            .sort_values("Mine", ascending=True)
        )

        fig = px.bar(
            broker_data,
            x="Mine",
            y="Broker",
            orientation="h",
            text="Mine",
            title="Bond Value by Broker"
        )

        fig.update_traces(
            texttemplate="%{x:,.0f}",
            textposition="outside"
        )

        st.plotly_chart(
            dark_chart(fig),
            use_container_width=True
        )

    with col2:

        rating_data = (
            filtered.groupby("Issuer Rating")["Mine"]
            .sum()
            .reset_index()
            .sort_values("Mine", ascending=False)
        )

        fig = px.pie(
            rating_data,
            names="Issuer Rating",
            values="Mine",
            hole=0.6,
            title="Bond Allocation by Rating"
        )

        fig.update_traces(
            textinfo="label+percent"
        )

        st.plotly_chart(
            dark_chart(fig),
            use_container_width=True
        )

    st.subheader("Bond Details")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Mine": st.column_config.NumberColumn(
                format="฿%,.0f"
            ),
            "Amount": st.column_config.NumberColumn(
                format="฿%,.0f"
            ),
            "Yield": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Issued Date": st.column_config.DateColumn(
                format="DD/MM/YYYY"
            ),
            "Maturity Date": st.column_config.DateColumn(
                format="DD/MM/YYYY"
            )
        }
    )


# ==========================================
# DIVIDEND PAGE
# ==========================================

elif page == "Dividend":

    st.title("💵 Dividend Analysis")
    st.caption("Historical Dividend Income")

    dividend_data = dividend.dropna(
        subset=["วันที่จ่ายเงินปันผล"]
    ).copy()

    dividend_data["Year"] = (
        dividend_data["วันที่จ่ายเงินปันผล"].dt.year
    )

    total_dividend = dividend_data["NETT"].sum()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Net Dividend",
        f"฿{total_dividend:,.0f}"
    )

    c2.metric(
        "Dividend Records",
        f"{len(dividend_data):,}"
    )

    c3.metric(
        "Number of Stocks",
        f"{dividend_data['Name'].nunique():,}"
    )

    st.divider()

    # Year Filter
    years = sorted(
        dividend_data["Year"].dropna().unique(),
        reverse=True
    )

    selected_years = st.multiselect(
        "Year",
        years,
        default=years
    )

    filtered = dividend_data[
        dividend_data["Year"].isin(selected_years)
    ].copy()

    col1, col2 = st.columns(2)

    with col1:

        yearly = (
            filtered.groupby("Year")["NETT"]
            .sum()
            .reset_index()
            .sort_values("Year")
        )

        fig = px.bar(
            yearly,
            x="Year",
            y="NETT",
            text="NETT",
            title="Annual Dividend Income"
        )

        fig.update_traces(
            texttemplate="%{y:,.0f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis=dict(type="category"),
            yaxis=dict(tickformat=",.0f")
        )

        st.plotly_chart(
            dark_chart(fig),
            use_container_width=True
        )

    with col2:

        stock_data = (
            filtered.groupby("Name")["NETT"]
            .sum()
            .reset_index()
            .sort_values("NETT", ascending=False)
            .head(10)
        )

        fig = px.bar(
            stock_data,
            x="NETT",
            y="Name",
            orientation="h",
            text="NETT",
            title="Top 10 Dividend Stocks"
        )

        fig.update_traces(
            texttemplate="%{x:,.0f}",
            textposition="outside"
        )

        st.plotly_chart(
            dark_chart(fig),
            use_container_width=True
        )

    st.subheader("Dividend Details")

    st.dataframe(
        filtered.sort_values(
            "วันที่จ่ายเงินปันผล",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True,
        column_config={
            "จำนวนหุ้นที่ได้รับสิทธิ":
                st.column_config.NumberColumn(
                    format="%,.0f"
                ),
            "อัตราเงินปันผล":
                st.column_config.NumberColumn(
                    format="%.2f"
                ),
            "เงินปันผล":
                st.column_config.NumberColumn(
                    format="฿%,.2f"
                ),
            "NETT":
                st.column_config.NumberColumn(
                    format="฿%,.2f"
                ),
            "วันที่จ่ายเงินปันผล":
                st.column_config.DateColumn(
                    format="DD/MM/YYYY"
                )
        }
    )


# ==========================================
# FUTURE 1
# ==========================================

elif page == "Future 1":

    st.title("📈 Future 1")

    st.info(
        "หน้านี้เตรียมไว้สำหรับพัฒนาฟังก์ชันเพิ่มเติมในอนาคต"
    )


# ==========================================
# FUTURE 2
# ==========================================

elif page == "Future 2":

    st.title("📉 Future 2")

    st.info(
        "หน้านี้เตรียมไว้สำหรับพัฒนาฟังก์ชันเพิ่มเติมในอนาคต"
    )

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()