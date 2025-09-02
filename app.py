import streamlit as st
from auth import autenticar_usuario

st.set_page_config(
    page_title="Ártico PRIME - Propostas",
    page_icon="📄",
    layout="wide"
)

# Autenticação multiusuário
usuario = autenticar_usuario()

# Se logado, continua o sistema
if usuario:
    st.sidebar.success(f"Bem-vindo(a), {usuario['nome']} 👷‍♀️")
    
    # Aqui futuramente entra a lógica da proposta
    st.title("📄 Sistema de Propostas Interativas - Ártico PRIME")
    st.write("Este sistema está em desenvolvimento. Em breve você poderá gerar propostas personalizadas para sua construtora.")
