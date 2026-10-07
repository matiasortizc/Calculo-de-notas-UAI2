import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Calculadora de Notas UAI", page_icon="🎓", layout="wide")

# ---------------------------------------------------------
# ESTILOS CSS - PALETA: DARK SLATE & VIOLETA NEÓN
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Fondo principal Dark Slate nocturno */
    .stApp {
        background-color: #0B0F19 !important;
        color: #F8FAFC !important;
    }
    
    /* Barra lateral (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1F2937 !important;
    }
    
    /* Tipografía e Instrucciones */
    .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp span {
        color: #F8FAFC !important;
    }
    
    /* Tarjetas, desplegables y campos de texto */
    div[data-testid="stExpander"], div[data-baseweb="input"], .stTextInput input, .stNumberInput input {
        background-color: #151C2C !important;
        color: #FFFFFF !important;
        border: 1px solid #2A354F !important;
        border-radius: 8px;
    }
    
    /* Borde en enfoque neón violeta */
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 8px rgba(139, 92, 246, 0.4) !important;
    }
    
    /* Tarjetas Métricas con violeta brillante */
    div[data-testid="stMetricValue"] {
        color: #A78BFA !important;
        font-weight: 700;
    }
    
    /* Separador visual */
    hr {
        border-color: #1F2937 !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Botones principales con acento Violeta */
    div.stButton > button {
        background-color: #7C3AED !important;
        color: #FFFFFF !important;
        border: None !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #8B5CF6 !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Calculadora Dinámica. MATIAS ORTIZ - UAI")
st.caption("Configura tus asignaturas asegurando que los porcentajes sumen exactamente 100%. Guardado automático disponible vía respaldo.")

# ---------------------------------------------------------
# MENÚ INICIAL DE BIENVENIDA (INICIA EN BLANCO)
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("👋 ¡Hola! ¿Qué deseas hacer hoy?")

opcion_menu = st.radio(
    "Selecciona una opción para desplegar las herramientas disponibles:",
    options=["🎓 Calcular mis notas de la universidad"],
    index=None,
    key="opcion_menu_principal"
)

if opcion_menu is None:
    st.info("👆 Selecciona la opción superior para comenzar a gestionar y calcular tus calificaciones.")

st.markdown("---")

# ---------------------------------------------------------
# DESPLIEGUE DE LA CALCULADORA TRAS SELECCIONAR LA OPCIÓN
# ---------------------------------------------------------
if opcion_menu == "🎓 Calcular mis notas de la universidad":

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

    with st.sidebar:
        st.header("💾 Respaldar y Cargar Notas")
        uploaded_file = st.file_uploader("Subir respaldo previo (.json)", type=["json"], key="file_uploader")
        
        if uploaded_file is not None:
            if st.session_state.get("last_uploaded_filename") != uploaded_file.name:
                try:
                    saved_data = json.load(uploaded_file)
                    for k, v in saved_data.items():
                        st.session_state[k] = v
                    st.session_state["last_uploaded_filename"] = uploaded_file.name
                    st.success("✅ ¡Notas cargadas! Ya puedes editarlas libremente.")
                    st.rerun()
                except Exception:
                    st.error("Error al cargar el archivo de respaldo.")
        st.divider()

    PLANTILLAS_RAMOS = {
        "CALCULO INTEGRAL": {
            "Pruebas / Certámenes": {"tiene": True, "cant": 3, "pct": 70},
            "Controles": {"tiene": True, "cant": 3, "pct": 15},
            "Laboratorio / Proyecto": {"tiene": True, "cant": 1, "pct": 15},
            "Tareas": {"tiene": False, "cant": 1, "pct": 0}
        },
        "ALGEBRA LINEAL": {
            "Pruebas / Certámenes": {"tiene": True, "cant": 3, "pct": 70},
            "Controles": {"tiene": True, "cant": 3, "pct": 15},
            "Laboratorio / Proyecto": {"tiene": True, "cant": 1, "pct": 15},
            "Tareas": {"tiene": False, "cant": 1, "pct": 0}
        },
        "ALGEBRA": {
            "Pruebas / Certámenes": {"tiene": True, "cant": 3, "pct": 70},
            "Controles": {"tiene": True, "cant": 3, "pct": 30},
            "Laboratorio / Proyecto": {"tiene": False, "cant": 1, "pct": 0},
            "Tareas": {"tiene": False, "cant": 1, "pct": 0}
        },
        "FISICA (CON TAREAS)": {
            "Pruebas / Certámenes": {"tiene": True, "cant": 3, "pct": 65},
            "Laboratorio / Proyecto": {"tiene": True, "cant": 3, "pct": 25},
            "Tareas": {"tiene": True, "cant": 3, "pct": 10},
            "Controles": {"tiene": False, "cant": 1, "pct": 0}
        }
    }

    # ---------------------------------------------------------
    # 1. CONFIGURACIÓN DE RAMOS Y PONDERACIONES (DESPLEGABLE)
    # ---------------------------------------------------------
    with st.expander("⚙️ Configuración Inicial de Ramos y Ponderaciones", expanded=False):
        
        st.markdown("### 📚 Seleccionar Ramos Predeterminados")
        ramos_pred_sel = st.multiselect(
            "Selecciona las asignaturas predefinidas que cursas:",
            options=list(PLANTILLAS_RAMOS.keys()),
            default=[],
            key="selector_predeterminados"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🛠️ Ramos Personalizados Adicionales")
        num_custom = st.number_input("¿Cuántos ramos adicionales deseas crear desde cero?", min_value=0, max_value=10, value=0, key="num_custom_input")

        lista_ramos_config = list(ramos_pred_sel) + [f"Asignatura Custom {i+1}" for i in range(int(num_custom))]
        
        estructura_ramos = {}

        for idx_ramo, nombre_default in enumerate(lista_ramos_config):
            st.markdown("---")
            st.markdown(f"### 📘 Configuración de: **{nombre_default}**")
            
            nombre_ramo = st.text_input(f"Nombre editable del ramo:", value=nombre_default, key=f"nombre_ramo_edit_{idx_ramo}").strip()
            
            if not nombre_ramo:
                nombre_ramo = f"Asignatura {idx_ramo + 1}"
                
            plantilla = PLANTILLAS_RAMOS.get(nombre_default, {
                "Pruebas / Certámenes": {"tiene": True, "cant": 2, "pct": 50},
                "Controles": {"tiene": True, "cant": 2, "pct": 50},
                "Laboratorio / Proyecto": {"tiene": False, "cant": 1, "pct": 0},
                "Tareas": {"tiene": False, "cant": 1, "pct": 0}
            })

            categorias = ["Pruebas / Certámenes", "Controles", "Laboratorio / Proyecto", "Tareas"]
            evaluaciones_ramo = []
            cols = st.columns(4)
            pct_acumulado = 0

            for cat_idx, cat in enumerate(categorias):
                with cols[cat_idx]:
                    p_info = plantilla.get(cat, {"tiene": False, "cant": 1, "pct": 0})
                    
                    st.markdown(f"**{cat}**")
                    tiene = st.checkbox(f"¿Tiene {cat}?", value=p_info["tiene"], key=f"chk_{idx_ramo}_{cat}")
                    
                    if tiene:
                        cant = st.number_input(f"Cantidad:", min_value=1, max_value=10, value=p_info["cant"], key=f"cant_{idx_ramo}_{cat}")
                        pct = st.number_input(f"% Total:", min_value=0, max_value=100, value=p_info["pct"], key=f"pct_{idx_ramo}_{cat}")
                        
                        pct_acumulado += pct
                        pond_indiv = (pct / 100.0) / cant if cant > 0 else 0.0
                        
                        for j in range(int(cant)):
                            nombre_eval = f"{cat[:-1] if cat.endswith('s') else cat} {j + 1}"
                            evaluaciones_ramo.append({
                                "Asignatura": nombre_ramo,
                                "Evaluación": nombre_eval,
                                "Ponderación (%)": round(pond_indiv * 100, 2),
                                "_pond_dec": pond_indiv
                            })

            st.write("")
            if pct_acumulado == 100:
                st.success(f"✅ ¡Perfecto! Los porcentajes de **{nombre_ramo}** suman el 100%.")
            elif pct_acumulado < 100:
                st.warning(f"⚠️ Suma actual en **{nombre_ramo}**: **{pct_acumulado}%**. Falta asignar **{100 - pct_acumulado}%**.")
            else:
                st.error(f"❌ La suma en **{nombre_ramo}** es **{pct_acumulado}%** (Supera el 100%). Ajusta los valores.")

            if evaluaciones_ramo:
                estructura_ramos[nombre_ramo] = evaluaciones_ramo

    # ---------------------------------------------------------
    # 2. PROCESAMIENTO DINÁMICO
    # ---------------------------------------------------------
    lista_filas = []

    for ramo, evals in estructura_ramos.items():
        for e in evals:
            key_rendida = f"rend_{ramo}_{e['Evaluación']}"
            key_nota = f"nota_{ramo}_{e['Evaluación']}"
            
            if key_rendida not in st.session_state:
                st.session_state[key_rendida] = False
            if key_nota not in st.session_state:
                st.session_state[key_nota] = "5,0"
            
            rendida = st.session_state[key_rendida]
            nota_raw = st.session_state[key_nota]
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
        st.info("👈 Selecciona o configura asignaturas arriba para comenzar a ingresar notas.")
        st.stop()

    df_panel = pd.DataFrame(lista_filas)

    # ---------------------------------------------------------
    # METAS POR ASIGNATURA (DESPLEGABLE)
    # ---------------------------------------------------------
    dict_metas = {}
    with st.expander("🎯 Definir Metas Objetivos por Asignatura", expanded=False):
        cols_metas = st.columns(min(len(df_panel["Asignatura"].unique()), 3))
        
        for idx_m, ramo in enumerate(df_panel["Asignatura"].unique()):
            if not ramo or str(ramo).strip() == "":
                continue
            mask_ramo = df_panel["Asignatura"] == ramo
            df_ramo = df_panel[mask_ramo]
            
            key_meta = f"meta_promedio_{ramo}"
            if key_meta not in st.session_state:
                st.session_state[key_meta] = 4.0

            with cols_metas[idx_m % 3]:
                meta_promedio = st.number_input(
                    f"Meta deseada para **{ramo}**:",
                    min_value=1.0,
                    max_value=7.0,
                    step=0.1,
                    key=key_meta
                )
                dict_metas[ramo] = meta_promedio

            df_rendidas = df_ramo[df_ramo["Rendida"] == True]
            puntos_actuales = (df_rendidas["Nota Obtenida / Requerida"] * df_rendidas["_pond_dec"]).sum()
            
            df_pendientes = df_ramo[df_ramo["Rendida"] == False]
            sum_pond_pendiente = df_pendientes["_pond_dec"].sum()
            sum_pond_total = df_ramo["_pond_dec"].sum()
            
            if sum_pond_pendiente > 0:
                puntos_necesarios = (meta_promedio * sum_pond_total) - puntos_actuales
                promedio_req = round(puntos_necesarios / sum_pond_pendiente, 2)
                promedio_req = max(1.0, min(7.0, promedio_req))
                df_panel.loc[mask_ramo & (df_panel["Rendida"] == False), "Nota Obtenida / Requerida"] = promedio_req

    st.markdown("---")

    # ---------------------------------------------------------
    # 3. PANEL DE CONTROL DE NOTAS (DESPLEGABLE POR ASIGNATURA)
    # ---------------------------------------------------------
    st.subheader("📝 Panel de Control de Notas")
    st.write("")

    df_actualizado = df_panel.copy()
    resumen_resultados = []

    for ramo in df_panel["Asignatura"].unique():
        if not ramo or str(ramo).strip() == "":
            continue

        df_ramo_filas = df_panel[df_panel["Asignatura"] == ramo]
        meta_actual = dict_metas.get(ramo, 4.0)
        
        df_ramo_pre = df_ramo_filas[df_ramo_filas["Rendida"] == True]
        sum_pond_rendida_pre = df_ramo_pre["_pond_dec"].sum()
        puntos_actuales_pre = (df_ramo_pre["Nota Obtenida / Requerida"] * df_ramo_pre["_pond_dec"]).sum()
        np_actual_pre = round(puntos_actuales_pre / sum_pond_rendida_pre, 2) if sum_pond_rendida_pre > 0 else 0.0

        # Expander individual por asignatura
        with st.expander(f"📘 {ramo} (Ponderado actual: {formatear_con_coma(np_actual_pre)} | Avance: {int(sum_pond_rendida_pre * 100)}%)", expanded=False):
            
            diferencia_meta = round(np_actual_pre - meta_actual, 2) if sum_pond_rendida_pre > 0 else 0.0

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric(
                label="📈 Nota Ponderada Actual", 
                value=formatear_con_coma(np_actual_pre),
                delta=f"{formatear_con_coma(diferencia_meta)} vs Meta" if sum_pond_rendida_pre > 0 else None
            )
            col_m2.metric(
                label="🎯 Meta Objetivo", 
                value=formatear_con_coma(meta_actual)
            )
            col_m3.metric(
                label="📊 Avance Evaluado", 
                value=f"{int(sum_pond_rendida_pre * 100)}%"
            )

            pct_progreso = min(1.0, float(sum_pond_rendida_pre))
            st.progress(
                pct_progreso, 
                text=f"Progreso evaluado del ramo: {int(sum_pond_rendida_pre * 100)}% completado ({int((1 - pct_progreso) * 100)}% pendiente)"
            )
            st.write("")

            cols_headers = st.columns([2.5, 1.5, 1.5, 2.5])
            cols_headers[0].markdown("**Evaluación**")
            cols_headers[1].markdown("**Ponderación**")
            cols_headers[2].markdown("**¿Rendida?**")
            cols_headers[3].markdown("**Nota (Obtenida / Requerida)**")
            
            for idx, row in df_ramo_filas.iterrows():
                c1, c2, c3, c4 = st.columns([2.5, 1.5, 1.5, 2.5])
                
                c1.write(row["Evaluación"])
                c2.write(f"{row['Ponderación (%)']}%")
                
                es_rendida = c3.checkbox("", key=row["_key_rend"])
                
                if es_rendida:
                    val_input = c4.text_input(
                        label=f"Nota para {row['Evaluación']}",
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
                    
            df_ramo_act = df_actualizado[df_actualizado["Asignatura"] == ramo]
            df_rendidas = df_ramo_act[df_ramo_act["Rendida"] == True]
            sum_pond_rendida = df_rendidas["_pond_dec"].sum()
            puntos_actuales = (df_rendidas["Nota Obtenida / Requerida"] * df_rendidas["_pond_dec"]).sum()
            
            np_actual = round(puntos_actuales / sum_pond_rendida, 2) if sum_pond_rendida > 0 else 0.0
            
            df_pendientes = df_ramo_act[df_ramo_act["Rendida"] == False]
            sum_pond_pendiente = df_pendientes["_pond_dec"].sum()
            sum_pond_total = df_ramo_act["_pond_dec"].sum()
            
            if sum_pond_pendiente > 0:
                puntos_necesarios = (meta_actual * sum_pond_total) - puntos_actuales
                promedio_req = round(puntos_necesarios / sum_pond_pendiente, 2)
                if promedio_req > 7.0:
                    estado_req = f"{formatear_con_coma(promedio_req)} ⚠️ (Imposible llegar al {formatear_con_coma(meta_actual)})"
                elif promedio_req <= 1.0:
                    estado_req = f"1,0 (¡Ya aseguraste el {formatear_con_coma(meta_actual)}!)"
                else:
                    estado_req = f"{formatear_con_coma(promedio_req)}"
            else:
                estado_req = "Sin evaluaciones pendientes"
                
            resumen_resultados.append({
                "Asignatura": ramo,
                "Meta Promedio": formatear_con_coma(meta_actual),
                "NP Actual (Evaluado)": formatear_con_coma(np_actual),
                "% Evaluado": f"{int(sum_pond_rendida * 100)}%",
                "Evaluaciones Pendientes": len(df_pendientes),
                f"Nota promedio requerida en pendientes (para {formatear_con_coma(meta_actual)})": estado_req
            })

    with st.sidebar:
        datos_exportar = {
            k: v for k, v in st.session_state.items() 
            if isinstance(v, (int, float, str, bool)) and k not in ["file_uploader", "last_uploaded_filename"]
        }
        json_str = json.dumps(datos_exportar, indent=2)
        
        st.download_button(
            label="📥 Descargar Respaldo de Notas",
            data=json_str,
            file_name="mis_notas_uai.json",
            mime="application/json",
            key="btn_download_json"
        )

    # ---------------------------------------------------------
    # 4. RESUMEN COMPARATIVO FINAL (DESPLEGABLE)
    # ---------------------------------------------------------
    if resumen_resultados:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📊 Resumen Comparativo de Asignaturas", expanded=True):
            st.dataframe(pd.DataFrame(resumen_resultados), use_container_width=True)
