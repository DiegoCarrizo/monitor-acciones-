import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. Configuración de página (Siempre al inicio)
st.set_page_config(layout="wide", page_title="Merval Alpha 2026", page_icon="🇦🇷")

st.title("📊 Monitor Merval: Estrategia Híbrida (AT + AF)")
st.write(f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.markdown("---")

# 2. Lista de Tickers
TICKERS = ["GGAL.BA", "YPFD.BA", "PAMP.BA", "ALUA.BA", "CEPU.BA", "EDN.BA", "TXAR.BA", 
           "VISTA.BA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

@st.cache_data(ttl=300)
def fetch_basic_data(ticker):
    """Obtiene datos técnicos y fundamentales sin objetos complejos para evitar errores de caché"""
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
        intrinsic = max((fcf / shares) * 18 if (fcf and shares) else 0, book_value if book_value else 0)
        
        return {
            "Ticker": ticker,
            "Precio": round(current_price, 2),
            "SMA 200": round(sma200, 2),
            "Tendencia": "ALCISTA" if current_price > sma200 else "BAJISTA",
            "Valuación": "Barata" if intrinsic > current_price * 1.10 else ("Cara" if intrinsic < current_price * 0.90 else "Neutro"),
            "Div. Yield": f"{round(info.get('dividendYield', 0)*100, 2)}%" if info.get('dividendYield') else "0.0%",
            "Intrinsic": round(intrinsic, 2)
        }
    except Exception:
        return None

# 3. Panel Lateral
st.sidebar.header("⚙️ Opciones de App")
if st.sidebar.button("🔄 Refrescar Mercado", key="refresh_btn_v3"):
    st.cache_data.clear()
    st.rerun()

# 4. Procesamiento de datos
results = []
with st.spinner('Descargando datos de Yahoo Finance...'):
    for t in TICKERS:
        res = fetch_basic_data(t)
        if res: results.append(res)

if results:
    df = pd.DataFrame(results)

    # Función de estilo (Uso de .map para compatibilidad con Pandas 2.2+)
    def style_status(val):
        if val in ["Barata", "ALCISTA"]: 
            return 'background-color: #d4edda; color: #155724'
        if val in ["Cara", "BAJISTA"]: 
            return 'background-color: #f8d7da; color: #721c24'
        return 'background-color: #fff3cd; color: #856404'

    st.subheader("📋 Cuadro de Mando (Tendencia + Valuación)")
    
    with st.container():
        # Aplicamos el estilo usando el método moderno .map()
        styled_df = df.style.map(style_status, subset=['Tendencia', 'Valuación'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            key="main_table_2026"
        )

    # 5. Sección de Gráficos
    st.divider()
    
    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        selected_t = st.selectbox(
            "Selecciona una empresa:", 
            df['Ticker'].tolist(),
            key="ticker_selector_v3"
        )
        
        # Mostrar métricas rápidas de la seleccionada
        s_data = df[df['Ticker'] == selected_t].iloc[0]
        st.metric("Precio", f"${s_data['Precio']}")
        st.metric("Valor Estimado", f"${s_data['Intrinsic']}")

    with col_info:
        with st.container():
            st.write(f"### 📈 Balances Trimestrales: {selected_t}")
            s_obj = yf.Ticker(selected_t)
            b = s_obj.quarterly_financials.T
            
            if not b.empty and 'Total Revenue' in b.columns:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=b.index, 
                    y=b.get('Total Revenue', []), 
                    name='Ingresos', 
                    marker_color='#1E293B'
                ))
                fig.add_trace(go.Bar(
                    x=b.index, 
                    y=b.get('Net Income', []), 
                    name='Ganancia Neta', 
                    marker_color='#6366f1'
                ))
                
                fig.update_layout(
                    barmode='group', 
                    height=400, 
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True, theme=None, key=f"ch_v3_{selected_t}")
            else:
                st.info(f"Datos de balances no disponibles temporalmente para {selected_t}.")
else:
    st.warning("No se pudieron cargar los datos. Revisa la conexión con Yahoo Finance.")
