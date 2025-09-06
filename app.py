# app.py

import streamlit as st
from pdf import gerar_pdf

# Base fictícia de usuários (futuramente pode vir do secrets.toml)
usuarios = {
    "admin": {"senha": "1234", "nome": "Administrador"},
    "cleo": {"senha": "senha123", "nome": "Cleo Ribeiro"}
}

# Função de autenticação
def autenticar_usuario():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.sidebar.title("🔐 Login")
        usuario_input = st.sidebar.text_input("Usuário")
        senha_input = st.sidebar.text_input("Senha", type="password")
        if st.sidebar.button("Entrar"):
            if usuario_input in usuarios and usuarios[usuario_input]["senha"] == senha_input:
                st.session_state.autenticado = True
                st.session_state.usuario = usuarios[usuario_input]
                st.rerun()
            else:
                st.sidebar.error("Usuário ou senha incorretos.")
        return None
    else:
        return st.session_state.usuario

# Inicia autenticação
usuario = autenticar_usuario()

# Se autenticado, mostra o formulário
if usuario:
    st.title("🧾 Sistema de Propostas Interativas")
    st.markdown("---")

    st.subheader("📋 Dados da Proposta")

    cliente = st.text_input("Nome do Cliente")
    projeto = st.text_input("Nome do Projeto")
    servicos = st.text_area("Serviços (separados por vírgula)", help="Ex: Pintura, Revestimento, Impermeabilização")
    valor_total = st.number_input("Valor Total da Proposta (R$)", min_value=0.0, format="%.2f")
    prazo = st.number_input("Prazo de Execução (dias)", min_value=1, step=1)

    if st.button("📄 Gerar PDF da proposta"):
        if not cliente or not projeto or not servicos or not valor_total or not prazo:
            st.warning("Por favor, preencha todos os campos.")
        else:
            dados_proposta = {
                "cliente": cliente,
                "projeto": projeto,
                "servicos": servicos,
                "valor_total": valor_total,
                "prazo": prazo
            }
            caminho_pdf = gerar_pdf(dados_proposta, usuario["nome"])
            with open(caminho_pdf, "rb") as f:
                st.success("✅ Proposta gerada com sucesso!")
                st.download_button("📥 Baixar Proposta PDF", data=f, file_name="proposta.pdf", mime="application/pdf")
