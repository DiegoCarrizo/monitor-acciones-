import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página - Debe ser la primera instrucción de Streamlit
st.set_page_config(layout="wide", page_title="Merval Alpha 2026", page_icon="🇦🇷")

st.title("📊 Monitor Merval: Estrategia Híbrida (AT + AF)")
st.markdown("---")

# Lista de Tickers
TICKERS = ["GGAL.BA", "YPFD.BA", "PAMP.BA", "ALUA.BA", "CEPU.BA", "EDN.BA", "TXAR.BA", 
           "VISTA.BA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

@st.cache_data(ttl=300)
def fetch_basic_data(ticker):
    """Función para obtener datos simples compatibles con caché"""
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
        
        # Valuación Optimista (FCF * 18 o Valor Libros)
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

# Panel Lateral
st.sidebar.header("⚙️ Opciones")
if st.sidebar.button("🔄 Refrescar Mercado", key="refresh_btn"):
    st.cache_data.clear()
    st.rerun()

# Procesamiento de datos
results = []
with st.spinner('Actualizando precios y balances...'):
    for t in TICKERS:
        res = fetch_basic_data(t)
        if res: results.append(res)

if results:
    df = pd.DataFrame(results)

    # Tabla Principal con estilo
    def style_df(v):
        if v in ["Barata", "ALCISTA"]: return 'background-color: #d4edda; color: #155724'
        if v in ["Cara", "BAJISTA"]: return 'background-color: #f8d7da; color: #721c24'
        return 'background-color: #fff3cd; color: #856404'

    st.subheader("📋 Cuadro de Mando (Tendencia + Valuación)")
    
    with st.container():
        st.dataframe(
            df.style.applymap(style_df, subset=['Tendencia', 'Valuación']),
            use_container_width=True,
            key="main_table" # Clave fija para evitar errores de renderizado
        )

    # Sección de Gráficos
    st.divider()
    
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        selected_t = st.selectbox(
            "Selecciona empresa para ver balances:", 
            df['Ticker'].tolist(),
            key="ticker_selector"
        )

    if selected_t:
        with st.container():
            st.write(f"### 📈 Análisis de Balances: {selected_t}")
            # Descarga de balance bajo demanda
            s_obj = yf.Ticker(selected_t)
            b = s_obj.quarterly_financials.T
            
            if not b.empty and 'Total Revenue' in b.columns:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=b.index, 
                    y=b['Total Revenue'], 
                    name='Ingresos', 
                    marker_color='#1E293B'
                ))
                fig.add_trace(go.Bar(
                    x=b.index, 
                    y=b['Net Income'], 
                    name='Ganancia Neta', 
                    marker_color='#6366f1'
                ))
                
                fig.update_layout(
                    barmode='group', 
                    height=450, 
                    margin=dict(l=20, r=20, t=30, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                # 'theme=None' ayuda a evitar errores de nodos en Streamlit Cloud
                st.plotly_chart(fig, use_container_width=True, theme=None, key=f"chart_{selected_t}")
            else:
                st.info(f"No hay suficientes datos de balance trimestral para {selected_t}.")
else:
    st.error("No se pudieron obtener datos del mercado. Intenta refrescar la página.")
