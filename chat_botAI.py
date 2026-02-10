import google.generativeai as genai
import streamlit as st

st.set_page_config(page_title="Chat bot con IA", page_icon="🤖")
st.title("Chat bot con IA 🤖")

# Sidebar para configuración de API key
with st.sidebar:
    st.header("🔑 Configuración")
    
    # Opción para ingresar o pegar la API key
    api_key = st.text_input(
        "Ingresa tu API Key de Google AI Studio",
        type="password",
        help="Obtén tu API key en: https://makersuite.google.com/app/apikey"
    )
    
    # Información adicional
    st.markdown("---")
    st.markdown("**Nota:** Tu API key se usa solo en esta sesión y no se almacena permanentemente.")
    
    # Enlace para obtener API key
    st.markdown("[Obtener API Key](https://makersuite.google.com/app/apikey)")

# Verificar si se ingresó una API key
if not api_key:
    st.info("👈 Por favor, ingresa tu API Key de Google AI Studio en la barra lateral para comenzar.")
    st.stop()

# Configurar el modelo con la API key proporcionada por el usuario
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"Error al configurar la API: {str(e)}")
    st.info("Por favor, verifica que tu API key sea correcta.")
    st.stop()

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de chat
if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Mostrar indicador de carga mientras se genera la respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # Generar respuesta
                response = model.generate_content(prompt)
                
                # Mostrar respuesta
                st.markdown(response.text)
                
                # Agregar respuesta al historial
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
