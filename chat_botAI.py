import streamlit as st
import ollama
from typing import Generator

st.set_page_config(
    page_title="Chat bot con IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def obtener_modelos():
    try:
        respuesta = ollama.list()
        
        # Diferentes formatos de respuesta
        if hasattr(respuesta, 'models'):
            modelos = respuesta.models
        elif isinstance(respuesta, dict) and 'models' in respuesta:
            modelos = respuesta['models']
        else:
            # Asumir que la respuesta ya es la lista
            modelos = respuesta if isinstance(respuesta, list) else []
            
        return modelos
    except Exception as e:
        st.error(f"Error al obtener modelos: {e}")
        return []

modelos = obtener_modelos()

# Mostrar información de debug en sidebar
with st.sidebar:
    st.write(f"Modelos encontrados: {len(modelos)}")
    
    @st.dialog("Informacion modelo", width="large")
    def mostrarModelos(modelo):
        if modelos:
            # Buscar el modelo específico
            modelo_info = next((m for m in modelos if m.get('name') == modelo or m.get('model') == modelo), None)
            if modelo_info:
                st.json(modelo_info)
            else:
                st.warning(f"Modelo {modelo} no encontrado")
        else:
            st.warning("No hay modelos disponibles")

    def generarListaModelos():
        listaModelos = []
        for m in modelos:
            # Intentar diferentes claves posibles
            nombre = m.get('name') or m.get('model') or m.get('model_name') or str(m)
            listaModelos.append(nombre)
        return listaModelos

if 'messages' not in st.session_state:
    st.session_state.messages = []
    promptSistema = """Siempre vas a responder en español. Te llamas Pedrito
                        y responderas preguntas de cultura general
                        """
    st.session_state.messages.append({"role": "system", "content": promptSistema})

with st.sidebar:
    opciones = generarListaModelos()
    if opciones:
        param_Modelo = st.selectbox("Modelos disponibles", options=opciones)
        btnVerInfoModelos = st.button("ver informacion")
        if btnVerInfoModelos:
            mostrarModelos(param_Modelo)
    else:
        st.warning("No hay modelos disponibles. Ejecuta: ollama pull llama3")
        param_Modelo = None

def generarRespuesta(chat_completion) -> Generator[str, None, None]:
    for chunk in chat_completion:
        if chunk.get('message', {}).get('content'):
            yield chunk['message']['content']
        elif chunk.get('content'):
            yield chunk['content']

# Mostrar historial de chat
with st.container():
    for message in st.session_state.messages:
        if message["role"] != "system":  # No mostrar mensajes del sistema
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

prompt = st.chat_input("Sobre que quieres saber???")

if prompt and param_Modelo:
    # Mostrar prompt del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Preparar mensajes para Ollama (excluyendo el system prompt si es necesario)
    messages_for_ollama = [
        {"role": m["role"], "content": m["content"]} 
        for m in st.session_state.messages 
        if m["role"] != "system"  # Algunos modelos no soportan system role
    ]
    
    # Agregar system prompt como user si es necesario
    system_messages = [m for m in st.session_state.messages if m["role"] == "system"]
    if system_messages:
        messages_for_ollama.insert(0, {"role": "user", "content": system_messages[0]["content"]})

    try:
        chat_completion = ollama.chat(
            model=param_Modelo,
            messages=messages_for_ollama,
            stream=True
        )

        # Generar y mostrar respuesta
        with st.chat_message("assistant"):
            chat_responses_generator = generarRespuesta(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"Error al generar respuesta: {e}")
        st.info("Asegúrate que el modelo está descargado: ollama pull nombre_modelo")

elif prompt and not param_Modelo:
    st.warning("Por favor, selecciona un modelo primero")
