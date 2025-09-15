import streamlit as st
import json

def autenticar():
    with open("usuarios.json", "r", encoding="utf-8") as f:
        usuarios = json.load(f)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            for u in usuarios:
                if usuario == u["usuario"] and senha == u["senha"]:
                    st.session_state["autenticado"] = True
                    st.session_state["nome"] = u["nome"]
                    st.session_state["usuario"] = usuario
                    st.session_state["tipo"] = u["tipo"]
                    st.success(f"Bem-vindo, {u['nome']}!")
                    st.rerun()

            st.error("Usuário ou senha incorretos.")

    if not st.session_state["autenticado"]:
        st.stop()
