import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from config import NOME_PLANILHA_CATALOGO, ABA_CATALOGO, ABA_PROPOSTAS

# Permissões para acessar o Sheets + Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Função para conectar com a planilha
def conectar_sheets():
    credentials_dict = st.secrets["google_sheets_credentials"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client.open_by_key("1uzFYoRqTD46dQYVyh__vpf09EujVSsXLjJYS4HA27-k")

# Função para carregar o catálogo
def carregar_catalogo():
    planilha = conectar_sheets()
    aba = planilha.worksheet(ABA_CATALOGO)
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    
    # Normalizar nomes de colunas
    df.columns = df.columns.str.strip().str.lower().str.normalize('NFKD')\
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
