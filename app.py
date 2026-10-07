# ---------------------------------------------------------
# TARJETAS MÉTRICAS VISUALES POR ASIGNATURA
# ---------------------------------------------------------
col_m1, col_m2, col_m3 = st.columns(3)

# Calculamos si el alumno está sobre o bajo su meta para darle contexto con 'delta'
diferencia_meta = round(np_actual - meta_actual, 2) if sum_pond_rendida > 0 else 0.0

col_m1.metric(
    label="📈 Nota Ponderada Actual", 
    value=formatear_con_coma(np_actual),
    delta=f"{formatear_con_coma(diferencia_meta)} vs Meta" if sum_pond_rendida > 0 else None
)

col_m2.metric(
    label="🎯 Meta Objetivo", 
    value=formatear_con_coma(meta_actual)
)

col_m3.metric(
    label="📊 Avance Evaluado", 
    value=f"{int(sum_pond_rendida * 100)}%"
)

# Barra visual de progreso
st.progress(min(1.0, float(sum_pond_rendida)), text=f"Porcentaje rendido del semestre: {int(sum_pond_rendida * 100)}%")
st.markdown("---")
