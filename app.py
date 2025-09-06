# ✅ pdf.py COMPLETO — modelo profissional de proposta comercial interativa

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
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, f"{self.empresa_nome} | Proposta Comercial", ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f"Gerado por {self.usuario_nome} em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 0, 'C')

    def adicionar_apresentacao(self):
        self.set_font("Arial", size=11)
        self.multi_cell(0, 8, (
            "\nA \u00c1rtico PRIME | Solu\u00e7\u00f5es Prediais atua h\u00e1 mais de 16 anos no segmento de engenharia civil, \n"
            "com foco em manuten\u00e7\u00e3o predial, pintura de fachadas, repara\u00e7\u00f5es e obras de pequeno a grande porte.\n"
            "\nPrezamos pela seguran\u00e7a, qualidade e pontualidade na execu\u00e7\u00e3o dos nossos servi\u00e7os."
        ))
        self.ln(10)

    def adicionar_dados_cliente(self, dados):
        self.set_font("Arial", size=12)
        self.cell(0, 10, f"Cliente: {dados['cliente']}", ln=True)
        self.cell(0, 10, f"Projeto: {dados['projeto']}", ln=True)
        self.cell(0, 10, f"Local da Obra: {dados['local']}", ln=True)
        self.cell(0, 10, f"Prazo de Execu\u00e7\u00e3o: {dados['prazo']} dias", ln=True)
        self.ln(5)

    def adicionar_tabela_servicos(self, servicos, total):
        self.set_font("Arial", 'B', 11)
        self.cell(50, 10, "Servi\u00e7o", 1)
        self.cell(30, 10, "Unidade", 1)
        self.cell(30, 10, "Quantidade", 1)
        self.cell(40, 10, "Valor Unit\u00e1rio", 1)
        self.cell(40, 10, "Subtotal", 1)
        self.ln()

        self.set_font("Arial", size=11)
        for item in servicos:
            self.cell(50, 10, item["nome"], 1)
            self.cell(30, 10, item["unidade"], 1)
            self.cell(30, 10, str(item["quantidade"]), 1)
            self.cell(40, 10, f"R$ {item['valor_unitario']:.2f}", 1)
            self.cell(40, 10, f"R$ {item['subtotal']:.2f}", 1)
            self.ln()

        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, f"Total Geral: R$ {total:.2f}", ln=True, align='R')
        self.ln(5)

    def adicionar_condicoes(self, dados):
        self.set_font("Arial", size=11)
        self.multi_cell(0, 8, f"\nForma de Pagamento: {dados['pagamento']}\n")
        self.multi_cell(0, 8, (
            "Equipe Envolvida: Engenheiro Civil, Mestre de Obras, Ajudantes, Pintores, etc.\n"
            "\nGarantias:\n- Produto: conforme especifica\u00e7\u00e3o do fabricante.\n- M\u00e3o de Obra: 12 meses a contar da entrega."
        ))
        self.multi_cell(0, 8, (
            "\nCondi\u00e7\u00f5es Gerais:\n"
            "- Esta proposta est\u00e1 sujeita a an\u00e1lise e aprova\u00e7\u00e3o final.\n"
            "- O prazo de execu\u00e7\u00e3o come\u00e7a a contar do primeiro dia \u00fatil ap\u00f3s a libera\u00e7\u00e3o do acesso ao local e aprova\u00e7\u00e3o da proposta.\n"
            "\nAtenciosamente,\n{self.usuario_nome} — Respons\u00e1vel T\u00e9cnico\n\n"
        ))

    def gerar_proposta_completa(self, dados_proposta, servicos, total_geral, nome_arquivo):
        self.add_page()
        self.adicionar_apresentacao()
        self.adicionar_dados_cliente(dados_proposta)
        self.adicionar_tabela_servicos(servicos, total_geral)
        self.adicionar_condicoes(dados_proposta)
        self.output(nome_arquivo)


def gerar_pdf(dados_proposta, usuario):
    empresa = dados_proposta["cliente"]
    servicos_raw = dados_proposta["servicos"].split(", ")
    total = dados_proposta["valor_total"]

    servicos = []
    for servico in servicos_raw:
        valor_unit = total / len(servicos_raw)
        servicos.append({
            "nome": servico,
            "unidade": "UND",
            "quantidade": 1,
            "valor_unitario": valor_unit,
            "subtotal": valor_unit
        })

    os.makedirs("pdfs", exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"pdfs/proposta_{empresa.lower().replace(' ', '_')}_{timestamp}.pdf"

    pdf = PropostaPDF(usuario_nome=usuario["nome"], empresa_nome=empresa, logotipo_path="assets/logo.png")
    pdf.gerar_proposta_completa(dados_proposta, servicos, total, nome_arquivo)
    return nome_arquivo
