import streamlit as st
import json
import os

# Caminho do arquivo de usuários
USUARIOS_PATH = "usuarios.json"

def carregar_usuarios():
    if os.path.exists(USUARIOS_PATH):
        with open(USUARIOS_PATH, "r") as f:
            return json.load(f)
    return []

def login():
    if "usuario" not in st.session_state:
        st.title("🔐 Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            usuarios = carregar_usuarios()
            for user in usuarios:
                if user["usuario"].lower() == usuario.lower() and user["senha"] == senha:
                    st.session_state.usuario = user
                    st.success("Login realizado com sucesso!")
                    st.rerun()
            st.error("Usuário ou senha inválidos.")
            return False
        
        return False  # Se botão não foi clicado ainda
    return True

def logout():
    if st.sidebar.button("🔓 Sair"):
        del st.session_state.usuario
        st.experimental_rerun()

def usuario_logado():
    return st.session_state.usuario
