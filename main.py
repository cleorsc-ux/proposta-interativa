# main.py

import streamlit as st
import pandas as pd
from auth import login, logout, usuario_logado
from sheets import carregar_catalogo, salvar_proposta_em_sheets
from pdf import gerar_pdf
from config import CAMPOS_EXTRAS

st.set_page_config(page_title="Proposta Interativa - Ártico PRIME", layout="wide")

# Login
if not login():
    st.stop()

logout()
user = usuario_logado()

st.title("📄 Gerador de Propostas - Ártico PRIME")

# Carga de serviços
df_catalogo = carregar_catalogo()
df_catalogo = df_catalogo.sort_values(by=["Categoria", "Serviço"])

# Agrupar por categoria
categorias = df_catalogo["Categoria"].unique()

servicos_selecionados = []
st.subheader("🛠️ Catálogo de Serviços")

for categoria in categorias:
    st.markdown(f"### 🔹 {categoria}")
    subset = df_catalogo[df_catalogo["Categoria"] == categoria]
    for _, row in subset.iterrows():
        col1, col2 = st.columns([6, 2])
        with col1:
            checked = st.checkbox(f"{row['Serviço']} ({row['Unidade']}) - R$ {row['Valor Unitário Médio (R$)']:.2f}",
                                  key=row["Serviço"])
        with col2:
            if checked:
                qtd = st.number_input(f"Qtd - {row['Serviço']}", min_value=1, value=1, key=f"qtd_{row['Serviço']}")
                servicos_selecionados.append({
                    "serviço": row["Serviço"],
                    "unidade": row["Unidade"],
                    "valor_unit": row["Valor Unitário Médio (R$)"],
                    "quantidade": qtd,
                    "total": qtd * row["Valor Unitário Médio (R$)"]
                })

# Serviço adicional manual
st.subheader("➕ Serviço Extra")
nome_extra = st.text_input("Descrição do serviço extra")
qtd_extra = st.number_input("Quantidade", min_value=1, step=1)
valor_extra = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f")

if nome_extra:
    servicos_selecionados.append({
        "serviço": nome_extra,
        "unidade": "UND",
        "valor_unit": valor_extra,
        "quantidade": qtd_extra,
        "total": qtd_extra * valor_extra
    })

# Informações do cliente
st.subheader("📇 Dados da Proposta")
nome_cliente = st.text_input("Nome do Cliente / Projeto")

# Campos extras
dados_extras = {}
for campo in CAMPOS_EXTRAS:
    dados_extras[campo] = st.text_input(campo)

# Botão de gerar proposta
if st.button("📄 Gerar PDF da Proposta"):
    if not nome_cliente:
        st.warning("Preencha o nome do cliente.")
    elif not servicos_selecionados:
        st.warning("Selecione pelo menos um serviço.")
    else:
        total_geral = sum([s["total"] for s in servicos_selecionados])

        # Gera o PDF
        pdf_file = gerar_pdf(nome_cliente, servicos_selecionados, total_geral, dados_extras, user["nome"])
        st.success("✅ Proposta gerada com sucesso!")

        st.download_button(
            label="⬇️ Baixar PDF da Proposta",
            data=pdf_file,
            file_name=f"Proposta_{nome_cliente}.pdf",
            mime="application/pdf"
        )

        # Salvar no histórico do Google Sheets
        salvar_proposta_em_sheets([
            nome_cliente,
            user["nome"],
            total_geral,
            str([s["serviço"] for s in servicos_selecionados]),
            dados_extras.get("Observações", "")
        ])
