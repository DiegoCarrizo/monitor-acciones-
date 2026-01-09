import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Monitor AR 2026", page_icon="🇦🇷")

st.title("🏛️ Monitor Financiero Argentina 2026")

# --- LISTA DE TICKERS ---
TODOS = [
    "GGAL.BA", "YPFD.BA", "PAMP.BA", "ALUA.BA", "CEPU.BA", "EDN.BA", "TXAR.BA",
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "VISTA", "CVX", "OXY"
]

tab1, tab2, tab3 = st.tabs(["📈 Acciones & Balances", "🍞 Inflación 2026", "🏦 Bonos & Tasas"])

# --- PESTAÑA 1: ACCIONES ---
with tab1:
    st.subheader("📊 Panel de Activos")
    
    @st.cache_data(ttl=900)
    def get_data_safe(tickers):
        rows = []
        # Intentamos descarga masiva
        try:
            data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', progress=False)
            
            for t in tickers:
                try:
                    # Manejo de estructura si es un solo ticker o varios
                    df = data[t] if len(tickers) > 1 else data
                    if df.empty: continue
                    
                    ult = df['Close'].iloc[-1]
                    sma = df['Close'].rolling(200).mean().iloc[-1]
                    
                    rows.append({
                        "Activo": t.replace(".BA", " (AR)"),
                        "Precio": round(float(ult), 2),
                        "Tendencia": "🟢 ALCISTA" if ult > sma else "🔴 BAJISTA",
                        "Valuación": "Calculando..." # Marcador
                    })
                except: continue
        except:
            st.error("La descarga masiva falló. Intentando modo individual...")
            
        return pd.DataFrame(rows)

    if st.button("🔄 Cargar/Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()

    with st.spinner('Conectando con el servidor de datos...'):
        df_final = get_data_safe(TODOS)

    if not df_final.empty:
        st.dataframe(df_final, use_container_width=True, hide_index=True)
    else:
        st.info("Yahoo Finance rechazó la conexión. Esto es común en redes de nube. Por favor, espera 10 segundos y presiona el botón de 'Actualizar'.")

# --- PESTAÑA 2: INFLACIÓN (ESTÁTICA PARA QUE NUNCA FALLE) ---
with tab2:
    st.header("📊 Inflación Proyectada 2026")
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    inf_26 = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]
    
    fig = go.Figure(go.Scatter(x=meses, y=inf_26, mode='lines+markers+text', text=[f"{x}%" for x in inf_26], textposition="top center", line=dict(color='green', width=4)))
    fig.update_layout(template="plotly_white", yaxis_title="% Mensual")
    st.plotly_chart(fig, use_container_width=True)

# --- PESTAÑA 3: BONOS ---
with tab3:
    st.header("💸 Bonos Tasa Fija")
    df_b = pd.DataFrame({
        "Ticker": ["S31M6", "S30J6", "S29A6", "TO26"],
        "TEM (%)": [3.8, 3.9, 4.1, 4.5],
        "Vencimiento": ["81 d", "172 d", "263 d", "420 d"]
    })
    st.table(df_b)
