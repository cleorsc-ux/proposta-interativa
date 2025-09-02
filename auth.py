import streamlit as st
import json
import os

# Caminho do arquivo de usuários
USUARIOS_PATH = "usuarios.json"

# Função para carregar os usuários salvos
def carregar_usuarios():
    if os.path.exists(USUARIOS_PATH):
        with open(USUARIOS_PATH, "r") as f:
            return json.load(f)
    return []

# Função de login com Streamlit
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
        
        return False  # Se o botão ainda não foi clicado
    return True

# Função de logout
def logout():
    if st.sidebar.button("🔓 Sair"):
        del st.session_state.usuario
        st.experimental_rerun()

# Função auxiliar para retornar usuário logado
def usuario_logado():
    return st.session_state.usuario

# ✅ Função principal usada no app.py
def autenticar_usuario():
    if login():
        return st.session_state.usuario
    return None
