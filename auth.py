# auth.py
import streamlit as st
import json

def autenticar():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔐 Login - Ártico PRIME")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        login = st.button("Entrar")

        if login:
            try:
                with open("usuarios.json", "r") as f:
                    usuarios = json.load(f)
                for u in usuarios:
                    if u["usuario"] == usuario and u["senha"] == senha:
                        st.session_state.autenticado = True
                        st.session_state["usuario"] = usuario
                        st.session_state["nome"] = u["nome"]
                        st.rerun()
                st.error("Usuário ou senha inválidos")
            except FileNotFoundError:
                st.error("Arquivo de usuários não encontrado!")

    if not st.session_state.autenticado:
        st.stop()
