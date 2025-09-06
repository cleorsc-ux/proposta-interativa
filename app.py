import streamlit as st
from pdf import gerar_pdf

st.set_page_config(page_title="Gerar Proposta Comercial", layout="centered")
st.title("📄 Gerar Proposta Comercial")

with st.form("form_proposta"):
    st.subheader("Informações da Proposta")
    cliente = st.text_input("Cliente")
    projeto = st.text_input("Projeto")
    servicos = st.text_area("Serviços (separados por vírgula)")
    valor_total = st.number_input("Valor Total da Proposta (R$)", min_value=0.0, step=100.0, format="%.2f")
    prazo = st.text_input("Prazo de Execução")
    garantias = st.text_input("Garantias")
    observacoes = st.text_area("Observações Adicionais")

    st.subheader("Usuário Responsável")
    usuario = st.text_input("Seu nome")

    gerar = st.form_submit_button("Gerar Proposta")

if gerar:
    if not cliente or not projeto or not servicos or valor_total == 0.0 or not usuario:
        st.error("Por favor, preencha todos os campos obrigatórios.")
    else:
        dados = {
            "cliente": cliente,
            "projeto": projeto,
            "servicos": servicos,
            "valor_total": valor_total,
            "prazo": prazo,
            "garantias": garantias,
            "observacoes": observacoes
        }
        caminho = gerar_pdf(dados, usuario)
        st.success("✅ Proposta gerada com sucesso!")
        with open(caminho, "rb") as f:
            st.download_button(
                label="📥 Baixar PDF",
                data=f,
                file_name=caminho.split("/")[-1],
                mime="application/pdf"
            )
