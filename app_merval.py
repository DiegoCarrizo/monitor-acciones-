import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Merval Alpha 2026", page_icon="🇦🇷")

st.title("📊 Monitor Merval: Estrategia Híbrida (AT + AF)")
st.write(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.markdown("---")

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
        fcf = info.get('freeCashflow', 0)
        shares = info.get('sharesOutstanding', 1)
        book_value = info.get('bookValue', 0)
        
        intrinsic = max((fcf / shares) * 18 if (fcf and shares) else 0, book_value if book_value else 0)
        
        # Lógica de Emojis para evitar errores de CSS/Styler
        tendencia_label = "🟢 ALCISTA" if current_price > sma200 else "🔴 BAJISTA"
        
        if intrinsic > current_price * 1.10:
            val_label = "✅ BARATA"
        elif intrinsic < current_price * 0.90:
            val_label = "❌ CARA"
        else:
            val_label = "🟡 NEUTRO"

        return {
            "Ticker": ticker,
            "Precio": round(current_price, 2),
            "SMA 200": round(sma200, 2),
            "Tendencia (AT)": tendencia_label,
            "Valuación (AF)": val_label,
            "Div. Yield": f"{round(info.get('dividendYield', 0)*100, 2)}%" if info.get('dividendYield') else "0.0%",
            "Valor Est.": round(intrinsic, 2)
        }
    except Exception:
        return None

# 3. Sidebar
if st.sidebar.button("🔄 Refrescar Mercado", key="refresh_v4"):
    st.cache_data.clear()
    st.rerun()

# 4. Procesamiento
results = []
with st.spinner('Obteniendo datos...'):
    for t in TICKERS:
        res = fetch_basic_data(t)
        if res: results.append(res)

if results:
    df = pd.DataFrame(results)

    st.subheader("📋 Cuadro de Mando")
    # Mostramos la tabla normal (sin .style) para asegurar compatibilidad total
    st.dataframe(df, use_container_width=True, key="fixed_table_v4")

    # 5. Sección de Gráficos
    st.divider()
    col_sel, col_chart = st.columns([1, 2])
    
    with col_sel:
        selected_t = st.selectbox("Selecciona empresa:", df['Ticker'].tolist(), key="sel_v4")
        s_data = df[df['Ticker'] == selected_t].iloc[0]
        st.metric("Precio Actual", f"${s_data['Precio']}")
        st.metric("Potencial vs Valuación", f"${s_data['Valor Est.']}")

    with col_chart:
        st.write(f"### 📈 Balances Trimestrales: {selected_t}")
        s_obj = yf.Ticker(selected_t)
        b = s_obj.quarterly_financials.T
        
        if not b.empty and 'Total Revenue' in b.columns:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=b.index, y=b.get('Total Revenue', []), name='Ingresos', marker_color='#1E293B'))
            fig.add_trace(go.Bar(x=b.index, y=b.get('Net Income', []), name='Ganancia Neta', marker_color='#6366f1'))
            fig.update_layout(barmode='group', height=350, margin=dict(l=0,r=0,t=0,b=0), template="plotly_white")
            st.plotly_chart(fig, use_container_width=True, theme=None, key=f"chart_v4_{selected_t}")
        else:
            st.info("Balances no disponibles.")
else:
    st.error("No se pudieron cargar los datos. Reintenta en unos minutos.")
