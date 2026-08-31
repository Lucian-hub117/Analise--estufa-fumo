import streamlit as st
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="Análise Estufas de Fumo - Lean Six Sigma", page_icon="🌱", layout="centered")

st.title("🌱 Análise de Dados - Estufas de Fumo")
st.caption("Lean Six Sigma | Multiagentes de IA")

with st.sidebar:
    st.header("Configuração")
    api_key = st.text_input("Chave de API (OpenAI)", type="password", help="Sua chave nunca é salva, só usada durante essa sessão")
    st.markdown("---")
    st.markdown("**Sobre este app**")
    st.markdown("3 agentes de IA (Coletor, Analista Six Sigma, Redator) analisam os dados dos lotes das estufas e geram um relatório com causas raiz e recomendações.")

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


def chamar_agente(client, system_prompt, user_prompt):
    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    return resposta.choices[0].message.content


st.subheader("2. Rodar análise")

if st.button("🔍 Analisar dados", type="primary", disabled=not (api_key and dados_texto)):
    with st.spinner("Os agentes estão analisando os dados..."):
        try:
            client = OpenAI(api_key=api_key)

            resumo = chamar_agente(
                client,
                system_prompt=(
                    "Você é um Coletor de Dados especialista em preparar dados de processos "
                    "industriais para análise estatística. Organize e resuma os dados recebidos, "
                    "destacando volumes por estufa e por classe. Responda em português."
                ),
                user_prompt=f"Organize e resuma estes dados de lotes de estufas de fumo:\n\n{dados_texto}",
            )
            st.markdown("### 📊 Dados organizados")
            st.markdown(resumo)

            analise = chamar_agente(
                client,
                system_prompt=(
                    "Você é um Analista Six Sigma especialista em processos agroindustriais. "
                    "Identifique causas raiz e padrões de variação na classificação de qualidade "
                    "(classes A, B, C) entre e dentro das estufas, considerando temperatura, "
                    "umidade e outras variáveis disponíveis. Use ferramentas como Pareto e análise "
                    "de variação. Responda em português."
                ),
                user_prompt=f"Dados organizados:\n\n{resumo}\n\nDados originais:\n\n{dados_texto}",
            )
            st.markdown("### 🔬 Análise de causas raiz")
            st.markdown(analise)

            relatorio = chamar_agente(
                client,
                system_prompt=(
                    "Você é um Redator Técnico especialista em comunicar achados técnicos para "
                    "gestores de produção. Escreva um relatório final claro e objetivo, em "
                    "português, com: resumo do problema, principais causas identificadas, e "
                    "recomendações práticas para reduzir o retrabalho e aumentar a % de lotes "
                    "na classe esperada."
                ),
                user_prompt=f"Análise realizada:\n\n{analise}",
            )
            st.success("Análise concluída!")
            st.markdown("### 📋 Relatório final")
            st.markdown(relatorio)
            st.download_button("Baixar relatório (.txt)", relatorio, file_name="relatorio_estufas.txt")

        except Exception as e:
            st.error(f"Erro ao rodar a análise: {e}")

elif not api_key:
    st.info("Insira sua chave de API na barra lateral para começar.")
elif not dados_texto:
    st.info("Envie ou cole os dados dos lotes para habilitar a análise.")
