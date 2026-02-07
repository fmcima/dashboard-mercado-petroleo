import streamlit as st
import sys
import os
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# Add project root to sys.path to import from execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from execution.utils import load_json
from execution.summarize import summarize_text
from execution import fetch_data # Import the module

# Page Configuration
st.set_page_config(
    page_title="Dashboard Petróleo",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css(os.path.join(os.path.dirname(__file__), 'style.css'))

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=50) # Generic Icon
    st.title("Oil & Gas Intelligence")
    st.markdown("---")
    st.write("**Menu**")
    st.button("Dashboard", width="stretch")
    st.button("Market Data", width="stretch")
    st.button("News Feed", width="stretch")
    st.markdown("---")
    if st.button("🔄 Atualizar Dados"):
        with st.spinner("Atualizando dados..."):
            fetch_data.main() # Direct call
        st.success("Dados atualizados!")
        st.rerun()

# Main Content
st.title("Dashboard de Mercado - Brent Crude")

# Load Data
data = load_json()

# Auto-fetch if no data (first run on cloud)
if not data:
    with st.spinner("Primeira execução: Buscando dados..."):
        fetch_data.main()
        data = load_json() # Reload data
        st.rerun()

# Main Content
st.title("Dashboard de Mercado - Brent Crude")

# Load Data
data = load_json()

if not data:
    st.warning("Nenhum dado encontrado. Por favor, clique em 'Atualizar Dados' na barra lateral.")
else:
    # 1. KPI Section
    col1, col2 = st.columns(2)

    with col1:
        brent = data.get('brent')
        if brent:
            delta_color = "normal"
            if brent['change'] > 0:
                delta_color = "normal" 
            
            st.metric(
                label="Brent Crude (USD)",
                value=f"${brent['current_price']}",
                delta=f"{brent['change']} ({brent['pct_change']}%)",
                delta_color=delta_color
            )
        else:
            st.metric(label="Brent Crude", value="N/A")

    with col2:
        st.metric(label="WTI Crude (Simulado)", value="$74.20", delta="-0.50 (-0.6%)", delta_color="inverse")
    
    st.markdown("---")

    # 2. Advanced Chart Section
    st.subheader("📈 Análise de Preço")
    
    if brent and 'history' in brent:
        # Prepare Data
        history_df = pd.DataFrame(brent['history'])
        history_df['Date'] = pd.to_datetime(history_df['Date'])
        
        # Time Range Selector
        # Time Range Selector
        range_options = ["1D", "5D", "1M", "6M", "YTD", "1Y"]
        selected_range = st.radio("Período", range_options, index=5, horizontal=True, label_visibility="collapsed")

        # Filter Logic
        end_date = history_df['Date'].max()
        start_date = end_date
        
        if selected_range == "1D":
            # 1D: Show the entire last available day
            last_day = end_date.date()
            filtered_df = history_df[history_df['Date'].dt.date == last_day]
        else:
            if selected_range == "5D":
                start_date = end_date - pd.Timedelta(days=5)
            elif selected_range == "1M":
                start_date = end_date - pd.Timedelta(days=30)
            elif selected_range == "6M":
                start_date = end_date - pd.Timedelta(days=180)
            elif selected_range == "YTD":
                start_date = pd.Timestamp(year=end_date.year, month=1, day=1)
            else: # 1Y
                start_date = end_date - pd.Timedelta(days=365)

            filtered_df = history_df[history_df['Date'] >= start_date]

        # Chart
        fig = go.Figure()
        
        # Area Chart with Gradient (Simulated with Fill)
        fig.add_trace(go.Scatter(
            x=filtered_df['Date'], 
            y=filtered_df['Close'], 
            mode='lines', 
            fill='tozeroy',
            line=dict(color='#00E396', width=2),
            fillcolor='rgba(0, 227, 150, 0.1)', # Low opacity green
            name='Brent Price'
        ))

        # Add Average Line
        avg_price = filtered_df['Close'].mean()
        fig.add_hline(y=avg_price, line_dash="dot", line_color="red", opacity=0.7, line_width=1, annotation_text=f"Média: ${avg_price:.2f}", annotation_position="top left")

        # Vertical Separation Lines
        v_dates = []
        if selected_range == "1D":
            v_dates = pd.date_range(start=filtered_df['Date'].min(), end=filtered_df['Date'].max(), freq="h")
        elif selected_range == "5D":
            v_dates = pd.date_range(start=filtered_df['Date'].min(), end=filtered_df['Date'].max(), freq="D") # Daily
        elif selected_range == "1M":
            v_dates = pd.date_range(start=filtered_df['Date'].min(), end=filtered_df['Date'].max(), freq="D") # Daily
        elif selected_range == "6M":
            v_dates = pd.date_range(start=filtered_df['Date'].min(), end=filtered_df['Date'].max(), freq="MS") # Monthly Start
        elif selected_range in ["YTD", "1Y"]:
            v_dates = pd.date_range(start=filtered_df['Date'].min(), end=filtered_df['Date'].max(), freq="MS") # Monthly Start

        for date in v_dates:
            fig.add_vline(x=date, line_width=1, line_dash="dot", line_color="gray", opacity=0.2)

        # Calculate dynamic range with padding
        y_min = filtered_df['Close'].min()
        y_max = filtered_df['Close'].max()
        y_range = [y_min - 10, y_max + 10] # Add 10 units of padding top and bottom as requested

        # Layout Updates to Match "Mountain" Style
        fig.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=False, 
                showline=False,
                tickfont=dict(color='#8b949e'),
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#21262d', # Subtle grid
                showline=False,
                tickfont=dict(color='#8b949e'),
                side='left', # Move price axis to left for better readability
                range=y_range,
                title="Brent Crude (USD)"
            ),
            yaxis2=dict(
                showgrid=False,
                showline=False,
                tickfont=dict(color='#8b949e'),
                side='right', 
                range=y_range,
                overlaying='y'
            ),
            hovermode="x unified",
            showlegend=False
        )
        
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        
        # Source and Metadata
        st.caption(f"Fonte: Yahoo Finance (Ticker: BZ=F) | Última atualização: {data.get('updated_at', 'N/A')}")

    else:
        st.info("Histórico de preços indisponível para o gráfico.")

    st.markdown("---")

    # 2. News Feed Section
    st.subheader("📰 Últimas Notícias")
    
    news_items = data.get('news', [])
    
    # Grid layout for news cards
    cols = st.columns(2) # 2 columns for news cards

    for index, item in enumerate(news_items):
        with cols[index % 2]:
            with st.container():
                st.markdown(f"""
                <div class="news-item">
                    <div class="news-title"><a href="{item['link']}" target="_blank">{item['title']}</a></div>
                    <div class="news-meta">{item['source']} • {item['published']}</div>
                    <div style="margin-top: 10px; font-size: 0.9em; color: #ccc;">{item['summary'][:150]}...</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Summarize Button
                if st.button(f"✨ Resumir c/ IA", key=f"btn_{index}"):
                    with st.spinner("Gerando resumo..."):
                        # In a real app, calling OpenAI here directly. 
                        # Ideally, this should update the JSON in background.
                        # For MVP, on-the-fly call:
                        summary = summarize_text(item['summary'] + " " + item['title'])
                        st.markdown(f"""
                        <div style="background-color: #0d3b66; color: white; padding: 15px; border-radius: 8px; border: 1px solid #1c6ea4; margin-top: 10px;">
                            <strong>Resumo:</strong> {summary}
                        </div>
                        """, unsafe_allow_html=True)

    st.markdown("---")
    st.write(f"*Última atualização: {data.get('updated_at', 'N/A')}*")
