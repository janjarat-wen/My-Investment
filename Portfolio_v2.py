# ==========================================
# GOOGLE SHEETS
# ==========================================

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "116GxxgQ7Qk5aifs_R-haUNTLIKPzVLY2"


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

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()