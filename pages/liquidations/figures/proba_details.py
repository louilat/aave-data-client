import plotly_express as px
import streamlit as st


def display_proba_details(user_proba_history, liquidation_time):
    fig = px.line(data_frame=user_proba_history, x="day", y="q_value")
    fig.add_vline(x=liquidation_time, line_width=3, line_dash="dash", line_color="red")
    fig.update_layout(title_text="User q value")
    st.plotly_chart(fig)

    fig = px.line(data_frame=user_proba_history, x="day", y="a")
    fig.add_vline(x=liquidation_time, line_width=3, line_dash="dash", line_color="red")
    fig.update_layout(title_text="User q numerator")
    st.plotly_chart(fig)

    fig = px.line(data_frame=user_proba_history, x="day", y="user_variance")
    fig.add_vline(x=liquidation_time, line_width=3, line_dash="dash", line_color="red")
    fig.update_layout(title_text="User Variance")
    st.plotly_chart(fig)
