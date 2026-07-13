"""
Main application entry point for the Sales Forecasting Streamlit App.
Handles Streamlit configuration, sidebar elements, and page navigation.
"""

import streamlit as st
from pathlib import Path


def main() -> None:
    """
    Main function to configure and run the Streamlit application.
    """
    # Streamlit configuration
    st.set_page_config(
        page_title="Sales Forecasting Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Page title
    st.title("Sales Forecasting Dashboard")
    st.markdown("Welcome to the Sales Forecasting Internship Project.")

    # Sidebar project information and logo placeholder
    with st.sidebar:
        st.header("Project Info")
        # Sidebar logo placeholder
        st.image("https://via.placeholder.com/150?text=Logo", caption="Sidebar Logo Placeholder")
        st.markdown(
            """
            **Internship Project**
            - Sales Overview
            - Forecasting
            - Anomaly Detection
            - Segmentation
            """
        )

    # Navigation is handled automatically by Streamlit multipage (pages/ directory)


if __name__ == "__main__":
    main()
