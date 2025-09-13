# app.py

import streamlit as st
import os
from auth import autenticar
from pdf import gerar_pdf
from sheets import carregar_catalogo

# Autenticação do usuário
autenticar()  # Define st.session_state["nome"]

# Configuração da página
st.set_page_config(page_title="Gerador de Propostas - Ártico PRIME", layout="wide")

st.markdown("# 📄 Gerador de Propostas - Ártico PRIME")
st.markdown(f"Usuário logado: **{st.session_state['nome']}**")
# ————📋 Catálogo Oficial de Serviços (clicável)
st.subheader("🔢 Selecione os serviços para esta proposta")
servicos_selecionados = []

# Carrega o catálogo do Google Sheets
catalogo = carregar_catalogo()

# Normaliza os nomes das colunas
catalogo.columns = catalogo.columns.str.strip().str.lower().str.normalize('NFKD')\
    .str.encode('ascii', errors='ignore').str.decode('utf-8')

categorias = catalogo["categoria"].dropna().unique()

for cat in categorias:
    st.markdown(f"### 🔹 {cat}")
    subset = catalogo[catalogo["categoria"] == cat]
    for _, row in subset.iterrows():
        col1, col2 = st.columns([6, 2])
        with col1:
            checked = st.checkbox(
                f"{row['servico']} ({row['unidade']}) - R$ {row['valor_unitario']:.2f}",
                key=row['servico']
            )
        with col2:
            if checked:
                qtd = st.number_input(f"Qtd - {row['servico']}", min_value=1, value=1, key=f"qtd_{row['servico']}")
                servicos_selecionados.append({
                    "servico": row["servico"],
                    "unidade": row["unidade"],
                    "valor_unit": row["valor_unitario"],
                    "quantidade": qtd,
                    "total": row["valor_unitario"] * qtd
                })

# ————📊 Resumo dos serviços selecionados
if servicos_selecionados:
    st.markdown("### 📊 Resumo dos Serviços Selecionados")
    df_resumo = pd.DataFrame(servicos_selecionados)
    df_resumo["valor_unit"] = df_resumo["valor_unit"].map("R$ {:,.2f}".format)
    df_resumo["total"] = df_resumo["total"].map("R$ {:,.2f}".format)
    st.dataframe(df_resumo[["servico", "unidade", "quantidade", "valor_unit", "total"]], use_container_width=True)

    total_geral = sum(
        float(str(x["total"]).replace("R$", "").replace(".", "").replace(",", "."))
        for x in df_resumo.to_dict(orient="records")
    )
    st.markdown(f"### 💰 Total Geral: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# ————📄 Dados da proposta
st.subheader("📄 Dados da Proposta")
cliente = st.text_input("Nome do Cliente ou Projeto", placeholder="Ex: Condomínio Ilhas Vivence")
prazo = st.text_input("Prazo de Execução", value="7 dias úteis")
garantias = st.text_input("Garantias", value="90 dias contra defeitos")
observacoes = st.text_area("Observações", value="Esta proposta está sujeita a alterações conforme avaliação técnica da obra.")

# ————📁 Gerar PDF
if st.button("📅 Gerar Proposta em PDF"):
    if not cliente:
        st.warning("Preencha o nome do cliente.")
    elif not servicos_selecionados:
        st.warning("Selecione ao menos um serviço.")
    else:
        total = sum(item["total"] for item in servicos_selecionados)
        pdf_path = gerar_pdf(
            cliente=cliente,
            servicos=servicos_selecionados,
            total=total,
            extras={
                "prazo": prazo,
                "garantias": garantias,
                "obs": observacoes
            },
            usuario=st.session_state["nome"]
        )

        with open(pdf_path, "rb") as f:
            st.success("✅ Proposta gerada com sucesso!")
            st.download_button("⬇️ Baixar PDF", data=f, file_name=os.path.basename(pdf_path), mime="application/pdf")
            st.info("Verifique o arquivo baixado ou envie para o cliente.")
