import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. Configuración
st.set_page_config(layout="wide", page_title="Monitor AR 2026", page_icon="🇦🇷")
st.title("🏛️ Monitor Financiero Argentina 2026")

tab1, tab2, tab3 = st.tabs(["📈 Acciones & Balances", "🍞 Inflación 2026", "🏦 Bonos & Tasas"])

# --- PESTAÑA 1: ACCIONES (CON VALUACIÓN POR FLUJO DE CAJA) ---
with tab1:
    st.subheader("📊 Panel Líder & USA: Análisis Técnico + Fundamental")
    
    panel_lider = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "METR.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA"]
    usa_petro = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "VISTA", "CVX", "OXY"]
    TICKERS_TOTAL = panel_lider + usa_petro
    
    @st.cache_data(ttl=3600)
    def fetch_full_data(lista):
        data = []
        for t in lista:
            try:
                stock = yf.Ticker(t)
                hist = stock.history(period="1.5y")
                if hist.empty: continue
                
                # Análisis Técnico
                ult = hist['Close'].iloc[-1]
                sma = hist['Close'].rolling(200).mean().iloc[-1]
                
                # Análisis Fundamental (Valuación por FCF)
                info = stock.info
                fcf = info.get('freeCashflow', 0) or 0
                shares = info.get('sharesOutstanding', 1) or 1
                book_val = info.get('bookValue', 0) or 0
                
                # Valuación Estimada (FCF * 15 o Valor Libros)
                intrinsic = max((fcf / shares) * 15, book_val)
                
                if intrinsic > ult * 1.15: val_status = "✅ BARATA"
                elif intrinsic < ult * 0.85: val_status = "❌ CARA"
                else: val_status = "🟡 NEUTRO"

                data.append({
                    "Activo": t.replace(".BA", " (AR)") if ".BA" in t else t + " (US)",
                    "Precio": round(ult, 2),
                    "Tendencia (AT)": "ALCISTA" if ult > sma else "BAJISTA",
                    "Valuación (AF)": val_status,
                    "Valor Est.": round(intrinsic, 2)
                })
            except: continue
        return pd.DataFrame(data)

    df_full = fetch_full_data(TICKERS_TOTAL)
    
    if not df_full.empty:
        # Buscador y tabla con colores
        busc = st.text_input("🔍 Filtrar activo:").upper()
        df_f = df_full[df_full['Activo'].str.contains(busc)] if busc else df_full
        
        def color_df(val):
            if "ALCISTA" in str(val) or "BARATA" in str(val): return 'background-color: #d4edda'
            if "BAJISTA" in str(val) or "CARA" in str(val): return 'background-color: #f8d7da'
            return ''

        st.dataframe(df_f.style.applymap(color_df), use_container_width=True, hide_index=True)
    else:
        st.warning("Cargando datos... Si no aparecen, refresca la página.")

# --- PESTAÑA 2: INFLACIÓN ---
with tab2:
    st.header("📊 Monitor de Inflación: INDEC vs REM")
    m25 = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    m26 = ["Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    
    v_indec = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3] + [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]
    v_rem = [21.5, 15.0, 12.5, 10.0, 5.5, 5.2, 4.8, 4.5, 4.0, 3.2, 3.0, 2.8] + [x + 0.5 for x in [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]]
    
    fig_i = go.Figure()
    fig_i.add_trace(go.Scatter(x=m25+m26, y=v_indec, name="INDEC / Proy.", line=dict(color='#2ecc71', width=4)))
    fig_i.add_trace(go.Scatter(x=m25+m26, y=v_rem, name="REM BCRA", line=dict(color='#e74c3c', dash='dash')))
    fig_i.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig_i, use_container_width=True)

# --- PESTAÑA 3: BONOS & CURVA ---
with tab3:
    st.header("💸 Bonos Tasa Fija Argentina")
    
    # Lista ampliada de bonos tasa fija (Lecaps, Boncaps y Botes)
    data_b = {
        "Ticker": ["S31M6", "S30J6", "S29A6", "S30S6", "TO26", "TO23 (MOD)", "S15D6"],
        "Precio": [99.20, 96.50, 93.80, 91.20, 68.20, 85.10, 82.30],
        "Dias": [81, 172, 263, 354, 420, 30, 330],
        "TEM (%)": [3.8, 3.9, 4.1, 4.2, 4.5, 3.5, 4.3]
    }
    df_b = pd.DataFrame(data_b)
    df_b["TEA (%)"] = round(((1 + df_b["TEM (%)"]/100)**12 - 1) * 100, 2)
    
    col_t1, col_t2 = st.columns([1, 2])
    with col_t1:
        st.write("### 📋 Tasas del Mercado")
        st.table(df_b[["Ticker", "TEM (%)", "TEA (%)"]])
        st.metric("TEM Plazo Fijo BNA", "3.2%")

    with col_t2:
        st.write("### 📈 Curva de Rendimiento (TEA)")
        # Ordenar por días para que la línea de tendencia no se cruce
        df_b = df_b.sort_values("Dias")
        z = np.polyfit(df_b["Dias"], df_b["TEA (%)"], 1)
        p = np.poly1d(z)
        
        fig_c = go.Figure()
        fig_c.add_trace(go.Scatter(x=df_b["Dias"], y=df_b["TEA (%)"], mode='markers+text', 
                                   text=df_b["Ticker"], textposition="top center", 
                                   name="Bonos", marker=dict(size=12, color='blue')))
        fig_c.add_trace(go.Scatter(x=df_b["Dias"], y=p(df_b["Dias"]), name="Tendencia", 
                                   line=dict(color='red', dash='dot')))
        fig_c.update_layout(template="plotly_white", xaxis_title="Plazo (Días)", yaxis_title="Rendimiento Anual (TEA %)")
        st.plotly_chart(fig_c, use_container_width=True)
