import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Conectar ao Google Sheets usando secrets
def conectar_sheets():
    credentials_dict = st.secrets["google"]["service_account"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    client = gspread.authorize(credentials)

    # Lê o ID da planilha a partir do secrets
    sheet_id = st.secrets["google"]["catalog_sheet_id"]
    return client.open_by_key(sheet_id)

# Carregar catálogo (com normalização de colunas)
def carregar_catalogo():
    planilha = conectar_sheets()
    aba = planilha.sheet1  # ou use .worksheet("Catálogo_principal") se o nome da aba for fixo
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)

    # Normalizar nomes das colunas
    df.columns = df.columns.str.strip().str.lower().str.normalize('NFKD') \
        .str.encode('ascii', errors='ignore').str.decode('utf-8')

    return df

# Função para salvar dados da proposta no Sheets
def salvar_proposta_em_sheets(dados):
    planilha = conectar_sheets()
    aba = planilha.worksheet(ABA_PROPOSTAS)
    
    # Garante que está passando uma lista (não dicionário)
    if isinstance(dados, dict):
        dados = list(dados.values())
    
    aba.append_row(dados)
