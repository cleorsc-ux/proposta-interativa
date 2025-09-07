import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from config import (
    NOME_PLANILHA_CATALOGO,
    ABA_CATALOGO,
    ABA_PROPOSTAS
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def conectar_sheets():
    credentials_dict = st.secrets["google_sheets_credentials"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client.open(NOME_PLANILHA_CATALOGO)

def carregar_catalogo():
    planilha = conectar_sheets()
    aba = planilha.worksheet(ABA_CATALOGO)
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    return df

def salvar_proposta_em_sheets(cliente, usuario, total, itens, observacoes):
    planilha = conectar_sheets()
    aba = planilha.worksheet(ABA_PROPOSTAS)

    valores = [
        cliente,
        usuario,
        f"R$ {total:.2f}".replace(".", ","),
        ", ".join([f"{item['servico']} (x{item['quantidade']})" for item in itens]),
        observacoes
    ]
    aba.append_row(valores)
