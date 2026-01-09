import requests

# --- DENTRO DE LA PESTAÑA 2: INFLACIÓN ---
with tab2:
    st.header("📊 Inflación Real (API INDEC)")

    @st.cache_data(ttl=86400) # Caché por 24 horas
    def get_inflacion_real():
        # URL de la serie IPC Cobertura Nacional del portal de datos públicos
        url = "https://apis.datos.gob.ar/series/api/series/?ids=143.3_NO_V_DR_0_21&limit=12&sort=desc&format=json"
        try:
            response = requests.get(url).json()
            data = response['data']
            # Armamos el DataFrame
            df_ipc = pd.DataFrame(data, columns=['Fecha', 'Valor'])
            df_ipc['Fecha'] = pd.to_datetime(df_ipc['Fecha']).dt.strftime('%b-%y')
            return df_ipc.iloc[::-1] # Invertir para que sea cronológico
        except:
            return None

    df_inflacion = get_inflacion_real()

    if df_inflacion is not None:
        # Gráfico Real vs REM (Simulamos el REM ya que el BCRA no tiene API abierta sin token)
        fig_inf = go.Figure()
        
        # Serie Real INDEC
        fig_inf.add_trace(go.Scatter(
            x=df_inflacion['Fecha'], 
            y=df_inflacion['Valor'], 
            name="IPC Real (INDEC)",
            line=dict(color='#2ecc71', width=4),
            mode='lines+markers'
        ))

        # Serie REM (Referencia estática para comparar)
        rem_dummy = [x + 0.5 for x in df_inflacion['Valor']] # Ejemplo: REM suele estimar un poco más
        fig_inf.add_trace(go.Scatter(
            x=df_inflacion['Fecha'], 
            y=rem_dummy, 
            name="Expectativa REM (BCRA)",
            line=dict(color='#e74c3c', dash='dash')
        ))

        fig_inf.update_layout(
            title="Variación Mensual IPC (%)",
            xaxis_title="Mes",
            yaxis_title="Porcentaje",
            hovermode="x unified",
            template="plotly_white"
        )
        st.plotly_chart(fig_inf, use_container_width=True)
    else:
        st.error("No se pudo conectar con la API de Datos Públicos.")
