import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

from config import NOME_PLANILHA_CATALOGO, ABA_CATALOGO

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Função para conectar ao Google Sheets
def conectar_sheets():
    credentials_dict = st.secrets["google_sheets_credentials"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client.open_by_key(NOME_PLANILHA_CATALOGO)

# Carrega os dados da aba do catálogo
def carregar_catalogo():
    planilha = conectar_sheets()
    aba = planilha.worksheet(ABA_CATALOGO)
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    return df

st.set_page_config(page_title="📄 Gerador de Propostas - Ártico PRIME", layout="wide")
st.markdown("## 📄 Gerador de Propostas - Ártico PRIME")
st.markdown("Usuário logado: **CLEO**")

st.subheader("🔢 Selecione os serviços para esta proposta")

catalogo = carregar_catalogo()
catalogo.columns = catalogo.columns.str.strip().str.lower().str.normalize('NFKD')\
    .str.encode('ascii', errors='ignore').str.decode('utf-8')

servicos_selecionados = []
categorias = catalogo["categoria"].dropna().unique()

for categoria in categorias:
    st.markdown(f"### 🔹 **{categoria.upper()}**")
    subset = catalogo[catalogo["categoria"] == categoria]

    for i, row in subset.iterrows():
        col1, col2, col3 = st.columns([6, 2, 2])

        with col1:
            selecionado = st.checkbox(f"{row['servico']} ({row['unidade']})", key=f"check_{i}")

        if selecionado:
            with col2:
                valor_unit = st.number_input(
                    label="🔥 Valor unitário",
                    value=float(row['valor unitario']) if row['valor unitario'] != '' else 0.0,
                    min_value=0.0,
                    step=10.0,
                    key=f"valor_{i}
                )
            with col3:
                qtd = st.number_input(
                    label="Qtd",
                    value=1,
                    min_value=1,
                    step=1,
                    key=f"qtd_{i}"
                )
            servicos_selecionados.append({
                "servico": row["servico"],
                "unidade": row["unidade"],
                "valor_unit": valor_unit,
                "quantidade": qtd,
                "total": valor_unit * qtd
            })

# 📊 Resumo dos Serviços Selecionados
if servicos_selecionados:
    st.markdown("## 📊 Resumo dos Serviços Selecionados")
    df_resumo = pd.DataFrame(servicos_selecionados)

    df_resumo["valor_unit"] = df_resumo["valor_unit"].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_resumo["total"] = df_resumo["total"].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(df_resumo, use_container_width=True)

    total_geral = sum(
        float(x["total"].replace("R$", "").replace(".", "").replace(",", "."))
        for x in df_resumo.to_dict(orient="records")
    )

    st.markdown(f"### 💰 Total Geral: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
