import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Calculadora de Notas UAI", page_icon="🎓", layout="wide")

st.title("🎓 Calculadora Dinámica de NP - UAI")
st.caption("Tus notas y configuraciones se guardan automáticamente en tu navegador para que no pierdas tu información al volver a entrar.")

# ---------------------------------------------------------
# COMPONENTE JAVASCRIPT PARA PERSISTENCIA EN LOCALSTORAGE
# ---------------------------------------------------------
def init_local_storage():
    """Inyecta JavaScript para leer/guardar datos en localStorage"""
    storage_code = """
    <script>
    // Guardar datos en localStorage
    window.saveToLocal = function(key, data) {
        localStorage.setItem(key, JSON.stringify(data));
    };
    
    // Cargar datos de localStorage
    window.loadFromLocal = function(key) {
        return JSON.parse(localStorage.getItem(key)) || {};
    };
    </script>
    """
    components.html(storage_code, height=0)

init_local_storage()

# ---------------------------------------------------------
# FUNCIONES DE FORMATO Y CONVERSIÓN DE NOTAS (Ej: 53 -> 5,3)
# ---------------------------------------------------------
def normalizar_nota(valor):
    try:
        if isinstance(valor, str):
            valor = valor.replace(',', '.')
        val = float(valor)
        if val >= 10.0 and val <= 70.0:
            val = val / 10.0
        val = max(1.0, min(7.0, val))
        return round(val, 2)
    except:
        return 1.0

def formatear_con_coma(num):
    if isinstance(num, (int, float)):
        return f"{num:.1f}".replace('.', ',')
    return str(num).replace('.', ',')

# ---------------------------------------------------------
# 1. PASO DE CONFIGURACIÓN (REPLEGABLE)
# ---------------------------------------------------------
with st.expander("⚙️ Configuración Inicial de Ramos y Ponderaciones", expanded=False):
    num_ramos = st.number_input("¿Cuántas asignaturas deseas gestionar?", min_value=1, max_value=10, value=1, key="num_ramos_input")
    
    estructura_ramos = {}
    
    for i in range(int(num_ramos)):
        st.markdown(f"### 📘 Asignatura {i + 1}")
        nombre_ramo = st.text_input(f"Nombre del ramo {i + 1}:", value=f"Asignatura {i + 1}", key=f"conf_ramo_{i}")
        
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
# 2. PROCESAMIENTO Y CÁLCULOS POR ASIGNATURA
# ---------------------------------------------------------
lista_filas = []

for ramo, evals in estructura_ramos.items():
    for e in evals:
        key_rendida = f"rend_{ramo}_{e['Evaluación']}"
        key_nota = f"nota_{ramo}_{e['Evaluación']}"
        
        rendida = st.session_state.get(key_rendida, False)
        nota_raw = st.session_state.get(key_nota, "5,0")
        nota_limpia = normalizar_nota(nota_raw)
        
        lista_filas.append({
            "Asignatura": e["Asignatura"],
            "Evaluación": e["Evaluación"],
            "Ponderación (%)": e["Ponderación (%)"],
            "Rendida": rendida,
            "Nota Obtenida / Requerida": nota_limpia,
            "_pond_dec": e["_pond_dec"],
            "_key_rend": key_rendida,
            "_key_nota": key_nota
        })

if not lista_filas:
    st.info("👈 Abre '⚙️ Configuración Inicial' arriba para estructurar tus asignaturas.")
    st.stop()

df_panel = pd.DataFrame(lista_filas)

# Recálculo de notas requeridas para los ítems pendientes
for ramo in df_panel["Asignatura"].unique():
    mask_ramo = df_panel["Asignatura"] == ramo
    df_ramo = df_panel[mask_ramo]
    
    df_rendidas = df_ramo[df_ramo["Rendida"] == True]
    puntos_actuales = (df_rendidas["Nota Obtenida / Requerida"] * df_rendidas["_pond_dec"]).sum()
    
    df_pendientes = df_ramo[df_ramo["Rendida"] == False]
    sum_pond_pendiente = df_pendientes["_pond_dec"].sum()
    sum_pond_total = df_ramo["_pond_dec"].sum()
    
    if sum_pond_pendiente > 0:
        puntos_necesarios = (4.0 * sum_pond_total) - puntos_actuales
        promedio_req = round(puntos_necesarios / sum_pond_pendiente, 2)
        promedio_req = max(1.0, min(7.0, promedio_req))
        
        df_panel.loc[mask_ramo & (df_panel["Rendida"] == False), "Nota Obtenida / Requerida"] = promedio_req

# ---------------------------------------------------------
# 3. PANEL DE CONTROL (TABLAS DIVIDIDAS POR ASIGNATURA)
# ---------------------------------------------------------
st.subheader("📝 Panel de Control de Notas")
st.caption("Ingresa notas en formato entero (ej: 53, 70) o decimal (ej: 5.3, 5,3). Toda la información se guarda automáticamente en este dispositivo.")

df_actualizado = df_panel.copy()
resumen_resultados = []

for ramo in df_panel["Asignatura"].unique():
    st.markdown(f"### 📘 Asignatura: {ramo}")
    
    df_ramo_filas = df_panel[df_panel["Asignatura"] == ramo]
    
    cols_headers = st.columns([2.5, 1.5, 1.5, 2.5])
    cols_headers[0].markdown("**Evaluación**")
    cols_headers[1].markdown("**Ponderación**")
    cols_headers[2].markdown("**¿Rendida?**")
    cols_headers[3].markdown("**Nota (Obtenida / Requerida)**")
    
    for idx, row in df_ramo_filas.iterrows():
        c1, c2, c3, c4 = st.columns([2.5, 1.5, 1.5, 2.5])
        
        c1.write(row["Evaluación"])
        c2.write(f"{row['Ponderación (%)']}%")
        
        es_rendida = c3.checkbox("", value=row["Rendida"], key=row["_key_rend"])
        
        if es_rendida:
            valor_defecto = formatear_con_coma(row["Nota Obtenida / Requerida"])
            val_input = c4.text_input(
                label=f"Nota para {row['Evaluación']}",
                value=valor_defecto,
                key=row["_key_nota"],
                label_visibility="collapsed"
            )
            nota_final = normalizar_nota(val_input)
            df_actualizado.at[idx, "Nota Obtenida / Requerida"] = nota_final
            df_actualizado.at[idx, "Rendida"] = True
        else:
            nota_req_txt = formatear_con_coma(row["Nota Obtenida / Requerida"])
            c4.info(f"🎯 Requerida: **{nota_req_txt}**")
            df_actualizado.at[idx, "Rendida"] = False
            
    # Resumen por asignatura
    df_ramo_act = df_actualizado[df_actualizado["Asignatura"] == ramo]
    df_rendidas = df_ramo_act[df_ramo_act["Rendida"] == True]
    sum_pond_rendida = df_rendidas["_pond_dec"].sum()
    puntos_actuales = (df_rendidas["Nota Obtenida / Requerida"] * df_rendidas["_pond_dec"]).sum()
    
    np_actual = round(puntos_actuales / sum_pond_rendida, 2) if sum_pond_rendida > 0 else 0.0
    
    df_pendientes = df_ramo_act[df_ramo_act["Rendida"] == False]
    sum_pond_pendiente = df_pendientes["_pond_dec"].sum()
    sum_pond_total = df_ramo_act["_pond_dec"].sum()
    
    if sum_pond_pendiente > 0:
        puntos_necesarios = (4.0 * sum_pond_total) - puntos_actuales
        promedio_req = round(puntos_necesarios / sum_pond_pendiente, 2)
        if promedio_req > 7.0:
            estado_req = f"{formatear_con_coma(promedio_req)} ⚠️ (Imposible llegar al 4.0)"
        elif promedio_req <= 1.0:
            estado_req = "1,0 (¡Ya aseguraste el 4.0!)"
        else:
            estado_req = f"{formatear_con_coma(promedio_req)}"
    else:
        estado_req = "Sin evaluaciones pendientes"
        
    resumen_resultados.append({
        "Asignatura": ramo,
        "NP Actual (Evaluado)": formatear_con_coma(np_actual),
        "% Evaluado": f"{int(sum_pond_rendida * 100)}%",
        "Evaluaciones Pendientes": len(df_pendientes),
        "Nota promedio requerida en pendientes (para 4.0)": estado_req
    })
    
    st.divider()

# ---------------------------------------------------------
# 4. RESUMEN COMPARATIVO FINAL
# ---------------------------------------------------------
st.subheader("📊 Resumen Comparativo de Asignaturas")
st.dataframe(pd.DataFrame(resumen_resultados), use_container_width=True)
