import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from config import NOME_PLANILHA_CATALOGO, ABA_CATALOGO, ABA_PROPOSTAS

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def conectar_sheets():
    credentials_dict = st.secrets["google_sheets_credentials"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client.open_by_key("1hr4U2rpAvU8lYu_CgIQiSXtG0TF4NbRQK-va8-e9Zqk")

def carregar_catalogo():
    planilha = conectar_sheets()
    aba = planilha.worksheet(ABA_CATALOGO)
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    return df

def salvar_proposta_em_sheets(dados):
    planilha = conectar_sheets()
    aba = planilha.worksheet(ABA_PROPOSTAS)
    aba.append_row(dados)
