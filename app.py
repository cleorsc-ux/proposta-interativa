import streamlit as st
from pdf import gerar_pdf

st.set_page_config(page_title="Proposta Interativa - Ártico PRIME", layout="centered")

st.title("📄 Gerar Proposta Comercial")

with st.form("formulario_proposta"):
    st.subheader("Informações da Proposta")

    cliente = st.text_input("Cliente")
    projeto = st.text_input("Projeto")
    servicos = st.text_area("Serviços (separados por vírgula)", help="Ex: Pintura, Impermeabilização, Manutenção")
    valor_total = st.number_input("Valor Total da Proposta (R$)", min_value=0.0, step=100.0)
    prazo = st.number_input("Prazo de Execução (dias)", min_value=1, step=1)

    st.subheader("Responsável pela Proposta")
    usuario_nome = st.text_input("Seu Nome")

    enviado = st.form_submit_button("Gerar Proposta 📤")

if enviado:
    if not all([cliente, projeto, servicos, valor_total, prazo, usuario_nome]):
        st.error("Por favor, preencha todos os campos.")
    else:
        dados = {
            "cliente": cliente,
            "projeto": projeto,
            "servicos": servicos,
            "valor_total": valor_total,
            "prazo": prazo
        }

        caminho_pdf = gerar_pdf(dados_proposta=dados, usuario=usuario_nome)
        st.success("✅ Proposta gerada com sucesso!")
        st.download_button("📥 Baixar Proposta PDF", data=open(caminho_pdf, "rb"), file_name=caminho_pdf.split("/")[-1])
