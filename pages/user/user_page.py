import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta


def UserPage():
    day = st.date_input(
        label="Choose a day",
        value=datetime.now() - timedelta(days=16),
        min_value=datetime(2023, 1, 27),
        max_value=datetime.now() - timedelta(days=16),
    )

    day_query = "-".join((day.strftime("%Y"), day.ctime()[4:7], day.strftime("%d")))
    users_balances = pd.json_normalize(
        requests.get(
            url=f"https://aavedata.lab.groupe-genes.fr/users-balances",
            params={"date": day_query},
            verify=False,
        ).json()
    )

    try:
        users_list = users_balances.user_address.unique().tolist()
    except AttributeError:
        users_list = []
    user = st.selectbox(label="Choose a user", options=users_list)

    user_balances = pd.json_normalize(
        requests.get(
            "https://aavedata.lab.groupe-genes.fr/user-selec-balances",
            params={"date": day_query, "user": user},
            verify=False,
        ).json()
    )

    resp = requests.get(
        "https://aavedata.lab.groupe-genes.fr/reserves",
        params={"date": day_query},
        verify=False,
    )
    day_reserves = pd.json_normalize(resp.json())
    user_balances = user_balances[
        [
            "user_address",
            "underlyingAsset",
            "scaledATokenBalance",
            "scaledVariableDebt",
        ]
    ].merge(
        day_reserves[
            [
                "underlyingAsset",
                "name",
                "decimals",
                "underlyingTokenPriceUSD",
                "liquidityIndex",
                "variableBorrowIndex",
                "reserveLiquidationThreshold",
            ]
        ],
        how="left",
        on="underlyingAsset",
    )
    user_balances["currentATokenBalanceUSD"] = (
        user_balances.scaledATokenBalance.apply(int)
        / 10**user_balances.decimals
        * user_balances.liquidityIndex.apply(int)
        * 1e-27
        * user_balances.underlyingTokenPriceUSD
    )
    user_balances["currentVariableDebtUSD"] = (
        user_balances.scaledVariableDebt.apply(int)
        / 10**user_balances.decimals
        * user_balances.variableBorrowIndex.apply(int)
        * 1e-27
        * user_balances.underlyingTokenPriceUSD
    )
    user_balances.reserveLiquidationThreshold = (
        user_balances.reserveLiquidationThreshold * 1e-4
    )

    user_balances = user_balances[
        [
            "name",
            "currentATokenBalanceUSD",
            "currentVariableDebtUSD",
            "reserveLiquidationThreshold",
        ]
    ]

    st.write(user_balances)
