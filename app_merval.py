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

# --- PESTAÑA 2: INFLACIÓN HISTÓRICA Y PROYECTADA ---
with tab2:
    st.header("📊 Monitor de Inflación: Histórico vs Proyectado 21%")
    
    # 1. DATOS HISTÓRICOS (Últimos 12 meses - 2025)
    meses_hist = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    inf_hist = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3] # Datos ilustrativos 2025

    # 2. TU PROYECCIÓN 2026 (Sendero 21%)
    meses_2026 = ["Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    inf_2026 = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]
    
    # 3. EXPECTATIVA REM (Suele ser levemente superior a la proyección oficial)
    rem_2026 = [x + 0.4 for x in inf_2026] 

    # Unificamos para el gráfico
    todo_meses = meses_hist + meses_2026
    todo_valores = inf_hist + inf_2026

    # --- VISUALIZACIÓN ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📋 Datos Mensuales")
        df_resumen = pd.DataFrame({
            "Mes": meses_2026,
            "Tu Proyección (%)": inf_2026,
            "Expectativa REM (%)": rem_2026
        })
        st.table(df_resumen)
        
        # Cálculo de acumulada
        total_anual = (np.prod([(1 + x/100) for x in inf_2026]) - 1) * 100
        st.metric("Objetivo Anual 2026", f"{total_anual:.1f}%", delta="-78% vs 2025")

    with col2:
        st.subheader("📈 Curva de Desinflación")
        fig_dual = go.Figure()

        # Área Histórica
        fig_dual.add_trace(go.Scatter(
            x=meses_hist, y=inf_hist, 
            name="Histórico INDEC (2025)",
            line=dict(color='#94a3b8', width=2),
            fill='tozeroy'
        ))

        # Tu Proyección
        fig_dual.add_trace(go.Scatter(
            x=meses_2026, y=inf_2026, 
            name="Proyección Propia (2026)",
            line=dict(color='#2ecc71', width=4),
            mode='lines+markers'
        ))

        # REM
        fig_dual.add_trace(go.Scatter(
            x=meses_2026, y=rem_2026, 
            name="REM BCRA (Expectativa)",
            line=dict(color='#e74c3c', dash='dash')
        ))

        fig_dual.update_layout(
            template="plotly_white",
            hovermode="x unified",
            yaxis_title="Inflación Mensual %",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_dual, use_container_width=True)

    st.info("💡 El área gris representa la inercia del año anterior. La línea verde muestra el sendero necesario para alcanzar el 21% anual.")
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

