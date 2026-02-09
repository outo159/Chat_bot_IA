import google.generativeai as genai
import streamlit as st

genai.configure(api_key="AIzaSyAeZnZjN08Ca-GnNhLswMrQ6NEw1zgIz5k")
model = genai.GenerativeModel('gemini-2.5-flash-lite')

st.set_page_config(page_title="Chat bot con IA",page_icon="Chat bot con IA 🤖")

st.title("Chat bot con IA 🤖")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("En que puedo ayudarte?"):
    st.session_state.messages.append({"role":"user", "content":prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = model.generate_content(prompt)

        with st.chat_message("assistant"):
            st.markdown(response.text)

        st.session_state.messages.append({"role" : "assistant" , "content" : response.text})
    except Exception as e:
        st.error(f"Error: {str(e)}")
