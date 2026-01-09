import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Monitor PRO 2026", page_icon="📈")

st.title("🏛️ Monitor Alpha 2026 (Powered by TradingView)")

tab1, tab2, tab3 = st.tabs(["📊 Análisis en Vivo", "🍞 Inflación 2026", "🏦 Tasas & Bonos"])

with tab1:
    col_selector, col_gauge = st.columns([1, 1])
    
    with col_selector:
        ticker_tv = st.selectbox("Seleccioná un Activo para ver en Vivo:", 
                                ["BCBA:GGAL", "BCBA:YPFD", "BCBA:PAMP", "NASDAQ:AAPL", "NASDAQ:NVDA", "NYSE:VISTA"])
    
    # --- WIDGET DE TRADINGVIEW (ANALISIS TECNICO) ---
    with col_gauge:
        # Este componente embebe el reloj de TradingView
        tv_gauge_html = f"""
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
          {{
          "interval": "1D",
          "width": "100%",
          "isTransparent": false,
          "height": 380,
          "symbol": "{ticker_tv}",
          "showIntervalTabs": true,
          "displayMode": "single",
          "locale": "es",
          "colorTheme": "light"
        }}
          </script>
        </div>
        """
        components.html(tv_gauge_html, height=400)

    st.markdown("---")
    
    # --- TABLA DE FUNDAMENTALES (CARGA DESDE TU CSV/GOOGLE SHEETS) ---
    st.subheader("📋 Datos Fundamentales (PER, FCF, Intrínseco)")
    
    # Datos que podés alimentar desde tu Google Sheets
    data = {
        "Ticker": ["GGAL", "YPFD", "PAMP", "AAPL", "NVDA", "VISTA"],
        "PER": [6.2, 5.8, 8.1, 28.4, 35.2, 7.5],
        "FCF (M)": ["120M", "850M", "45M", "95B", "27B", "310M"],
        "Valor Intrínseco": [6200, 38000, 3100, 170.0, 750.0, 65.0],
        "Estado": ["✅ BARATA", "✅ BARATA", "✅ BARATA", "❌ CARA", "✅ BARATA", "✅ BARATA"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df.style.applymap(lambda x: 'color: green' if x == "✅ BARATA" else 'color: red', subset=['Estado']), 
                 use_container_width=True, hide_index=True)

# --- PESTAÑA INFLACIÓN (TRANSICIÓN 2025-2026) ---
with tab2:
    st.header("📉 Trayectoria de Inflación 2025-2026")
    m_25 = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    v_25 = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3]
    m_26 = ["Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    v_26 = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m_25, y=v_25, name="INDEC (Sólida)", line=dict(color='#1f77b4', width=4)))
    fig.add_trace(go.Scatter(x=[m_25[-1]] + m_26, y=[v_25[-1]] + v_26, 
                             name="Proy. 2026 (Punteada)", line=dict(color='#d62728', width=3, dash='dash')))
    fig.update_layout(template="plotly_white", yaxis_title="Inflación %")
    st.plotly_chart(fig, use_container_width=True)

# --- PESTAÑA TASAS ---
with tab3:
    st.metric("Tasa Plazo Fijo BNA (Mensual)", "3.20%")
    st.table(pd.DataFrame({
        "Ticker": ["S31M6", "S30J6", "S29A6", "TO26"],
        "TEM %": [3.80, 3.92, 4.10, 4.50],
        "TEA %": [56.4, 58.7, 61.9, 69.6]
    }))
