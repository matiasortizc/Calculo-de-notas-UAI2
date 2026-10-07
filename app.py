import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Calculadora de notas - Matías Ortiz - UAI", page_icon="🎓", layout="wide")

# ---------------------------------------------------------
# ESTILOS CSS COMPACTOS - PALETA DARK SLATE & VIOLETA NEÓN
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #0B0F19 !important;
        color: #F8FAFC !important;
        font-size: 0.88rem !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1F2937 !important;
    }
    
    h1 { font-size: 1.6rem !important; margin-bottom: 0.3rem !important; }
    h2 { font-size: 1.3rem !important; margin-bottom: 0.3rem !important; }
    h3 { font-size: 1.05rem !important; margin-bottom: 0.2rem !important; }
    
    .stApp p, .stApp label, .stApp span, div[data-testid="stMarkdownContainer"] p {
        font-size: 0.88rem !important;
        color: #F8FAFC !important;
    }
    
    /* Estilos personalizados para la pantalla de bienvenida llamativa */
    .hero-container {
        background: linear-gradient(135deg, #151C2C 0%, #1E1B4B 100%);
        border: 1px solid #3B82F633;
        border-radius: 12px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(124, 58, 237, 0.2);
    }
    .hero-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #F8FAFC !important;
        margin-bottom: 0.5rem;
    }
    .hero-title span {
        color: #A78BFA;
    }
    .hero-subtitle {
        font-size: 1.15rem !important;
        color: #94A3B8 !important;
        max-width: 700px;
        margin: 0 auto;
    }
    
    div[data-testid="stExpander"], div[data-baseweb="input"], .stTextInput input, .stNumberInput input {
        background-color: #151C2C !important;
        color: #FFFFFF !important;
        border: 1px solid #2A354F !important;
        border-radius: 6px !important;
        padding: 2px 8px !important;
        font-size: 0.85rem !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 6px rgba(139, 92, 246, 0.3) !important;
    }
    
    div[data-testid="stMetric"] {
        background-color: #151C2C !important;
        border: 1px solid #2A354F !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
    }
    div[data-testid="stMetricValue"] {
        color: #A78BFA !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
    }
    
    hr {
        border-color: #1F2937 !important;
        margin: 0.8rem 0 !important;
    }
    
    div.stButton > button {
        background-color: #7C3AED !important;
        color: #FFFFFF !important;
        border: None !important;
        border-radius: 6px !important;
        padding: 0.4rem 1rem !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #8B5CF6 !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES AUXILIARES
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

# Control de Navegación entre Pasos
if "paso_actual" not in st.session_state:
    st.session_state["paso_actual"] = 1

def cambiar_paso(nuevo_paso):
    st.session_state["paso_actual"] = nuevo_paso
    st.rerun()

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
# BARRA LATERAL (NAVEGACIÓN DIRECTA Y RESPALDO)
# ---------------------------------------------------------
with st.sidebar:
    st.title("🎓 Calculadora UAI")
    st.caption("MATIAS ORTIZ - UAI")
    st.divider()
    
    st.markdown("### 📍 Navegación de Pasos")
    
    pasos_map = {
        "1. Bienvenida e Inicio": 1,
        "2. Configurar Asignaturas": 2,
        "3. Definir Metas Objetivos": 3,
        "4. Ingresar Notas y Resultados": 4
    }
    
    paso_inverso = {v: k for k, v in pasos_map.items()}
    nombre_paso_actual = paso_inverso.get(st.session_state["paso_actual"], "1. Bienvenida e Inicio")
    
    seleccion_sidebar = st.selectbox(
        "Ir directamente a:",
        options=list(pasos_map.keys()),
        index=list(pasos_map.keys()).index(nombre_paso_actual),
        key="select_navegacion_lateral"
    )
    
    nuevo_paso_elegido = pasos_map[seleccion_sidebar]
    if nuevo_paso_elegido != st.session_state["paso_actual"]:
        st.session_state["paso_actual"] = nuevo_paso_elegido
        st.rerun()

    st.divider()
    st.header("💾 Respaldar y Cargar Notas")
    uploaded_file = st.file_uploader("Subir respaldo (.json)", type=["json"], key="file_uploader")
    
    if uploaded_file is not None:
        if st.session_state.get("last_uploaded_filename") != uploaded_file.name:
            try:
                saved_data = json.load(uploaded_file)
                for k, v in saved_data.items():
                    st.session_state[k] = v
                st.session_state["last_uploaded_filename"] = uploaded_file.name
                st.success("✅ ¡Notas cargadas! Redirigiendo a notas...")
                st.session_state["paso_actual"] = 4
                st.rerun()
            except Exception:
                st.error("Error al cargar el archivo de respaldo.")

    datos_exportar = {
        k: v for k, v in st.session_state.items() 
        if isinstance(v, (int, float, str, bool)) and k not in ["file_uploader", "last_uploaded_filename", "paso_actual", "select_navegacion_lateral"]
    }
    json_str = json.dumps(datos_exportar, indent=2)
    
    st.download_button(
        label="📥 Descargar Respaldo (.json)",
        data=json_str,
        file_name="mis_notas_uai.json",
        mime="application/json",
        key="btn_download_json",
        use_container_width=True
    )

# =========================================================
# PASO 1: PANTALLA DE BIENVENIDA
# =========================================================
if st.session_state["paso_actual"] == 1:
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">👋 ¡Bienvenido a <span>Calculadora UAI</span>!</div>
            <div class="hero-subtitle">La herramienta definitiva para simular, planificar y dominar tus calificaciones académicas de forma rápida y sencilla.</div>
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 🚀 Comenzar desde cero")
        st.write("Configura tus ramos, pruebas, controles y laboratorios paso a paso de forma personalizada.")
        if st.button("Comenzar Configuración ➔"):
            cambiar_paso(2)

    with col_b:
        st.markdown("#### 📂 Cargar un respaldo existente")
        st.write("Si ya descargaste previamente tu archivo `.json`, súbelo desde la barra lateral izquierda para cargar tus notas guardadas al instante.")

# =========================================================
# PASO 2: CONFIGURACIÓN DE ASIGNATURAS Y PONDERACIONES
# =========================================================
elif st.session_state["paso_actual"] == 2:
    st.title("📚 Paso 2: Selección y Configuración de Asignaturas")
    st.caption("Selecciona las asignaturas predefinidas o crea nuevas. Asegúrate de que los porcentajes sumen el 100%.")
    
    st.markdown("### 📚 Ramos Predeterminados")
    ramos_pred_sel = st.multiselect(
        "Selecciona las asignaturas que cursas actualmente:",
        options=list(PLANTILLAS_RAMOS.keys()),
        default=st.session_state.get("selector_predeterminados", []),
        key="selector_predeterminados"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🛠️ Ramos Personalizados Adicionales")
    num_custom = st.number_input("¿Cuántos ramos adicionales deseas crear desde cero?", min_value=0, max_value=10, value=st.session_state.get("num_custom_input", 0), key="num_custom_input")

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

    st.session_state["estructura_ramos_cache"] = estructura_ramos

    st.markdown("---")
    col_n1, col_n2 = st.columns([1, 1])
    with col_n1:
        if st.button("⬅️ Volver a Bienvenida", use_container_width=True):
            cambiar_paso(1)
    with col_n2:
        if st.button("Siguiente: Definir Metas ➔", use_container_width=True):
            if not estructura_ramos:
                st.error("Debes seleccionar o configurar al menos un ramo antes de continuar.")
            else:
                cambiar_paso(3)

# =========================================================
# PASO 3: DEFINICIÓN DE METAS OBJETIVOS
# =========================================================
elif st.session_state["paso_actual"] == 3:
    st.title("🎯 Paso 3: Definir Metas Objetivos")
    st.caption("Establece la nota final promedio que deseas obtener en cada una de todas tus asignaturas.")
    
    estructura_ramos = st.session_state.get("estructura_ramos_cache", {})
    if not estructura_ramos:
        st.warning("No hay ramos configurados. Por favor regresa al Paso 2.")
        if st.button("⬅️ Ir a Configuración"):
            cambiar_paso(2)
        st.stop()

    dict_metas = {}
    cols_metas = st.columns(min(len(estructura_ramos.keys()), 3))
    
    for idx_m, ramo in enumerate(estructura_ramos.keys()):
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

    st.markdown("---")
    col_n1, col_n2 = st.columns([1, 1])
    with col_n1:
        if st.button("⬅️ Volver a Configuración", use_container_width=True):
            cambiar_paso(2)
    with col_n2:
        if st.button("Siguiente: Ingresar Notas ➔", use_container_width=True):
            cambiar_paso(4)

# =========================================================
# PASO 4: INGRESO DE NOTAS Y RESULTADOS
# =========================================================
elif st.session_state["paso_actual"] == 4:
    st.title("📝 Paso 4: Ingreso de Notas y Panel de Control")
    st.caption("Marca las evaluaciones rendidas, ingresa tus notas obtenidas y consulta tus requerimientos académicos.")
    
    estructura_ramos = st.session_state.get("estructura_ramos_cache", {})
    
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
        st.info("👈 No hay ramos configurados. Dirígete a la sección de configuración para comenzar.")
        if st.button("⬅️ Configurar Ramos"):
            cambiar_paso(2)
        st.stop()

    df_panel = pd.DataFrame(lista_filas)
    
    dict_metas = {}
    for ramo in df_panel["Asignatura"].unique():
        key_meta = f"meta_promedio_{ramo}"
        meta_promedio = st.session_state.get(key_meta, 4.0)
        dict_metas[ramo] = meta_promedio

        mask_ramo = df_panel["Asignatura"] == ramo
        df_ramo = df_panel[mask_ramo]
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

        with st.expander(f"📘 {ramo} (Ponderado: {formatear_con_coma(np_actual_pre)} | Avance: {int(sum_pond_rendida_pre * 100)}%)", expanded=True):
            
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
                text=f"Progreso evaluado: {int(sum_pond_rendida_pre * 100)}% completado ({int((1 - pct_progreso) * 100)}% pendiente)"
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
                    estado_req = f"{formatear_con_coma(promedio_req)} ⚠️ (Imposible)"
                elif promedio_req <= 1.0:
                    estado_req = f"1,0 (¡Asegurado!)"
                else:
                    estado_req = f"{formatear_con_coma(promedio_req)}"
            else:
                estado_req = "Sin pendientes"
                
            resumen_resultados.append({
                "Asignatura": ramo,
                "Meta Promedio": formatear_con_coma(meta_actual),
                "NP Actual (Evaluado)": formatear_con_coma(np_actual),
                "% Evaluado": f"{int(sum_pond_rendida * 100)}%",
                "Evaluaciones Pendientes": len(df_pendientes),
                f"Nota promedio requerida en pendientes (para {formatear_con_coma(meta_actual)})": estado_req
            })

    if resumen_resultados:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📊 Resumen Comparativo de Asignaturas", expanded=True):
            st.dataframe(pd.DataFrame(resumen_resultados), use_container_width=True)

    st.markdown("---")
    if st.button("⬅️ Volver a Definición de Metas", use_container_width=True):
        cambiar_paso(3)
