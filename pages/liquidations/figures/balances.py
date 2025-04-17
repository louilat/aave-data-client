import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from pandas import DataFrame
import pandas as pd


def display_hf_and_proba(
    user_proba_history,
    liquidation_times,
):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=pd.to_datetime(user_proba_history.Timestamp, unit="s", utc=True),
            y=user_proba_history.hf,
            name="Health Factor",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=pd.to_datetime(user_proba_history.Timestamp, unit="s", utc=True),
            y=user_proba_history.proba_p2,
            name="Liquidation Proba",
        ),
        secondary_y=True,
    )
    for t in liquidation_times:
        fig.add_vline(x=t, line_width=3, line_dash="dash", line_color="red")
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Health Factor", secondary_y=False)
    fig.update_yaxes(title_text="Liquidation Proba.", secondary_y=True)
    fig.update_layout(title_text="Health Factor and Liquidation Probability")
    st.plotly_chart(fig)


def display_asset_balances(user_balances_history, liquidation_times):
    all_user_assets = user_balances_history.name.unique().tolist()
    for asset in all_user_assets:
        user_asset_history = user_balances_history[user_balances_history.name == asset]
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(user_asset_history.Timestamp, unit="s", utc=True),
                y=user_asset_history.currentATokenBalanceUSD,
                name="Collateral",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(user_asset_history.Timestamp, unit="s", utc=True),
                y=user_asset_history.currentVariableDebtUSD,
                name="Debt",
            ),
            secondary_y=True,
        )
        for t in liquidation_times:
            fig.add_vline(x=t, line_width=3, line_dash="dash", line_color="red")
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Collateral Balance", secondary_y=False)
        fig.update_yaxes(title_text="Debt Balance", secondary_y=True)
        fig.update_layout(title_text=f"User Balance in {asset}")
        st.plotly_chart(fig)
