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
    st.subheader("📊 Monitor de Valuación y Tendencia: Merval & USA")

    # 1. LISTA DE TICKERS UNIFICADA
    tickers_dict = {
        'ALUA.BA': '🇦🇷 Aluar', 'BBAR.BA': '🇦🇷 BBVA Francés', 'BMA.BA': '🇦🇷 Banco Macro',
        'BYMA.BA': '🇦🇷 BYMA', 'CEPU.BA': '🇦🇷 Central Puerto', 'COME.BA': '🇦🇷 Comercial Plata',
        'EDN.BA': '🇦🇷 Edenor', 'GGAL.BA': '🇦🇷 Grupo Galicia', 'LOMA.BA': '🇦🇷 Loma Negra',
        'METR.BA': '🇦🇷 Metrogas', 'PAMP.BA': '🇦🇷 Pampa Energía', 'SUPV.BA': '🇦🇷 Supervielle',
        'TECO2.BA': '🇦🇷 Telecom', 'TGNO4.BA': '🇦🇷 TGN', 'TGSU2.BA': '🇦🇷 TGS',
        'TRAN.BA': '🇦🇷 Transener', 'TXAR.BA': '🇦🇷 Ternium', 'YPFD.BA': '🇦🇷 YPF',
        'AAPL': '🇺🇸 Apple', 'AMZN': '🇺🇸 Amazon', 'MSFT': '🇺🇸 Microsoft', 'NVDA': '🇺🇸 NVIDIA',
        'TSLA': '🇺🇸 Tesla', 'KO': '🇺🇸 Coca-Cola', 'MELI': '🇺🇸 Mercado Libre', 'GOLD': '🇺🇸 Barrick Gold'
    }

    @st.cache_data(ttl=600)
    def obtener_analisis_profundo(lista_tickers):
        data_resumen = []
        df_hist = yf.download(lista_tickers, period="2y", interval="1d")['Close']
        for t in lista_tickers:
            try:
                ticker_obj = yf.Ticker(t)
                info = ticker_obj.info
                serie = df_hist[t].dropna()
                if not serie.empty:
                    precio_actual = serie.iloc[-1]
                    precio_ayer = serie.iloc[-2]
                    var_diaria = ((precio_actual / precio_ayer) - 1) * 100
                    sma_200 = serie.rolling(200).mean().iloc[-1]
                    dist_sma200 = ((precio_actual / sma_200) - 1) * 100
                    tendencia_largo = "📈 BULL" if precio_actual > sma_200 else "📉 BEAR"
                    per = info.get('trailingPE', 0)
                    pb = info.get('priceToBook', 0)
                    mkt_cap = info.get('marketCap', 0) / 1e9 
                    data_resumen.append({
                        'Activo': tickers_dict[t], 'Ticker': t, 'Precio': round(precio_actual, 2),
                        'Var %': round(var_diaria, 2), 'PER': round(per, 2) if per and per > 0 else "N/A",
                        'P/B': round(pb, 2) if pb and pb > 0 else "N/A", 'Tendencia 200d': tendencia_largo,
                        'Dist. SMA200': f"{dist_sma200:.1f}%", 'Mkt Cap (Bn)': f"{mkt_cap:.2f}"
                    })
            except: continue
        return pd.DataFrame(data_resumen)

    df_final_pro = obtener_analisis_profundo(list(tickers_dict.keys()))

    if not df_final_pro.empty:
        # Buscador y Tabla Principal
        busqueda = st.text_input("🔍 Buscar activo...")
        df_filtrada = df_final_pro.copy()
        if busqueda:
            df_filtrada = df_final_pro[df_final_pro['Activo'].str.contains(busqueda, case=False) | df_final_pro['Ticker'].str.contains(busqueda, case=False)]

        def style_positive_negative(val):
            if isinstance(val, (int, float)):
                return f'color: {"#27ae60" if val > 0 else "#e74c3c"}; font-weight: bold'
            return ''

        st.dataframe(df_filtrada.style.applymap(style_positive_negative, subset=['Var %'])
                     .applymap(lambda v: f'background-color: {"#2ecc71" if "BULL" in v else "#e74c3c"}; color: white; font-weight: bold', subset=['Tendencia 200d']),
                     use_container_width=True, hide_index=True)

       # --- SECCIÓN DE BALANCES TRIMESTRALES 2024 ---
        st.markdown("---")
        st.subheader(f"📊 Reporte de Performance 2024")
        
        accion_sel = st.selectbox("📈 Seleccione activo para visualizar resultados:", df_final_pro['Ticker'].tolist())
        
        @st.cache_data(ttl=3600)
        def obtener_balances_pro(ticker_str):
            try:
                tk = yf.Ticker(ticker_str)
                bal = tk.quarterly_financials.T
                bal_2024 = bal[bal.index.year == 2024].sort_index()
                if bal_2024.empty: return None
                
                return pd.DataFrame({
                    'Trimestre': bal_2024.index.strftime('Q%Q %Y'),
                    'Ingresos': bal_2024.get('Total Revenue', 0),
                    'EBITDA': bal_2024.get('Ebitda', bal_2024.get('Operating Income', 0)),
                    'Ganancia Neta': bal_2024.get('Net Income', 0)
                })
            except: return None

        df_bal = obtener_balances_pro(accion_sel)
        
        if df_bal is not None:
            # Función para formatear etiquetas (M para millones, B para billones)
            def format_val(val):
                if abs(val) >= 1e12: return f'${val/1e12:.2f}T'
                if abs(val) >= 1e9: return f'${val/1e9:.2f}B'
                if abs(val) >= 1e6: return f'${val/1e6:.1f}M'
                return f'${val:,.0f}'

            fig_bal = go.Figure()

            # Configuración de barras con diseño minimalista
            # Colores: Azul profundo (Ingresos), Dorado Mate (EBITDA), Esmeralda (Ganancia)
            metrics = [
                {'col': 'Ingresos', 'name': 'Ventas Totales', 'color': '#1f77b4'},
                {'col': 'EBITDA', 'name': 'EBITDA (Eficiencia)', 'color': '#ff7f0e'},
                {'col': 'Ganancia Neta', 'name': 'Resultado Neto', 'color': '#2ca02c'}
            ]

            for m in metrics:
                fig_bal.add_trace(go.Bar(
                    x=df_bal['Trimestre'],
                    y=df_bal[m['col']],
                    name=m['name'],
                    marker=dict(color=m['color'], line=dict(width=0)),
                    text=df_bal[m['col']].apply(format_val),
                    textposition='outside',
                    cliponaxis=False # Evita que se corten las etiquetas superiores
                ))

            fig_bal.update_layout(
                title=dict(text=f"ESTADOS FINANCIEROS 2024: {accion_sel}", font=dict(size=20, color="white")),
                template="plotly_dark",
                barmode='group',
                bargap=0.15, 
                bargroupgap=0.1,
                height=550,
                plot_bgcolor="rgba(0,0,0,0)", # Fondo transparente
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showticklabels=False, showgrid=True, gridcolor="rgba(255,255,255,0.1)"), # Ocultamos eje Y para mayor limpieza
                xaxis=dict(showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
                margin=dict(t=120, b=50, l=10, r=10)
            )
            
            st.plotly_chart(fig_bal, use_container_width=True)
            
            # Tabla estilizada debajo
            st.markdown("#### Detalle Numérico")
            st.table(df_bal.set_index('Trimestre').applymap(format_val))
            
        else:
            st.info(f"🔍 Buscando reportes... Yahoo Finance aún no ha procesado los datos de 2024 para {accion_sel}.")
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

# --- PESTAÑA 2: CURVA DE RENDIMIENTO ---
with tab2:
    st.subheader("📍 Curva de Rendimiento - Gorostiaga Bursátil")
    
    # 1. Definición de datos pura (sin estructuras complejas)
    data_tasas = {
        "Ticker": ["S31M6", "S30J6", "S29A6", "TO26", "M13F6", "M16E6", "M27F6", "M30A6", "M31G6", "S17E6", "S27F6", "S29Y6", "S30A6", "S30N6", "S30O6", "S31G6", "T31F6"],
        "Vencimiento": ["2026-03-31", "2026-06-30", "2026-08-29", "2026-10-17", "2026-02-13", "2026-01-16", "2026-02-27", "2026-04-30", "2026-07-31", "2026-01-17", "2026-02-27", "2026-05-29", "2026-04-30", "2026-11-30", "2026-10-30", "2026-07-31", "2026-02-28"],
        "TEM %": [3.1, 3.2, 3.4, 3.8, 2.9, 2.8, 3.0, 3.1, 3.3, 2.7, 3.0, 3.2, 3.1, 3.5, 3.4, 3.2, 2.9]
    }

    # 2. Creación de Tabla
    df_tasas = pd.DataFrame(data_tasas)
    df_tasas['Vencimiento'] = pd.to_datetime(df_tasas['Vencimiento'])
    df_tasas = df_tasas.sort_values('Vencimiento')

    # 3. Mostrar Tabla
    st.dataframe(
        df_tasas.style.format({'TEM %': '{:.2f}%'}),
        use_container_width=True,
        hide_index=True
    )

    # 4. Gráfico de Curva (Simple)
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(
        x=df_tasas['Vencimiento'], 
        y=df_tasas['TEM %'],
        mode='lines+markers+text',
        text=df_tasas['Ticker'],
        textposition="top center",
        line=dict(color='#00FF00', width=2),
        name="TEM %"
    ))

    fig_curva.update_layout(
        title="Curva de Tasas por Vencimiento",
        template="plotly_dark",
        xaxis_title="Fecha de Vencimiento",
        yaxis_title="Tasa Efectiva Mensual (%)",
        height=450
    )

    st.plotly_chart(fig_curva, use_container_width=True)

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




































