import streamlit as st
from pdf import gerar_pdf
from datetime import datetime

st.set_page_config(page_title="Proposta Interativa - Ártico PRIME", layout="centered")
st.title("📄 Gerador de Propostas - Ártico PRIME")
st.write("Preencha os dados da proposta abaixo:")

with st.form("form_proposta"):
    cliente = st.text_input("Nome do Cliente")
    projeto = st.text_input("Nome do Projeto")
    servicos = st.text_area("Serviços (separados por vírgula)", height=150)
    valor_total = st.number_input("Valor Total da Proposta (R$)", min_value=0.0, step=100.0, format="%.2f")

    prazo = st.selectbox("Prazo de Execução", [
        "7 dias úteis",
        "15 dias corridos",
        "30 dias corridos",
        "A definir após vistoria"
    ])

    garantias = st.selectbox("Garantias", [
        "90 dias contra defeitos",
        "6 meses contra infiltrações",
        "1 ano de garantia estrutural",
        "Sem garantia"
    ])

    observacoes = st.text_area(
        "Observações",
        value="Esta proposta está sujeita a alterações conforme avaliação técnica da obra.",
        height=100
    )

    usuario_logado = st.text_input("Seu nome (quem está gerando a proposta)")
    enviar = st.form_submit_button("Gerar Proposta")

if enviar:
    if not all([cliente, projeto, servicos, valor_total, prazo, garantias, usuario_logado]):
        st.error("❌ Por favor, preencha todos os campos obrigatórios.")
    else:
        dados_proposta = {
            "cliente": cliente,
            "projeto": projeto,
            "servicos": servicos,
            "valor_total": valor_total,
            "prazo": prazo,
            "garantias": garantias,
            "observacoes": observacoes
        }

        caminho = gerar_pdf(dados_proposta, usuario_logado)
        st.success("✅ Proposta gerada com sucesso!")
        with open(caminho, "rb") as file:
            st.download_button(
                label="📥 Baixar Proposta em PDF",
                data=file,
                file_name=caminho.split("/")[-1],
                mime="application/pdf"
            )
