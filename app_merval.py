import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Configuración de página
st.set_page_config(layout="wide", page_title="Monitor Estratégico 2026", page_icon="🏛️")

st.title("🏛️ Monitor Financiero Integral - Argentina 2026")

tab1, tab2, tab3 = st.tabs(["📊 Análisis Fundamental & Técnico", "🍞 Inflación (INDEC + 21%)", "🏦 Tasas & LECAPS"])

# --- PESTAÑA 1: ACCIONES ---
with tab1:
    st.subheader("🔎 Evaluación de Activos")
    
    # Lista optimizada
    panel_lider = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "GGAL.BA", "PAMP.BA", "TXAR.BA", "YPFD.BA"]
    usa_petro = ["AAPL", "MSFT", "NVDA", "VISTA", "CVX", "OXY"]
    TODOS = panel_lider + usa_petro

    @st.cache_data(ttl=3600)
    def fetch_market_data(tickers):
        rows = []
        # Descarga masiva de precios (esto rara vez falla)
        data = yf.download(tickers, period="1.5y", group_by='ticker', progress=False)
        
        for t in tickers:
            try:
                hist = data[t] if len(tickers) > 1 else data
                if hist.empty: continue
                
                precio = hist['Close'].iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                
                # Intentar obtener fundamentales sin romper el bucle
                # Si Yahoo bloquea el 'info', usamos valores estimados
                per, fcf, eps = "N/A", "N/A", precio / 15 # Estimación conservadora
                
                try:
                    s_info = yf.Ticker(t).info
                    per = s_info.get('forwardPE') or s_info.get('trailingPE') or "N/A"
                    fcf_val = s_info.get('freeCashflow')
                    fcf = f"{round(fcf_val/1e6, 2)}M" if fcf_val else "N/A"
                    eps = s_info.get('trailingEps') or eps
                except:
                    pass # Si falla el fundamental, seguimos con los precios

                # Valuación Intrínseca (Modelo simplificado)
                valor_int = eps * 12 # Multiplicador base
                if ".BA" in t: valor_int *= 0.6 # Descuento riesgo AR
                
                rows.append({
                    "Activo": t,
                    "Precio": round(precio, 2),
                    "PER": per,
                    "FCF": fcf,
                    "V. Intrínseco": round(valor_int, 2),
                    "Estado": "✅ BARATA" if precio < valor_int else "❌ CARA",
                    "Media 200d": round(sma200, 2)
                })
            except:
                continue
        return pd.DataFrame(rows)

    with st.spinner('Sincronizando con mercados internacionales...'):
        df_acciones = fetch_market_data(TODOS)
    
    if not df_acciones.empty:
        # Mostramos la tabla. Si el fundamental falló, verás "N/A" pero la tabla carga.
        st.dataframe(df_acciones.style.map(
            lambda x: 'background-color: #d4edda' if x == "✅ BARATA" else ('background-color: #f8d7da' if x == "❌ CARA" else ''),
            subset=['Estado']
        ), use_container_width=True, hide_index=True)
    else:
        st.error("Error crítico: Yahoo Finance rechazó la conexión. Intenta refrescar la página.")

# --- PESTAÑA 2: INFLACIÓN (ESTÁTICA Y SEGURA) ---
with tab2:
    st.header("📉 Trayectoria de Inflación 2025-2026")
    m_full = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25",
              "Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    
    v_hist = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3]
    v_proy = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m_full[:12], y=v_hist, name="Histórico INDEC", line=dict(color='blue', width=4)))
    fig.add_trace(go.Scatter(x=m_full[11:], y=[v_hist[-1]] + v_proy, name="Proy. 2026 (Meta 21%)", line=dict(color='red', width=3, dash='dash')))

    fig.update_layout(template="plotly_white", yaxis_title="Inflación Mensual %", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- PESTAÑA 3: TASAS ---
with tab3:
    st.header("🏦 Sistema de Tasas")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Plazo Fijo BNA (Mensual)", "3.2%")
        st.write("**LECAPS / BONCAPS**")
        df_l = pd.DataFrame({
            "Ticker": ["S31M6", "S30J6", "S29A6", "TO26"],
            "TEM %": [3.80, 3.92, 4.10, 4.50],
            "TEA %": [56.4, 58.7, 61.9, 69.6]
        })
        st.table(df_l)
    with col2:
        st.write("### Comparativa de Curva")
        fig_t = go.Figure(go.Scatter(x=df_l["Ticker"], y=df_l["TEM %"], mode='lines+markers', line=dict(color='green')))
        fig_t.update_layout(template="plotly_white", yaxis_title="TEM %")
        st.plotly_chart(fig_t, use_container_width=True)
