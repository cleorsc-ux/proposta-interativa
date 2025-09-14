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

# ——— Carrega Catálogo
data = carregar_catalogo()
data.columns = data.columns.str.strip().str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
categorias = data["categoria"].dropna().unique()

# ——— Seleção de serviços
st.subheader("🔢 Selecione os serviços para esta proposta")
servicos_selecionados = []

for categoria in categorias:
    st.markdown(f"### 🔹 **{categoria.upper()}**")
    subset = data[data["categoria"] == categoria]

    for _, row in subset.iterrows():
        servico = row["servico"] or "(Serviço sem nome)"
        unidade = row["unidade"] or "UND"

        col1, col2, col3 = st.columns([5, 2, 2])
        with col1:
            marcado = st.checkbox(f"{servico} ({unidade})", key=servico)

        if marcado:
            with col2:
                valor_unit = st.number_input(
                    f"🔥 Valor unitário - {servico}",
                    min_value=0.0,
                    value=float(row["valor_unitario"]),
                    step=100.0,
                    format="%.2f",
                    key=f"valor_{servico}"
                )
            with col3:
                qtd = st.number_input(
                    f"📦 Qtd - {servico}",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"qtd_{servico}"
                )

            total = valor_unit * qtd

            servicos_selecionados.append({
                "servico": servico,
                "unidade": unidade,
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
