import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Monitor AR 2026", page_icon="🇦🇷")

st.title("🏛️ Monitor Financiero Argentina 2026")

# --- LISTA DE TICKERS ---
PANEL_LIDER = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "METR.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA"]
USA_PETRO = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "VISTA", "CVX", "OXY"]
TODOS = PANEL_LIDER + USA_PETRO

tab1, tab2, tab3 = st.tabs(["📈 Acciones & Balances", "🍞 Inflación 2026", "🏦 Bonos & Tasas"])

# --- PESTAÑA 1: ACCIONES ---
with tab1:
    st.subheader("📊 Panel Líder & USA")
    
    @st.cache_data(ttl=600)
    def get_simple_data(tickers):
        # Descarga masiva en una sola petición (mucho más rápido y no se bloquea)
        df_prices = yf.download(tickers, period="1.5y", group_by='ticker', progress=False)
        rows = []
        for t in tickers:
            try:
                hist = df_prices[t]
                if hist.empty: continue
                
                ult = hist['Close'].iloc[-1]
                sma = hist['Close'].rolling(200).mean().iloc[-1]
                
                # Para la valuación, usamos datos estáticos o simplificados para evitar bloqueos
                # En un entorno real, aquí llamaríamos a una base de datos propia
                label = t.replace(".BA", " (AR)") if ".BA" in t else t + " (US)"
                
                rows.append({
                    "Activo": label,
                    "Precio": round(ult, 2),
                    "Tendencia (AT)": "ALCISTA" if ult > sma else "BAJISTA",
                    "Valuación (AF)": "Análisis en Log...", # Marcador de posición
                    "Valor Est.": "-"
                })
            except: continue
        return pd.DataFrame(rows)

    with st.spinner('Descargando cotizaciones...'):
        df_final = get_simple_data(TODOS)

    if not df_final.empty:
        # Buscador
        busc = st.text_input("🔍 Buscar activo:").upper()
        df_show = df_final[df_final['Activo'].str.contains(busc)] if busc else df_final
        
        # Estilos
        def style_rows(val):
            if val == "ALCISTA": return 'background-color: #d4edda'
            if val == "BAJISTA": return 'background-color: #f8d7da'
            return ''

        st.dataframe(df_show.style.applymap(style_rows, subset=['Tendencia (AT)']), use_container_width=True)
    else:
        st.error("Error de conexión con el proveedor de datos. Por favor, refresca la página.")

# --- PESTAÑA 2: INFLACIÓN ---
with tab2:
    st.header("📊 Monitor de Inflación")
    m = [f"{i}-25" for i in range(1,13)] + [f"{i}-26" for i in range(1,13)]
    v_i = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3] + [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]
    fig = go.Figure(go.Scatter(x=m, y=v_i, name="INDEC", line=dict(color='green', width=3)))
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# --- PESTAÑA 3: BONOS ---
with tab3:
    st.header("💸 Bonos & Curva")
    df_b = pd.DataFrame({
        "Ticker": ["S31M6", "S30J6", "S29A6", "S30S6", "TO26"],
        "Precio": [99.2, 96.5, 93.8, 91.2, 68.2],
        "Dias": [81, 172, 263, 354, 420],
        "TEM (%)": [3.8, 3.9, 4.1, 4.2, 4.5]
    })
    df_b["TEA (%)"] = round(((1 + df_b["TEM (%)"]/100)**12 - 1) * 100, 2)
    st.table(df_b)
    
    # Gráfico de puntos
    fig_c = go.Figure(go.Scatter(x=df_b["Dias"], y=df_b["TEA (%)"], mode='markers+text', text=df_b["Ticker"], textposition="top center"))
    fig_c.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="TEA %")
    st.plotly_chart(fig_c, use_container_width=True)
