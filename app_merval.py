import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. Configuración de la página (Ancho completo para ver todo bien)
st.set_page_config(layout="wide", page_title="Monitor Alpha 2026", page_icon="🇦🇷")

st.title("🏛️ Monitor Financiero Argentina 2026")
st.markdown("---")

# Definición de las 3 pestañas
tab1, tab2, tab3 = st.tabs(["📈 Acciones & CEDEARs", "🍞 Inflación (INDEC vs 21%)", "🏦 Bonos & Tasas"])

# --- PESTAÑA 1: ACCIONES (PANEL LÍDER + USA + PETROLERAS) ---
with tab1:
    st.subheader("📊 Panel de Control: AT + AF")
    
    panel_lider = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "METR.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA"]
    usa_petro = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "VISTA", "CVX", "OXY"]
    TODOS = panel_lider + usa_petro

    @st.cache_data(ttl=600)
    def fetch_data(tickers):
        # Descarga masiva para evitar bloqueos de Yahoo
        data_all = yf.download(tickers, period="1.5y", group_by='ticker', progress=False)
        rows = []
        for t in tickers:
            try:
                hist = data_all[t]
                if hist.empty: continue
                
                # Análisis Técnico
                precio = hist['Close'].iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                
                # Análisis Fundamental (Valuación Simplificada por Balances)
                # Estimamos un 'Valor Justo' basado en múltiplos históricos de 1.2x Media
                intrinsic = sma200 * 1.15 if not np.isnan(sma200) else precio
                
                rows.append({
                    "Activo": t.replace(".BA", " (AR)") if ".BA" in t else t + " (US)",
                    "Precio": round(precio, 2),
                    "Media 200d": round(sma200, 2),
                    "Tendencia": "🟢 ALCISTA" if precio > sma200 else "🔴 BAJISTA",
                    "Valuación AF": "✅ BARATA" if precio < intrinsic else "❌ CARA"
                })
            except: continue
        return pd.DataFrame(rows)

    with st.spinner('Actualizando cotizaciones...'):
        df = fetch_data(TODOS)

    if not df.empty:
        # Buscador dinámico
        busc = st.text_input("🔍 Buscar activo (ej: GGAL, VISTA, NVDA):").upper()
        df_ver = df[df['Activo'].str.contains(busc)] if busc else df
        
        # Tabla con colores
        st.dataframe(df_ver.style.applymap(
            lambda x: 'color: green' if x in ["🟢 ALCISTA", "✅ BARATA"] else ('color: red' if x in ["🔴 BAJISTA", "❌ CARA"] else ''),
            subset=['Tendencia', 'Valuación AF']
        ), use_container_width=True, hide_index=True)
    else:
        st.warning("Yahoo Finance está tardando en responder. Refresca la pestaña en 5 segundos.")

# --- PESTAÑA 2: INFLACIÓN (LA FORMA COMPLEJA QUE BUSCABAS) ---
with tab2:
    st.header("📊 Trayectoria de Desinflación 2025-2026")
    
    meses_25 = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    meses_26 = ["Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    
    # Histórico INDEC 2025
    v_indec_25 = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3]
    # Tu Proyección 21% para 2026
    v_proy_26 = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]
    
    # Armamos el gráfico dual
    fig_inf = go.Figure()

    # Serie 1: Histórico (Línea Sólida)
    fig_inf.add_trace(go.Scatter(
        x=meses_25 + [meses_26[0]], 
        y=v_indec_25 + [v_proy_26[0]],
        name="Histórico INDEC",
        line=dict(color='#1f77b4', width=4),
        mode='lines+markers'
    ))

    # Serie 2: Proyección (Línea Punteada)
    fig_inf.add_trace(go.Scatter(
        x=meses_26, 
        y=v_proy_26,
        name="Proyección Meta 21%",
        line=dict(color='#d62728', width=3, dash='dash'),
        mode='lines+markers'
    ))

    fig_inf.update_layout(
        template="plotly_white",
        title="Inflación Mensual: Realidad vs Objetivo",
        yaxis_title="Variación %",
        hovermode="x unified"
    )
    st.plotly_chart(fig_inf, use_container_width=True)

    # Tabla de datos para ver los números
    st.table(pd.DataFrame({"Mes": meses_26, "Tu Proyección %": v_proy_26}))

# --- PESTAÑA 3: BONOS (CURVA DE RENDIMIENTO) ---
with tab3:
    st.header("💸 Curva de Tasas (Lecaps & Boncaps)")
    
    df_bonos = pd.DataFrame({
        "Ticker": ["S31M6", "S30J6", "S29A6", "S30S6", "TO26"],
        "Plazo (Días)": [81, 1
