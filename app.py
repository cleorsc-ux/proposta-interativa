# ✅ streamlit_app.py — versão limpa e completa

import streamlit as st
from auth import autenticar_usuario
from sheets import carregar_catalogo, salvar_proposta_em_sheets
from pdf import gerar_pdf
from config import get_config_by_tenant

# Configura a página
st.set_page_config(page_title="Gerador de Propostas - Ártico PRIME", layout="wide")

# Autenticação com suporte a multitenancy
tenant_id, usuario = autenticar_usuario()
if not usuario:
    st.stop()

# Botão de logout
if st.sidebar.button("🔓 Sair"):
    del st.session_state.usuario
    st.experimental_rerun()

# Carrega configurações da empresa (logo, nome, planilha...)
config = get_config_by_tenant(tenant_id)
st.sidebar.image(config['logo'], use_column_width=True)
st.sidebar.markdown(f"**{config['nome_empresa']}**")

st.markdown("# 📄 Gerador de Propostas Interativas")

# 📦 Carregar catálogo de serviços
catalogo = carregar_catalogo(config)
categorias = catalogo["categoria"].dropna().unique()

st.subheader("1️⃣ Escolha os serviços")
carrinho = []

for categoria in categorias:
    st.markdown(f"### 🔹 {categoria}")
    servicos_categoria = catalogo[catalogo["categoria"] == categoria]

    for _, row in servicos_categoria.iterrows():
        col1, col2 = st.columns([6, 2])
        with col1:
            marcado = st.checkbox(f"{row['servico']} ({row['unidade']}) - R$ {row['valor_unitario']:.2f}", key=row["servico"])
        with col2:
            if marcado:
                qtd = st.number_input(f"Qtd - {row['servico']}", min_value=1, value=1, key=f"qtd_{row['servico']}")
                carrinho.append({
                    "servico": row["servico"],
                    "unidade": row["unidade"],
                    "valor_unit": row["valor_unitario"],
                    "quantidade": qtd,
                    "total": qtd * row["valor_unitario"]
                })

# ➕ Serviço manual extra
st.markdown("### ➕ Adicionar serviço extra")
nome_extra = st.text_input("Descrição do serviço extra")
qtd_extra = st.number_input("Quantidade", min_value=1, step=1)
valor_extra = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f")

if nome_extra:
    carrinho.append({
        "servico": nome_extra,
        "unidade": "UND",
        "valor_unit": valor_extra,
        "quantidade": qtd_extra,
        "total": qtd_extra * valor_extra
    })

# 🧾 Informações do cliente
st.subheader("2️⃣ Dados da Proposta")
nome_cliente = st.text_input("Nome do Cliente ou Projeto")
prazo = st.text_input("Prazo de Execução", value="30 dias")
garantias = st.text_input("Garantias", value="90 dias contra defeitos")
obs = st.text_area("Observações", value="Esta proposta está sujeita a alterações mediante vistoria técnica.")

# ✅ Gerar proposta PDF
if st.button("📎 Gerar Proposta em PDF"):
    if not nome_cliente:
        st.warning("⚠️ Informe o nome do cliente.")
    elif not carrinho:
        st.warning("⚠️ Selecione ao menos um serviço para gerar a proposta.")
    else:
        total = sum(item["total"] for item in carrinho)

        pdf = gerar_pdf(
            tenant=config,
            cliente=nome_cliente,
            servicos=carrinho,
            total=total,
            extras={
                "prazo": prazo,
                "garantias": garantias,
                "obs": obs
            },
            usuario=usuario["nome"]
        )

        st.success("✅ Proposta gerada com sucesso!")
        st.download_button("⬇️ Baixar PDF", data=pdf, file_name=f"proposta_{nome_cliente}.pdf", mime="application/pdf")

        salvar_proposta_em_sheets(config, nome_cliente, usuario["nome"], total, carrinho, obs)
