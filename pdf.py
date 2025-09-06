# novo_pdf.py
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
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, f'{self.empresa_nome} | Proposta Comercial', ln=True, align='C')
        self.set_font('Arial', '', 12)
        self.ln(10)
        self.multi_cell(0, 8, "A Ártico PRIME | Soluções Prediais atua há mais de 16 anos no segmento da construção civil, oferecendo excelência em manutenção predial, reformas e soluções técnicas de engenharia. Esta proposta apresenta os serviços cotados conforme necessidade do cliente.")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100)
        self.cell(0, 10, f'Gerado por {self.usuario_nome} em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 0, 'C')

    def adicionar_detalhes(self, dados):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, "Dados da Proposta", ln=True, fill=True)

        self.set_font('Arial', '', 11)
        self.cell(40, 10, "Cliente:", 0)
        self.cell(0, 10, dados['cliente'], ln=True)

        self.cell(40, 10, "Projeto:", 0)
        self.cell(0, 10, dados['projeto'], ln=True)

        self.cell(40, 10, "Prazo de Execução:", 0)
        self.cell(0, 10, dados['prazo'], ln=True)

        self.cell(40, 10, "Garantias:", 0)
        self.cell(0, 10, dados['garantias'], ln=True)

        self.cell(40, 10, "Observações:", 0)
        self.multi_cell(0, 10, dados['observacoes'])
        self.ln(5)

    def adicionar_servicos(self, servicos):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, "Serviços Propostos", ln=True, fill=True)

        self.set_font('Arial', 'B', 11)
        self.cell(80, 10, "Serviço", 1)
        self.cell(30, 10, "Unidade", 1)
        self.cell(30, 10, "Qtd.", 1)
        self.cell(40, 10, "Subtotal (R$)", 1)
        self.ln()

        self.set_font('Arial', '', 11)
        for s in servicos:
            self.cell(80, 10, s['nome'], 1)
            self.cell(30, 10, s['unidade'], 1)
            self.cell(30, 10, str(s['quantidade']), 1)
            self.cell(40, 10, f"R$ {s['subtotal']:.2f}", 1)
            self.ln()

    def adicionar_total(self, total):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f"Total Geral: R$ {total:.2f}", ln=True, align='R')


def gerar_pdf(dados_proposta, usuario_nome):
    empresa_nome = "Ártico PRIME | Soluções Prediais"
    logotipo_path = "assets/logo.png"
    os.makedirs("pdfs", exist_ok=True)

    servicos_raw = dados_proposta['servicos'].split(", ")
    total = dados_proposta['valor_total']
    valor_unitario = total / len(servicos_raw)

    servicos = [
        {"nome": nome, "unidade": "UND", "quantidade": 1, "subtotal": valor_unitario}
        for nome in servicos_raw
    ]

    pdf = PropostaPDF(usuario_nome, empresa_nome, logotipo_path)
    pdf.add_page()
    pdf.adicionar_detalhes(dados_proposta)
    pdf.adicionar_servicos(servicos)
    pdf.adicionar_total(total)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    caminho = f"pdfs/proposta_{dados_proposta['cliente'].lower().replace(' ', '_')}_{timestamp}.pdf"
    pdf.output(caminho)
    return caminho
