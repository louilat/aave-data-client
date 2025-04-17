import streamlit as st

from pages.user.user_page import UserPage
from pages.prices.prices_page import PricesPage
from pages.liquidations.page import LiquidationsPage

st.title("Aave-V3 Data")

st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Pages",
    options=[
        "Users Balances",
        "Liquidations Trajectories",
        "Prices & Volatility",
    ],
)

if section == "Users Balances":
    UserPage()
elif section == "Liquidations Trajectories":
    LiquidationsPage()
elif section == "Prices & Volatility":
    PricesPage()
