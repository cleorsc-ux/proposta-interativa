# streamlit_app.py

import streamlit as st
from auth import autenticar_usuario
from sheets import carregar_catalogo, salvar_proposta_em_sheets
from pdf import gerar_pdf
from config import get_config_by_tenant

st.set_page_config(page_title="Plataforma de Propostas", layout="wide")

# Login multiempresa
tenant_id, user = autenticar_usuario()
if not user:
    st.stop()

logout_button = st.sidebar.button("🔓 Sair")
if logout_button:
    del st.session_state.usuario
    st.experimental_rerun()

# Carregar configurações da empresa (cores, logo, planilha)
config = get_config_by_tenant(tenant_id)
st.sidebar.image(config['logo'], use_column_width=True)
st.sidebar.markdown(f"**{config['nome_empresa']}**")

st.title("📄 Gerador de Propostas Interativas")

# Carregar serviços
catalogo = carregar_catalogo(config)
categorias = catalogo["categoria"].dropna().unique()

st.subheader("1) Escolha de serviços")
carrinho = []
for cat in categorias:
    st.markdown(f"### 🔹 {cat}")
    subset = catalogo[catalogo["categoria"] == cat]
    for _, row in subset.iterrows():
        col1, col2 = st.columns([6, 2])
        with col1:
            checked = st.checkbox(f"{row['servico']} ({row['unidade']}) - R$ {row['valor_unitario']:.2f}", key=row["servico"])
        with col2:
            if checked:
                qtd = st.number_input(f"Qtd - {row['servico']}", min_value=1, value=1, key=f"qtd_{row['servico']}")
                carrinho.append({
                    "servico": row["servico"],
                    "unidade": row["unidade"],
                    "valor_unit": row["valor_unitario"],
                    "quantidade": qtd,
                    "total": qtd * row["valor_unitario"]
                })

# Serviço extra manual
st.markdown("### ➕ Serviço extra")
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

# Dados do cliente e proposta
st.subheader("2) Dados do Cliente")
nome_cliente = st.text_input("Nome do Cliente / Projeto")
prazo = st.text_input("Prazo de Execução", value="30 dias")
garantias = st.text_input("Garantias", value="90 dias contra defeitos")
obs = st.text_area("Observações", value="Esta proposta está sujeita a alterações mediante vistorias técnicas.")

# Gerar proposta
if st.button("📄 Gerar Proposta em PDF"):
    if not nome_cliente:
        st.warning("Preencha o nome do cliente.")
    elif not carrinho:
        st.warning("Selecione ao menos um serviço.")
    else:
        total = sum(item["total"] for item in carrinho)
        pdf = gerar_pdf(
            tenant=config,
            cliente=nome_cliente,
            servicos=carrinho,
            total=total,
            extras={"prazo": prazo, "garantias": garantias, "obs": obs},
            usuario=user["nome"]
        )
        st.success("✅ Proposta gerada com sucesso!")
        st.download_button("⬇️ Baixar PDF", data=pdf, file_name=f"proposta_{nome_cliente}.pdf", mime="application/pdf")
        salvar_proposta_em_sheets(config, nome_cliente, user["nome"], total, carrinho, obs)
