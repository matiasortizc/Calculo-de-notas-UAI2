import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Notas UAI", page_icon="🎓", layout="wide")

st.title("🎓 Calculadora Interactiva de NP - UAI")
st.caption("Configura tus ramos y visualiza automáticamente la nota mínima que necesitas en cada evaluación pendiente para aprobar con 4.0.")

# ---------------------------------------------------------
# 1. PASO DE CONFIGURACIÓN (REPLEGABLE)
# ---------------------------------------------------------
with st.expander("⚙️ Configuración Inicial de Ramos y Ponderaciones", expanded=False):
    num_ramos = st.number_input("¿Cuántas asignaturas deseas gestionar?", min_value=1, max_value=10, value=1)
    
    estructura_ramos = {}
    
    for i in range(int(num_ramos)):
        st.markdown(f"### 📘 Asignatura {i + 1}")
        nombre_ramo = st.text_input(f"Nombre del ramo {i + 1}:", value=f"Ramo {i + 1}", key=f"conf_ramo_{i}")
        
        categorias = ["Pruebas / Certámenes", "Controles", "Laboratorio / Proyecto", "Tareas"]
        evaluaciones_ramo = []
        
        cols = st.columns(4)
        for idx, cat in enumerate(categorias):
            with cols[idx]:
                st.markdown(f"**{cat}**")
                tiene = st.checkbox(f"¿Tiene?", key=f"conf_check_{cat}_{i}")
                if tiene:
                    cant = st.number_input(f"Cantidad:", min_value=1, max_value=10, value=2, key=f"conf_cant_{cat}_{i}")
                    pct = st.number_input(f"% Total NP:", min_value=0, max_value=100, value=20, key=f"conf_pct_{cat}_{i}") / 100.0
                    
                    pond_indiv = pct / cant if cant > 0 else 0.0
                    for j in range(int(cant)):
                        nombre_eval = f"{cat[:-1] if cat.endswith('s') else cat} {j + 1}"
                        evaluaciones_ramo.append({
                            "Asignatura": nombre_ramo,
                            "Evaluación": nombre_eval,
                            "Ponderación (%)": round(pond_indiv * 100, 1),
                            "_pond_dec": pond_indiv
                        })
        
        estructura_ramos[nombre_ramo] = evaluaciones_ramo
        st.divider()

# ---------------------------------------------------------
# 2. PROCESAMIENTO Y CÁLCULO DE NOTAS MÍNIMAS
# ---------------------------------------------------------
lista_filas_iniciales = []
for ramo, evals in estructura_ramos.items():
    for e in evals:
        # Se obtiene el estado previo de si fue rendida o la nota ingresada (mantiene la sesión)
        rendida = st.session_state.get(f"rend_{ramo}_{e['Evaluación']}", False)
        nota_ingresada = st.session_state.get(f"nota_{ramo}_{e['Evaluación']}", 5.0)
        
        lista_filas_iniciales.append({
            "Asignatura": e["Asignatura"],
            "Evaluación": e["Evaluación"],
            "Ponderación (%)": e["Ponderación (%)"],
            "Rendida": rendida,
            "Nota Obtenida / Requerida": nota_ingresada if rendida else 1.0,
            "_pond_dec": e["_pond_dec"]
        })

if not lista_filas_iniciales:
    st.info("👈 Abre la pestaña de arriba '⚙️ Configuración Inicial' para seleccionar las evaluaciones de tus ramos.")
    st.stop()

df_base = pd.DataFrame(lista_filas_iniciales)

# Cálculo dinámico de la nota requerida para los ítems no rendidos
for ramo in df_base["Asignatura"].unique():
    mask_ramo = df_base["Asignatura"] == ramo
    df_ramo = df_base[mask_ramo]
    
    df_rendidas = df_ramo[df_ramo["Rendida"] == True]
    puntos_actuales = (df_rendidas["Nota Obtenida / Requerida"] * df_rendidas["_pond_dec"]).sum()
    
    df_pendientes = df_ramo[df_ramo["Rendida"] == False]
    sum_pond_pendiente = df_pendientes["_pond_dec"].sum()
    sum_pond_total = df_ramo["_pond_dec"].sum()
    
    if sum_pond_pendiente > 0:
        puntos_necesarios = (4.0 * sum_pond_total) - puntos_actuales
        promedio_req = round(puntos_necesarios / sum_pond_pendiente, 2)
        # Asegurar límite de escala 1.0 a 7.0
        promedio_req = max(1.0, min(7.0, promedio_req))
        
        # Asignar la nota mínima calculada a las filas no rendidas
        df_base.loc[mask_ramo & (df_base["Rendida"] == False), "Nota Obtenida / Requerida"] = promedio_req

# ---------------------------------------------------------
# 3. PANEL DE CONTROL DE NOTAS (EDITABLE)
# ---------------------------------------------------------
st.subheader("📝 Panel de Control de Notas")
st.write("• Si **no has rendido** una evaluación, verás la **nota mínima requerida** para promediar un 4.0.\n• Marca la casilla **¿Rendida?** para activar la celda e ingresar tu nota real obtenido.")

df_editado = st.data_editor(
    df_base,
    column_config={
        "Asignatura": st.column_config.TextColumn("Asignatura", disabled=True),
        "Evaluación": st.column_config.TextColumn("Evaluación", disabled=True),
        "Ponderación (%)": st.column_config.NumberColumn("Ponderación (%)", format="%.1f%%", disabled=True),
        "Rendida": st.column_config.CheckboxColumn("¿Rendida?"),
        "Nota Obtenida / Requerida": st.column_config.NumberColumn(
            "Nota (Obtenida / Requerida)", min_value=1.0, max_value=7.0, step=0.1, format="%.2f"
        ),
        "_pond_dec": None
    },
    hide_index=True,
    use_container_width=True
)

# ---------------------------------------------------------
# 4. RESUMEN FINAL DE ESTADO
# ---------------------------------------------------------
st.divider()
st.subheader("📊 Resumen y Proyección de Nota de Presentación (NP)")

resumen_resultados = []

for ramo in df_editado["Asignatura"].unique():
    df_ramo = df_editado[df_editado["Asignatura"] == ramo]
    
    df_rendidas = df_ramo[df_ramo["Rendida"] == True]
    sum_pond_rendida = df_rendidas["_pond_dec"].sum()
    puntos_actuales = (df_rendidas["Nota Obtenida / Requerida"] * df_rendidas["_pond_dec"]).sum()
    
    np_actual = round(puntos_actuales / sum_pond_rendida, 2) if sum_pond_rendida > 0 else 0.0
    
    df_pendientes = df_ramo[df_ramo["Rendida"] == False]
    sum_pond_pendiente = df_pendientes["_pond_dec"].sum()
    cant_pendientes = len(df_pendientes)
    sum_pond_total = df_ramo["_pond_dec"].sum()
    
    if sum_pond_pendiente > 0:
        puntos_necesarios = (4.0 * sum_pond_total) - puntos_actuales
        promedio_req = round(puntos_necesarios / sum_pond_pendiente, 2)
        if promedio_req > 7.0:
            estado_req = f"{promedio_req} ⚠️ (Imposible con 4.0)"
        elif promedio_req <= 1.0:
            estado_req = "1.0 (¡Ya aseguraste el 4.0!)"
        else:
            estado_req = f"{promedio_req}"
    else:
        estado_req = "Sin pendientes"
        
    resumen_resultados.append({
        "Asignatura": ramo,
        "NP Actual (Solo Rendido)": np_actual,
        "% Evaluado": f"{int(sum_pond_rendida * 100)}%",
        "Evaluaciones Pendientes": cant_pendientes,
        "Nota mínima requerida en pendientes (para 4.0)": estado_req
    })

st.dataframe(pd.DataFrame(resumen_resultados), use_container_width=True)
