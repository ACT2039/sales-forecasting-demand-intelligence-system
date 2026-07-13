"""
Sales Overview Page.
Displays yearly sales, monthly trends, and regional analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from plotly.graph_objs import Figure


@st.cache_data
def load_superstore_data(file_path: Path) -> pd.DataFrame:
    """
    Loads and caches the superstore dataset.
    
    Args:
        file_path (Path): Path to the CSV file.
        
    Returns:
        pd.DataFrame: The loaded dataset.
    """
    df = pd.read_csv(file_path)
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df


def filter_data(df: pd.DataFrame, years: list, regions: list, categories: list) -> pd.DataFrame:
    """
    Filters the DataFrame based on selected parameters.
    
    Args:
        df (pd.DataFrame): The original dataframe.
        years (list): Selected years.
        regions (list): Selected regions.
        categories (list): Selected categories.
        
    Returns:
        pd.DataFrame: The filtered dataframe.
    """
    filtered_df = df.copy()
    if years:
        filtered_df = filtered_df[filtered_df['Year'].isin(years)]
    if regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(regions)]
    if categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
    return filtered_df


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculates key performance indicators.
    
    Args:
        df (pd.DataFrame): The data to calculate KPIs for.
        
    Returns:
        dict: A dictionary containing KPI names and their formatted string values.
    """
    sales = df['Sales'].sum() if 'Sales' in df.columns else 0.0
    profit = df['Profit'].sum() if 'Profit' in df.columns else 0.0
    orders = df['Order ID'].nunique() if 'Order ID' in df.columns else 0
    customers = df['Customer ID'].nunique() if 'Customer ID' in df.columns else 0
    
    return {
        "Total Sales": f"${sales:,.2f}",
        "Total Profit": f"${profit:,.2f}",
        "Total Orders": f"{orders:,}",
        "Total Customers": f"{customers:,}"
    }


def create_sales_by_year_chart(df: pd.DataFrame) -> Figure:
    """Creates a bar chart for Total Sales by Year."""
    sales_by_year = df.groupby("Year", as_index=False)["Sales"].sum()
    fig = px.bar(
        sales_by_year, 
        x="Year", 
        y="Sales", 
        title="Total Sales by Year", 
        text_auto='.2s'
    )
    fig.update_layout(xaxis_type='category')
    return fig


def create_monthly_sales_trend(df: pd.DataFrame) -> Figure:
    """Creates a line chart for Monthly Sales Trend."""
    df_copy = df.copy()
    # Convert 'Order Date' to Period ('M') and then to string for plotting
    df_copy['Month_Year'] = df_copy['Order Date'].dt.to_period('M').astype(str)
    monthly_trend = df_copy.groupby("Month_Year", as_index=False)["Sales"].sum().sort_values("Month_Year")
    fig = px.line(
        monthly_trend, 
        x="Month_Year", 
        y="Sales", 
        title="Monthly Sales Trend", 
        markers=True
    )
    return fig


def create_sales_by_region_chart(df: pd.DataFrame) -> Figure:
    """Creates a bar chart for Sales by Region."""
    sales_by_region = df.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    fig = px.bar(
        sales_by_region, 
        x="Region", 
        y="Sales", 
        title="Sales by Region", 
        color="Region",
        text_auto='.2s'
    )
    return fig


def create_sales_by_category_chart(df: pd.DataFrame) -> Figure:
    """Creates a bar chart for Sales by Category."""
    sales_by_category = df.groupby("Category", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    fig = px.bar(
        sales_by_category, 
        x="Category", 
        y="Sales", 
        title="Sales by Category", 
        color="Category",
        text_auto='.2s'
    )
    return fig


def main() -> None:
    """
    Renders the Sales Overview page.
    """
    st.title("Sales Overview")
    
    # Load data using pathlib
    data_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "final_processed_superstore.csv"
    try:
        df = load_superstore_data(data_path)
    except FileNotFoundError:
        st.error(f"Data file not found at {data_path}")
        return
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    # Sidebar filters
    st.sidebar.header("Filters")
    
    available_years = sorted(df['Year'].dropna().unique().tolist()) if 'Year' in df.columns else []
    available_regions = sorted(df['Region'].dropna().unique().tolist()) if 'Region' in df.columns else []
    available_categories = sorted(df['Category'].dropna().unique().tolist()) if 'Category' in df.columns else []
    
    selected_years = st.sidebar.multiselect("Select Year", options=available_years, default=available_years)
    selected_regions = st.sidebar.multiselect("Select Region", options=available_regions, default=available_regions)
    selected_categories = st.sidebar.multiselect("Select Category", options=available_categories, default=available_categories)
    
    # Apply filters
    filtered_df = filter_data(df, selected_years, selected_regions, selected_categories)
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return

    # Render KPIs
    kpis = calculate_kpis(filtered_df)
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric("Total Sales", kpis["Total Sales"])
    with kpi_cols[1]:
        st.metric("Total Profit", kpis["Total Profit"])
    with kpi_cols[2]:
        st.metric("Total Orders", kpis["Total Orders"])
    with kpi_cols[3]:
        st.metric("Total Customers", kpis["Total Customers"])
        
    st.divider()
    
    # Render Charts in Two Columns
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Year' in filtered_df.columns and 'Sales' in filtered_df.columns:
            st.plotly_chart(create_sales_by_year_chart(filtered_df), use_container_width=True)
            
        if 'Region' in filtered_df.columns and 'Sales' in filtered_df.columns:
            st.plotly_chart(create_sales_by_region_chart(filtered_df), use_container_width=True)
            
    with col2:
        if 'Order Date' in filtered_df.columns and 'Sales' in filtered_df.columns:
            st.plotly_chart(create_monthly_sales_trend(filtered_df), use_container_width=True)
            
        if 'Category' in filtered_df.columns and 'Sales' in filtered_df.columns:
            st.plotly_chart(create_sales_by_category_chart(filtered_df), use_container_width=True)


if __name__ == "__main__":
    main()
