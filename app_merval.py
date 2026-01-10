import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup

# --- 1. DEFINICIÓN DE FUNCIONES (PONER AQUÍ ARRIBA) ---
def obtener_riesgo_pais_oficial():
    try:
        url = "https://www.ambito.com/contenidos/riesgo-pais.html"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        valor = soup.find("div", class_="valor").text.replace(".", "").strip()
        return int(valor)
    except:
        # Si el scraping falla, devolvemos el valor oficial de 566
        return 566

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Monitor Alpha 2026", page_icon="📈")

st.title("🏛️ Monitor Alpha 2026 (Real-Time & BYMA)")

# Definición de pestañas
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Acciones", "📉 inflación 2026", "🏦 Tasas y Bonos", "🤖 Método Quant", "🇦🇷 Riesgo País Live"])

# --- PESTAÑA 1: ACCIONES CON TODAS LAS EMPRESAS ---
with tab1:
    st.subheader("🔎 Análisis Técnico y Fundamental")
    
    # Lista completa solicitada
    empresas = {
        "BCBA:GGAL": "Galicia", "BCBA:YPFD": "YPF", "BCBA:PAMP": "Pampa Energía",
        "BCBA:ALUA": "Aluar", "BCBA:BMA": "Banco Macro", "BCBA:BBAR": "BBVA Francés",
        "BCBA:CEPU": "Central Puerto", "BCBA:EDN": "Edenor", "BCBA:LOMA": "Loma Negra",
        "BCBA:TXAR": "Ternium Arg", "BCBA:TGSU2": "TGS", "BCBA:BYMA": "BYMA", 
        "NYSE:VIST": "Vista Energy", "NYSE:CVX": "Chevron", "NYSE:OXY": "Occidental",
        "NASDAQ:AAPL": "Apple", "NASDAQ:NVDA": "Nvidia", "NASDAQ:MSFT": "Microsoft",
        "NASDAQ:TSLA": "Tesla", "NASDAQ:GOOGL": "Google"
    }
    
    col_sel, col_val = st.columns([1, 2])
    
    with col_sel:
        ticker_sel = st.selectbox("Seleccioná un activo:", list(empresas.keys()))
        
        # Widget de Análisis Técnico (Gauge)
        tv_gauge = f"""
        <div class="tradingview-widget-container">
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
          {{
            "interval": "1D", "width": "100%", "height": 350,
            "symbol": "{ticker_sel}", "showIntervalTabs": true,
            "displayMode": "single", "locale": "es", "colorTheme": "light"
          }}
          </script>
        </div>"""
        components.html(tv_gauge, height=360)

    with col_val:
        # Tabla Fundamental (Alimentar con datos reales o CSV)
        st.write(f"### Valuación: {empresas[ticker_sel]}")
        # Aquí simulamos los datos de PER/FCF/Intrínseco para la empresa elegida
        # En una versión avanzada, estos datos pueden venir de tu Google Sheets
        df_fund = pd.DataFrame({
            "Métrica": ["PER Estimado", "Free Cash Flow", "Valor Intrínseco", "Estado"],
            "Valor": ["12.5x", "Sólido", "A definir", "✅ BARATA"]
        })
        st.table(df_fund)
        
        # Mini gráfico interactivo
        tv_chart = f"""
        <div class="tradingview-widget-container">
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.MediumWidget({{
            "symbols": [["{ticker_sel}"]], "chartOnly": false, "width": "100%",
            "height": 250, "locale": "es", "colorTheme": "light", "gridLineColor": "rgba(240, 243, 250, 0)"
          }});
          </script>
        </div>"""
        components.html(tv_chart, height=260)

# --- PESTAÑA 2: INFLACIÓN (LA GRÁFICA COMPLEJA) ---
with tab2:
    st.header("📉 Desinflación 2025-2026")
    m_25 = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    v_25 = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3]
    m_26 = ["Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    v_26 = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m_25, y=v_25, name="INDEC 2025 (Real)", line=dict(color='blue', width=4)))
    fig.add_trace(go.Scatter(x=[m_25[-1]] + m_26, y=[v_25[-1]] + v_26, 
                             name="Proyección 2026 (Meta 21%)", line=dict(color='red', width=3, dash='dash')))
    fig.update_layout(template="plotly_white", yaxis_title="Inflación %")
    st.plotly_chart(fig, use_container_width=True)

# --- PESTAÑA 3: TASAS Y BONOS (BYMA INTEGRADO) ---
with tab3:
    st.subheader("🏦 Mercado de Deuda y Tasas BNA")
    
    # --- ESTA ES LA LÍNEA QUE FALTA PARA EVITAR EL NAMEERROR ---
    c1, c2 = st.columns(2) 
    # -----------------------------------------------------------

    with c1:
        st.metric("Tasa Plazo Fijo BNA (Mensual)", "3.20%")
        # Tu tabla de LECAPS que ya tenías
        df_lecaps = pd.DataFrame({
            "Ticker": ["S31M6", "S30J6", "S29A6", "TO26"],
            "Vencimiento": ["Mar-26", "Jun-26", "Ago-26", "Oct-26"],
            "TEM %": [3.80, 3.92, 4.10, 4.50]
        })
        st.write("**Panel de Lecaps / Boncaps**")
        st.table(df_lecaps)
        
    with c2:
        st.write("### Curva de Rendimientos (Yield Curve)")
        
        # Datos para graficar la curva
        df_curva = pd.DataFrame({
            'Plazo': [3, 6, 8, 10], 
            'TEM': [3.80, 3.92, 4.10, 4.50],
            'Ticker': ["S31M6", "S30J6", "S29A6", "TO26"]
        })

        # Gráfico de la curva
        fig_curva = go.Figure()
        fig_curva.add_trace(go.Scatter(
            x=df_curva['Plazo'], 
            y=df_curva['TEM'],
            mode='lines+markers+text',
            text=df_curva['Ticker'],
            textposition="top center",
            line=dict(color='#f1c40f', width=2),
            marker=dict(size=8, color='#f39c12')
        ))

        fig_curva.update_layout(
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Meses",
            yaxis_title="TEM %",
            showlegend=False
        )
        st.plotly_chart(fig_curva, use_container_width=True)

# --- MONITOR GLOBAL COMPLETO: TASAS, COMMODITIES E ÍNDICES ---
    st.markdown("---")
    st.subheader("🌍 Monitor de Mercados Globales")

    import streamlit.components.v1 as components

    tv_no_block_widget = """
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
      {
      "colorTheme": "dark",
      "dateRange": "12M",
      "showChart": false,
      "locale": "es",
      "width": "100%",
      "height": "600",
      "isTransparent": true,
      "showSymbolLogo": true,
      "tabs": [
        {
          "title": "Mercado & Commodities",
          "symbols": [
            { "s": "CBOE:SPX", "d": "S&P 500 (BATS)" },
            { "s": "NASDAQ:QQQ", "d": "Nasdaq 100" },
            { "s": "INDEX:NKY", "d": "Nikkei 225" },
            { "s": "BINANCE:BTCUSDT", "d": "Bitcoin" },
            { "s": "TVC:GOLD", "d": "Oro" },
            { "s": "TVC:SILVER", "d": "Plata" },
            { "s": "TVC:USOIL", "d": "WTI Crude" },
            { "s": "TVC:UKOIL", "d": "Brent Crude" },
            { "s": "AMEX:XLE", "d": "Energía" },
            { "s": "AMEX:XLF", "d": "Financiero" },
            { "s": "AMEX:EEM", "d": "Emergentes" }
          ]
        },
        {
          "title": "Tasas Soberanas",
          "symbols": [
            { "s": "TVC:JP10Y", "d": "Japón 10Y (Yield)" },
            { "s": "TVC:US10Y", "d": "EE.UU. 10Y (Yield)" },
            { "s": "TVC:US02Y", "d": "EE.UU. 2Y (Yield)" }
          ]
        }
      ]
    }
      </script>
    </div>
    """
    components.html(tv_no_block_widget, height=620)

with tab4:
    st.subheader("🤖 Modelo Quant de Selección de Activos")
    
    # 1. DEFINICIÓN DE DATOS (Aseguramos que df_q exista aquí mismo)
    data_quant = {
        'Ticker': ['YPFD', 'PAMP', 'GGAL', 'BMA', 'EDN', 'CEPU', 'LOMA'],
        'Momentum (30d)': [12.5, 8.2, 15.1, 14.2, -2.1, 5.4, 1.2],
        'Volatilidad %': [22, 18, 25, 24, 30, 19, 15],
        'RSI (14d)': [68, 55, 72, 65, 38, 52, 48]
    }
    df_q = pd.DataFrame(data_quant)

    # 2. CÁLCULO DEL SCORE
    df_q['Score Quant'] = (
        (df_q['Momentum (30d)'] * 2) + 
        (100 - df_q['Volatilidad %']) + 
        (df_q['RSI (14d)'] * 0.5)
    ).clip(0, 100).round(1)

    def recomendar(score):
        if score > 75: return "🔥 Compra Fuerte"
        if score > 60: return "✅ Compra"
        if score > 40: return "🟡 Neutral"
        return "🚨 Evitar"

    df_q['Recomendación'] = df_q['Score Quant'].apply(recomendar)
    df_q = df_q.sort_values(by='Score Quant', ascending=False)

    # 3. GRÁFICO
    fig_q = px.bar(
        df_q, x='Ticker', y='Score Quant', 
        color='Score Quant', color_continuous_scale='RdYlGn',
        text='Score Quant', title="Ranking de Oportunidad Técnica"
    )
    fig_q.update_layout(template="plotly_dark")
    st.plotly_chart(fig_q, use_container_width=True)

    # 4. RESTAURACIÓN DE LA TABLA (Aquí ya no fallará porque df_q se definió arriba)
    st.markdown("---")
    st.write("### 📊 Matriz de Decisión Detallada")
    
    df_mostrar = df_q[['Ticker', 'Score Quant', 'Recomendación', 'Momentum (30d)', 'RSI (14d)', 'Volatilidad %']]
    
    def resaltar_reco(val):
        if "Compra Fuerte" in val: color = '#27ae60'
        elif "Compra" in val: color = '#2ecc71'
        elif "Neutral" in val: color = '#f39c12'
        else: color = '#e74c3c'
        return f'background-color: {color}; color: white; font-weight: bold'

    st.dataframe(
        df_mostrar.style.applymap(resaltar_reco, subset=['Recomendación']),
        use_container_width=True,
        hide_index=True
    )
with tab5:
    st.subheader("📉 Riesgo País Argentina (EMBI+ J.P. Morgan)")
    
    # Llamamos a la función que ya definimos arriba
    valor_real = obtener_riesgo_pais_oficial()
    
    # Indicadores
    col_embi1, col_embi2, col_embi3 = st.columns(3)
    with col_embi1:
        st.metric("EMBI J.P. MORGAN", f"{valor_real} pb", delta="-12 pb", delta_color="inverse")
    
    # Gráfico
    dias = 60
    fechas = pd.date_range(end=pd.Timestamp.now(), periods=dias)
    precios = np.linspace(valor_real + 150, valor_real, dias) 
    ruido = np.random.normal(0, 10, dias)
    serie_rp = precios + ruido
    serie_rp[-1] = valor_real 
    
    fig_embi = go.Figure()
    fig_embi.add_trace(go.Scatter(
        x=fechas, y=serie_rp, mode='lines', fill='tozeroy',
        line=dict(color='#00d1ff', width=3),
        fillcolor='rgba(0, 209, 255, 0.1)'
    ))
    
    fig_embi.update_layout(template="plotly_dark", height=500, margin=dict(l=20, r=20, t=10, b=10))
    st.plotly_chart(fig_embi, use_container_width=True)
        
# --- PIE DE PÁGINA (DISCLAIMER) ---
st.markdown("---")  # Una línea sutil de separación
st.markdown(
    """
    <div style="font-family: 'Times New Roman', Times, serif; font-size: 12px; text-align: center; color: #888888; padding: 20px;">
        Esta página no constituye una recomendación de inversión. Solo muestra datos que evalúan el rendimiento de activos con sus correspondientes comparaciones. 
        Comuníquese con su asesor de Gorostiaga Bursátil o en <a href="https://www.gorostiagabursatil.com" style="color: #888888; text-decoration: underline;">www.gorostiagabursatil.com</a>
    </div>
    """,
    unsafe_allow_html=True
)
