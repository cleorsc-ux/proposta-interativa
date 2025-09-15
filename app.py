import streamlit as st
import os
import pandas as pd
from auth import autenticar
from pdf import gerar_pdf
from sheets import carregar_catalogo

# Autenticação do usuário
autenticar()  # Define st.session_state["nome"], ["usuario"], ["tipo"]

# Configuração da página
st.set_page_config(page_title="Gerador de Propostas - Ártico PRIME", layout="wide")

# Recupera os dados do usuário logado com segurança
usuario_nome = st.session_state.get("nome", "Desconhecido")
usuario_login = st.session_state.get("usuario", "N/A")
usuario_tipo = st.session_state.get("tipo", "N/A")

st.markdown("# 📄 Gerador de Propostas - Ártico PRIME")
st.markdown(f"Usuário logado: **{usuario_nome}** ({usuario_login} - {usuario_tipo})")

st.subheader("🔢 Selecione os serviços para esta proposta")

# Carrega o catálogo
catalogo = carregar_catalogo()
catalogo.columns = (
    catalogo.columns
    .str.strip()
    .str.lower()
    .str.normalize('NFKD')
    .str.encode('ascii', errors='ignore')
    .str.decode('utf-8')
)

# Garante que a coluna de valores seja numérica
if "valor_unitario" in catalogo.columns:
    catalogo["valor_unitario"] = pd.to_numeric(
        catalogo["valor_unitario"], errors="coerce"
    ).fillna(0.0)

servicos_selecionados = []
categorias = catalogo["categoria"].dropna().unique()

for cat in categorias:
    st.markdown(f"### 🔹 {cat}")
    subset = catalogo[catalogo["categoria"] == cat]

    for _, row in subset.iterrows():
        with st.container(border=True):
            st.markdown(f"**{row['servico']}** ({row['unidade']})")
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                checked = st.checkbox("Incluir", key=f"check_{row['servico']}_{_}")

            with col2:
                valor_raw = row.get("valor_unitario", 0)
                try:
                    valor_float = float(valor_raw)
                except (ValueError, TypeError):
                    try:
                        valor_float = float(str(valor_raw).replace(",", "."))
                    except Exception:
                        valor_float = 0.0

                valor_editado = st.number_input(
                    "Valor Unitário (R$)",
                    min_value=0.0,
                    value=valor_float,
                    step=0.01,
                    format="%.2f",
                    key=f"valor_{row['servico']}_{_}"
                )

            with col3:
                qtd = st.number_input(
                    "Quantidade",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"qtd_{row['servico']}_{_}"
                )

            if checked:
                total = valor_editado * qtd
                servicos_selecionados.append({
                    "servico": row["servico"],
                    "unidade": row["unidade"],
                    "valor_unit": valor_editado,
                    "quantidade": qtd,
                    "total": total
                })

# RESUMO DOS SERVIÇOS SELECIONADOS
if servicos_selecionados:
    st.markdown("## 📊 Resumo dos Serviços Selecionados")
    df_resumo = pd.DataFrame(servicos_selecionados)
    df_resumo["valor_unit"] = df_resumo["valor_unit"].map(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    df_resumo["total"] = df_resumo["total"].map(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.dataframe(
        df_resumo[["servico", "unidade", "quantidade", "valor_unit", "total"]],
        use_container_width=True
    )

    total_geral = sum(
        float(str(x["total"]).replace("R$", "").replace(".", "").replace(",", "."))
        for x in df_resumo.to_dict(orient="records")
    )
    st.markdown(
        f"### 💰 Total Geral: R$ {total_geral:,.2f}"
        .replace(",", "X").replace(".", ",").replace("X", ".")
    )

# DADOS DA PROPOSTA
st.subheader("📄 Dados da Proposta")
cliente = st.text_input("Cliente / Projeto", placeholder="Ex: Condomínio Ilhas Vivence")
objeto = st.text_area("Objeto da Proposta", placeholder="Ex: Execução de pintura de fachada / piso intertravado")
prazo = st.text_input("Prazo de Execução", value="7 dias úteis")
garantias = st.text_input("Garantias", value="90 dias contra defeitos")
forma_pagamento = st.text_input("Forma de Pagamento", placeholder="Ex: Entrada + 10 parcelas mensais")
simulacao = st.text_area("Simulação de Financiamento", placeholder="Detalhe aqui a simulação se houver")
validade = st.text_input("Validade da Proposta", value="15 dias")

observacoes = st.text_area("Condições Gerais / Observações", value="Esta proposta está sujeita a alterações conforme avaliação técnica da obra.")

# GERAR PDF
if st.button("🗓️ Gerar Proposta em PDF"):
    if not cliente:
        st.warning("Preencha o nome do cliente.")
    elif not servicos_selecionados:
        st.warning("Selecione ao menos um serviço.")
    else:
        total = sum(item["total"] for item in servicos_selecionados)
        pdf_path = gerar_pdf(
            cliente=cliente,
            servicos=servicos_selecionados,
            total=total,
            extras={
                "objeto": objeto,
                "prazo": prazo,
                "garantias": garantias,
                "forma_pagamento": forma_pagamento,
                "simulacao": simulacao,
                "validade": validade,
                "obs": observacoes,
                "emitido_por": f"{usuario_nome} ({usuario_login} - {usuario_tipo})"
            },
            usuario=usuario_nome
        )

        # Salva referência ao último PDF
        st.session_state['ultimo_pdf'] = pdf_path

        with open(pdf_path, "rb") as f:
            st.success("✅ Proposta gerada com sucesso!")
            st.download_button(
                "⬇️ Baixar PDF",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )
            st.info("Verifique o arquivo baixado ou envie para o cliente.")

# ➕ Botão Nova Proposta
if st.button("➕ Nova Proposta"):
    for key in list(st.session_state.keys()):
        if key.startswith("check_") or key.startswith("valor_") or key.startswith("qtd_"):
            del st.session_state[key]
    st.experimental_rerun()

# 🗑️ Botão Excluir Última Proposta
if st.button("🗑️ Excluir Última Proposta"):
    if 'ultimo_pdf' in st.session_state and os.path.exists(st.session_state['ultimo_pdf']):
        os.remove(st.session_state['ultimo_pdf'])
        st.success("🗑️ Proposta excluída com sucesso.")
        del st.session_state['ultimo_pdf']
    else:
        st.warning("Nenhuma proposta encontrada para excluir.")
