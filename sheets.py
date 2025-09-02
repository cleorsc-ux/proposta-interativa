# sheets.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from config import NOME_PLANILHA_CATALOGO, ABA_CATALOGO, ABA_PROPOSTAS

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CRED_FILE = "credencial.json"

def conectar_sheets():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CRED_FILE, SCOPES)
    client = gspread.authorize(credentials)
    return client.open(NOME_PLANILHA_CATALOGO)

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
