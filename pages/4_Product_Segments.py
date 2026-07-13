"""
Product Demand Segments Page.
Displays product/customer demand segmentation generated during the machine learning analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


@st.cache_data
def load_segments_data(file_path: Path) -> pd.DataFrame:
    """
    Loads customer segmentation data.
    
    Args:
        file_path (Path): Path to the customer segments CSV file.
        
    Returns:
        pd.DataFrame: The loaded DataFrame, or an empty DataFrame if not found.
    """
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame()


def filter_data(df: pd.DataFrame, segments: list, customers: list, regions: list) -> pd.DataFrame:
    """
    Filters the dataset based on sidebar selections.
    
    Args:
        df (pd.DataFrame): The segmentation dataframe.
        segments (list): Selected segments.
        customers (list): Selected customer IDs.
        regions (list): Selected regions.
        
    Returns:
        pd.DataFrame: The filtered dataframe.
    """
    if df.empty:
        return df
        
    filtered = df.copy()
    
    if segments and 'Segment' in filtered.columns:
        filtered = filtered[filtered['Segment'].isin(segments)]
        
    if customers and 'Customer ID' in filtered.columns:
        filtered = filtered[filtered['Customer ID'].isin(customers)]
        
    if regions and 'Region' in filtered.columns:
        filtered = filtered[filtered['Region'].isin(regions)]
        
    return filtered


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculates KPI metrics for segments.
    
    Args:
        df (pd.DataFrame): The filtered dataframe.
        
    Returns:
        dict: The computed KPIs.
    """
    metrics = {
        "Total Segments": "0",
        "Total Customers": "0",
        "Largest Segment": "N/A",
        "Average Sales": "N/A"
    }
    
    if not df.empty:
        if 'Segment' in df.columns:
            metrics["Total Segments"] = str(df['Segment'].nunique())
            mode_series = df['Segment'].mode()
            metrics["Largest Segment"] = mode_series[0] if not mode_series.empty else "N/A"
            
        if 'Customer ID' in df.columns:
            metrics["Total Customers"] = str(df['Customer ID'].nunique())
            
        # Safely determine the appropriate column for 'Sales'
        sales_col = 'Sales' if 'Sales' in df.columns else 'Monetary' if 'Monetary' in df.columns else None
        
        if sales_col is not None:
            avg_sales = df[sales_col].mean()
            metrics["Average Sales"] = f"${avg_sales:,.2f}"
            
    return metrics


def create_segment_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates a bar chart showing the distribution of segments.
    
    Args:
        df (pd.DataFrame): The data to plot.
        
    Returns:
        go.Figure: The Plotly figure object.
    """
    if df.empty or 'Segment' not in df.columns:
        return go.Figure()
        
    segment_counts = df['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    
    fig = px.bar(
        segment_counts, 
        x='Segment', 
        y='Count', 
        title='Segment Distribution',
        text_auto=True,
        color='Segment'
    )
    return fig


def create_scatter_plot(df: pd.DataFrame) -> go.Figure:
    """
    Creates a scatter plot for Customer Segments (PCA or Frequency vs Monetary).
    
    Args:
        df (pd.DataFrame): The data to plot.
        
    Returns:
        go.Figure: The Plotly figure object, or None if required columns are missing.
    """
    if df.empty or 'Segment' not in df.columns:
        return go.Figure()
        
    # Priority 1: PCA coordinates if they exist
    if 'PCA1' in df.columns and 'PCA2' in df.columns:
        fig = px.scatter(
            df, 
            x='PCA1', 
            y='PCA2', 
            color='Segment', 
            title='Customer Segments (PCA Projection)',
            hover_data=['Customer ID'] if 'Customer ID' in df.columns else None
        )
        return fig
        
    # Priority 2: Fallback to Frequency vs Monetary
    if 'Frequency' in df.columns and 'Monetary' in df.columns:
        fig = px.scatter(
            df, 
            x='Frequency', 
            y='Monetary', 
            color='Segment', 
            title='Customer Segments (Frequency vs Monetary)',
            hover_data=['Customer ID'] if 'Customer ID' in df.columns else None
        )
        return fig
        
    return None # Return None if no valid plotting axes exist


def create_top_customers_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates a horizontal bar chart for top customers by sales/monetary value.
    
    Args:
        df (pd.DataFrame): The data to plot.
        
    Returns:
        go.Figure: The Plotly figure object.
    """
    sales_col = 'Sales' if 'Sales' in df.columns else 'Monetary' if 'Monetary' in df.columns else None
    
    if df.empty or 'Customer ID' not in df.columns or not sales_col:
        return go.Figure()
        
    # Get top 10 customers
    top_n = df.sort_values(by=sales_col, ascending=False).head(10)
    top_n = top_n.sort_values(by=sales_col, ascending=True) # Ascending for correct horizontal rendering
    
    fig = px.bar(
        top_n, 
        x=sales_col, 
        y='Customer ID', 
        orientation='h', 
        title='Top Customers by Sales Volume',
        text_auto='.2s',
        color='Segment' if 'Segment' in df.columns else None
    )
    return fig


def main() -> None:
    """
    Main function to render the Product Demand Segments page.
    """
    st.title("Product Demand Segments")
    st.write("Display product/customer demand segmentation generated during the machine learning analysis.")
    
    # Robust path construction
    base_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    segments_path = base_dir / "customer_segments.csv"
    
    df = load_segments_data(segments_path)
    
    if df.empty:
        st.warning("Customer segments data not available.")
        return
        
    # Sidebar Filters
    st.sidebar.header("Segmentation Filters")
    
    # Safe extraction of unique filter values
    available_segments = sorted(df['Segment'].dropna().unique().tolist()) if 'Segment' in df.columns else []
    available_customers = sorted(df['Customer ID'].dropna().unique().tolist()) if 'Customer ID' in df.columns else []
    available_regions = sorted(df['Region'].dropna().unique().tolist()) if 'Region' in df.columns else []
    
    selected_segments = st.sidebar.multiselect("Segment", options=available_segments, default=available_segments)
    
    # Default to empty selection for customers to avoid overly restrictive initial state
    selected_customers = st.sidebar.multiselect("Customer", options=available_customers, default=[])
    
    selected_regions = []
    if available_regions:
        selected_regions = st.sidebar.multiselect("Region", options=available_regions, default=available_regions)
        
    # Apply filters
    filtered_df = filter_data(df, selected_segments, selected_customers, selected_regions)
        
    if filtered_df.empty:
        st.info("No data available for the selected filters.")
        return

    # 1. KPI Cards
    metrics = calculate_kpis(filtered_df)
    
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric("Total Segments", metrics["Total Segments"])
    with kpi_cols[1]:
        st.metric("Total Customers", metrics["Total Customers"])
    with kpi_cols[2]:
        st.metric("Largest Segment", metrics["Largest Segment"])
    with kpi_cols[3]:
        st.metric("Average Sales", metrics["Average Sales"])
        
    st.divider()
    
    # 2. Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Segment Distribution")
        st.plotly_chart(create_segment_distribution_chart(filtered_df), use_container_width=True)
        
        st.subheader("3. Top Customers by Sales")
        st.plotly_chart(create_top_customers_chart(filtered_df), use_container_width=True)
        
    with col2:
        st.subheader("2. Customer Segments Scatter")
        scatter_fig = create_scatter_plot(filtered_df)
        if scatter_fig is None:
            st.warning("Required columns (PCA coordinates or Frequency/Monetary) are unavailable to plot the scatter chart.")
        else:
            st.plotly_chart(scatter_fig, use_container_width=True)
            
    st.divider()
    
    # 3. Segment Summary Table
    st.subheader("4. Segment Summary Table")
    st.dataframe(filtered_df, use_container_width=True)


if __name__ == "__main__":
    main()
