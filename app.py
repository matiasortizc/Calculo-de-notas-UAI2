import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Notas UAI", page_icon="🎓", layout="wide")

st.title("🎓 Calculadora de Nota de Presentación (NP) - UAI")
st.write("Configura tus asignaturas y simula las notas requeridas en tus evaluaciones pendientes para aprobar con 4.0.")

num_ramos = st.number_input("¿Cuántas asignaturas deseas ingresar?", min_value=1, max_value=10, value=1)

resumen_general = []
desglose_todas_evaluaciones = []

for i in range(int(num_ramos)):
    st.header(f"📘 Asignatura {i + 1}")
    nombre_ramo = st.text_input(f"Nombre de la asignatura {i + 1}:", value=f"Asignatura {i + 1}", key=f"ramo_{i}")
    
    categorias = ["Pruebas / Certámenes", "Controles", "Laboratorio / Proyecto", "Tareas"]
    
    evaluaciones_ingresadas = []
    evaluaciones_pendientes = []
    
    for cat in categorias:
        with st.expander(f"Configurar {cat} para {nombre_ramo}"):
            tiene_cat = st.checkbox(f"¿Tiene {cat}?", key=f"check_{cat}_{i}")
            if tiene_cat:
                cantidad = st.number_input(f"Cantidad de {cat}:", min_value=1, max_value=10, value=1, key=f"cant_{cat}_{i}")
                pct_total = st.slider(f"Porcentaje TOTAL de {cat} en la NP (%):", min_value=0, max_value=100, value=20, key=f"pct_{cat}_{i}") / 100.0
                
                pond_indiv = pct_total / cantidad if cantidad > 0 else 0.0
                
                for j in range(int(cantidad)):
                    nombre_eval = f"{cat[:-1] if cat.endswith('s') else cat} {j + 1}"
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        tiene_nota = st.checkbox(f"¿Tiene nota {nombre_eval}?", key=f"t_nota_{cat}_{i}_{j}")
                    
                    with col2:
                        if tiene_nota:
                            nota = st.number_input(f"Nota obtenida:", min_value=1.0, max_value=7.0, value=5.0, step=0.1, key=f"nota_{cat}_{i}_{j}")
                            evaluaciones_ingresadas.append({
                                'ramo': nombre_ramo,
                                'evaluacion': nombre_eval,
                                'nota': nota,
                                'pond': pond_indiv,
                                'estado': 'Rendida'
                            })
                        else:
                            evaluaciones_pendientes.append({
                                'ramo': nombre_ramo,
                                'evaluacion': nombre_eval,
                                'pond': pond_indiv,
                                'estado': 'Pendiente'
                            })

    # Ponderaciones totales
    suma_pond_ingresada = sum(e['pond'] for e in evaluaciones_ingresadas)
    suma_pond_pendiente = sum(e['pond'] for e in evaluaciones_pendientes)
    suma_pond_total = suma_pond_ingresada + suma_pond_pendiente

    puntos_actuales = sum(e['nota'] * e['pond'] for e in evaluaciones_ingresadas)
    np_actual = round(puntos_actuales / suma_pond_ingresada, 2) if suma_pond_ingresada > 0 else 0.0

    # Lógica de estimación para pendientes
    req_promedio = None
    if suma_pond_pendiente > 0:
        puntos_necesarios = 4.0 * suma_pond_total - puntos_actuales
        if puntos_necesarios <= 0:
            req_promedio = 1.0
        else:
            req_promedio = round(puntos_necesarios / suma_pond_pendiente, 2)

    # Registro individual de notas para el desglose detallado
    for e in evaluaciones_ingresadas:
        desglose_todas_evaluaciones.append({
            "Asignatura": e['ramo'],
            "Evaluación": e['evaluacion'],
            "Nota": e['nota'],
            "Ponderación": f"{round(e['pond'] * 100, 1)}%",
            "Estado": "Rendida"
        })

    for e in evaluaciones_pendientes:
        nota_est = req_promedio if req_promedio is not None else "N/A"
        desglose_todas_evaluaciones.append({
            "Asignatura": e['ramo'],
            "Evaluación": e['evaluacion'],
            "Nota": f"{nota_est} (Requerida)" if req_promedio is not None else "Pendiente",
            "Ponderación": f"{round(e['pond'] * 100, 1)}%",
            "Estado": "Pendiente para 4.0"
        })

    resumen_general.append({
        "Asignatura": nombre_ramo,
        "NP Actual": np_actual,
        "% Evaluado": f"{int(suma_pond_ingresada * 100)}%",
        "Nota requerida en pendientes (para 4.0)": req_promedio if req_promedio is not None else "Sin pendientes"
    })
    st.divider()

# --- SECCIÓN DE RESULTADOS FINAL Y DESGLOSE ---
if resumen_general:
    st.subheader("📊 Resumen General de Asignaturas")
    st.dataframe(pd.DataFrame(resumen_general), use_container_width=True)

if desglose_todas_evaluaciones:
    st.subheader("📝 Desglose Detallado por Evaluación y Nota")
    df_desglose = pd.DataFrame(desglose_todas_evaluaciones)
    
    # Filtro opcional por ramo en el desglose
    lista_ramos = df_desglose["Asignatura"].unique().tolist()
    ramo_seleccionado = st.selectbox("Filtrar desglose por asignatura:", ["Todas"] + lista_ramos)
    
    if ramo_seleccionado != "Todas":
        df_desglose = df_desglose[df_desglose["Asignatura"] == ramo_seleccionado]
        
    st.dataframe(df_desglose, use_container_width=True)
