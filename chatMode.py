import streamlit as st
import os

def chat_response(user_prompt, assistant_response):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(f"**You**: {message['content']}")

        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(f"**Assistant**: {message['content']}")

    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(f"**You**: {user_prompt}")

        with st.chat_message("assistant"):
            st.write(f"**Assistant**: {assistant_response}")
        
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})