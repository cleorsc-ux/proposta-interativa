from gerar_pdf import gerar_pdf
import streamlit as st

# Simulação (depois esses dados virão de um formulário)
dados_proposta = {
    "cliente": "Construtora Exemplo",
    "projeto": "Edifício Residencial",
    "servicos": "Fundação, Estrutura, Acabamento",
    "valor_total": 125000.00,
    "prazo": 60
}

if st.button("Gerar PDF da proposta"):
    caminho = gerar_pdf(dados_proposta, usuario)
    with open(caminho, "rb") as f:
        st.download_button("📥 Baixar PDF", data=f, file_name="proposta.pdf")


# Base de dados fictícia de usuários
usuarios = {
    "admin": {"senha": "1234", "nome": "Administrador"},
    "engenheiro": {"senha": "obras123", "nome": "Engenheiro João"},
    "arquiteta": {"senha": "design456", "nome": "Arquiteta Maria"}
}

def autenticar_usuario():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.sidebar.title("🔐 Login")
        usuario_input = st.sidebar.text_input("Usuário")
        senha_input = st.sidebar.text_input("Senha", type="password")
        botao_login = st.sidebar.button("Entrar")

        if botao_login:
            if usuario_input in usuarios and usuarios[usuario_input]["senha"] == senha_input:
                st.session_state.autenticado = True
                st.session_state.usuario = usuarios[usuario_input]
                st.success("Login realizado com sucesso.")
                st.rerun()
            else:
                st.sidebar.error("Usuário ou senha incorretos.")
        return None
    else:
        return st.session_state.usuario
