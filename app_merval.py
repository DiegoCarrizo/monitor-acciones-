import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Configuración de página
st.set_page_config(layout="wide", page_title="Monitor Alpha 2026", page_icon="🏛️")

st.title("🏛️ Monitor Financiero Integral - Argentina 2026")

tab1, tab2, tab3 = st.tabs(["📊 Análisis Fundamental & Técnico", "🍞 Inflación (INDEC + 21%)", "🏦 Tasas & LECAPS"])

# --- PESTAÑA 1: ACCIONES ---
with tab1:
    st.subheader("🔎 Evaluación de Activos")
    
    panel_lider = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "GGAL.BA", "PAMP.BA", "TXAR.BA", "YPFD.BA"]
    usa_petro = ["AAPL", "MSFT", "NVDA", "VISTA", "CVX", "OXY"]
    TODOS = panel_lider + usa_petro

    @st.cache_data(ttl=3600)
    def fetch_fundamental_data(tickers):
        rows = []
        for t in tickers:
            try:
                stock = yf.Ticker(t)
                # Descargamos histórico primero para asegurar que hay datos
                hist = stock.history(period="1.5y")
                if hist.empty: continue
                
                info = stock.info
                precio = hist['Close'].iloc[-1]
                
                # Múltiplos con valores por defecto para evitar errores
                per = info.get('forwardPE') or info.get('trailingPE') or 0
                fcf = info.get('freeCashflow') or 0
                eps = info.get('trailingEps') or (precio / per if per > 0 else 1)
                
                # Valuación Intrínseca (Modelo simplificado Graham)
                # Valor = EPS * (8.5 + 2 * g)
                growth = 0.05 
                valor_intrinseco = eps * (8.5 + 2 * (growth * 100))
                if ".BA" in t: valor_intrinseco *= 0.65 # Ajuste riesgo argentino
                
                rows.append({
                    "Activo": t,
                    "Precio": round(precio, 2),
                    "PER": round(per, 2) if per > 0 else "N/A",
                    "FCF (M)": f"{round(fcf/1e6, 2)}M" if fcf != 0 else "N/A",
                    "V. Intrínseco": round(valor_intrinseco, 2),
                    "Estado": "✅ BARATA" if precio < valor_intrinseco else "❌ CARA",
                    "Media 200d": round(hist['Close'].rolling(200).mean().iloc[-1], 2)
                })
            except Exception as e:
                continue
        
        # Si no hay datos, creamos un DF con las columnas vacías para evitar el KeyError
        if not rows:
            return pd.DataFrame(columns=["Activo", "Precio", "PER", "FCF (M)", "V. Intrínseco", "Estado", "Media 200d"])
        return pd.DataFrame(rows)

    with st.spinner('Calculando Valuaciones Fundamentales...'):
        df_acciones = fetch_fundamental_data(TODOS)
    
    if not df_acciones.empty:
        # Aplicamos estilo solo si el DataFrame tiene datos
        st.dataframe(df_acciones.style.map(
            lambda x: 'background-color: #d4edda' if x == "✅ BARATA" else ('background-color: #f8d7da' if x == "❌ CARA" else ''),
            subset=['Estado']
        ), use_container_width=True, hide_index=True)
    else:
        st.warning("No se pudieron obtener datos financieros en este momento. Reintenta en unos minutos.")

# --- PESTAÑA 2: INFLACIÓN ---
with tab2:
    st.header("📉 Trayectoria de Inflación 2025-2026")
    m_25 = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    v_25 = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3]
    m_26 = ["Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    v_26 = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m_25, y=v_25, name="INDEC (Histórico)", line=dict(color='blue', width=4)))
    fig.add_trace(go.Scatter(x=[m_25[-1]] + m_26, y=[v_25[-1]] + v_26, 
                             name="Proyección 2026 (Meta 21%)", line=dict(color='red', width=3, dash='dash')))

    fig.update_layout(template="plotly_white", yaxis_title="Inflación Mensual %", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- PESTAÑA 3: TASAS & LECAPS ---
with tab3:
    st.header("🏦 Sistema de Tasas y Renta Fija")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Plazo Fijo BNA (Mensual)", "3.2%")
        df_lecaps = pd.DataFrame({
            "Instrumento": ["S31M6", "S30J6", "S29A6", "S30S6", "TO26"],
            "Días": [81, 172, 263, 354, 420],
            "TEM %": [3.80, 3.92, 4.10, 4.25, 4.50]
        })
        df_lecaps["TEA %"] = round(((1 + df_lecaps["TEM %"]/100)**12 - 1) * 100, 2)
        st.table(df_lecaps)
    with c2:
        st.metric("Promedio TEM Mercado", f"{round(df_lecaps['TEM %'].mean(), 2)}%")
        fig_tasa = go.Figure(go.Scatter(x=df_lecaps["Días"], y=df_lecaps["TEM %"], mode='lines+markers', line=dict(color='green')))
        fig_tasa.update_layout(template="plotly_white", title="Curva TEM", xaxis_title="Días", yaxis_title="TEM %")
        st.plotly_chart(fig_tasa, use_container_width=True)
