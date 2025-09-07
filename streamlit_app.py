# streamlit_app.py

import streamlit as st
import os
from auth import autenticar
from pdf import gerar_pdf

# Autenticação (antes de qualquer coisa)
autenticar()

# Configuração da página
st.set_page_config(page_title="Gerador de Propostas - Ártico PRIME", layout="centered")

st.markdown("# 📄 Gerador de Propostas - Ártico PRIME")
st.markdown("Preencha os dados da proposta abaixo para gerar um PDF personalizado.")

with st.form("form_proposta"):
    st.subheader("📟 Informações do Cliente")
    cliente = st.text_input("Nome do Cliente", placeholder="Ex: Condomínio Ilhas Vivence")
    projeto = st.text_input("Nome do Projeto", placeholder="Ex: Reparo da Fachada Bloco A")

    st.subheader("🛠️ Detalhes da Proposta")
    servicos = st.text_area("Serviços (separados por vírgula)", placeholder="Ex: Pintura, Limpeza de calha, Impermeabilização")
    valor_total = st.number_input("Valor Total da Proposta (R$)", min_value=0.0, step=100.0, format="%.2f")

    prazo = st.text_input("Prazo de Execução", value="7 dias útis")
    garantias = st.text_input("Garantias", value="90 dias contra defeitos")
    observacoes = st.text_area("Observações", value="Esta proposta está sujeita a alterações conforme avaliação técnica da obra.")

    st.subheader("👤 Responsável pela Proposta")
    usuario_nome = st.session_state["nome"]  # Nome obtido após autenticar()
    st.text(f"Usuário logado: {usuario_nome}")

    gerar = st.form_submit_button("📌 Gerar Proposta em PDF")

if gerar:
    if not cliente or not projeto or not servicos or valor_total <= 0:
        st.warning("⚠️ Preencha todos os campos obrigatórios antes de gerar a proposta.")
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

        caminho_pdf = gerar_pdf(dados_proposta, usuario_nome)

        with open(caminho_pdf, "rb") as f:
            st.success("✅ Proposta gerada com sucesso!")
            st.download_button(
                label="📅 Baixar PDF",
                data=f,
                file_name=os.path.basename(caminho_pdf),
                mime="application/pdf"
            )

        st.info("Verifique o arquivo baixado ou salve para envio ao cliente.")
