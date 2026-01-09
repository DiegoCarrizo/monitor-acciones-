import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Monitor AR 2026", page_icon="🇦🇷")

st.title("🏛️ Monitor Financiero Argentina 2026")
st.markdown(f"**Escenario: Inflación Objetivo Anual 21%**")

tab1, tab2, tab3 = st.tabs(["📈 Acciones", "🍞 Inflación 2026", "🏦 Bonos & Tasas"])

# --- DATOS DE INFLACIÓN PROYECTADA ---
meses_2026 = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
# Ajuste fino para dar 21% anual (Producto de 1+i)
inf_proyectada = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]

# --- PESTAÑA 1: ACCIONES ---
with tab1:
    st.subheader("📋 Resumen de Mercado (Acciones & CEDEARs)")
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

# --- PESTAÑA 2: INFLACIÓN 21% ANUAL ---
with tab2:
    st.header("📊 Proyección de Inflación Mensual 2026")
    
    # Creamos el DataFrame para la tabla y el gráfico
    df_inf = pd.DataFrame({
        "Mes": meses_2026,
        "Inflación Mensual (%)": inf_proyectada
    })
    
    # Cálculo acumulado para verificar el 21%
    acumulada = [(1 + x/100) for x in inf_proyectada]
    total_anual = (np.prod(acumulada) - 1) * 100
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### 📅 Hoja de Ruta")
        st.table(df_inf)
        st.metric("Inflación Acumulada Dic-2026", f"{total_anual:.1f}%")
        
    with col2:
        fig_inf = go.Figure()
        fig_inf.add_trace(go.Scatter(
            x=meses_2026, y=inf_proyectada,
            mode='lines+markers+text',
            text=[f"{x}%" for x in inf_proyectada],
            textposition="top center",
            line=dict(color='#00cf8d', width=4),
            name="Proyección 2026"
        ))
        fig_inf.update_layout(
            title="Sendero de Desinflación Proyectado",
            yaxis_title="Variación % Mensual",
            template="plotly_white",
            yaxis=dict(range=[0, 3])
        )
        st.plotly_chart(fig_inf, use_container_width=True)

# --- PESTAÑA 3: BONOS & COMPARATIVA ---
with tab3:
    st.header("💸 Bonos Tasa Fija vs Plazo Fijo")
    
    # Datos de mercado (Simulados para visualización)
    tasa_pf_nacion = 3.2 # TEM Mensual Plazo Fijo
    
    data_bonos = {
        "Ticker": ["TO26", "S31M6", "S30J6", "S29A6"],
        "Precio": [68.20, 99.10, 96.50, 93.80],
        "Vencimiento (Días)": [365, 90, 180, 270],
        "TEM (%)": [4.2, 3.8, 3.9, 4.1] # Tasa Efectiva Mensual del bono
    }
    df_bonos = pd.DataFrame(data_bonos)
    df_bonos["TEA (%)"] = round(((1 + df_bonos["TEM (%)"]/100)**12 - 1) * 100, 2)
    
    st.subheader("⚖️ ¿Qué conviene más?")
    m1, m2 = st.columns(2)
    m1.metric("TEM Plazo Fijo Nación", f"{tasa_pf_nacion}%")
    m2.metric("TEM Promedio Bonos", f"{df_bonos['TEM (%)'].mean():.2f}%")

    st.table(df_bonos)

    # Gráfico de Curva de Rendimiento
    st.subheader("📈 Curva de Rendimiento (TEA)")
    
    # Línea de tendencia
    z = np.polyfit(df_bonos["Vencimiento (Días)"], df_bonos["TEA (%)"], 1)
    p = np.poly1d(z)
    
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(
        x=df_bonos["Vencimiento (Días)"], y=df_bonos["TEA (%)"],
        mode='markers+text', text=df_bonos["Ticker"],
        textposition="top center", marker=dict(size=15, color='#6366f1')
    ))
    fig_curva.add_trace(go.Scatter(
        x=df_bonos["Vencimiento (
