import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Configuración de página
st.set_page_config(layout="wide", page_title="Monitor Alpha 2026", page_icon="🇦🇷")

st.title("🏛️ Monitor Financiero Argentina 2026")
st.markdown("---")

# --- FUNCION PARA LEER DE GOOGLE SHEETS (CSV) ---
# Reemplaza 'TU_LINK_AQUI' por el link que obtuviste al publicar en la web
URL_GOOGLE_SHEETS = 'TU_LINK_AQUI' 

def cargar_datos():
    try:
        # Intentamos leer de Google Sheets, si falla usamos datos de respaldo
        df = pd.read_csv(URL_GOOGLE_SHEETS)
    except:
        # Datos de Respaldo para que la App nunca se vea vacía
        data = {
            "Ticker": ["GGAL", "YPFD", "PAMP", "ALUA", "VISTA", "AAPL", "NVDA", "MSFT", "CVX", "OXY"],
            "Precio": [5600, 32000, 2900, 950, 52.4, 185.2, 890.5, 410.2, 155.0, 62.1],
            "PER": [6.2, 5.8, 8.1, 12.4, 7.5, 28.4, 35.2, 32.1, 11.5, 14.2],
            "FCF_M": [120, 850, 45, 30, 310, 95000, 27000, 63000, 15000, 6000],
            "Valor_Intrinseco": [6200, 38000, 3100, 850, 65.0, 170.0, 750.0, 380.0, 165.0, 70.0],
            "Media_200": [5100, 28000, 2750, 980, 48.2, 175.5, 720.0, 395.0, 148.0, 59.5]
        }
        df = pd.DataFrame(data)
    
    # Cálculos dinámicos
    df["Estado"] = df.apply(lambda r: "✅ BARATA" if r["Precio"] < r["Valor_Intrinseco"] else "❌ CARA", axis=1)
    df["Tendencia"] = df.apply(lambda r: "🟢 ALCISTA" if r["Precio"] > r["Media_200"] else "🔴 BAJISTA", axis=1)
    return df

tab1, tab2, tab3 = st.tabs(["📊 Acciones & Valuación", "🍞 Inflación 2026", "🏦 Bonos & Tasas"])

# --- PESTAÑA 1: ACCIONES (PER, FCF, INTRINSECO) ---
with tab1:
    st.subheader("🔎 Análisis Fundamental y Técnico")
    df_acciones = cargar_datos()
    
    # Buscador
    busc = st.text_input("🔍 Filtrar activo:").upper()
    if busc:
        df_acciones = df_acciones[df_acciones['Ticker'].str.contains(busc)]

    st.dataframe(df_acciones.style.map(
        lambda x: 'background-color: #d4edda' if x in ["✅ BARATA", "🟢 ALCISTA"] 
        else ('background-color: #f8d7da' if x in ["❌ CARA", "🔴 BAJISTA"] else ''),
        subset=['Estado', 'Tendencia']
    ), use_container_width=True, hide_index=True)

# --- PESTAÑA 2: INFLACIÓN (12 MESES HIST + PROY PUNTEADA) ---
with tab2:
    st.header("📉 Trayectoria de Inflación 2025-2026")
    m_25 = ["Ene-25", "Feb-25", "Mar-25", "Abr-25", "May-25", "Jun-25", "Jul-25", "Ago-25", "Sep-25", "Oct-25", "Nov-25", "Dic-25"]
    v_25 = [20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.5, 2.3]
    m_26 = ["Ene-26", "Feb-26", "Mar-26", "Abr-26", "May-26", "Jun-26", "Jul-26", "Ago-26", "Sep-26", "Oct-26", "Nov-26", "Dic-26"]
    v_26 = [2.0, 1.8, 1.8, 1.5, 1.3, 1.2, 1.8, 0.9, 0.8, 0.8, 0.6, 1.1]

    fig = go.Figure()
    # Pasado (Sólido)
    fig.add_trace(go.Scatter(x=m_25, y=v_25, name="INDEC (Real)", line=dict(color='blue', width=4)))
    # Proyección (Punteada) - Empieza desde el último dato de Dic-25
    fig.add_trace(go.Scatter(x=[m_25[-1]] + m_26, y=[v_25[-1]] + v_26, 
                             name="Proyección 2026 (21%)", line=dict(color='red', width=3, dash='dash')))

    fig.update_layout(template="plotly_white", yaxis_title="Inflación Mensual %", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- PESTAÑA 3: BONOS & BNA ---
with tab3:
    st.header("🏦 Sistema de Tasas y Renta Fija")
    c1, c2 = st.columns(2)
    
    with c1:
        st.metric("Tasa Plazo Fijo Electrónico BNA", "3.20% TEM")
        st.markdown("---")
        df_l = pd.DataFrame({
            "Instrumento": ["S31M6", "S30J6", "S29A6", "S30S6", "TO26"],
            "Plazo": [81, 172, 263, 354, 420],
            "TEM %": [3.80, 3.92, 4.10, 4.25, 4.50]
        })
        df_l["TEA %"] = round(((1 + df_l["TEM %"]/100)**12 - 1) * 100, 2)
        st.table(df_l)
        
    with c2:
        st.metric("Promedio TEM Mercado", f"{round(df_l['TEM %'].mean(), 2)}%")
        fig_t = go.Figure(go.Scatter(x=df_l["Plazo"], y=df_l["TEM %"], mode='lines+markers+text', 
                                      text=df_l["Instrumento"], textposition="top center",
                                      line=dict(color='green', width=2)))
        fig_t.update_layout(template="plotly_white", xaxis_title="Días", yaxis_title="TEM %")
        st.plotly_chart(fig_t, use_container_width=True)
