import streamlit as st
import pandas as pd
import os
from crewai import Agent, Task, Crew

st.set_page_config(page_title="Análise Estufas de Fumo - Lean Six Sigma", page_icon="🌱", layout="centered")

st.title("🌱 Análise de Dados - Estufas de Fumo")
st.caption("Lean Six Sigma | Multiagentes de IA")

# --- Configuração da chave de API ---
with st.sidebar:
    st.header("Configuração")
    api_key = st.text_input("Chave de API (OpenAI)", type="password", help="Sua chave nunca é salva, só usada durante essa sessão")
    st.markdown("---")
    st.markdown("**Sobre este app**")
    st.markdown("3 agentes de IA analisam os dados dos lotes das estufas e geram um relatório com causas raiz e recomendações.")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

# --- Entrada de dados ---
st.subheader("1. Envie os dados")
modo = st.radio("Como você quer enviar os dados?", ["Upload de CSV/Excel", "Colar texto manualmente"])

dados_texto = None

if modo == "Upload de CSV/Excel":
    arquivo = st.file_uploader("Selecione o arquivo (CSV ou XLSX)", type=["csv", "xlsx"])
    if arquivo is not None:
        if arquivo.name.endswith(".csv"):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)
        st.dataframe(df, use_container_width=True)
        dados_texto = df.to_string()
else:
    dados_texto = st.text_area("Cole os dados dos lotes aqui", height=200,
                                 placeholder="Ex: Estufa, Lote, Data, Temperatura, Umidade, Classe...")

# --- Executar análise ---
st.subheader("2. Rodar análise")

if st.button("🔍 Analisar dados", type="primary", disabled=not (api_key and dados_texto)):
    with st.spinner("Os agentes estão analisando os dados... isso pode levar 1-2 minutos"):

        coletor = Agent(
            role="Coletor de Dados",
            goal="Organizar e resumir os dados brutos recebidos",
            backstory="Especialista em preparar dados de processos industriais para análise estatística.",
            verbose=False
        )

        analista = Agent(
            role="Analista Six Sigma",
            goal="Identificar causas raiz e padrões nos dados de qualidade das estufas de fumo",
            backstory=(
                "Especialista em Lean Six Sigma com foco em processos agroindustriais. "
                "Usa ferramentas como Pareto, análise de variação entre e dentro de estufas, "
                "e correlação entre temperatura/umidade e classificação de qualidade (A, B, C)."
            ),
            verbose=False
        )

        redator = Agent(
            role="Redator Técnico",
            goal="Transformar a análise em um relatório claro e acionável",
            backstory="Especialista em comunicar achados técnicos para gestores de produção, em português.",
            verbose=False
        )

        tarefa_coleta = Task(
            description=f"Organize e resuma os seguintes dados de lotes de estufas de fumo: {dados_texto}",
            agent=coletor,
            expected_output="Dados organizados e resumidos, destacando volumes por estufa e por classe"
        )

        tarefa_analise = Task(
            description=(
                "Com base nos dados organizados, identifique as principais causas de variação "
                "na classificação de qualidade (classes A, B, C) entre e dentro das estufas. "
                "Considere temperatura, umidade e outras variáveis disponíveis."
            ),
            agent=analista,
            expected_output="Lista de causas raiz prováveis, com evidências estatísticas quando possível"
        )

        tarefa_relatorio = Task(
            description=(
                "Escreva um relatório final em português, claro e objetivo, com: "
                "resumo do problema, principais causas identificadas, e recomendações práticas "
                "para reduzir o retrabalho e aumentar a % de lotes na classe esperada."
            ),
            agent=redator,
            expected_output="Relatório estruturado em português"
        )

        crew = Crew(
            agents=[coletor, analista, redator],
            tasks=[tarefa_coleta, tarefa_analise, tarefa_relatorio],
            verbose=False
        )

        try:
            resultado = crew.kickoff()
            st.success("Análise concluída!")
            st.subheader("📋 Relatório")
            st.markdown(str(resultado))
            st.download_button("Baixar relatório (.txt)", str(resultado), file_name="relatorio_estufas.txt")
        except Exception as e:
            st.error(f"Erro ao rodar a análise: {e}")

elif not api_key:
    st.info("Insira sua chave de API na barra lateral para começar.")
elif not dados_texto:
    st.info("Envie ou cole os dados dos lotes para habilitar a análise.")
