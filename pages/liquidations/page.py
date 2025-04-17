import streamlit as st
from datetime import datetime, timedelta, timezone
import requests
import pandas as pd
import os
import boto3
import numpy as np

from pages.liquidations.figures.balances import (
    display_hf_and_proba,
    display_asset_balances,
)
from pages.liquidations.user_events import get_user_events


def LiquidationsPage():
    client_s3 = boto3.client(
        "s3",
        endpoint_url="https://" + "minio-simple.lab.groupe-genes.fr",
        aws_access_key_id=os.environ["ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
        verify=False,
    )
    day = st.date_input("Choose a day", value=datetime(2025, 2, 28))

    day_query = "-".join((day.strftime("%Y"), day.ctime()[4:7], day.strftime("%d")))
    day_str = day.strftime("%Y-%m-%d")

    probas_trajectories = pd.read_csv(
        client_s3.get_object(
            Bucket="projet-datalab-group-jprat",
            Key=f"liquidations/liquidation_trajectories/liquidation_trajectories_snapshot_date={day_str}/liquidation_trajectories.csv",
        )["Body"]
    )

    users_balances_trajectories = pd.read_csv(
        client_s3.get_object(
            Bucket="projet-datalab-group-jprat",
            Key=f"liquidations/liquidation_trajectories/liquidation_trajectories_snapshot_date={day_str}/users_balances.csv",
        )["Body"]
    )

    resp = requests.get(
        "https://aavedata.lab.groupe-genes.fr/events/liquidation",
        params={"date": day_query},
        verify=False,
    )
    liquidation_events = pd.json_normalize(resp.json())

    user = st.selectbox(
        "Choose a user",
        options=probas_trajectories.user_address.unique().tolist(),
    )

    user_probas_history = probas_trajectories[
        probas_trajectories.user_address == user
    ].reset_index(drop=True)
    user_balances_history = users_balances_trajectories[
        users_balances_trajectories.user_address == user
    ].reset_index(drop=True)

    liquidation_blocks = liquidation_events.loc[
        liquidation_events.user == user, "blockNumber"
    ].tolist()
    idx = [
        np.argmin(np.abs(user_probas_history.BlockNumber - block))
        for block in liquidation_blocks
    ]
    liquidation_times = [
        datetime.fromtimestamp(user_probas_history.Timestamp[i], tz=timezone.utc)
        for i in idx
    ]

    display_hf_and_proba(
        user_proba_history=user_probas_history, liquidation_times=liquidation_times
    )

    display_asset_balances(
        user_balances_history=user_balances_history, liquidation_times=liquidation_times
    )

    st.markdown("### User Events")

    st.write(get_user_events(user=user, day=day))
