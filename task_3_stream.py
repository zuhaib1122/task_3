import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Advanced Retail Analytics", layout="wide")

st.title("🚀 Enterprise Retail Command Center")

# --- DATA LOADING ---
uploaded_file = st.sidebar.file_uploader("Upload your csv retail file", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
elif uploaded_file is none:
    df = pd.read_csv("FMCG_2022_2024.csv")
    
    # --- 1. BRAND SEGMENTATION LOGIC ---
    brand_stats = df.groupby('brand').agg({
        'units_sold': 'mean',
        'delivery_days': 'mean',
        'revenue': 'sum',
        'stock_available': 'last' # Most recent stock level
    }).reset_index()

    # Segmentation (The Automation Engine)
    conditions = [
        (brand_stats['units_sold'] >= 21) & (brand_stats['delivery_days'] <= 3),
        (brand_stats['units_sold'] >= 21) & (brand_stats['delivery_days'] > 3),
        (brand_stats['units_sold'] < 21) & (brand_stats['delivery_days'] <= 3),
        (brand_stats['units_sold'] < 21) & (brand_stats['delivery_days'] > 3)
    ]
    choices = ['Leader', 'At_risk', 'Rising_star', 'Under_performer']
    brand_stats['segment'] = np.select(conditions, choices, default='Other')

    # --- 2. KPI TOP ROW ---
    total_rev = df['revenue'].sum()
    total_qty = df['units_sold'].sum()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Revenue", f"${total_rev:,.2f}")
    m2.metric("Units Sold", f"{total_qty:,}")
    m3.metric("Top Region", df.groupby('region')['revenue'].sum().idxmax())
    m4.metric("Avg Price/Unit", f"${df['price_unit'].mean():.2f}")

    # --- 3. REGIONAL PERFORMANCE & REVENUE ---
    st.divider()
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Revenue by Region")
        reg_data = df.groupby('region')['revenue'].sum().sort_values(ascending=False).reset_index()
        fig_reg = px.bar(reg_data, x='region', y='revenue', color='revenue', color_continuous_scale='Viridis')
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_right:
        st.subheader("Stock Runway (Days Remaining)")
        # Runway calculation: Current Stock / Avg Daily Sales
        brand_stats['stock_runway'] = brand_stats['stock_available'] / brand_stats['units_sold']
        fig_runway = px.bar(brand_stats.sort_values('stock_runway'), x='brand', y='stock_runway', 
                            color='stock_runway', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_runway, use_container_width=True)

    # --- 4. STOCK PREDICTION ALERTS ---
    st.subheader("🚨 Automated Inventory Alerts")
    low_stock = brand_stats[brand_stats['stock_runway'] < 7] # Less than a week of stock
    if not low_stock.empty:
        st.error(f"ATTENTION: {len(low_stock)} brands will run out of stock in less than 7 days!")
        st.table(low_stock[['brand', 'stock_available', 'stock_runway', 'segment']])
    
    # --- 5. CHANNEL ANALYSIS ---
    st.subheader("Sales Channel Performance")
    fig_chan = px.pie(df, values='revenue', names='channel', hole=0.4, title="Revenue by Channel")
                            st.plotly_chart(fig_chan)

