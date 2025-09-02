# auth.py

import streamlit as st
import json
from pathlib import Path

USERS_FILE = "users.json"

def carregar_usuarios():
    if not Path(USERS_FILE).exists():
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def autenticar(usuario, senha):
    usuarios = carregar_usuarios()
    for user in usuarios:
        if user["usuario"] == usuario and user["senha"] == senha:
            return user
    return None

def login():
    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if st.session_state.usuario:
        st.sidebar.success(f"Logado como: {st.session_state.usuario['nome']}")
        return True

    st.sidebar.title("🔐 Login")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        user = autenticar(usuario, senha)
        if user:
            st.session_state.usuario = user
            st.rerun()
        else:
            st.sidebar.error("Usuário ou senha incorretos.")

    return False

def logout():
    if st.sidebar.button("Sair"):
        st.session_state.usuario = None
        st.rerun()

def usuario_logado():
    return st.session_state.get("usuario")

def is_admin():
    user = usuario_logado()
    return user and user["papel"] == "admin"
