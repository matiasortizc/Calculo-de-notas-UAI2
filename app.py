import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Notas UAI", page_icon="🎓")

st.title("🎓 Calculadora de Nota de Presentación (NP) - UAI")
st.write("Calcula tu Nota de Presentación para tus asignaturas de manera interactiva.")

num_ramos = st.number_input("¿Cuántas asignaturas deseas ingresar?", min_value=1, max_value=10, value=1)

resumen = []

for i in range(int(num_ramos)):
    st.header(f"📘 Asignatura {i + 1}")
    nombre_ramo = st.text_input(f"Nombre de la asignatura {i + 1}:", value=f"Asignatura {i + 1}", key=f"ramo_{i}")
    
    categorias = ["Pruebas / Certámenes", "Controles", "Laboratorios", "Tareas"]
    evaluaciones = []
    
    for cat in categorias:
        with st.expander(f"Configurar {cat} para {nombre_ramo}"):
            tiene_cat = st.checkbox(f"¿Tiene {cat}?", key=f"check_{cat}_{i}")
            if tiene_cat:
                cantidad = st.number_input(f"Cantidad de {cat}:", min_value=1, max_value=10, value=1, key=f"cant_{cat}_{i}")
                pct_total = st.slider(f"Porcentaje TOTAL de {cat} en la NP (%):", min_value=0, max_value=100, value=20, key=f"pct_{cat}_{i}") / 100.0
                
                pond_indiv = pct_total / cantidad
                
                for j in range(int(cantidad)):
                    st.write(f"**{cat[:-1] if cat.endswith('s') else cat} {j + 1}**")
                    tiene_nota = st.checkbox(f"¿Tienes la nota {j + 1}?", key=f"t_nota_{cat}_{i}_{j}")
                    if tiene_nota:
                        nota = st.number_input(f"Nota (1.0 - 7.0):", min_value=1.0, max_value=7.0, value=5.0, step=0.1, key=f"nota_{cat}_{i}_{j}")
                        evaluaciones.append({'nota': nota, 'pond': pond_indiv})

    # Cálculo de NP
    if evaluaciones:
        suma_pond = sum(item['pond'] for item in evaluaciones)
        if suma_pond > 0:
            np_actual = sum(item['nota'] * item['pond'] for item in evaluaciones) / suma_pond
            np_actual = round(np_actual, 2)
            pct_evaluado = int(suma_pond * 100)
        else:
            np_actual = 0.0
            pct_evaluado = 0
    else:
        np_actual = 0.0
        pct_evaluado = 0
        
    resumen.append({
        "Asignatura": nombre_ramo,
        "NP Actual": np_actual,
        "% Evaluado de la NP": f"{pct_evaluado}%"
    })
    st.divider()

if resumen:
    st.subheader("📊 Resumen de Resultados")
    df = pd.DataFrame(resumen)
    st.dataframe(df, use_container_width=True)
