from datetime import datetime, timedelta
import pandas as pd
from pandas import DataFrame
import requests


def get_user_proba_history(client_s3, user: str, start: datetime, stop: datetime):
    day = start
    probas_output = DataFrame()
    while day <= stop:
        day_str = day.strftime("%Y-%m-%d")
        day_users_proba = pd.read_csv(
            client_s3.get_object(
                Bucket="llatournerie-ensae",
                Key=f"aave-liquidations-proba/dev-jobs/simulation_liquidation_snapshot_date={day_str}/probas.csv",
            )["Body"]
        )
        if user in day_users_proba.user_address.unique().tolist():
            print("Day = ", day)
            day_users_proba = day_users_proba.set_index("user_address")
            l = len(probas_output)
            probas_output.loc[l, "day"] = day
            probas_output.loc[l, "a"] = day_users_proba.loc[user, "a"].item()
            probas_output.loc[l, "user_variance"] = day_users_proba.loc[
                user, "user_variance"
            ].item()
            probas_output.loc[l, "q_value"] = day_users_proba.loc[
                user, "q_value"
            ].item()
            probas_output.loc[l, "proba_liquidation"] = day_users_proba.loc[
                user, "proba_liquidation"
            ].item()

        day += timedelta(days=1)
    return probas_output


def get_user_balances_history(user: str, start: datetime, stop: datetime):
    day = start
    user_history = DataFrame()
    while day <= stop:
        month = day.ctime()[4:7]
        day_str = "-".join([day.strftime("%Y"), month, day.strftime("%d")])
        # day_str = day.strftime("%Y-%b-%d")
        # print(day_str)
        resp = requests.get(
            "https://aavedata.lab.groupe-genes.fr/user-selec-balances",
            params={"date": day_str, "user": user},
            verify=False,
        )
        if resp.json() is not None:
            day_users_balances = pd.json_normalize(resp.json())
            print("Day = ", day)
            day_users_balances["day"] = day
            resp = requests.get(
                "https://aavedata.lab.groupe-genes.fr/reserves",
                params={"date": day_str},
                verify=False,
            )
            day_reserves = pd.json_normalize(resp.json())
            day_users_balances = day_users_balances[
                [
                    "user_address",
                    "underlyingAsset",
                    "scaledATokenBalance",
                    "scaledVariableDebt",
                    "day",
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
            user_history = pd.concat((user_history, day_users_balances))
        day += timedelta(days=1)
    return user_history


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
                Bucket="llatournerie-ensae",
                Key=f"aave-liquidations-proba/dev-jobs/simulation_liquidation_snapshot_date={day_str}/correlations.csv",
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
