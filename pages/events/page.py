import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import requests


def EventsPage():
    day = st.date_input("Choose a day", value=datetime.now() - timedelta(days=14))
    event = st.selectbox(
        "Choose an event type", ["Supply", "Withdraw", "Borrow", "Repay", "Liquidation"]
    )

    day_query = "-".join((day.strftime("%Y"), day.ctime()[4:7], day.strftime("%d")))
    day_str = day.strftime("%Y-%m-%d")
    event_name = event.lower()

    try:
        events_data = pd.json_normalize(
            requests.get(
                url=f"https://aavedata.lab.groupe-genes.fr/events/{event_name}",
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
        # liquidations.debtToCover = liquidations.debtToCover.apply(str)
        # liquidations.liquidatedCollateralAmount = liquidations.liquidatedCollateralAmount.apply(str)
    except AttributeError:
        events_data = pd.DataFrame()

    nb_events = len(events_data)

    st.header(f"Found {nb_events} {event} events on {day_str}")
    st.write(events_data)
    st.download_button(
        label="Download CSV",
        data=events_data.to_csv().encode("utf-8"),
        file_name=f"{event_name}_events_{day_str}.csv",
        mime="text/csv",
        # icon=":material/download:",
    )
