from fpdf import FPDF
from datetime import datetime
import os

class PDFProposta(FPDF):
    def header(self):
        if os.path.exists("assets/logo.png"):
            self.image("assets/logo.png", 10, 8, 33)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Proposta Comercial - Ártico PRIME", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

    def adicionar_dados_proposta(self, dados, usuario_logado):
        self.set_font("Arial", "", 12)

        self.cell(0, 10, f"Cliente: {dados['cliente']}", ln=True)
        self.cell(0, 10, f"Projeto: {dados['projeto']}", ln=True)
        self.cell(0, 10, f"Serviços: {dados['servicos']}", ln=True)
        self.cell(0, 10, f"Valor Total: R$ {dados['valor_total']:.2f}", ln=True)
        self.cell(0, 10, f"Prazo de execução: {dados['prazo']} dias", ln=True)
        self.cell(0, 10, f"Responsável: {usuario_logado['nome']}", ln=True)
        self.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)

def gerar_pdf(dados, usuario_logado, caminho="proposta.pdf"):
    pdf = PDFProposta()
    pdf.add_page()
    pdf.adicionar_dados_proposta(dados, usuario_logado)
    pdf.output(caminho)
    return caminho
