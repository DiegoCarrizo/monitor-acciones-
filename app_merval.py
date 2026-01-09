import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Monitor AR 2026", page_icon="🇦🇷")

st.title("🏛️ Monitor Financiero Argentina 2026")
tab1, tab2, tab3 = st.tabs(["📈 Acciones & Balances", "🍞 Inflación vs REM", "🏦 Bonos Tasa Fija"])

# --- DATOS COMPARTIDOS ---
# Simulación de Tasas y Macro (Basado en proyecciones 2026)
TASA_PF_NACION = 3.5  # TEM (Tasa Efectiva Mensual) simulada Banco Nación

# --- PESTAÑA 1: ACCIONES (Tu código anterior optimizado) ---
with tab1:
    TICKERS = ["GGAL.BA", "YPFD.BA", "PAMP.BA", "ALUA.BA", "VISTA.BA", "AAPL", "NVDA"]
    results = []
    for t in TICKERS:
        try:
            s = yf.Ticker(t)
            h = s.history(period="1y")
            if not h.empty:
                current = h['Close'].iloc[-1]
                sma200 = h['Close'].rolling(200).mean().iloc[-1]
                results.append({
                    "Ticker": t, "Precio": round(current, 2),
                    "Tendencia": "🟢 ALCISTA" if current > sma200 else "🔴 BAJISTA"
                })
        except: pass
    st.table(pd.DataFrame(results))

# --- PESTAÑA 2: INFLACIÓN INDEC vs REM ---
with tab2:
    st.header("📊 Evolución de Precios (IPC)")
    # Datos ejemplo (Ene 2025 - Ene 2026)
    meses = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    ipc_indec = [15.0, 13.2, 11.0, 8.5, 7.0, 6.0, 5.5, 4.8, 4.2, 3.8, 3.5, 3.2]
    rem_bcra = [16.5, 14.0, 12.5, 9.5, 8.5, 7.5, 6.5, 5.5, 5.0, 4.5, 4.0, 3.8]

    fig_inf = go.Figure()
    fig_inf.add_trace(go.Scatter(x=meses, y=ipc_indec, name="IPC INDEC (Real)", line=dict(color='#1f77b4', width=4)))
    fig_inf.add_trace(go.Scatter(x=meses, y=rem_bcra, name="REM BCRA (Expectativa)", line=dict(color='#ff7f0e', dash='dash')))
    fig_inf.update_layout(title="Inflación Mensual: Realidad vs Expectativa REM", yaxis_title="Variación % Mensual", template="plotly_white")
    st.plotly_chart(fig_inf, use_container_width=True)
    
    st.info("💡 El gráfico muestra el proceso de desinflación proyectado hacia 2026.")

# --- PESTAÑA 3: BONOS TASA FIJA & CURVA DE RENDIMIENTO ---
with tab3:
    st.header("💸 Bonos Soberanos Tasa Fija")
    
    # Datos simulados de bonos comunes (ej: Botes, Lecaps o similares en 2026)
    data_bonos = {
        "Ticker": ["TO26", "S31M6", "S30J6", "S29A6"],
        "Precio": [65.40, 98.20, 95.10, 92.50],
        "Vencimiento (Días)": [365, 90, 180, 270],
        "TNA (%)": [55.0, 48.5, 50.2, 52.0]
    }
    df_bonos = pd.DataFrame(data_bonos)
    
    # Cálculos
    df_bonos["TEM (%)"] = round(df_bonos["TNA (%)"] / 12, 2)
    df_bonos["TEA (%)"] = round(((1 + df_bonos["TEM (%)"]/100)**12 - 1) * 100, 2)
    
    # Comparativa Banco Nación
    st.subheader("⚖️ Comparativa de Inversión Mensual")
    col_a, col_b = st.columns(2)
    col_a.metric("TEM Plazo Fijo BNA", f"{TASA_PF_NACION}%")
    mejor_bono = df_bonos.loc[df_bonos['TEM (%)'].idxmax()]
    col_b.metric(f"Mejor Bono: {mejor_bono['Ticker']}", f"{mejor_bono['TEM (%)']}% TEM")

    st.table(df_bonos[["Ticker", "Precio", "TEM (%)", "TEA (%)"]])

    # Gráfico de Puntos: Curva de Rendimiento
    st.subheader("📈 Curva de Rendimiento Anual (TEA)")
    
    # Ajuste de curva (Promedio trazado)
    z = np.polyfit(df_bonos["Vencimiento (Días)"], df_bonos["TEA (%)"], 1)
    p = np.poly1d(z)
    x_range = np.linspace(df_bonos["Vencimiento (Días)"].min(), df_bonos["Vencimiento (Días)"].max(), 100)

    fig_curva = go.Figure()
    # Puntos de los bonos
    fig_curva.add_trace(go.Scatter(x=df_bonos["Vencimiento (Días)"], y=df_bonos["TEA (%)"], 
                                  mode='markers+text', text=df_bonos["Ticker"],
                                  textposition="top center", name="Bonos Individuales",
                                  marker=dict(size=12, color='#6366f1')))
    # Línea de tendencia (Curva)
    fig_curva.add_trace(go.Scatter(x=x_range, y=p(x_range), name="Curva de Rendimiento (Tendencia)",
                                  line=dict(color='rgba(255, 0, 0, 0.5)', width=2)))
    
    fig_curva.update_layout(xaxis_title="Días al Vencimiento", yaxis_title="Rendimiento Anual (TEA %)",
                            template="plotly_white")
    st.plotly_chart(fig_curva, use_container_width=True)

    st.caption("Nota: Una curva ascendente indica que el mercado exige más tasa a largo plazo (incertidumbre), mientras que una descendente o invertida sugiere una baja de inflación esperada.")
