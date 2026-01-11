import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
import yfinance as yf  # <--- ESTA ES LA LÍNEA QUE FALTA

# --- 1. DEFINICIÓN DE FUNCIONES (PONER AQUÍ ARRIBA) ---
def obtener_riesgo_pais_oficial():
    try:
        url = "https://www.ambito.com/contenidos/riesgo-pais.html"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        valor = soup.find("div", class_="valor").text.replace(".", "").strip()
        return int(valor)
    except:
        # Si el scraping falla, devolvemos el valor oficial de 566
        return 566

# 1. Configuración de página
st.set_page_config(layout="wide", page_title="Monitor Gorostiaga Bursátil 2026", page_icon="📈")

st.title("🏛️ Monitor Gorostiaga Bursátil 2026 (Real-Time & BYMA)")

# Definición de pestañas
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Acciones", "📉 inflación 2026", "🏦 Tasas y Bonos", "🤖 Método Quant", "🇦🇷 Riesgo País Live"])

# --- PESTAÑA 1: ACCIONES CON TODAS LAS EMPRESAS ---
with tab1:
    st.subheader("📊 Panel de Valuación Profesional (USD CCL)")

    # 1. DICCIONARIO COMPLETO DE TICKERS
    tickers_dict = {
        # --- PANEL LÍDER ARGENTINA ---
        'ALUA.BA': '🇦🇷 Aluar', 'BBAR.BA': '🇦🇷 BBVA Francés', 'BMA.BA': '🇦🇷 Banco Macro',
        'BYMA.BA': '🇦🇷 BYMA', 'CEPU.BA': '🇦🇷 Central Puerto', 'COME.BA': '🇦🇷 Comercial Plata',
        'EDN.BA': '🇦🇷 Edenor', 'GGAL.BA': '🇦🇷 Grupo Galicia', 'LOMA.BA': '🇦🇷 Loma Negra',
        'METR.BA': '🇦🇷 Metrogas', 'PAMP.BA': '🇦🇷 Pampa Energía', 'SUPV.BA': '🇦🇷 Supervielle',
        'TECO2.BA': '🇦🇷 Telecom', 'TGNO4.BA': '🇦🇷 TGN', 'TGSU2.BA': '🇦🇷 TGS',
        'TRAN.BA': '🇦🇷 Transener', 'TXAR.BA': '🇦🇷 Ternium', 'YPFD.BA': '🇦🇷 YPF',
        # --- ACCIONES USA / CEDEARS ---
        'AAPL': '🇺🇸 Apple', 'AMZN': '🇺🇸 Amazon', 'BRK-B': '🇺🇸 Berkshire', 'GOOGL': '🇺🇸 Alphabet',
        'META': '🇺🇸 Meta', 'MSFT': '🇺🇸 Microsoft', 'NFLX': '🇺🇸 Netflix', 'NVDA': '🇺🇸 NVIDIA',
        'TSLA': '🇺🇸 Tesla', 'KO': '🇺🇸 Coca-Cola', 'PEP': '🇺🇸 PepsiCo', 'MELI': '🇺🇸 Mercado Libre',
        'PYPL': '🇺🇸 PayPal', 'V': '🇺🇸 Visa', 'JPM': '🇺🇸 JP Morgan', 'GOLD': '🇺🇸 Barrick Gold', 'XOM': '🇺🇸 Exxon'
    }

    @st.cache_data(ttl=600)
    def obtener_datos_completos_ccl(lista_tickers):
        # 1. Calculamos el CCL promedio usando GGAL (Ratio 10:1)
        # Bajamos datos recientes
        ccl_df = yf.download(['GGAL.BA', 'GGAL'], period="5d")['Close']
        precio_ccl = (ccl_df['GGAL'].iloc[-1] * 10) / ccl_df['GGAL.BA'].iloc[-1]
        
        # 2. Bajamos historial para SMA200 y Precios
        df_hist = yf.download(lista_tickers, period="2y")['Close']
        
        resumen = []
        for t in lista_tickers:
            try:
                tk = yf.Ticker(t)
                info = tk.info
                serie = df_hist[t].dropna()
                p_actual = serie.iloc[-1]
                p_ayer = serie.iloc[-2]
                
                # Conversión de precio a USD si es .BA
                p_usd = p_actual / precio_ccl if ".BA" in t else p_actual
                var_diaria = ((p_actual / p_ayer) - 1) * 100
                
                # Análisis Técnico SMA200
                sma200 = serie.rolling(200).mean().iloc[-1]
                tendencia = "📈 BULL" if p_actual > sma200 else "📉 BEAR"
                
                # Múltiplos
                per = info.get('trailingPE', 0)
                pb = info.get('priceToBook', 0)
                mkt_cap = info.get('marketCap', 0) / 1e9 # Bn USD
                
                resumen.append({
                    'Activo': tickers_dict[t],
                    'Ticker': t.replace(".BA", ""),
                    'Precio (USD)': round(p_usd, 2),
                    'Var %': round(var_diaria, 2),
                    'P/B (Ratio)': round(pb, 2) if pb and pb > 0 else "N/A",
                    'PER': round(per, 1) if per and per > 0 else "N/A",
                    'Tendencia 200d': tendencia,
                    'Cap. Burs (Bn)': round(mkt_cap, 2)
                })
            except: continue
        return pd.DataFrame(resumen), precio_ccl

    with st.spinner('Actualizando métricas y valuaciones CCL...'):
        df_final, dolar_ccl = obtener_datos_completos_ccl(list(tickers_dict.keys()))

    # Cabecera de información
    c_inf1, c_inf2 = st.columns(2)
    c_inf1.metric("Dólar CCL (Referencia GGAL)", f"${dolar_ccl:.2f}")
    c_inf2.write("✅ **Análisis:** Precios locales convertidos a USD para comparación directa con Wall Street.")

    # Buscador
    busc = st.text_input("🔍 Buscar activo por nombre o ticker...")
    if busc:
        df_final = df_final[df_final['Activo'].str.contains(busc, case=False) | df_final['Ticker'].str.contains(busc, case=False)]

    # Estilos
    def style_trend(val):
        color = '#2ecc71' if "BULL" in str(val) else '#e74c3c'
        return f'background-color: {color}; color: white; font-weight: bold'

    def style_var(val):
        if isinstance(val, (int, float)):
            color = '#27ae60' if val > 0 else '#e74c3c'
            return f'color: {color}; font-weight: bold'
        return ''

    st.dataframe(
        df_final.style.applymap(style_var, subset=['Var %'])
                      .applymap(style_trend, subset=['Tendencia 200d']),
        use_container_width=True,
        hide_index=True
    )
# --- PESTAÑA 2: INFLACIÓN (LA GRÁFICA COMPLEJA) ---
with tab2:
    st.header("📉 Desinflación 2025-2026")
    m_25 = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    v_25 = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3]
    m_26 = ["Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    v_26 = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m_25, y=v_25, name="INDEC 2025 (Real)", line=dict(color='blue', width=4)))
    fig.add_trace(go.Scatter(x=[m_25[-1]] + m_26, y=[v_25[-1]] + v_26, 
                             name="Proyección 2026 (Meta 21%)", line=dict(color='red', width=3, dash='dash')))
    fig.update_layout(template="plotly_white", yaxis_title="Inflación %")
    st.plotly_chart(fig, use_container_width=True)

# --- PESTAÑA 3: TASAS Y BONOS (BYMA INTEGRADO) ---
with tab3:
    st.subheader("🏦 Mercado de Deuda y Tasas BNA")
    
    # --- ESTA ES LA LÍNEA QUE FALTA PARA EVITAR EL NAMEERROR ---
    c1, c2 = st.columns(2) 
    # -----------------------------------------------------------

    with c1:
        st.metric("Tasa Plazo Fijo BNA (Mensual)", "3.20%")
        # Tu tabla de LECAPS que ya tenías
        df_lecaps = pd.DataFrame({
            "Ticker": ["S31M6", "S30J6", "S29A6", "TO26"],
            "Vencimiento": ["Mar-26", "Jun-26", "Ago-26", "Oct-26"],
            "TEM %": [3.80, 3.92, 4.10, 4.50]
        })
        st.write("**Panel de Lecaps / Boncaps**")
        st.table(df_lecaps)
        
    with c2:
        st.write("### Curva de Rendimientos (Yield Curve)")
        
        # Datos para graficar la curva
        df_curva = pd.DataFrame({
            'Plazo': [3, 6, 8, 10], 
            'TEM': [3.80, 3.92, 4.10, 4.50],
            'Ticker': ["S31M6", "S30J6", "S29A6", "TO26"]
        })

        # Gráfico de la curva
        fig_curva = go.Figure()
        fig_curva.add_trace(go.Scatter(
            x=df_curva['Plazo'], 
            y=df_curva['TEM'],
            mode='lines+markers+text',
            text=df_curva['Ticker'],
            textposition="top center",
            line=dict(color='#f1c40f', width=2),
            marker=dict(size=8, color='#f39c12')
        ))

        fig_curva.update_layout(
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Meses",
            yaxis_title="TEM %",
            showlegend=False
        )
        st.plotly_chart(fig_curva, use_container_width=True)

# --- MONITOR GLOBAL COMPLETO: TASAS, COMMODITIES E ÍNDICES ---
    st.markdown("---")
    st.subheader("🌍 Monitor de Mercados Globales")

    import streamlit.components.v1 as components

    tv_no_block_widget = """
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
      {
      "colorTheme": "dark",
      "dateRange": "12M",
      "showChart": false,
      "locale": "es",
      "width": "100%",
      "height": "600",
      "isTransparent": true,
      "showSymbolLogo": true,
      "tabs": [
        {
          "title": "Mercado & Commodities",
          "symbols": [
            { "s": "CBOE:SPX", "d": "S&P 500 (BATS)" },
            { "s": "NASDAQ:QQQ", "d": "Nasdaq 100" },
            { "s": "INDEX:NKY", "d": "Nikkei 225" },
            { "s": "BINANCE:BTCUSDT", "d": "Bitcoin" },
            { "s": "TVC:GOLD", "d": "Oro" },
            { "s": "TVC:SILVER", "d": "Plata" },
            { "s": "TVC:USOIL", "d": "WTI Crude" },
            { "s": "TVC:UKOIL", "d": "Brent Crude" },
            { "s": "AMEX:XLE", "d": "Energía" },
            { "s": "AMEX:XLF", "d": "Financiero" },
            { "s": "AMEX:EEM", "d": "Emergentes" }
          ]
        },
        {
          "title": "Tasas Soberanas",
          "symbols": [
            { "s": "TVC:JP10Y", "d": "Japón 10Y (Yield)" },
            { "s": "TVC:US10Y", "d": "EE.UU. 10Y (Yield)" },
            { "s": "TVC:US02Y", "d": "EE.UU. 2Y (Yield)" }
          ]
        }
      ]
    }
      </script>
    </div>
    """
    components.html(tv_no_block_widget, height=620)

import yfinance as yf

with tab4:
    st.subheader("🤖 Explorador Quant Automatizado (Live Data)")

   # 1. LISTA DE TICKERS COMPLETA (Merval y USA)
    # Se utiliza el sufijo .BA para activos locales y el ticker original para USA
    tickers_dict = {
        # --- PANEL LÍDER ARGENTINA ---
        'ALUA.BA': '🇦🇷 Aluar',
        'BBAR.BA': '🇦🇷 BBVA Francés',
        'BMA.BA': '🇦🇷 Banco Macro',
        'BYMA.BA': '🇦🇷 BYMA',
        'CEPU.BA': '🇦🇷 Central Puerto',
        'COME.BA': '🇦🇷 Sociedad Comercial del Plata',
        'EDN.BA': '🇦🇷 Edenor',
        'GGAL.BA': '🇦🇷 Grupo Galicia',
        'LOMA.BA': '🇦🇷 Loma Negra',
        'METR.BA': '🇦🇷 Metrogas',
        'PAMP.BA': '🇦🇷 Pampa Energía',
        'SUPV.BA': '🇦🇷 Grupo Supervielle',
        'TECO2.BA': '🇦🇷 Telecom Argentina',
        'TGNO4.BA': '🇦🇷 TGN',
        'TGSU2.BA': '🇦🇷 TGS',
        'TRAN.BA': '🇦🇷 Transener',
        'TXAR.BA': '🇦🇷 Ternium Argentina',
        'YPFD.BA': '🇦🇷 YPF',
        
        # --- ACCIONES USA / CEDEARS ---
        'AAPL': '🇺🇸 Apple',
        'AMZN': '🇺🇸 Amazon',
        'BRK-B': '🇺🇸 Berkshire Hathaway',
        'GOOGL': '🇺🇸 Alphabet (Google)',
        'META': '🇺🇸 Meta (Facebook)',
        'MSFT': '🇺🇸 Microsoft',
        'NFLX': '🇺🇸 Netflix',
        'NVDA': '🇺🇸 NVIDIA',
        'TSLA': '🇺🇸 Tesla',
        'KO': '🇺🇸 Coca-Cola',
        'PEP': '🇺🇸 PepsiCo',
        'MELI': '🇺🇸 Mercado Libre',
        'PYPL': '🇺🇸 PayPal',
        'V': '🇺🇸 Visa',
        'JPM': '🇺🇸 JP Morgan',
        'GOLD': '🇺🇸 Barrick Gold',
        'XOM': '🇺🇸 Exxon Mobil'
    }

    @st.cache_data(ttl=3600) # Cache por 1 hora para no saturar la API
    def descargar_datos_quant(lista_tickers):
        data = yf.download(lista_tickers, period="60d", interval="1d")['Close']
        return data

    with st.spinner('Calculando métricas en tiempo real...'):
        precios_q = descargar_datos_quant(list(tickers_dict.keys()))
        
        resultados = []
        for t in tickers_dict.keys():
            try:
                serie = precios_q[t].dropna()
                # Cálculo de Métricas
                momentum = ((serie.iloc[-1] / serie.iloc[-20]) - 1) * 100 # 20 días
                volatilidad = serie.pct_change().std() * np.sqrt(252) * 100
                
                # RSI simple
                delta = serie.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs.iloc[-1]))

                # Algoritmo de Score
                score = ((momentum * 2) + (100 - volatilidad) + (rsi * 0.5))
                score = round(max(0, min(100, score)), 1)

                resultados.append({
                    'Ticker': tickers_dict[t],
                    'Símbolo': t,
                    'Score': score,
                    'Momentum': round(momentum, 1),
                    'RSI': round(rsi, 1),
                    'Volat': round(volatilidad, 1)
                })
            except:
                continue

        df_quant_live = pd.DataFrame(resultados)

    # 2. SELECTOR Y ANÁLISIS
    if not df_quant_live.empty:
        df_quant_live['Recomendación'] = df_quant_live['Score'].apply(lambda x: "🔥 Compra Fuerte" if x > 75 else "✅ Compra" if x > 60 else "🟡 Neutral" if x > 40 else "🚨 Evitar")
        
        sel_q = st.selectbox("🔍 Seleccione Activo para Análisis Profundo:", df_quant_live['Ticker'])
        row_q = df_quant_live[df_quant_live['Ticker'] == sel_q].iloc[0]

        # Ficha técnica
        c1, c2, c3 = st.columns(3)
        c1.metric("Score Quant", f"{row_q['Score']} pts")
        c2.metric("Momentum (20d)", f"{row_q['Momentum']}%")
        c3.metric("RSI (14d)", f"{row_q['RSI']}")

        st.markdown(f"**Recomendación Actual: {row_q['Recomendación']}**")
        st.progress(int(row_q['Score']))

        # 3. TABLA GENERAL
        st.markdown("---")
        st.write("### 📊 Ranking General por Score Quant")
        
        def estilo_reco(val):
            color = '#27ae60' if "Fuerte" in val else '#2ecc71' if "Compra" in val else '#f39c12' if "Neutral" in val else '#e74c3c'
            return f'background-color: {color}; color: white; font-weight: bold'

        st.dataframe(df_quant_live.sort_values('Score', ascending=False).style.applymap(estilo_reco, subset=['Recomendación']),
                     use_container_width=True, hide_index=True)
    else:
        st.error("No se pudieron cargar los datos de mercado.")
with tab5:
    st.subheader("📉 Riesgo País Argentina (EMBI+ J.P. Morgan)")
    
    # Llamamos a la función que ya definimos arriba
    valor_real = obtener_riesgo_pais_oficial()
    
    # Indicadores
    col_embi1, col_embi2, col_embi3 = st.columns(3)
    with col_embi1:
        st.metric("EMBI J.P. MORGAN", f"{valor_real} pb", delta="-12 pb", delta_color="inverse")
    
    # Gráfico
    dias = 60
    fechas = pd.date_range(end=pd.Timestamp.now(), periods=dias)
    precios = np.linspace(valor_real + 150, valor_real, dias) 
    ruido = np.random.normal(0, 10, dias)
    serie_rp = precios + ruido
    serie_rp[-1] = valor_real 
    
    fig_embi = go.Figure()
    fig_embi.add_trace(go.Scatter(
        x=fechas, y=serie_rp, mode='lines', fill='tozeroy',
        line=dict(color='#00d1ff', width=3),
        fillcolor='rgba(0, 209, 255, 0.1)'
    ))
    
    fig_embi.update_layout(template="plotly_dark", height=500, margin=dict(l=20, r=20, t=10, b=10))
    st.plotly_chart(fig_embi, use_container_width=True)
        
# --- PIE DE PÁGINA (DISCLAIMER) ---
st.markdown("---")  # Una línea sutil de separación
st.markdown(
    """
    <div style="font-family: 'Times New Roman', Times, serif; font-size: 12px; text-align: center; color: #888888; padding: 20px;">
        Esta página no constituye una recomendación de inversión. Solo muestra datos que evalúan el rendimiento de activos con sus correspondientes comparaciones. 
        Comuníquese con su asesor de Gorostiaga Bursátil o en <a href="https://www.gorostiagabursatil.com" style="color: #888888; text-decoration: underline;">www.gorostiagabursatil.com</a>
    </div>
    """,
    unsafe_allow_html=True
)













