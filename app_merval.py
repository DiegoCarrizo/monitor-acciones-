import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import plotly.graph_objects as go  # <--- Esto soluciona el NameError
from datetime import datetime
import numpy as np  # <-- ESTA ES LA LÍNEA QUE FALTA

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
    st.subheader("🏛️ Terminal de Valuación Global - Gorostiaga Bursátil")

    # 1. INICIALIZACIÓN DE DATOS (Los 31 activos que pediste)
    if 'df_quant' not in st.session_state:
        datos_completos = [
            # --- ARGENTINA ---
            {"Ticker": "ALUA", "Precio_Arg": 950.0, "Ganancia_Accion": 142.1, "Libros_Accion": 980.5},
            {"Ticker": "GGAL", "Precio_Arg": 5600.0, "Ganancia_Accion": 310.4, "Libros_Accion": 1350.2},
            {"Ticker": "YPFD", "Precio_Arg": 28000.0, "Ganancia_Accion": 420.0, "Libros_Accion": 42000.0},
            {"Ticker": "PAMP", "Precio_Arg": 3100.0, "Ganancia_Accion": 210.3, "Libros_Accion": 1680.0},
            {"Ticker": "BMA", "Precio_Arg": 9200.0, "Ganancia_Accion": 450.2, "Libros_Accion": 2100.0},
            {"Ticker": "BBAR", "Precio_Arg": 4800.0, "Ganancia_Accion": 220.5, "Libros_Accion": 1150.0},
            {"Ticker": "CEPU", "Precio_Arg": 1250.0, "Ganancia_Accion": 115.0, "Libros_Accion": 1100.0},
            {"Ticker": "TRAN", "Precio_Arg": 1850.0, "Ganancia_Accion": 95.0, "Libros_Accion": 850.0},
            {"Ticker": "METR", "Precio_Arg": 1100.0, "Ganancia_Accion": 65.0, "Libros_Accion": 720.0},
            # --- USA: 7 MAGNÍFICAS + VISTA + NFLX ---
            {"Ticker": "AAPL", "Precio_Arg": 242.1, "Ganancia_Accion": 6.57, "Libros_Accion": 4.83},
            {"Ticker": "MSFT", "Precio_Arg": 415.2, "Ganancia_Accion": 11.8, "Libros_Accion": 34.2},
            {"Ticker": "GOOGL", "Precio_Arg": 188.4, "Ganancia_Accion": 7.54, "Libros_Accion": 26.15},
            {"Ticker": "AMZN", "Precio_Arg": 210.15, "Ganancia_Accion": 4.25, "Libros_Accion": 20.4},
            {"Ticker": "NVDA", "Precio_Arg": 135.8, "Ganancia_Accion": 1.8, "Libros_Accion": 2.35},
            {"Ticker": "META", "Precio_Arg": 580.3, "Ganancia_Accion": 21.1, "Libros_Accion": 60.2},
            {"Ticker": "TSLA", "Precio_Arg": 255.4, "Ganancia_Accion": 3.45, "Libros_Accion": 22.1},
            {"Ticker": "VIST", "Precio_Arg": 55.4, "Ganancia_Accion": 5.8, "Libros_Accion": 18.5},
            {"Ticker": "NFLX", "Precio_Arg": 88.0, "Ganancia_Accion": 19.2, "Libros_Accion": 6.13},
            # --- OTROS USA ---
            {"Ticker": "BRK-B", "Precio_Arg": 475.2, "Ganancia_Accion": 18.5, "Libros_Accion": 265.4},
            {"Ticker": "LLY", "Precio_Arg": 890.1, "Ganancia_Accion": 14.2, "Libros_Accion": 15.3},
            {"Ticker": "AVGO", "Precio_Arg": 175.4, "Ganancia_Accion": 4.55, "Libros_Accion": 16.2},
            {"Ticker": "JPM", "Precio_Arg": 220.15, "Ganancia_Accion": 16.4, "Libros_Accion": 108.3},
            {"Ticker": "V", "Precio_Arg": 310.45, "Ganancia_Accion": 9.9, "Libros_Accion": 18.4},
            {"Ticker": "UNH", "Precio_Arg": 540.3, "Ganancia_Accion": 25.1, "Libros_Accion": 105.2},
            {"Ticker": "MA", "Precio_Arg": 510.2, "Ganancia_Accion": 13.2, "Libros_Accion": 8.4},
            {"Ticker": "XOM", "Precio_Arg": 112.4, "Ganancia_Accion": 9.2, "Libros_Accion": 52.15},
            {"Ticker": "COST", "Precio_Arg": 920.1, "Ganancia_Accion": 16.3, "Libros_Accion": 45.2},
            {"Ticker": "HD", "Precio_Arg": 410.5, "Ganancia_Accion": 15.1, "Libros_Accion": 4.2},
            {"Ticker": "PG", "Precio_Arg": 172.3, "Ganancia_Accion": 6.6, "Libros_Accion": 19.8},
            {"Ticker": "JNJ", "Precio_Arg": 160.5, "Ganancia_Accion": 10.1, "Libros_Accion": 30.25}
        ]
        st.session_state.df_quant = pd.DataFrame(datos_completos)

    # 2. EL EDITOR (Donde cargás los datos)
df_editado = st.data_editor(
    st.session_state.df_quant, 
    num_rows="dynamic", 
    key="editor_global_final", 
    use_container_width=True
)

# 3. LÓGICA DE CÁLCULO Y TABLA DE RESULTADOS
if df_editado is not None and not df_editado.empty:
    # Creamos df_calc AQUÍ adentro
    df_calc = df_editado.copy()
    
    # Ratios
    df_calc['PER'] = df_calc['Precio_Arg'] / df_calc['Ganancia_Accion'].replace(0, np.nan)
    df_calc['P/B'] = df_calc['Precio_Arg'] / df_calc['Libros_Accion'].replace(0, np.nan)

    # Función de Valuación
    def categorizar(fila):
        pb = fila['P/B']
        t = str(fila['Ticker']).upper()
        
        # DEFINICIÓN DE SECTORES
        # Agrupamos todas las tecnológicas, semiconductores y growth
        tecnologicas = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 
            'NFLX', 'AVGO', 'VIST', 'MA', 'V', 'CRM', 'AMD'
        ]
        
        if pd.isna(pb): return "⚪ SIN DATOS"
        
        # APLICACIÓN DE LÓGICA POR SECTOR
        if any(tec in t for tec in tecnologicas):
            # Lógica Tecnológica: El mercado convalida múltiplos altos.
            # Un P/B de 14x (como el de NFLX) es sano para el sector.
            if pb < 15.0: return "🟢 OPORTUNIDAD"
            elif pb <= 28.0: return "🟡 NEUTRO"
            else: return "🔴 EXCESIVO"
        else:
            # Lógica Argentina / Valor Tradicional (Bancos, Energía, Industria):
            # Se valúan por "fierros" o patrimonio neto real.
            if pb < 1.1: return "🟢 BARATO"
            elif pb <= 2.5: return "🟡 NEUTRO"
            else: return "🔴 CARO"

    df_calc['Valuacion'] = df_calc.apply(categorizar, axis=1)
    # --- VISUALIZACIÓN (Debe estar indentada para ver a df_calc) ---
    st.markdown("---")
    st.subheader("📊 Matriz de Valuación Gorostiaga")
    
    columnas_deseadas = ['Ticker', 'Precio_Arg', 'PER', 'P/B', 'Valuacion']
    # Esta línea ahora sí encontrará a df_calc porque está en el mismo bloque
    columnas_visibles = [c for c in columnas_deseadas if c in df_calc.columns]

    st.dataframe(
        df_calc[columnas_visibles].style.format({
            'Precio_Arg': '${:,.2f}',
            'PER': '{:.1f}x',
            'P/B': '{:.2f}x'
        }).map(
            lambda x: 'background-color: #1e4620; color: #adff2f; font-weight: bold' if "🟢" in str(x) else 
                      ('background-color: #4a1c1c; color: #ffcccb; font-weight: bold' if "🔴" in str(x) else ''),
            subset=['Valuacion']
        ),
        use_container_width=True, 
        hide_index=True
    )

    # Resumen de oportunidades (también dentro del if)
    oportunidades = df_calc[df_calc['Valuacion'] == "🟢 OPORTUNIDAD"]['Ticker'].tolist()
    if oportunidades:
        st.success(f"🚀 **Oportunidades:** {', '.join(oportunidades)}")

    # 5. GLOSARIO RÁPIDO
    
    st.info("""
    **Guía de Interpretación:**
    * **PER:** Cuántos años de ganancias pagás hoy. (Bajo = Atractivo).
    * **P/B:** Precio vs Activos Físicos. **Menor a 1.0** es la zona de oportunidad máxima (compras valor por debajo de su costo).
    """)

    # 6. GRÁFICO TÉCNICO (Opcional, para referencia visual)
    st.markdown("---")
    sel_acc = st.selectbox("Ver gráfico de referencia (TradingView):", df_editado['Ticker'].tolist())
    
    # Ajuste de Ticker para Argentina o USA en TradingView
    # Si el precio cargado es grande (en pesos), asumimos BCBA
    if not df_editado.empty:
        fila_sel = df_editado[df_editado['Ticker'] == sel_acc].iloc[0]
        prefijo = "BCBA:" if fila_sel['Precio_Arg'] > 500 else ""
        tv_s = f"{prefijo}{sel_acc}"
        
        tv_html = f"""
        <div style="height:350px;">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
            {{
                "interval": "1D", "width": "100%", "isTransparent": true, "height": 350,
                "symbol": "{tv_s}", "showIntervalTabs": true, "displayMode": "single", "locale": "es", "theme": "dark"
            }}
            </script>
        </div>
        """
        st.components.v1.html(tv_html, height=380)
# --- MOSTRAR LA TABLA FINAL (UBICACIÓN: AL FINAL DEL BLOQUE 'if df_editado...') ---
    st.markdown("---")
    st.subheader("📊 Matriz de Valuación Gorostiaga")
    
    # 1. Definimos las columnas que queremos mostrar
    columnas_deseadas = ['Ticker', 'Precio_Arg', 'PER', 'P/B', 'Valuacion']
    
    # 2. Filtramos solo las que realmente existen en df_calc para evitar el KeyError
    columnas_existentes = [c for c in columnas_deseadas if c in df_calc.columns]
    df_final = df_calc[columnas_existentes]

    # 3. Definimos formatos solo para las columnas numéricas que están presentes
    formatos_dict = {}
    if 'Precio_Arg' in df_final.columns: formatos_dict['Precio_Arg'] = '${:,.2f}'
    if 'PER' in df_final.columns: formatos_dict['PER'] = '{:.1f}x'
    if 'P/B' in df_final.columns: formatos_dict['P/B'] = '{:.2f}x'

    # 4. Renderizado con validación de columna de estilo
    st.dataframe(
        df_final.style.format(formatos_dict).map(
            lambda x: 'background-color: #1e4620; color: #adff2f; font-weight: bold' if "🟢" in str(x) else 
                      ('background-color: #4a1c1c; color: #ffcccb; font-weight: bold' if "🔴" in str(x) else ''),
            subset=['Valuacion'] if 'Valuacion' in df_final.columns else []
        ),
        use_container_width=True, 
        hide_index=True
    )
        
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
    
    # Actualización al valor de hoy
    valor_real = 573 
    
    # Indicadores
    col_embi1, col_embi2, col_embi3 = st.columns(3)
    with col_embi1:
        # Mostramos la métrica con el delta de compresión
        st.metric("EMBI J.P. MORGAN", f"{valor_real} pb", delta="-22 pb", delta_color="inverse")
    
    with col_embi2:
        st.caption("Estado del Crédito")
        st.success("✅ COMPRESIÓN DE SPREADS")

    # Gráfico: Simulación de tendencia bajista (Compresión)
    dias = 60
    fechas = pd.date_range(end=pd.Timestamp.now(), periods=dias)
    
    # Simulamos que venía de 800 y bajó a 573
    precios = np.linspace(800, valor_real, dias) 
    ruido = np.random.normal(0, 15, dias)
    serie_rp = precios + ruido
    serie_rp[-1] = valor_real # Aseguramos que el último punto sea el valor real
    
    fig_embi = go.Figure()
    fig_embi.add_trace(go.Scatter(
        x=fechas, 
        y=serie_rp, 
        mode='lines', 
        fill='tozeroy',
        line=dict(color='#00d1ff', width=3),
        fillcolor='rgba(0, 209, 255, 0.1)',
        name="Riesgo País"
    ))
    
    fig_embi.update_layout(
        template="plotly_dark", 
        height=450, 
        yaxis_title="Puntos Básicos",
        xaxis_title="Últimos 60 días",
        margin=dict(l=20, r=20, t=10, b=10)
    )
    st.plotly_chart(fig_embi, use_container_width=True)

    st.info(f"""
    **Análisis de Gorostiaga:** Con el Riesgo País en **{valor_real} pb**, el costo del capital para las empresas argentinas se reduce drásticamente. 
    Esto permite que activos que antes veíamos 'caros' con un riesgo de 1200 pb, ahora resulten atractivos por la mejora en la tasa de descuento.
    """)

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

    # --- TABLA DE PROYECCIONES INDEPENDIENTE ---
st.markdown("---")
st.header("🚀 Proyecciones de Precios Objetivo (Targets 2026)")
st.subheader("Análisis basado en Riesgo País 543 pb y Breakout del Merval")

# 1. PARÁMETROS TÉCNICOS DEL ÍNDICE
IMV_ACTUAL = 3076946
IMV_TARGET_BASE = 3475415  # Objetivo 1: Techo del canal alcista
IMV_TARGET_BULL = 3938521  # Objetivo 2: Proyección por ruptura (Fibonacci)

# 

upside_base = IMV_TARGET_BASE / IMV_ACTUAL
upside_bull = IMV_TARGET_BULL / IMV_ACTUAL

# 2. CONSOLA DE CARGA PARA PROYECCIONES
st.info(f"Cargue sus activos para calcular el precio objetivo si el Merval alcanza los **{IMV_TARGET_BASE:,.0f}** (Base) o los **{IMV_TARGET_BULL:,.0f}** (Bull).")

if 'df_proyecciones' not in st.session_state:
    # Datos iniciales para que la tabla no aparezca vacía
    datos_proy = [
        {"Ticker": "GGAL", "Precio_Actual": 5600.0},
        {"Ticker": "YPFD", "Precio_Actual": 28000.0},
        {"Ticker": "PAMP", "Precio_Actual": 3100.0},
        {"Ticker": "ALUA", "Precio_Actual": 950.0}
    ]
    st.session_state.df_proyecciones = pd.DataFrame(datos_proy)

# Editor de datos independiente
df_editor_proy = st.data_editor(
    st.session_state.df_proyecciones, 
    num_rows="dynamic", 
    key="editor_proyectado",
    use_container_width=True
)

if not df_editor_proy.empty:
    # 3. CÁLCULO DE TARGETS INDIVIDUALES
    df_editor_proy['Target_Base'] = df_editor_proy['Precio_Actual'] * upside_base
    df_editor_proy['Upside_Base_%'] = (upside_base - 1) * 100
    
    df_editor_proy['Target_Bull'] = df_editor_proy['Precio_Actual'] * upside_bull
    df_editor_proy['Upside_Bull_%'] = (upside_bull - 1) * 100

    # 4. VISUALIZACIÓN DE LA TABLA DE OBJETIVOS
    st.markdown("### 🎯 Matriz de Precios Objetivo")
    
    st.dataframe(
        df_editor_proy.style.format({
            'Precio_Actual': '${:,.2f}',
            'Target_Base': '${:,.2f}',
            'Target_Bull': '${:,.2f}',
            'Upside_Base_%': '{:.1f}%',
            'Upside_Bull_%': '{:.1f}%'
        }).map(
            lambda x: 'color: #adff2f; font-weight: bold', 
            subset=['Target_Bull', 'Upside_Bull_%']
        ),
        use_container_width=True, 
        hide_index=True
    )

# 5. GRÁFICO DE TRAYECTORIA TÉCNICA
st.markdown("---")
st.subheader("📈 Trayectoria Estimada del Índice")

dias_proy = 90
fechas_proy = pd.date_range(start=pd.Timestamp.now(), periods=dias_proy)

# Simulación de curvas de precios
curva_base = np.linspace(IMV_ACTUAL, IMV_TARGET_BASE, dias_proy) + np.random.normal(0, 35000, dias_proy)
curva_bull = np.linspace(IMV_ACTUAL, IMV_TARGET_BULL, dias_proy) + np.random.normal(0, 50000, dias_proy)

fig_targets = go.Figure()

fig_targets.add_trace(go.Scatter(
    x=fechas_proy, y=curva_base, 
    name='Escenario Base (Normalización)', 
    line=dict(color='#00d1ff', width=2, dash='dash')
))

fig_targets.add_trace(go.Scatter(
    x=fechas_proy, y=curva_bull, 
    name='Escenario Bull (Investment Grade)', 
    line=dict(color='#adff2f', width=4)
))

fig_targets.update_layout(
    template="plotly_dark",
    title="Proyección Merval: Rumbo a los 4M de puntos",
    yaxis_title="Puntos IMV",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1)
)

st.plotly_chart(fig_targets, use_container_width=True)

st.success("""
**Nota Estratégica:** Esta proyección asume que el Merval mantiene la simetría de su canal alcista histórico. 
Con un Riesgo País en **573 pb**, la probabilidad de alcanzar el **Escenario Bull** aumenta, ya que Argentina comienza a ser atractiva para fondos de mercados emergentes.
""")
import streamlit as st

# Creamos pestañas para organizar el contenido
tab1, tab2 = st.tabs(["📈 Monitor de Activos", "🏦 Tasas & Teoría del Amago"])

with tab1:
    st.write("Aquí va tu código actual de los 31 activos...")

with tab2:
    st.header("Monitor de Tasas: Arbitraje y Costo de Oportunidad")
    
    # Simulación de datos (Aquí conectarías con tu API de precios)
    col1, col2, col3 = st.columns(3)
    col1.metric("T-Bill 3M (USA)", "4.85%", "TACO Trade")
    col2.metric("Lecap S15D6", "42.0%", "ARS Bench")
    col3.metric("Bopreal BP26", "18.5%", "Hard Dollar")

    st.subheader("Análisis de la Teoría del Amago")
    st.write("""
    Este monitor mide el diferencial de tasas. Cuando el **Riesgo País** sube por un amago arancelario, 
    la brecha entre la ON Argentina y el T-Bill se expande, señalando una ventana de compra.
    """)
    
    # Aquí podés agregar una tabla con el estilo de tasas.ar
    st.table({
        "Instrumento": ["Plazo Fijo", "Caución 7d", "FCI Money Market", "Lecap"],
        "TNA": ["37%", "35%", "34%", "42%"],
        "Estado (Amago)": ["Neutral", "Liquidez para compra", "Neutral", "Oportunidad"]
    })
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









































































































