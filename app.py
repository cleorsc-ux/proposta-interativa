import streamlit as st
import pandas as pd
from sheets import carregar_catalogo
from auth import autenticar
from pdf import gerar_pdf
import os

# Autenticação
autenticar()

st.set_page_config(page_title="Gerador de Propostas - Ártico PRIME", layout="wide")
st.markdown("# 📄 Gerador de Propostas - Ártico PRIME")
st.markdown(f"Usuário logado: **{st.session_state['nome']}**")

st.subheader("🧾 Catálogo Oficial de Serviços")

catalogo = carregar_catalogo()

# Normaliza nomes de colunas
catalogo.columns = catalogo.columns.str.strip().str.lower().str.normalize('NFKD')\
    .str.encode('ascii', errors='ignore').str.decode('utf-8')

categorias = catalogo["categoria"].dropna().unique()
servicos_selecionados = []

for categoria in categorias:
    st.markdown(f"## 🔹 {categoria}")
    subset = catalogo[catalogo["categoria"] == categoria]

    for _, row in subset.iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([6, 2, 2])
            with col1:
                check = st.checkbox(f"{row['servico']} ({row['unidade']})", key=row['servico'])
            with col2:
                valor_unit = st.number_input(
                    "🔥 Valor unitário",
                    min_value=0.00,
                    format="%.2f",
                    step=1.00,
                    value=row["valor_unitario"] if pd.notnull(row["valor_unitario"]) else 0.00,
                    key=f"valor_{row['servico']}"
                )
            with col3:
                qtd = st.number_input(
                    "📦 Qtd",
                    min_value=1,
                    step=1,
                    value=1,
                    key=f"qtd_{row['servico']}"
                )

            if check:
                total = valor_unit * qtd
                servicos_selecionados.append({
                    "servico": row["servico"],
                    "unidade": row["unidade"],
                    "valor_unit": valor_unit,
                    "quantidade": qtd,
                    "total": total
                })

# ——— Tabela Resumo
if servicos_selecionados:
    st.markdown("### 📊 **Resumo dos Serviços Selecionados**")
    df = pd.DataFrame(servicos_selecionados)
    df["valor_unit"] = df["valor_unit"].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df["total"] = df["total"].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.dataframe(df, use_container_width=True)

    total_geral = sum([float(x['total'].replace("R$", "").replace(".", "").replace(",", ".")) for x in df.to_dict(orient="records")])
    st.markdown(f"### 💰 **Total Geral: R$ {total_geral:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))

# ——— Dados da proposta
st.subheader("📄 Dados da Proposta")
cliente = st.text_input("👤 Nome do Cliente ou Projeto", placeholder="Ex: Condomínio Ilhas Vivence")
prazo = st.text_input("🗓 Prazo de Execução", value="7 dias úteis")
garantias = st.text_input("🛡 Garantias", value="90 dias contra defeitos")
observacoes = st.text_area("📝 Observações", value="Esta proposta está sujeita a avaliação técnica da obra.")

# ——— Botão para gerar proposta
if st.button("📅 Gerar Proposta em PDF"):
    if not cliente:
        st.warning("Preencha o nome do cliente.")
    elif not servicos_selecionados:
        st.warning("Selecione pelo menos um serviço.")
    else:
        total_real = sum(item["total"] for item in servicos_selecionados)
        caminho_pdf = gerar_pdf(
            cliente=cliente,
            servicos=servicos_selecionados,
            total=total_real,
            extras={"prazo": prazo, "garantias": garantias, "obs": observacoes},
            usuario=st.session_state["nome"]
        )

        with open(caminho_pdf, "rb") as f:
            st.success("✅ Proposta gerada com sucesso!")
            st.download_button("⬇️ Baixar PDF", data=f, file_name=os.path.basename(caminho_pdf), mime="application/pdf")
