import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Monitor AR 2026", page_icon="🇦🇷")

st.title("🏛️ Monitor Financiero Argentina 2026")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📈 Acciones & Balances", "🍞 Inflación 2026", "🏦 Bonos & Tasas"])

# --- PESTAÑA 1: ACCIONES (ANÁLISIS TÉCNICO + FUNDAMENTAL) ---
with tab1:
    st.subheader("📊 Panel Líder & USA: Estrategia Híbrida")
    
    panel_lider = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "METR.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA"]
    usa_petro = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "VISTA", "CVX", "OXY"]
    TICKERS_TOTAL = panel_lider + usa_petro
    
    @st.cache_data(ttl=3600)
    def fetch_market_data(lista):
        data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, t in enumerate(lista):
            try:
                status_text.text(f"Analizando {t}...")
                stock = yf.Ticker(t)
                # Bajamos 1.5 años para SMA 200
                hist = stock.history(period="1.5y")
                if hist.empty: continue
                
                # Análisis Técnico
                ult = hist['Close'].iloc[-1]
                sma = hist['Close'].rolling(200).mean().iloc[-1]
                
                # Análisis Fundamental (Valuación)
                info = stock.info
                fcf = info.get('freeCashflow', 0) or 0
                shares = info.get('sharesOutstanding', 1) or 1
                book_val = info.get('bookValue', 0) or 0
                
                # Valuación: Máximo entre FCF*15 o Valor Libros
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
            progress_bar.progress((i + 1) / len(lista))
        
        status_text.empty()
        progress_bar.empty()
        return pd.DataFrame(data)

    df_full = fetch_market_data(TICKERS_TOTAL)
    
    if not df_full.empty:
        busc = st.text_input("🔍 Buscar activo (ej: GGAL, VISTA):").upper()
        df_f = df_full[df_full['Activo'].str.contains(busc)] if busc else df_full
        
        # Estilo de colores
        def color_status(val):
            if val in ["ALCISTA", "✅ BARATA"]: return 'color: #155724; background-color: #d4edda;'
            if val in ["BAJISTA", "❌ CARA"]: return 'color: #721c24; background-color: #f8d7da;'
            return ''

        st.dataframe(
            df_f.style.applymap(color_status, subset=['Tendencia (AT)', 'Valuación (AF)']),
            use_container_width=True, hide_index=True
        )

# --- PESTAÑA 2: INFLACIÓN ---
with tab2:
    st.header("📊 Monitor de Inflación: INDEC vs REM")
    m_full = [f"{m}-25" for m in ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]] + \
             [f"{m}-26" for m in ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]]
    
    v_indec = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3] + [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]
    v_rem = [21.5, 15.0, 12.5, 10.0, 5.5, 5.2, 4.8, 4.5, 4.0, 3.2, 3.0, 2.8] + [x + 0.4 for x in v_indec[12:]]
    
    fig_inf = go.Figure()
    fig_inf.add_trace(go.Scatter(x=m_full, y=v_indec, name="INDEC / Proy.", line=dict(color='#2ecc71', width=4)))
    fig_inf.add_trace(go.Scatter(x=m_full, y=v_rem, name="REM BCRA", line=dict(color='#e74c3c', dash='dash')))
    fig_inf.add_vrect(x0="Ene-25", x1="Dic-25", fillcolor="gray", opacity=0.1, layer="below", annotation_text="HISTÓRICO")
    fig_inf.update_layout(template="plotly_white", hovermode="x unified", title="Sendero de Desinflación 2025-2026")
    st.plotly_chart(fig_inf, use_container_width=True)

# --- PESTAÑA 3: BONOS & CURVA ---
with tab3:
    st.header("💸 Bonos Tasa Fija vs Plazo Fijo")
    
    data_b = {
        "Ticker": ["S31M6", "S30J6", "S29A6", "S30S6", "TO26", "S15D6", "TO23M"],
        "Precio": [99.20, 96.50, 93.80, 91.20, 68.20, 82.30, 85.10],
        "Dias": [81, 172, 263, 354, 420, 330, 30],
        "TEM (%)": [3.8, 3.9, 4.1, 4.2, 4.5, 4.3, 3.5]
    }
    df_b = pd.DataFrame(data_b).sort_values("Dias")
    df_b["TEA (%)"] = round(((1 + df_b["TEM (%)"]/100)**12 - 1) * 100, 2)
    
    c_b1, c_b2 = st.columns([1, 2])
    with c_b1:
        st.table(df_b[["Ticker", "TEM (%)", "TEA (%)"]])
        st.metric("TEM Plazo Fijo Nación (Ref)", "3.2%")

    with c_b2:
        z = np.polyfit(df_b["Dias"], df_b["TEA (%)"], 1)
        p = np.poly1d(z)
        fig_curva = go.Figure()
        fig_curva.add_trace(go.Scatter(x=df_b["Dias"], y=df_b["TEA (%)"], mode='markers+text', text=df_b["Ticker"], textposition="top center", marker=dict(size=12, color='blue')))
        fig_curva.add_trace(go.Scatter(x=df_b["Dias"], y=p(df_b["Dias"]), name="Tendencia", line=dict(color='red', dash='dot')))
        fig_curva.update_layout(template="plotly_white", title="Curva de Rendimiento Argentina", xaxis_title="Días al Vencimiento", yaxis_title="TEA %")
        st.plotly_chart(fig_curva, use_container_width=True)
