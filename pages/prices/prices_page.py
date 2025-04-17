import os
import boto3
import streamlit as st
from datetime import datetime

from pages.prices.extract_prices import (
    get_prices_history,
    get_volatility_prices_history,
)
from pages.prices.display_prices import display_prices


def PricesPage():
    client_s3 = boto3.client(
        "s3",
        endpoint_url="https://" + "minio-simple.lab.groupe-genes.fr",
        aws_access_key_id=os.environ["ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
        verify=False,
    )
    start = st.date_input(
        "Choose a day", value=datetime(2025, 2, 1), min_value=datetime(2023, 1, 28)
    )
    stop = st.date_input(
        "Choose a day",
        value=datetime(2025, 2, 28),
        min_value=start,
        max_value=datetime(2025, 2, 28),
    )

    prices = get_prices_history(start=start, stop=stop)
    volatility = get_volatility_prices_history(
        client_s3=client_s3, start=start, stop=stop
    )

    display_prices(prices_history=prices, volatility_history=volatility)
