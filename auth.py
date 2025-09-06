import streamlit as st
import json

# Carrega usuários e tenants
def carregar_usuarios():
    with open("usuarios.json", "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_tenants():
    with open("tenants.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Autenticação
def autenticar_usuario():
    if "usuario" not in st.session_state:
        st.title("🔐 Login")

        tenants = carregar_tenants()
        tenant_nomes = [t["nome_empresa"] for t in tenants]
        empresa = st.selectbox("Selecione sua empresa", tenant_nomes)
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            tenant = next((t for t in tenants if t["nome_empresa"] == empresa), None)
            if tenant:
                tenant_id = tenant["id"]
                usuarios = carregar_usuarios()
                for u in usuarios:
                    if u["usuario"].lower() == usuario.lower() and u["senha"] == senha and u["tenant_id"] == tenant_id:
                        st.session_state.usuario = u
                        st.session_state.tenant_id = tenant_id
                        st.success("Login realizado com sucesso!")
                        st.rerun()
            st.error("Credenciais inválidas ou empresa incorreta.")
            return None, None

        return None, None

    return st.session_state.tenant_id, st.session_state.usuario
