import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta
import requests


def get_prices_history(start: datetime, stop: datetime):
    prices_history = DataFrame()
    day = start
    while day <= stop:
        month = day.ctime()[4:7]
        day_str = "-".join([day.strftime("%Y"), month, day.strftime("%d")])
        resp = requests.get(
            "https://aavedata.lab.groupe-genes.fr/prices",
            params={"date": day_str},
            verify=False,
        )
        day_prices = pd.json_normalize(resp.json())
        prices_history = pd.concat((prices_history, day_prices))
        day += timedelta(days=1)
    return prices_history


def get_volatility_prices_history(client_s3, start: datetime, stop: datetime):
    day = start
    volatility_output = DataFrame()
    while day <= stop:
        day_str = day.strftime("%Y-%m-%d")
        day_correlations = pd.read_csv(
            client_s3.get_object(
                Bucket="projet-datalab-group-jprat",
                Key=f"liquidations/liquidation_trajectories/liquidation_trajectories_snapshot_date={day_str}/volatility.csv",
            )["Body"]
        )
        day_correlations = day_correlations[
            day_correlations.pair1 == day_correlations.pair2
        ]
        day_correlations["day"] = day
        volatility_output = pd.concat((volatility_output, day_correlations))
        day += timedelta(days=1)

    volatility_output = volatility_output[["pair1", "day", "rho"]].rename(
        columns={"pair1": "underlyingAsset", "rho": "volatility"}
    )

    month = stop.ctime()[4:7]
    day_str = "-".join([stop.strftime("%Y"), month, stop.strftime("%d")])
    resp = requests.get(
        "https://aavedata.lab.groupe-genes.fr/reserves",
        params={"date": day_str},
        verify=False,
    )
    reserves = pd.json_normalize(resp.json())

    volatility_output = volatility_output.merge(
        reserves[["underlyingAsset", "name"]], how="left", on="underlyingAsset"
    )
    return volatility_output
