import pandas as pd
from datetime import datetime
import requests
from requests.exceptions import ChunkedEncodingError


def get_user_events(user: str, day: datetime):
    all_user_events = []
    month = day.ctime()[4:7]
    day_str = "-".join([day.strftime("%Y"), month, day.strftime("%d")])
    for event in ["supply", "borrow", "withdraw", "repay"]:
        try:
            resp = requests.get(
                f"https://aavedata.lab.groupe-genes.fr/events/{event}",
                params={"date": day_str},
                verify=False,
            )
        except ChunkedEncodingError:
            resp = requests.get(
                f"https://aavedata.lab.groupe-genes.fr/events/{event}",
                params={"date": day_str},
                verify=False,
            )
        if event in ["withdraw", "repay"]:
            user_events = [ev for ev in resp.json() if ev["user"] == user]
        else:
            user_events = [ev for ev in resp.json() if ev["onBehalfOf"] == user]
        for ev in user_events:
            ev["action"] = event
        all_user_events.extend(user_events)

    # AToken transfer
    try:
        resp = requests.get(
            "https://aavedata.lab.groupe-genes.fr/events/balancetransfer",
            params={"date": day_str},
            verify=False,
        )
    except ChunkedEncodingError:
        resp = requests.get(
            "https://aavedata.lab.groupe-genes.fr/events/balancetransfer",
            params={"date": day_str},
            verify=False,
        )
    # Send
    user_events = [ev for ev in resp.json() if ev["from"] == user]
    for ev in user_events:
        ev["action"] = "balancetransfer_send"
    all_user_events.extend(user_events)
    # Receive
    user_events = [ev for ev in resp.json() if ev["to"] == user]
    for ev in user_events:
        ev["action"] = "balancetransfer_receive"
    all_user_events.extend(user_events)

    try:
        all_user_events = pd.json_normalize(all_user_events)[
            ["blockNumber", "reserve", "action", "amount"]
        ]
    except KeyError:
        return pd.DataFrame(
            {"blockNumber": [], "reserve": [], "action": [], "amount": []}
        )
    all_user_events.amount = all_user_events.amount.apply(str)
    return all_user_events.sort_values("blockNumber").reset_index(drop=True)
