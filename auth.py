import streamlit as st
import json
import os

USERS_FILE = "users.json"

def carregar_usuarios():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def autenticar_usuario():
    if "usuario_autenticado" not in st.session_state:
        st.session_state.usuario_autenticado = None

    if st.session_state.usuario_autenticado:
        usuario = st.session_state.usuario_autenticado
        st.sidebar.success(f"👤 {usuario['nome']} ({usuario['tipo']})")
        if st.sidebar.button("🔒 Sair"):
            st.session_state.usuario_autenticado = None
            st.experimental_rerun()
        return usuario

    st.sidebar.title("🔐 Login de Usuário")
    usuario_input = st.sidebar.text_input("Usuário")
    senha_input = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        usuarios = carregar_usuarios()
        for user in usuarios:
            if user["usuario"] == usuario_input and user["senha"] == senha_input:
                st.session_state.usuario_autenticado = user
                st.success("Login realizado com sucesso!")
                st.experimental_rerun()
                return user
        st.error("Usuário ou senha inválidos.")

    return None
