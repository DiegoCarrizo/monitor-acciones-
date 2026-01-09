import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Merval 2026", page_icon="🇦🇷")

st.title("📊 Monitor Merval (Versión Alta Compatibilidad)")
st.write(f"Actualizado: {datetime.now().strftime('%H:%M:%S')}")

# 2. Lista de Tickers
TICKERS = ["GGAL.BA", "YPFD.BA", "PAMP.BA", "ALUA.BA", "CEPU.BA", "EDN.BA", "TXAR.BA", 
           "VISTA.BA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

@st.cache_data(ttl=300)
def fetch_basic_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if hist.empty or len(hist) < 200: return None
        
        current_price = hist['Close'].iloc[-1]
        sma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        
        info = stock.info
        fcf = info.get('freeCashflow', 0) or 0
        shares = info.get('sharesOutstanding', 1) or 1
        book_value = info.get('bookValue', 0) or 0
        
        intrinsic = max((fcf / shares) * 18, book_value)
        
        # Usamos texto plano para máxima compatibilidad
        tendencia = "ALCISTA" if current_price > sma200 else "BAJISTA"
        if intrinsic > current_price * 1.10: val = "BARATA"
        elif intrinsic < current_price * 0.90: val = "CARA"
        else: val = "NEUTRO"

        return {
            "Ticker": ticker,
            "Precio": float(round(current_price, 2)),
            "Tendencia": tendencia,
            "Valuacion": val,
            "Valor_Est": float(round(intrinsic, 2))
        }
    except:
        return None

# 3. Procesamiento
results = []
for t in TICKERS:
    res = fetch_basic_data(t)
    if res: results.append(res)

if results:
    df = pd.DataFrame(results)

    # USAMOS st.table PARA EVITAR ERRORES DE JAVASCRIPT/NODE
    st.subheader("📋 Resumen de Mercado")
    st.table(df) 

    st.divider()
    
    # 4. Gráficos (Solo si se selecciona uno)
    selected_t = st.selectbox("Selecciona para ver Balances:", df['Ticker'].tolist())
    
    if selected_t:
        s_obj = yf.Ticker(selected_t)
        b = s_obj.quarterly_financials.T
        if not b.empty and 'Total Revenue' in b.columns:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=b.index, y=b['Total Revenue'], name='Ingresos'))
            fig.add_trace(go.Bar(x=b.index, y=b['Net Income'], name='Ganancia'))
            fig.update_layout(barmode='group', height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Esperando datos de la API de Yahoo Finance...")
