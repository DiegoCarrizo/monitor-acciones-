import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Monitor AR 2026", page_icon="🇦🇷")

st.title("🏛️ Monitor Financiero Argentina 2026")
st.markdown("**Escenario: Inflación Objetivo Anual 21%**")

tab1, tab2, tab3 = st.tabs(["📈 Acciones & CEDEARs", "🍞 Inflación 2026", "🏦 Bonos & Tasas"])

# --- PESTAÑA 1: ACCIONES ---
with tab1:
    st.subheader("📊 Panel Líder Argentina & Gigantes de EEUU")
    
    panel_lider = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "METR.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA"]
    usa_petro = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "VISTA", "CVX", "OXY"]
    TICKERS_TOTAL = panel_lider + usa_petro
    
    @st.cache_data(ttl=3600)
    def obtener_datos_mercado(lista):
        data = []
        for t in lista:
            try:
                stock = yf.Ticker(t)
                hist = stock.history(period="1.5y")
                if not hist.empty:
                    ult = hist['Close'].iloc[-1]
                    sma = hist['Close'].rolling(200).mean().iloc[-1]
                    label = t.replace(".BA", " (AR)") if ".BA" in t else t + " (US)"
                    data.append({"Activo": label, "Precio": round(ult, 2), "Media 200d": round(sma, 2), "Tendencia": "🟢 ALCISTA" if ult > sma else "🔴 BAJISTA"})
            except: continue
        return pd.DataFrame(data)

    df_mercado = obtener_datos_mercado(TICKERS_TOTAL)
    
    if not df_mercado.empty:
        busqueda = st.text_input("🔍 Buscar acción (ej: GGAL, VISTA, NVDA):").upper()
        df_ver = df_mercado[df_mercado['Activo'].str.contains(busqueda)] if busqueda else df_mercado
        st.dataframe(df_ver, use_container_width=True, hide_index=True)

# --- PESTAÑA 2: INFLACIÓN ---
with tab2:
    st.header("📊 Monitor de Inflación: INDEC vs REM")
    meses_25 = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    meses_26 = ["Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    
    val_indec = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3] + [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]
    val_rem = [21.5, 15.0, 12.5, 10.0, 5.5, 5.2, 4.8, 4.5, 4.0, 3.2, 3.0, 2.8] + [x + 0.5 for x in [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]]
    
    fig_m = go.Figure()
    fig_m.add_trace(go.Scatter(x=meses_25 + meses_26, y=val_indec, name="INDEC / Proy.", line=dict(color='#2ecc71', width=4)))
    fig_m.add_trace(go.Scatter(x=meses_25 + meses_26, y=val_rem, name="REM BCRA", line=dict(color='#e74c3c', dash='dash')))
    fig_m.add_vrect(x0="Ene-25", x1="Dic-25", fillcolor="gray", opacity=0.1, layer="below", line_width=0, annotation_text="HISTÓRICO 2025")
    fig_m.update_layout(template="plotly_white", hovermode="x unified", yaxis_title="Inflación Mensual %")
    st.plotly_chart(fig_m, use_container_width=True)

# --- PESTAÑA 3: BONOS ---
with tab3:
    st.header("💸 Bonos Tasa Fija vs Plazo Fijo")
    df_b = pd.DataFrame({
        "Ticker": ["TO26", "S31M6", "S30J6", "S29A6"],
        "Precio": [68.20, 99.10, 96.50, 93.80],
        "Dias": [365, 90, 180, 270],
        "TEM": [4.2, 3.8, 3.9, 4.1]
    })
    df_b["TEA %"] = round(((1 + df_b["TEM"]/100)**12 - 1) * 100, 2)
    st.table(df_b)
    
    z = np.polyfit(df_b["Dias"], df_b["TEA %"], 1)
    p = np.poly1d(z)
    fig_c = go.Figure()
    fig_c.add_trace(go.Scatter(x=df_b["Dias"], y=df_b["TEA %"], mode='markers+text', text=df_b["Ticker"], textposition="top center", marker=dict(size=15, color='blue')))
    fig_c.add_trace(go.Scatter(x=df_b["Dias"], y=p(df_b["Dias"]), name="Tendencia", line=dict(color='red', dash='dot')))
    fig_c.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="TEA %")
    st.plotly_chart(fig_c, use_container_width=True)

