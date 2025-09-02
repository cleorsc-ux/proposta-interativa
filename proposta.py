import streamlit as st
import pandas as pd
import uuid, json, datetime as dt
from slugify import slugify

from sheets import read_catalog, write_catalog, save_proposal, list_proposals
from pdf import build_pdf
from config import brand

st.set_page_config(page_title="Ártico PRIME - Propostas", page_icon="📄", layout="wide")

# --- THEME (simple CSS) ---
st.markdown(f"""
<style>
:root {{
  --accent: {brand.accent};
  --gray: {brand.gray};
}}
.stButton>button {{
  background: var(--accent);
  color: white;
  border-radius: 10px;
  border: 0;
  padding: 0.6rem 1rem;
}}
.block-container {{
  padding-top: 1rem;
}}
thead tr th {{
  background: #e6eef5 !important;
}}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR BRAND ---
st.sidebar.image(brand.logo_path, use_column_width=True)
st.sidebar.markdown(f"**{brand.name}**")
st.sidebar.markdown("---")

# --- AUTH (simple) ---
with st.sidebar:
  st.markdown("### Login interno")
  user = st.text_input("Usuário", value="", key="user")
  pwd = st.text_input("Senha", value="", type="password", key="pwd")
  logged = st.button("Entrar")

if logged:
  st.session_state["logged"] = (len(user) > 0 and len(pwd) > 0)

if not st.session_state.get("logged"):
  st.info("Faça login para continuar (use qualquer usuário/senha por enquanto).")
  st.stop()

# --- Load Catalog ---
@st.cache_data(ttl=60)
def _get_catalog():
  df = read_catalog(st.secrets)
  # Normalize columns
  rename = {c:c.lower() for c in df.columns}
  df = df.rename(columns=rename)
  needed = ["categoria","servico","unidade","valor_unitario","descricao"]
  for c in needed:
    if c not in df.columns:
      df[c] = "" if c!="valor_unitario" else 0.0
  df["valor_unitario"] = pd.to_numeric(df["valor_unitario"], errors="coerce").fillna(0.0)
  return df

catalog = _get_catalog()

# --- Query params: open proposal via link ---
params = st.experimental_get_query_params()
pid_from_link = params.get("pid", [None])[0]

st.title("📄 Gerador de Propostas Interativas")

tab_nova, tab_historico, tab_catalogo, tab_config = st.tabs(["Nova proposta", "Histórico", "Catálogo (Sheets)", "Config"])

with tab_nova:
  st.subheader("1) Escolha de serviços")

  # Filtros
  colf1, colf2 = st.columns([2,1])
  with colf1:
    filtro = st.text_input("Buscar por palavra-chave", "")
  with colf2:
    categoria_sel = st.selectbox("Filtrar por categoria", ["Todas"] + sorted([c for c in catalog["categoria"].dropna().unique() if c]))

  df = catalog.copy()
  if filtro:
    df = df[df["servico"].str.contains(filtro, case=False, na=False) | df["descricao"].str.contains(filtro, case=False, na=False)]
  if categoria_sel != "Todas":
    df = df[df["categoria"] == categoria_sel]

  # Listagem interativa
  st.write("Selecione os serviços e defina as quantidades:")
  if "cart" not in st.session_state:
    st.session_state["cart"] = []

  for idx, row in df.sort_values(["categoria","servico"]).iterrows():
    with st.expander(f"{row['categoria']} • {row['servico']} — R$ {row['valor_unitario']:.2f}"):
      c1, c2, c3 = st.columns([1,1,1])
      with c1:
        qtd = st.number_input("Quantidade", min_value=0.0, step=1.0, key=f"q_{idx}")
      with c2:
        add = st.button("Adicionar ao carrinho", key=f"a_{idx}")
      with c3:
        st.caption(row.get("descricao",""))
      if add and qtd>0:
        st.session_state["cart"].append({
          "categoria": row["categoria"],
          "servico": row["servico"],
          "unidade": row["unidade"],
          "valor_unitario": float(row["valor_unitario"]),
          "quantidade": float(qtd),
        })
        st.success(f"Adicionado: {row['servico']} x {qtd}")

  # Serviço extra manual
  st.markdown("**Adicionar serviço extra**")
  cex1, cex2, cex3, cex4 = st.columns([2,1,1,1])
  with cex1:
    sx = st.text_input("Serviço")
  with cex2:
    unx = st.text_input("Unidade", value="UND")
  with cex3:
    vx = st.number_input("Valor Unitário", min_value=0.0, step=1.0)
  with cex4:
    qx = st.number_input("Quantidade", min_value=0.0, step=1.0)
  if st.button("Adicionar serviço extra"):
    if sx and vx>0 and qx>0:
      st.session_state["cart"].append({
        "categoria": "Extra",
        "servico": sx, "unidade": unx,
        "valor_unitario": float(vx), "quantidade": float(qx)
      })
      st.success(f"Serviço extra adicionado: {sx}")
    else:
      st.warning("Preencha serviço, valor e quantidade.")

  st.subheader("2) Carrinho")
  cart = pd.DataFrame(st.session_state["cart"])
  if not cart.empty:
    cart["subtotal"] = cart["quantidade"] * cart["valor_unitario"]
    st.dataframe(cart, use_container_width=True)
    total = float(cart["subtotal"].sum())
    st.metric("Total", f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X","."))
  else:
    total = 0.0
    st.info("Nenhum serviço no carrinho.")

  st.subheader("3) Cadastro do Cliente/Obra")
  c1, c2 = st.columns(2)
  with c1:
    nome_obra = st.text_input("Nome do cliente/obra *")
    email = st.text_input("E-mail *")
  with c2:
    telefone = st.text_input("Telefone *")
    endereco = st.text_input("Endereço *")

  # Parcelamento
  st.subheader("4) Condições e Parcelamento")
  condicoes = st.text_area("Condições comerciais (editar livremente)", "Proposta válida por 30 dias. Pagamento: 20% na mobilização e saldo por medições mensais. Inclui materiais, mão de obra, EPIs e administração. ")
  parcelas_n = st.number_input("Número de parcelas", min_value=1, max_value=24, value=1)
  entrada_pct = st.number_input("Entrada (%)", min_value=0, max_value=100, value=20 if parcelas_n>1 else 0)
  parcelas = []
  if total>0:
    entrada_val = total * (entrada_pct/100.0)
    restante = total - entrada_val
    par_val = restante/parcelas_n if parcelas_n>0 else 0
    parcelas = [{"parcela": i+1, "valor": par_val} for i in range(parcelas_n)]
    st.write(pd.DataFrame(parcelas))

  # Apresentação (portfólio resumido)
  apresentacao = st.text_area("Apresentação da empresa", "Desde 2008, a Ártico PRIME executa obras civis com qualidade, eficiência e rigor técnico, priorizando segurança e cumprimento de cronogramas. Atuamos em pintura predial, impermeabilização, reformas e obras de infraestrutura, com histórico de parcerias públicas e privadas em Alagoas.")

  # Ações finais
  colf = st.columns(3)
  can_generate = (total>0 and nome_obra and email and telefone and endereco)

  if st.button("💾 Salvar e gerar PDF", disabled=not can_generate):
    proposal_id = str(uuid.uuid4())[:8]
    ts = dt.datetime.now().isoformat(timespec="seconds")
    items_json = json.dumps(st.session_state["cart"], ensure_ascii=False)
    parcelas_json = json.dumps(parcelas, ensure_ascii=False)

    # Build PDF
    pdf_file = f"proposta_{slugify(nome_obra)}_{proposal_id}.pdf"
    build_pdf(pdf_file,
              cliente={"nome_obra":nome_obra, "email":email, "telefone":telefone, "endereco":endereco},
              itens=st.session_state["cart"],
              total=total, condicoes=condicoes, apresentacao=apresentacao)

    # Link único (via query param)
    base_url = st.secrets.get("app_base_url", "https://seu-app-streamlit.streamlit.app")
    link_unico = f"{base_url}?pid={proposal_id}"

    payload = {
      "proposal_id": proposal_id,
      "timestamp": ts,
      "cliente": {"nome_obra":nome_obra, "email":email, "telefone":telefone, "endereco":endereco},
      "total": total,
      "parcelas_json": parcelas_json,
      "items_json": items_json,
      "pdf_filename": pdf_file,
      "link_unico": link_unico,
    }
    save_proposal(st.secrets, payload)
    st.success("Proposta salva com sucesso!")
    st.download_button("⬇️ Baixar PDF", data=open(pdf_file, "rb"), file_name=pdf_file, mime="application/pdf")
    st.write("🔗 Link único da proposta:", link_unico)

with tab_historico:
  st.subheader("Histórico de propostas")
  try:
    hist = list_proposals(st.secrets)
    st.dataframe(hist, use_container_width=True)
  except Exception as e:
    st.warning("Configure a aba de integração com o Google Sheets para ver o histórico.")
    st.exception(e)

with tab_catalogo:
  st.subheader("Catálogo oficial (Google Sheets)")
  st.caption("O catálogo abaixo é carregado da planilha do Google Sheets definida em `secrets`. Você pode editar e reenviar para atualizar.")
  st.dataframe(catalog, use_container_width=True, height=400)

  st.markdown("**Editar catálogo aqui e enviar para o Sheets:**")
  edited = st.data_editor(catalog, num_rows="dynamic", use_container_width=True)
  if st.button("Enviar alterações para o Google Sheets"):
    write_catalog(st.secrets, edited)
    st.success("Catálogo atualizado com sucesso!")
    st.cache_data.clear()
    st.experimental_rerun()

with tab_config:
  st.subheader("Configurações e instruções")
  st.markdown("""
**Secrets necessários (`.streamlit/secrets.toml` ou painel do Streamlit Cloud):**

```toml
[google]
# cole o JSON da conta de serviço aqui
service_account = { }
catalog_sheet_id = "SHEET_ID_CATALOGO"
proposals_sheet_id = "SHEET_ID_PROPOSTAS"

# URL pública do seu app para gerar links únicos
app_base_url = "https://seu-app.streamlit.app"