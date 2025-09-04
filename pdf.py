# gerar_pdf.py

from fpdf import FPDF
from datetime import datetime
import os

class PropostaPDF(FPDF):
    def __init__(self, usuario_nome, empresa_nome, logotipo_path):
        super().__init__()
        self.usuario_nome = usuario_nome
        self.empresa_nome = empresa_nome
        self.logotipo_path = logotipo_path
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        if os.path.exists(self.logotipo_path):
            self.image(self.logotipo_path, 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, f"{self.empresa_nome} - Proposta Comercial", ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f"Gerado por {self.usuario_nome} em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 0, 'C')

    def gerar_proposta(self, servicos, total_geral, nome_arquivo="proposta.pdf"):
        self.add_page()
        self.set_font("Arial", size=12)

        # Cabeçalho da Tabela
        self.cell(40, 10, "Serviço", 1)
        self.cell(30, 10, "Unidade", 1)
        self.cell(30, 10, "Qtd.", 1)
        self.cell(40, 10, "Valor Unitário", 1)
        self.cell(40, 10, "Subtotal", 1)
        self.ln()

        for item in servicos:
            self.cell(40, 10, item["nome"], 1)
            self.cell(30, 10, item["unidade"], 1)
            self.cell(30, 10, str(item["quantidade"]), 1)
            self.cell(40, 10, f"R$ {item['valor_unitario']:.2f}", 1)
            self.cell(40, 10, f"R$ {item['subtotal']:.2f}", 1)
            self.ln()

        self.ln(5)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"Total Geral: R$ {total_geral:.2f}", ln=True, align='R')

        self.set_font("Arial", "", 10)
        self.multi_cell(0, 10, "Observações: Esta proposta está sujeita a alterações conforme avaliação técnica da obra.")

        self.output(nome_arquivo)

# Função externa para usar no app
def gerar_pdf(dados_proposta, usuario):
    empresa = dados_proposta["cliente"]
    servicos_raw = dados_proposta["servicos"].split(", ")
    total = dados_proposta["valor_total"]

    servicos = []
    for servico in servicos_raw:
        servicos.append({
            "nome": servico,
            "unidade": "UND",
            "quantidade": 1,
            "valor_unitario": total / len(servicos_raw),
            "subtotal": total / len(servicos_raw)
        })

    pdf = PropostaPDF(usuario_nome=usuario["nome"], empresa_nome=empresa, logotipo_path="assets/logo.png")
    nome_arquivo = f"pdfs/proposta_{empresa.lower().replace(' ', '_')}.pdf"
    pdf.gerar_proposta(servicos, total, nome_arquivo)
    return nome_arquivo
