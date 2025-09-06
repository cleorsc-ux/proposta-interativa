# app.py

import streamlit as st
from pdf import gerar_pdf

st.set_page_config(page_title="Gerador de Propostas - Ártico PRIME", layout="centered")

st.title("📄 Gerador de Propostas - Ártico PRIME")
st.markdown("Preencha os dados da proposta abaixo:")

# Formulário
with st.form("form_proposta"):
    cliente = st.text_input("Nome do Cliente")
    projeto = st.text_input("Nome do Projeto")
    servicos = st.text_area("Serviços (separados por vírgula)")
    valor_total = st.number_input("Valor Total da Proposta (R$)", min_value=0.0, step=100.0)
    prazo = st.text_input("Prazo de Execução", value="7 dias úteis")
    garantias = st.text_input("Garantias", value="90 dias contra defeitos")
    observacoes = st.text_area("Observações", value="Esta proposta está sujeita a alterações conforme avaliação técnica da obra.")
    usuario = st.text_input("Seu nome (quem está gerando a proposta)")

    submitted = st.form_submit_button("📄 Gerar Proposta")

# Ação após envio
if submitted:
    if not cliente or not projeto or not servicos or not valor_total or not usuario:
        st.warning("⚠️ Por favor, preencha todos os campos obrigatórios.")
    else:
        with st.spinner("Gerando proposta em PDF..."):
            dados_proposta = {
                "cliente": cliente,
                "projeto": projeto,
                "servicos": servicos,
                "valor_total": valor_total,
                "prazo": prazo,
                "garantias": garantias,
                "observacoes": observacoes
            }

            caminho_pdf = gerar_pdf(dados_proposta, usuario)

        st.success("✅ Proposta gerada com sucesso!")
        with open(caminho_pdf, "rb") as file:
            st.download_button(
                label="📥 Baixar Proposta em PDF",
                data=file,
                file_name=caminho_pdf.split("/")[-1],
                mime="application/pdf"
            )
