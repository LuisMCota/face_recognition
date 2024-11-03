import streamlit as st

def set_styles():
    st.set_page_config(page_title="Facial Recognition & Attendance", page_icon="👤", layout="wide")
    st.markdown(
        """
        <style>
            .main {
                background-color: #F5EEF8;
                color: #4A148C;
            }
            .css-18e3th9 {
                padding: 1rem;
                background-color: #FF7043 !important;
            }
            .css-1d391kg {
                color: #4A148C !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
