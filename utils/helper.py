"""
Utility module for helper functions.
Contains reusable UI components and formatting functions.
"""

import streamlit as st
from typing import Optional


def page_header(title: str, description: Optional[str] = None) -> None:
    """
    Renders a standard page header.
    
    Args:
        title (str): The main title of the page.
        description (Optional[str]): A short description below the title.
    """
    st.title(title)
    if description:
        st.write(description)


def metric_card(label: str, value: str, delta: Optional[str] = None) -> None:
    """
    Renders a styled metric card.
    
    Args:
        label (str): The metric label.
        value (str): The metric value.
        delta (Optional[str]): The change in metric value.
    """
    # Placeholder for metric card implementation
    st.metric(label=label, value=value, delta=delta)


def section_title(title: str) -> None:
    """
    Renders a standard section title.
    
    Args:
        title (str): The section title.
    """
    st.subheader(title)
    st.divider()
