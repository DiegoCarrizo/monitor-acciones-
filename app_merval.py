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

tab1, tab2, tab3 = st.tabs(["📈 Acciones", "🍞 Inflación 2026", "🏦 Bonos & Tasas"])

# --- DATOS PROYECTADOS ---
meses_2026 = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
inf_proyectada = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]

# --- PESTAÑA 1: ACCIONES ---
with tab1:
    st.subheader("📋 Resumen de Mercado")
    TICKERS = ["GGAL.BA", "YPFD.BA", "PAMP.BA", "ALUA.BA", "VISTA.BA", "AAPL", "NVDA"]
    res_acc = []
    for t in TICKERS:
        try:
            s = yf.Ticker(t)
            h = s.history(period="1y")
            if not h.empty:
                c = h['Close'].iloc[-1]
                m = h['Close'].rolling(200).mean().iloc[-1]
                res_acc.append({"Ticker": t, "Precio": round(c, 2), "Tendencia": "🟢 ALCISTA" if c > m else "🔴 BAJISTA"})
        except: pass
    if res_acc:
        st.table(pd.DataFrame(res_acc))

# --- PESTAÑA 2: INFLACIÓN ---
with tab2:
    st.header("📊 Proyección de Inflación 2026")
    df_inf = pd.DataFrame({"Mes": meses_2026, "IPC Mensual %": inf_proyectada})
    total_anual = (np.prod([(1 + x/100) for x in inf_proyectada]) - 1) * 100
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.table(df_inf)
        st.metric("Acumulada Anual", f"{total_anual:.1f}%")
    with c2:
        fig_inf = go.Figure()
        fig_inf.add_trace(go.Scatter(x=meses_2026, y=inf_proyectada, mode='lines+markers+text', 
                                     text=[f"{x}%" for x in inf_proyectada], textposition="top center"))
        fig_inf.update_layout(template="plotly_white", yaxis_title="% Mensual")
        st.plotly_chart(fig_inf, use_container_width=True)

# --- PESTAÑA 3: BONOS ---
with tab3:
    st.header("💸 Bonos Tasa Fija vs Plazo Fijo")
    tasa_pf = 3.2 
    
    d_bonos = {
        "Ticker": ["TO26", "S31M6", "S30J6", "S29A6"],
        "Precio": [68.20, 99.10, 96.50, 93.80],
        "Dias": [365, 90, 180, 270],
        "TEM": [4.2, 3.8, 3.9, 4.1]
    }
    df_b = pd.DataFrame(d_bonos)
    df_b["TEA %"] = round(((1 + df_b["TEM"]/100)**12 - 1) * 100, 2)
    
    m1, m2 = st.columns(2)
    m1.metric("TEM Plazo Fijo BNA", f"{tasa_pf}%")
    m2.metric("TEM Promedio Bonos", f"{df_b['TEM'].mean():.2f}%")
    st.table(df_b)

    st.subheader("📈 Curva de Rendimiento (TEA)")
    # Línea de tendencia
    z = np.polyfit(df_b["Dias"], df_b["TEA %"], 1)
    p = np.poly1d(z)
    
    fig_c = go.Figure()
    fig_c.add_trace(go.Scatter(x=df_b["Dias"], y=df_b["TEA %"], mode='markers+text', 
                               text=df_b["Ticker"], textposition="top center", 
                               marker=dict(size=15, color='blue')))
    fig_c.add_trace(go.Scatter(x=df_b["Dias"], y=p(df_b["Dias"]), name="Tendencia", 
                               line=dict(color='red', dash='dot')))
    fig_c.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="TEA %")
    st.plotly_chart(fig_c, use_container_width=True)
