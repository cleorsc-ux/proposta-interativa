from pdf import PropostaPDF

usuario = "Eng. Cleo"
empresa = "Ártico PRIME"
logotipo = "static/logo.png"

servicos = [
    {"nome": "Fundação", "unidade": "m²", "quantidade": 100, "valor_unitario": 50.0, "subtotal": 5000.0},
    {"nome": "Estrutura", "unidade": "m²", "quantidade": 200, "valor_unitario": 70.0, "subtotal": 14000.0},
]

total = sum(item["subtotal"] for item in servicos)

pdf = PropostaPDF(usuario_nome=usuario, empresa_nome=empresa, logotipo_path=logotipo)
pdf.gerar_proposta(servicos, total)
