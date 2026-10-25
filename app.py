"""EcoPrato IA — estrutura inicial da aplicação web (Pessoa 5)

Instalação local:
    python -m pip install streamlit pandas
Execução:
    streamlit run EcoPrato_App_Starter_Pessoa5.py

A tela de previsão é apenas uma estrutura. Ela NÃO prevê nada até a integração
com o modelo treinado pela Pessoa 3.
"""

from pathlib import Path
from datetime import date, datetime
import pandas as pd
import streamlit as st

ARQUIVO_DADOS = "registros_eco_prato.csv"
SEPARADOR = ";"

COLUNAS = [
    "registro_id", "data", "turno", "tipo_refeicao", "cardapio",
    "refeicoes_previstas", "refeicoes_servidas", "alimentos_preparados_kg",
    "sobras_nao_servidas_kg", "metodo_sobras_nao_servidas",
    "restos_pratos_kg", "metodo_restos_pratos", "perdas_preparo_kg",
    "metodo_perdas_preparo", "motivo_principal_sobras", "observacoes"
]

TURNOS = ["manha", "tarde", "noite", "outro"]
TIPOS_REFEICAO = ["cafe_da_manha", "lanche", "almoco", "jantar", "outro"]
METODOS_PESO = ["balanca", "estimativa", "nao_medido"]
MOTIVOS = [
    "nao_avaliado", "demanda_menor_que_prevista", "baixa_aceitacao_cardapio",
    "porcoes_maiores_que_consumo", "alteracao_numero_refeicoes",
    "problema_qualidade_preparo", "atraso_ou_interrupcao_servico",
    "producao_excedente", "outro"
]

st.set_page_config(page_title="EcoPrato IA", page_icon="🌱", layout="wide")


def carregar_dados() -> pd.DataFrame:
    caminho = Path(ARQUIVO_DADOS)
    if not caminho.exists() or caminho.stat().st_size == 0:
        return pd.DataFrame(columns=COLUNAS)
    try:
        df = pd.read_csv(caminho, sep=SEPARADOR, encoding="utf-8-sig")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
        st.warning("Não foi possível ler o arquivo de registros. Confira o CSV.")
        return pd.DataFrame(columns=COLUNAS)
    for coluna in COLUNAS:
        if coluna not in df.columns:
            df[coluna] = pd.NA
    return df[COLUNAS]


def salvar_registro(registro: dict) -> None:
    df = carregar_dados()
    atualizado = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    atualizado.to_csv(ARQUIVO_DADOS, sep=SEPARADOR, index=False, encoding="utf-8-sig")


def campo_peso(rotulo: str, chave: str) -> tuple[float | None, str]:
    metodo = st.selectbox(
        f"Como o peso de {rotulo} foi obtido?",
        METODOS_PESO,
        index=2,
        key=f"metodo_{chave}"
    )
    if metodo == "nao_medido":
        st.caption("O peso será registrado como ausente, não como zero.")
        return None, metodo
    peso = st.number_input(
        f"Peso de {rotulo} (kg)", min_value=0.0, value=0.0,
        step=0.1, format="%.2f", key=f"peso_{chave}"
    )
    return float(peso), metodo


df = carregar_dados()

st.title("🌱 EcoPrato IA")
st.caption("Registro e análise do desperdício de alimentos na escola")
pagina = st.sidebar.radio(
    "Navegação",
    ["Início", "Registrar refeição", "Previsão de sobras", "Histórico e indicadores"]
)

if pagina == "Início":
    st.subheader("Painel do projeto")
    st.write(
        "O EcoPrato IA organiza os registros das refeições e, após a integração "
        "com o modelo treinado, ajudará a estimar sobras de alimentos não servidos."
    )
    a, b, c = st.columns(3)
    a.metric("Registros salvos", len(df))
    if not df.empty:
        pesos = pd.to_numeric(df["sobras_nao_servidas_kg"], errors="coerce")
        b.metric("Registros com peso de sobras", int(pesos.notna().sum()))
        c.metric("Último registro", str(df["data"].dropna().iloc[-1]) if df["data"].notna().any() else "—")
    else:
        b.metric("Registros com peso de sobras", 0)
        c.metric("Último registro", "—")
    st.info("A aplicação está em construção. A previsão ainda não está conectada ao modelo real.")

elif pagina == "Registrar refeição":
    st.subheader("Registrar uma refeição já realizada")
    st.caption("Preencha os pesos medidos. Se não houve medição, selecione 'nao_medido'; não use zero como substituto.")

    with st.form("form_registro", clear_on_submit=False):
        data_servico = st.date_input("Data do serviço", value=date.today())
        col1, col2 = st.columns(2)
        with col1:
            turno = st.selectbox("Turno", TURNOS)
            tipo = st.selectbox("Tipo de refeição", TIPOS_REFEICAO)
            cardapio = st.text_input("Cardápio", placeholder="Ex.: arroz, feijão e frango")
            previstas = st.number_input("Refeições previstas", min_value=0, value=0, step=1)
            servidas = st.number_input("Refeições servidas", min_value=0, value=0, step=1)
        with col2:
            if st.checkbox("Peso dos alimentos preparados foi registrado?"):
                preparados = st.number_input("Alimentos preparados (kg)", min_value=0.0, value=0.0, step=0.1)
            else:
                preparados = None
            sobras, metodo_sobras = campo_peso("sobras não servidas", "sobras")
            restos, metodo_restos = campo_peso("restos de pratos", "restos")
            perdas, metodo_perdas = campo_peso("perdas no preparo", "perdas")
        motivo = st.selectbox("Motivo principal observado (opcional)", MOTIVOS)
        observacoes = st.text_area("Observações sem dados pessoais", placeholder="Ex.: mudança de cardápio")
        enviado = st.form_submit_button("Salvar registro")

    if enviado:
        if not cardapio.strip():
            st.error("Preencha o cardápio antes de salvar.")
        elif int(previstas) <= 0:
            st.error("Informe a quantidade de refeições previstas.")
        else:
            registro = {
                "registro_id": f"R{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "data": data_servico.isoformat(),
                "turno": turno,
                "tipo_refeicao": tipo,
                "cardapio": cardapio.strip(),
                "refeicoes_previstas": int(previstas),
                "refeicoes_servidas": int(servidas),
                "alimentos_preparados_kg": preparados,
                "sobras_nao_servidas_kg": sobras,
                "metodo_sobras_nao_servidas": metodo_sobras,
                "restos_pratos_kg": restos,
                "metodo_restos_pratos": metodo_restos,
                "perdas_preparo_kg": perdas,
                "metodo_perdas_preparo": metodo_perdas,
                "motivo_principal_sobras": motivo,
                "observacoes": observacoes.strip()
            }
            salvar_registro(registro)
            st.success("Registro salvo no arquivo registros_eco_prato.csv.")
            st.info("Confirme periodicamente o arquivo e mantenha uma cópia de segurança dos registros.")

elif pagina == "Previsão de sobras":
    st.subheader("Prever sobras antes do serviço")
    st.caption("A previsão deve usar somente informações conhecidas antes da refeição.")
    with st.form("form_previsao"):
        data_prevista = st.date_input("Data da refeição", value=date.today(), key="prev_data")
        turno_previsto = st.selectbox("Turno", TURNOS, key="prev_turno")
        tipo_previsto = st.selectbox("Tipo de refeição", TIPOS_REFEICAO, key="prev_tipo")
        cardapio_previsto = st.text_input("Cardápio planejado", key="prev_cardapio")
        refeicoes_previstas = st.number_input(
            "Refeições previstas", min_value=1, value=100, step=1, key="prev_qtd"
        )
        solicitar = st.form_submit_button("Solicitar previsão")
    if solicitar:
        st.info(
            "A tela está pronta para integração, mas o modelo de IA ainda não foi conectado. "
            "Não use um valor fictício como previsão real. Combine com a Pessoa 3 a função "
            "de previsão e as colunas exigidas pelo modelo."
        )
        st.write("Dados enviados futuramente ao modelo:")
        st.json({
            "data": data_prevista.isoformat(),
            "turno": turno_previsto,
            "tipo_refeicao": tipo_previsto,
            "cardapio": cardapio_previsto,
            "refeicoes_previstas": int(refeicoes_previstas)
        })

else:
    st.subheader("Histórico e indicadores")
    if df.empty:
        st.info("Ainda não há registros. Adicione dados na página 'Registrar refeição'.")
    else:
        visual = df.copy()
        for col in ["sobras_nao_servidas_kg", "restos_pratos_kg", "perdas_preparo_kg"]:
            visual[col] = pd.to_numeric(visual[col], errors="coerce")
        st.dataframe(visual, use_container_width=True, hide_index=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Sobras não servidas (kg)", f"{visual['sobras_nao_servidas_kg'].sum(min_count=1):.2f}" if visual['sobras_nao_servidas_kg'].notna().any() else "—")
        m2.metric("Restos de pratos (kg)", f"{visual['restos_pratos_kg'].sum(min_count=1):.2f}" if visual['restos_pratos_kg'].notna().any() else "—")
        m3.metric("Perdas no preparo (kg)", f"{visual['perdas_preparo_kg'].sum(min_count=1):.2f}" if visual['perdas_preparo_kg'].notna().any() else "—")

        st.caption("As três categorias são exibidas separadamente e não devem ser somadas como se fossem o mesmo tipo de sobra.")
        csv_bytes = visual.to_csv(index=False, sep=SEPARADOR).encode("utf-8-sig")
        st.download_button(
            "Baixar registros em CSV", data=csv_bytes,
            file_name="EcoPrato_Registro_Refeicoes.csv", mime="text/csv"
        )

st.sidebar.divider()
st.sidebar.caption("Projeto escolar • Protótipo inicial • Não contém previsão real até a integração com o modelo.")
