import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(layout="wide", page_title="Merval Alpha 2026", page_icon="🇦🇷")

st.title("📊 Monitor Merval: Estrategia Híbrida")
st.markdown("---")

# Lista de Tickers
TICKERS = ["GGAL.BA", "YPFD.BA", "PAMP.BA", "ALUA.BA", "CEPU.BA", "EDN.BA", "TXAR.BA", 
           "VISTA.BA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

@st.cache_data(ttl=300)
def fetch_basic_data(ticker):
    """Esta función solo guarda datos simples (números y texto), así no da error de caché."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if hist.empty or len(hist) < 200: return None
        
        current_price = hist['Close'].iloc[-1]
        sma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        
        info = stock.info
        fcf = info.get('freeCashflow', 0)
        shares = info.get('sharesOutstanding', 1)
        book_value = info.get('bookValue', 0)
        
        intrinsic = max((fcf / shares) * 18 if fcf > 0 else 0, book_value)
        
        return {
            "Ticker": ticker,
            "Precio": round(current_price, 2),
            "SMA 200": round(sma200, 2),
            "Tendencia": "ALCISTA" if current_price > sma200 else "BAJISTA",
            "Valuación": "Barata" if intrinsic > current_price * 1.10 else ("Cara" if intrinsic < current_price * 0.90 else "Neutro"),
            "Div. Yield": f"{round(info.get('dividendYield', 0)*100, 2)}%" if info.get('dividendYield') else "0.0%",
            "Intrinsic": round(intrinsic, 2)
        }
    except:
        return None

# Sidebar
st.sidebar.header("Opciones")
if st.sidebar.button("🔄 Refrescar Mercado"):
    st.cache_data.clear()
    st.rerun()

# Procesamiento de la tabla
results = []
with st.spinner('Actualizando precios y balances...'):
    for t in TICKERS:
        res = fetch_basic_data(t)
        if res: results.append(res)

df = pd.DataFrame(results)

# Tabla Principal
def style_df(v):
    if v in ["Barata", "ALCISTA"]: return 'background-color: #d4edda; color: #155724'
    if v in ["Cara", "BAJISTA"]: return 'background-color: #f8d7da; color: #721c24'
    return 'background-color: #fff3cd; color: #856404'

st.subheader("Cuadro de Mando (AT + AF)")
st.dataframe(df.style.applymap(style_df, subset=['Tendencia', 'Valuación']), use_container_width=True)

# Sección de Gráficos (Aquí descargamos el balance solo de la que selecciones)
st.divider()
selected_t = st.selectbox("Selecciona empresa para ver balances trimestrales (3 años):", df['Ticker'].tolist())

if selected_t:
    st.write(f"### Detalle de Balances: {selected_t}")
    # Descargamos el objeto de balance solo al hacer click (para no romper la caché anterior)
    s_obj = yf.Ticker(selected_t)
    b = s_obj.quarterly_financials.T
    
    if not b.empty and 'Total Revenue' in b.columns:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=b.index, y=b['Total Revenue'], name='Ingresos', marker_color='#1E293B'))
        fig.add_trace(go.Bar(x=b.index, y=b['Net Income'], name='Ganancia Neta', marker_color='#6366f1'))
        fig.update_layout(barmode='group', height=450, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de balance trimestral disponibles para este Ticker en este momento.")