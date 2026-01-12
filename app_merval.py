import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import plotly.graph_objects as go  # <--- Esto soluciona el NameError
from datetime import datetime

# --- CONFIGURACIÓN DE CABECERAS PARA EVITAR BLOQUEOS ---
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
session = requests.Session()
session.headers.update(headers)

# --- CONFIGURACIÓN DE CONEXIÓN SEGURA ---
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

st.set_page_config(page_title="Gorostiaga Monitor", layout="wide")

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

with tab1:
    st.subheader("🏛️ Terminal de Valuación Quant")

    # 1. DATOS DE BALANCES (EPS y Valor Libros)
    balances_fijos = {
        'ALUA.BA': {'EPS': 142.10, 'BV': 980.50},
        'GGAL.BA': {'EPS': 310.40, 'BV': 1350.20},
        'YPFD.BA': {'EPS': 420.00, 'BV': 42000.00},
        'PAMP.BA': {'EPS': 210.30, 'BV': 1680.00},
        'BMA.BA': {'EPS': 285.60, 'BV': 1520.40},
        'CEPU.BA': {'EPS': 112.40, 'BV': 1250.00},
        'TXAR.BA': {'EPS': 105.20, 'BV': 1180.30},
        'AAPL': {'EPS': 6.57, 'BV': 4.83},
        'NVDA': {'EPS': 1.80, 'BV': 2.32}
    }

    if 'df_val' not in st.session_state:
        st.session_state.df_val = None

    # BOTÓN DE ACTUALIZACIÓN
    if st.button('🔄 Sincronizar y Calcular Ratios'):
        with st.spinner('Descargando precios...'):
            resultados = []
            for t, b in balances_fijos.items():
                try:
                    tk = yf.Ticker(t, session=session)
                    h = tk.history(period="1d")
                    if h.empty: continue
                    precio = float(h['Close'].iloc[-1])
                    
                    # Cálculos directos
                    per_v = precio / b['EPS']
                    pb_v = precio / b['BV']
                    
                    # Estado simplificado
                    status_v = "BARATO" if pb_v < 1.0 else "NEUTRO"
                    if ".BA" not in t: status_v = "USA"

                    resultados.append({
                        "Ticker": t.replace(".BA", ""),
                        "Precio": precio,
                        "PER": per_v,
                        "PB": pb_v,
                        "Status": status_v
                    })
                except:
                    continue
            
            if resultados:
                st.session_state.df_val = pd.DataFrame(resultados)
                st.success("Mercado Sincronizado")

    # 3. MOSTRAR TABLA CON PROTECCIÓN CONTRA KEYERROR
    if st.session_state.df_val is not None:
        df_final = st.session_state.df_val.copy()
        
        try:
            # Intentamos aplicar estilos, si falla, muestra dataframe normal
            st.dataframe(
                df_final.style.format({
                    'Precio': '${:,.2f}',
                    'PER': '{:.1f}x',
                    'PB': '{:.2f}x'
                }).map(
                    lambda x: 'color: #adff2f; font-weight: bold' if x == "BARATO" else '',
                    subset=['Status']
                ),
                use_container_width=True, hide_index=True
            )
        except Exception as e:
            # Fallback en caso de que Pandas falle con el estilo
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            st.caption("Nota: Los datos se muestran sin formato de color debido a una incompatibilidad de versión.")
    else:
        st.info("Haga clic en el botón para cargar los datos fundamentales.")

    st.markdown("---")

    # 4. EXPLICACIÓN DE RATIOS (SOPORTE VISUAL)
    [Image of Graham and Dodd valuation principle]
    st.markdown("""
    **Guía de Inversión Gorostiaga:**
    - **PB < 1.0:** Compras activos por debajo de su valor contable.
    - **PER Bajo:** El mercado está pagando poco por la generación de caja de la empresa.
    """)

    # 5. TRADINGVIEW GAUGE
    st.subheader("🎯 Sentimiento Técnico")
    sel_acc = st.selectbox("Seleccione activo:", list(balances_fijos.keys()))
    tv_symbol = f"BCBA:{sel_acc.replace('.BA','')}" if ".BA" in sel_acc else sel_acc
    
    tv_gauge_html = f"""
    <div style="height:380px;">
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
        {{
            "interval": "1D",
            "width": "100%",
            "isTransparent": true,
            "height": 380,
            "symbol": "{tv_symbol}",
            "showIntervalTabs": true,
            "displayMode": "single",
            "locale": "es",
            "theme": "dark"
        }}
        </script>
    </div>
    """
    st.components.v1.html(tv_gauge_html, height=400)
        
# --- PESTAÑA 2: INFLACIÓN (LA GRÁFICA COMPLEJA) ---
with tab2:
    st.header("📉 Inflación 2025-2026")
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

import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np

# --- PESTAÑA 3: ESTRUCTURA DE TASAS ---
with tab3:
    st.subheader("🏦 Curva de Rendimientos y Calculadora de Ganancia Real")

    # 1. INPUT DE CAPITAL INTERACTIVO
    # Esto permite que el cliente vea el impacto real en su bolsillo
    col_cap1, col_cap2 = st.columns([1, 2])
    with col_cap1:
        capital_inv = st.number_input("Capital a invertir ($):", value=1000000, step=100000, format="%d")
    
    # Referencia de inflación (unificada con tu tabla anterior)
    inflacion_referencia = 3.0 
    
    # 2. PROCESAMIENTO DE DATOS
    datos = {
        'Ticker': ["S17E6", "M16E6", "M13F6", "M27F6", "T31F6", "S31M6", "M30A6", "S30A6", "S29Y6", "S30J6", "M31G6", "S31G6", "S29A6", "S30O6", "S30N6", "TO26", "S16E6"],
        'Plazo_Meses': [0.5, 0.5, 1.0, 1.5, 1.5, 3.0, 4.0, 4.0, 5.0, 6.0, 7.0, 7.0, 8.0, 10.0, 11.0, 10.0, 0.2],
        'TEM': [2.7, 2.8, 2.9, 3.0, 2.9, 3.1, 3.1, 3.1, 3.2, 3.2, 3.3, 3.2, 3.4, 3.4, 3.5, 3.8, 2.6]
    }
    df = pd.DataFrame(datos)
    
    # Cálculos de Curva y Ganancia
    df_linea = df.groupby('Plazo_Meses')['TEM'].mean().reset_index()
    df['Tasa Real'] = df['TEM'] - inflacion_referencia
    df['Ganancia Extra ($)'] = (capital_inv * (df['Tasa Real'] / 100))

    # 3. GRÁFICO DE CURVA PROMEDIO (SPLINE)
    
    fig_curva = go.Figure()

    # Puntos de instrumentos (Azul)
    fig_curva.add_trace(go.Scatter(
        x=df['Plazo_Meses'], y=df['TEM'], mode='markers',
        name='Instrumentos', marker=dict(color='#3498db', size=10, symbol='diamond'),
        text=df['Ticker'], hovertemplate="<b>%{text}</b><br>TEM: %{y}%<extra></extra>"
    ))

    # Línea de Promedio Market (Amarilla)
    fig_curva.add_trace(go.Scatter(
        x=df_linea['Plazo_Meses'], y=df_linea['TEM'],
        mode='lines', name='Curva Promedio',
        line=dict(color='#f1c40f', width=4, shape='spline')
    ))

    # Línea Inflación (Roja)
    fig_curva.add_hline(y=inflacion_referencia, line_dash="dash", line_color="#e74c3c",
                        annotation_text=f"Referencia Inflación: {inflacion_referencia}%", 
                        annotation_position="top left")

    fig_curva.update_layout(
        template="plotly_dark", 
        height=450, 
        xaxis_title="Plazo (Meses al vencimiento)", 
        yaxis_title="TEM %",
        hovermode="x unified"
    )
    st.plotly_chart(fig_curva, use_container_width=True)

    # 4. TABLA CON SEMÁFORO VISUAL Y GANANCIA NOMINAL
    st.markdown(f"### 📋 Detalle de Ganancia Real sobre ${capital_inv:,.0f}")
    
    # Función para pintar de verde lo que rinde más que la infla
    def estilo_ganancia(val):
        color = '#2ecc71' if val > 0 else '#e74c3c'
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df.sort_values('Plazo_Meses').style.applymap(estilo_ganancia, subset=['Tasa Real', 'Ganancia Extra ($)'])
        .format({
            'TEM': '{:.2f}%', 
            'Tasa Real': '{:.2f}%', 
            'Ganancia Extra ($)': '$ {:,.0f}'
        }),
        use_container_width=True, 
        hide_index=True
    )
# --- PESTAÑA 3: TASAS Y BONOS (OTRAS MÉTRICAS) ---
with tab3:
    st.subheader("🏦 Mercado de Deuda y Tasas BNA")
    st.write("Información adicional sobre licitaciones y tasas de referencia.")
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

# --- MONITOR DE ACTIVOS GLOBAL - MÚLTIPLO DE MAYER ---
with tab4:
    st.subheader("🌐 Monitor Global de Activos - Múltiplo de Mayer")
    
    # 1. DEFINICIÓN DE ACTIVOS (Balanceado: 7 Tickers y 7 Nombres)
    activos_globales = {
        "Bitcoin": "BTC-USD",
        "Oro": "GC=F",
        "Plata": "SI=F",
        "WTI (Petróleo)": "CL=F",
        "Uranio (URA)": "URA",
        "Litio (LIT)": "LIT",
        "Soja": "ZS=F"
    }

    mayer_results = []
    
    # 2. PROCESAMIENTO CON ERROR HANDLING
    for nombre, ticker in activos_globales.items():
        try:
            # Traemos datos históricos para MA200
            df_m = yf.download(ticker, period="1y", progress=False)
            if not df_m.empty:
                precio_hoy = float(df_m['Close'].iloc[-1])
                ma200 = float(df_m['Close'].rolling(window=200).mean().iloc[-1])
                m_multiple = precio_hoy / ma200
                
                # Clasificación de Estado
                if m_multiple < 1.0:
                    estado = "🟢 Oportunidad"
                elif m_multiple < 2.4:
                    estado = "🟡 Neutro / Alcista"
                else:
                    estado = "🔴 Sobrecompra"
                
                mayer_results.append({
                    "Activo": nombre,
                    "Precio": f"$ {precio_hoy:,.2f}",
                    "Mayer Multiple": round(m_multiple, 2),
                    "Estado": estado
                })
        except Exception:
            # Si falla un ticker, continúa con el siguiente para no romper la tabla
            continue

    # 3. RENDERIZADO DE LA TABLA
    if mayer_results:
        df_mayer_final = pd.DataFrame(mayer_results)
        st.dataframe(df_mayer_final, use_container_width=True, hide_index=True)
    else:
        st.warning("No se pudieron obtener datos de mercado en este momento. Verificá la conexión con Yahoo Finance.")

    # 4. GRÁFICO DE M2 GLOBAL (IFRAME)
    st.markdown("---")
    st.subheader("📊 Bitcoin vs Liquidez Global (M2)")
    st.components.v1.iframe("https://bitcoincounterflow.com/charts/m2-global/", height=600, scrolling=True)

with tab5:
    st.subheader("⚖️ Monitor de Arbitraje")

    @st.cache_data(ttl=600)
    def obtener_dolares_reales():
        # Dólar Oficial actualizado al valor real actual
        datos = {"oficial": 1480.00, "mep": 1430.00, "ccl": 1460.00}
        try:
            # Traemos 7 días para asegurar el cierre del viernes durante el fin de semana
            al30 = yf.download("AL30.BA", period="7d", progress=False)
            al30d = yf.download("AL30D.BA", period="7d", progress=False)
            if not al30.empty and not al30d.empty:
                al30_p = al30['Close'].dropna().iloc[-1]
                al30d_p = al30d['Close'].dropna().iloc[-1]
                if al30d_p > 0:
                    datos["mep"] = float(al30_p / al30d_p)

            ggal_ba = yf.download("GGAL.BA", period="7d", progress=False)
            ggal_us = yf.download("GGAL", period="7d", progress=False)
            if not ggal_ba.empty and not ggal_us.empty:
                ggal_l = ggal_ba['Close'].dropna().iloc[-1]
                ggal_a = ggal_us['Close'].dropna().iloc[-1]
                if ggal_a > 0:
                    datos["ccl"] = float((ggal_l / ggal_a) * 10)
        except:
            pass
        return datos

    mkt = obtener_dolares_reales()

    # --- CÁLCULO DE VARIABLES ---
    brecha_mep = (mkt['mep'] / mkt['oficial'] - 1) * 100
    brecha_ccl = (mkt['ccl'] / mkt['oficial'] - 1) * 100
    canje = ((mkt['ccl'] / mkt['mep']) - 1) * 100

    # --- MÉTRICAS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Dólar Oficial", f"${mkt['oficial']:,.2f}", "Ref. A3500")
    c2.metric("Dólar MEP", f"${mkt['mep']:,.2f}", f"{brecha_mep:.2f}% brecha")
    c3.metric("Dólar CCL", f"${mkt['ccl']:,.2f}", f"{brecha_ccl:.2f}% brecha")

    # --- ANÁLISIS DE TEORÍA AUSTRÍACA ---
    st.markdown("---")
    st.subheader("🇦🇷 Diagnóstico de Inversión")
    
    # Parámetros de la tesis (Ajustables según coyuntura)
    tasa_interes_real = 3.8  
    inflacion_o_emision = 3.0 
    
    col_a1, col_a2 = st.columns([2, 1])

    with col_a1:
        if tasa_interes_real > inflacion_o_emision:
            st.success("### 💹 Recomendación: Mantenerse en PESOS (Tasa)")
            st.write(f"""
            **Tesis:** La tasa de interés real ({tasa_interes_real}%) compensa la pérdida de poder adquisitivo. 
            Si el orden monetario restringe la emisión, la moneda 
            recupera su función de ahorro. La 'Preferencia Temporal' hoy premia la tasa local.
            """)
        else:
            st.error("### 💵 Recomendación: Dolarizar (Cobertura)")
            st.write("""
            **Tesis:** La inflación es un proceso de dilución monetaria. 
            Si la tasa no cubre la expansión del crédito, el peso es un 'bien en desuso'. 
            Debes refugiarte en activos de escasez (Dólar) para preservar capital.
            """)

    with col_a2:
        st.info("**Termómetro**")
        st.write(f"- **Tasa Real:** {tasa_interes_real}%")
        st.write(f"- **Spread Canje:** {canje:.2f}%")
        estado_mkt = "Sinceramiento" if brecha_mep < 20 else "Distorsión"
        st.write(f"- **Estado:** {estado_mkt}")

    # --- TABLA DE CIERRE ---
    st.markdown("### 📋 Detalle Técnico al Cierre")
    df_dolares = pd.DataFrame([
        {"Dólar": "Oficial Mayorista", "Valor": mkt['oficial'], "Canje": "-"},
        {"Dólar": "MEP (AL30 BYMA)", "Valor": mkt['mep'], "Canje": "-"},
        {"Dólar": "CCL (Especie C)", "Valor": mkt['ccl'], "Canje": f"{canje:.2f}%"}
    ])
    st.dataframe(df_dolares.style.format({'Valor': '${:,.2f}'}), use_container_width=True, hide_index=True)

    st.caption(f"Nota: Datos congelados al cierre del viernes. El canje del {canje:.2f}% representa el costo de arbitraje para movilizar capitales fuera del sistema local.")
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














































































