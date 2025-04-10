import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from pandas import DataFrame


def display_hf_and_proba(
    processed_user_balance_history,
    user_proba_history,
    liquidation_time,
):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=processed_user_balance_history.day,
            y=processed_user_balance_history.hf,
            name="Health Factor",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=user_proba_history.day,
            y=2 * user_proba_history.proba_liquidation,
            name="Liquidation Proba",
        ),
        secondary_y=True,
    )
    fig.add_vline(x=liquidation_time, line_width=3, line_dash="dash", line_color="red")
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Health Factor", secondary_y=False)
    fig.update_yaxes(title_text="Liquidation Proba.", secondary_y=True)
    fig.update_layout(title_text="Health Factor and Liquidation Probability")
    st.plotly_chart(fig)


def display_asset_balances(user_balances_history, liquidation_time):
    user_balances_history_ = user_balances_history.copy()
    user_balances_history_["currentATokenBalance"] = (
        user_balances_history_.scaledATokenBalance.apply(int)
        / 10**user_balances_history_.decimals
        * user_balances_history_.liquidityIndex.apply(int)
        * 1e-27
        # * user_balances_history_.underlyingTokenPriceUSD
    )
    user_balances_history_["currentVariableDebt"] = (
        user_balances_history_.scaledVariableDebt.apply(int)
        / 10**user_balances_history_.decimals
        * user_balances_history_.variableBorrowIndex.apply(int)
        * 1e-27
        # * user_balances_history_.underlyingTokenPriceUSD
    )
    all_user_assets = user_balances_history_.name.unique().tolist()
    for asset in all_user_assets:
        base_days = user_balances_history_.day.unique().tolist()
        base_days = DataFrame({"day": base_days})
        asset_balance = user_balances_history_[user_balances_history_.name == asset]
        price = base_days.merge(
            asset_balance[["day", "currentATokenBalance", "currentVariableDebt"]],
            how="left",
            on="day",
        )
        price = price.fillna(0)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=price.day, y=price.currentATokenBalance, name="Collateral"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=price.day, y=price.currentVariableDebt, name="Debt"),
            secondary_y=True,
        )
        fig.add_vline(
            x=liquidation_time, line_width=3, line_dash="dash", line_color="red"
        )
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Collateral Balance", secondary_y=False)
        fig.update_yaxes(title_text="Debt Balance", secondary_y=True)
        fig.update_layout(title_text=f"User Balance in {asset}")
        st.plotly_chart(fig)
