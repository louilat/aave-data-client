import plotly_express as px
import streamlit as st
import pandas as pd


def display_proba_details(user_proba_history, liquidation_times):
    user_proba_history_ = user_proba_history.copy()
    user_proba_history_["time"] = pd.to_datetime(user_proba_history_.Timestamp)
    fig = px.line(data_frame=user_proba_history_, x="time", y="q_value")
    for t in liquidation_times:
        fig.add_vline(x=t, line_width=3, line_dash="dash", line_color="red")
    fig.update_layout(title_text="User q value")
    st.plotly_chart(fig)

    fig = px.line(data_frame=user_proba_history_, x="time", y="a")
    for t in liquidation_times:
        fig.add_vline(x=t, line_width=3, line_dash="dash", line_color="red")
    fig.update_layout(title_text="User q numerator")
    st.plotly_chart(fig)

    fig = px.line(data_frame=user_proba_history_, x="time", y="user_variance")
    for t in liquidation_times:
        fig.add_vline(x=t, line_width=3, line_dash="dash", line_color="red")
    fig.update_layout(title_text="User Variance")
    st.plotly_chart(fig)
