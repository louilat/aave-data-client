import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
import os
import boto3
from pages.liquidations.data.extract_data import (
    get_user_proba_history,
    get_user_balances_history,
    get_prices_history,
    get_volatility_prices_history,
)
from pages.liquidations.data.process_data import process_user_balance_history
from pages.liquidations.figures.prices import display_prices
from pages.liquidations.figures.balances import (
    display_hf_and_proba,
    display_asset_balances,
)
from pages.liquidations.figures.proba_details import display_proba_details


def LiquidationsPage():
    client_s3 = boto3.client(
        "s3",
        endpoint_url="https://" + "minio-simple.lab.groupe-genes.fr",
        aws_access_key_id=os.environ["ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
        verify=False,
    )
    day = st.date_input("Choose a day", value=datetime.now() - timedelta(days=16))

    day_query = "-".join((day.strftime("%Y"), day.ctime()[4:7], day.strftime("%d")))

    try:
        events_data = pd.json_normalize(
            requests.get(
                url=f"https://aavedata.lab.groupe-genes.fr/events/liquidation",
                params={"date": day_query},
                verify=False,
            ).json()
        )
        for col in events_data.columns:
            if col in [
                "amount",
                "debtToCover",
                "liquidatedCollateralAmount",
                "borrowRate",
            ]:
                events_data[col] = events_data[col].apply(str)
    except AttributeError:
        events_data = pd.DataFrame({"user": []})

    try:
        users_list = events_data.user.unique().tolist()
    except AttributeError:
        users_list = []
    user = st.selectbox("Choose a user", users_list)

    start = day - timedelta(days=8)
    stop = day + timedelta(days=2)

    user_proba_history = get_user_proba_history(
        client_s3=client_s3, user=user, start=start, stop=stop
    )
    user_balances_history = get_user_balances_history(user=user, start=start, stop=stop)
    aggregated_user_balances_history = process_user_balance_history(
        user_balances_history=user_balances_history
    )

    st.markdown("##### User Balance the Before Liquidation")
    sample = user_balances_history[
        user_balances_history.day == day - timedelta(days=1)
    ].copy()
    sample["currentATokenBalanceUSD"] = (
        sample.scaledATokenBalance.apply(int)
        / 10**sample.decimals
        * sample.liquidityIndex.apply(int)
        * 1e-27
        * sample.underlyingTokenPriceUSD
    )
    sample["currentVariableDebtUSD"] = (
        sample.scaledVariableDebt.apply(int)
        / 10**sample.decimals
        * sample.variableBorrowIndex.apply(int)
        * 1e-27
        * sample.underlyingTokenPriceUSD
    )
    sample.reserveLiquidationThreshold = sample.reserveLiquidationThreshold * 1e-4
    sample = sample[
        [
            "day",
            "name",
            "currentATokenBalanceUSD",
            "currentVariableDebtUSD",
            "reserveLiquidationThreshold",
        ]
    ]
    st.write(sample)

    display_hf_and_proba(
        processed_user_balance_history=aggregated_user_balances_history,
        user_proba_history=user_proba_history,
        liquidation_time=day,
    )

    display_asset_balances(
        user_balances_history=user_balances_history,
        liquidation_time=day,
    )

    prices_history = get_prices_history(start=start, stop=stop)
    volatility_history = get_volatility_prices_history(
        client_s3=client_s3,
        start=start,
        stop=stop,
    )
    display_prices(
        user_balances_history=user_balances_history,
        prices_history=prices_history,
        volatility_history=volatility_history,
        liquidation_time=day,
    )

    display_proba_details(user_proba_history=user_proba_history, liquidation_time=day)


def LiqProbaPage():
    client_s3 = boto3.client(
        "s3",
        endpoint_url="https://" + "minio-simple.lab.groupe-genes.fr",
        aws_access_key_id=os.environ["ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
        verify=False,
    )
    day = st.date_input("Choose a day", value=datetime.now() - timedelta(days=16))
    day_str = day.strftime("%Y-%m-%d")
    day_users_proba = pd.read_csv(
        client_s3.get_object(
            Bucket="llatournerie-ensae",
            Key=f"aave-liquidations-proba/dev-jobs/simulation_liquidation_snapshot_date={day_str}/probas.csv",
        )["Body"]
    )
    st.write(day_users_proba.sort_values("proba_liquidation", ascending=False))
