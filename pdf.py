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

    def gerar_proposta_completa(self, dados, nome_arquivo="proposta.pdf"):
        self.add_page()
        self.set_font("Arial", size=12)

        # 1. Introdução institucional
        self.multi_cell(0, 10, 
            "A \u00c1rtico PRIME | Soluções Prediais atua há mais de 16 anos no segmento da construção civil, com \\n            foco em manutenção de fachadas, reformas, pinturas prediais e obras estruturais. \\n            Nosso compromisso é entregar qualidade, segurança e transparência em todas as etapas do projeto.")
        self.ln(8)

        # 2. Dados do cliente e projeto
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, "Informacoes da Proposta", ln=True)
        self.set_font("Arial", size=12)
        self.cell(0, 10, f"Cliente: {dados['cliente']}", ln=True)
        self.cell(0, 10, f"Projeto: {dados['projeto']}", ln=True)
        self.ln(5)

        # 3. Lista de serviços
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, "Serviços Incluídos:", ln=True)
        self.set_font("Arial", size=12)
        for item in dados['servicos']:
            self.cell(0, 10, f"- {item['nome']} ({item['quantidade']} {item['unidade']}) - R$ {item['subtotal']:.2f}", ln=True)

        self.ln(5)
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, f"Valor Total da Proposta: R$ {dados['valor_total']:.2f}", ln=True)
        self.ln(5)

        # 4. Prazo, garantias e observacoes
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, "Prazo de Execução:", ln=True)
        self.set_font("Arial", size=12)
        self.cell(0, 10, dados['prazo'], ln=True)
        self.ln(5)

        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, "Garantias:", ln=True)
        self.set_font("Arial", size=12)
        self.multi_cell(0, 10, dados['garantias'])
        self.ln(5)

        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, "Observações:", ln=True)
        self.set_font("Arial", size=12)
        self.multi_cell(0, 10, dados['observacoes'])
        self.ln(10)

        # 5. Responsável pela proposta
        self.set_font("Arial", 'I', 11)
        self.cell(0, 10, f"Responsável: {self.usuario_nome}", ln=True)

        self.output(nome_arquivo)


def gerar_pdf(dados_proposta, usuario):
    os.makedirs("pdfs", exist_ok=True)

    servicos_raw = dados_proposta["servicos"].split(", ")
    total = dados_proposta["valor_total"]
    qtd_por_item = 1
    valor_unitario = total / len(servicos_raw)

    servicos = []
    for s in servicos_raw:
        servicos.append({
            "nome": s,
            "unidade": "UND",
            "quantidade": qtd_por_item,
            "valor_unitario": valor_unitario,
            "subtotal": valor_unitario
        })

    dados = {
        "cliente": dados_proposta["cliente"],
        "projeto": dados_proposta["projeto"],
        "servicos": servicos,
        "valor_total": total,
        "prazo": dados_proposta["prazo"],
        "garantias": dados_proposta["garantias"],
        "observacoes": dados_proposta["observacoes"]
    }

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"pdfs/proposta_{dados['cliente'].lower().replace(' ', '_')}_{timestamp}.pdf"

    pdf = PropostaPDF(usuario_nome=usuario, empresa_nome="Ártico PRIME | Soluções Prediais", logotipo_path="assets/logo.png")
    pdf.gerar_proposta_completa(dados, nome_arquivo)
    return nome_arquivo
