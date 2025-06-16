
import streamlit as st
import pandas as pd
import json
import os
import datetime

ORGAOS_FILE = "orgaos.json"
SERVICOS_FILE = "servicos.json"
DATA_FILE = "dados_documentos.xlsx"

def carregar_lista(path, padrao):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(padrao, f, ensure_ascii=False, indent=4)
        return padrao

def salvar_nova_opcao(opcao, path):
    lista = carregar_lista(path, [])
    if opcao not in lista:
        lista.append(opcao)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(lista, f, ensure_ascii=False, indent=4)

orgaos = carregar_lista(ORGAOS_FILE, ["Prefeitura", "Secretaria de Saúde"])
servicos = carregar_lista(SERVICOS_FILE, ["Atendimento", "Consulta Técnica"])

if os.path.exists(DATA_FILE):
    df_dados = pd.read_excel(DATA_FILE)
else:
    df_dados = pd.DataFrame(columns=["DATA DE RECEBIMENTO", "ÓRGÃO SOLICITANTE", "TIPO DE SERVIÇO", "DESCRIÇÃO", "STATUS", "OBSERVAÇÕES"])

st.set_page_config(page_title="Controle de Documentos", layout="centered")
st.title("📁 Controle de Documentos")

if "iniciar" not in st.session_state:
    st.session_state.iniciar = False

if not st.session_state.iniciar:
    if st.button("📝 Novo Documento"):
        st.session_state.iniciar = True
else:
    with st.form("formulario"):
        col1, col2, col3 = st.columns([1, 1, 1])
        data_recebimento = col1.date_input("📅 Data de Recebimento", datetime.date.today())

        orgao = col2.selectbox("🏢 Órgão Solicitante", options=orgaos + ["Outro"])
        if orgao == "Outro":
            novo_orgao = col2.text_input("Informe o novo órgão")
            if novo_orgao:
                salvar_nova_opcao(novo_orgao, ORGAOS_FILE)
                orgaos.append(novo_orgao)
                orgao = novo_orgao

        servico = col3.selectbox("📌 Tipo de Serviço", options=servicos + ["Outro"])
        if servico == "Outro":
            novo_servico = col3.text_input("Informe o novo tipo de serviço")
            if novo_servico:
                salvar_nova_opcao(novo_servico, SERVICOS_FILE)
                servicos.append(novo_servico)
                servico = novo_servico

        descricao = st.text_area("📝 Descrição do Documento")
        status = st.selectbox("📊 Status", ["Pendente", "Respondido", "Finalizado"])
        observacoes = st.text_area("🗒️ Observações (opcional)")

        if st.form_submit_button("Salvar Documento"):
            nova_linha = {
                "DATA DE RECEBIMENTO": data_recebimento,
                "ÓRGÃO SOLICITANTE": orgao,
                "TIPO DE SERVIÇO": servico,
                "DESCRIÇÃO": descricao,
                "STATUS": status,
                "OBSERVAÇÕES": observacoes
            }
            df_dados = pd.concat([df_dados, pd.DataFrame([nova_linha])], ignore_index=True)
            df_dados.to_excel(DATA_FILE, index=False)
            st.success("Documento salvo com sucesso!")
            st.session_state.iniciar = False

st.markdown("---")
st.subheader("📊 Histórico de Documentos")
status_filtro = st.selectbox("Filtrar por Status", ["Todos"] + df_dados["STATUS"].unique().tolist() if not df_dados.empty else ["Todos"])

if status_filtro == "Todos":
    st.dataframe(df_dados, use_container_width=True)
else:
    st.dataframe(df_dados[df_dados["STATUS"] == status_filtro], use_container_width=True)
