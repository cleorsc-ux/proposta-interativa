# pdf.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import matplotlib.pyplot as plt

from config import EMPRESA_NOME, LOGO_PATH

def gerar_pdf(nome_cliente, servicos, totais, extras, criado_por):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    # Logotipo
    c.drawImage(LOGO_PATH, 40, altura - 100, width=100, height=50)

    # Cabeçalho
    c.setFont("Helvetica-Bold", 14)
    c.drawString(160, altura - 60, f"Proposta Comercial - {EMPRESA_NOME}")
    c.setFont("Helvetica", 12)
    c.drawString(40, altura - 130, f"Cliente: {nome_cliente}")
    c.drawString(40, altura - 150, f"Criado por: {criado_por}")

    y = altura - 180

    # Serviços
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Serviços Selecionados:")
    y -= 20
    c.setFont("Helvetica", 10)
    for serv in servicos:
        c.drawString(60, y, f"{serv['quantidade']} x {serv['serviço']} - R$ {serv['total']:.2f}")
        y -= 15

    y -= 10

    # Totais
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, f"Total Geral: R$ {totais:.2f}")
    y -= 30

    # Campos Extras
    for campo, valor in extras.items():
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, f"{campo}:")
        c.setFont("Helvetica", 10)
        c.drawString(150, y, valor)
        y -= 20

    # Gráfico
    if servicos:
        nomes = [s['serviço'] for s in servicos]
        valores = [s['total'] for s in servicos]
        fig, ax = plt.subplots()
        ax.barh(nomes, valores)
        ax.set_xlabel("R$ Total")
        ax.set_title("Distribuição por Serviço")
        fig.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, format="PNG")
        plt.close(fig)
        img_buf.seek(0)
        c.drawImage(ImageReader(img_buf), 40, 80, width=500, height=200)

    # Rodapé
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(40, 30, f"Proposta gerada por {EMPRESA_NOME}")

    c.save()
    buffer.seek(0)
    return buffer
