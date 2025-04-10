import streamlit as st

from pages.user.user_page import UserPage
from pages.events.page import EventsPage
from pages.liquidations.page import LiquidationsPage, LiqProbaPage

st.title("Aave-V3 Data")

st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Pages",
    options=[
        "Liquidation Probabilities",
        "Users Balances",
        "Liquidations Trajectories",
        "Prices Volatility",
    ],
)

if section == "Events":
    EventsPage()
elif section == "Liquidation Probabilities":
    LiqProbaPage()
elif section == "Users Balances":
    UserPage()
elif section == "Liquidations Trajectories":
    LiquidationsPage()
