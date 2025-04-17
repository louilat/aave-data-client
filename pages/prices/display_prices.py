import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def display_prices(prices_history, volatility_history):
    coll = prices_history.UnderlyingToken.unique().tolist()

    debt = prices_history.UnderlyingToken.unique().tolist()

    names = volatility_history[["underlyingAsset", "name"]].drop_duplicates()
    assets_names = dict(zip(names.underlyingAsset, names.name))

    for asset in coll:
        price_token = prices_history[prices_history.UnderlyingToken == asset].copy()
        price_token["time"] = pd.to_datetime(price_token.Timestamp, unit="s")
        price_token["Price"] = price_token.Price * 1e-8
        volatility_token = volatility_history[
            volatility_history.underlyingAsset == asset
        ]
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=price_token.time, y=price_token.Price, name="Asset Price"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=volatility_token.day,
                y=2 * volatility_token.volatility,
                name="Token Volatility",
            ),
            secondary_y=True,
        )
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Price", secondary_y=False)
        fig.update_yaxes(title_text="Volatility", secondary_y=True)
        fig.update_layout(
            title_text=f"Collateral Price Evolution: {assets_names[asset]}"
        )
        st.plotly_chart(fig)

    for asset in debt:
        price_token = prices_history[prices_history.UnderlyingToken == asset].copy()
        price_token["time"] = pd.to_datetime(price_token.Timestamp, unit="s")
        price_token["Price"] = price_token.Price * 1e-8
        volatility_token = volatility_history[
            volatility_history.underlyingAsset == asset
        ]
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=price_token.time, y=price_token.Price, name="Asset Price"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=volatility_token.day,
                y=2 * volatility_token.volatility,
                name="Token Volatility",
            ),
            secondary_y=True,
        )
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Price", secondary_y=False)
        fig.update_yaxes(title_text="Volatility", secondary_y=True)
        fig.update_layout(title_text=f"Debt Price Evolution: {assets_names[asset]}")
        st.plotly_chart(fig)
