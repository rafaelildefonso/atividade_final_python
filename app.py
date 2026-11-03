# 4. Indicador: Índice de Desenvolvimento Humano (IDH / IDHM) 
# ●  Persona / Cenário:

# ○  Personagens: João (Governador do Maranhão), Helder (Governador do Pará) , Gladson (Governador do Acre), Susu (Governador da Bahia), Verinha (Governadora de Minas Gerais). 
# ○  História: O consórcio de governadores deseja criar um fundo regional para redução de desigualdades. Eles necessitam analisar as três dimensões do IDH (Longevidade, Educação e Renda) para identificar as prioridades de investimento social. 

# ●  Perguntas de Negócio / Análise:
# ○  Qual a evolução temporal do IDHM desde os anos 2000 até o dado mais recente? 
# ○  Quais municípios possuem os menores/maiores índices e qual é a dispersão entre os estados? 

# ●  Requisitos para o Dashboard (Streamlit): 
# ○  Barra lateral: Seleção do filtro de UF e anos. 
# ○  Gráficos: Gráfico de radar/aranha paEra comparar os subíndices do IDH por estado; 
# ○  Conteúdo adicional: Reportagens sobre projetos de superação da extrema pobreza no Brasil e infográficos/imagens sobre índices sociais. 

# Apresentação 
# ●  Roda de conversa e explicação dos cenários. 
# ●  Vocês são uma startup de análise de dados.

# pip install xlrd streamlit plotly pandas

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IDH", layout="wide", page_icon="📈")


# # # Carregar arquivo
caminho_arquivo = "Tabela4.csv"


df_raw = pd.read_csv(caminho_arquivo, sep=";", encoding="latin-1", skiprows=1, decimal=",")

filtrado = ["MA","PA","BA","MG"]

df_raw_filtrado = df_raw[df_raw["Sigla"].isin(filtrado)]


anos = [c for c in df_raw_filtrado.columns if str(c).isdigit()]
print(anos)

id_vars = [c for c in df_raw_filtrado.columns if c not in anos]
df_filtrado_longo = df_raw_filtrado.melt(
    id_vars=id_vars,
    value_vars=anos,
    var_name="Ano",
    value_name="IDH",
)
df_filtrado_longo["Ano"] = df_filtrado_longo["Ano"].astype(int)
df_filtrado_longo["IDH"] = pd.to_numeric(df_filtrado_longo["IDH"])
df_filtrado_longo["KPI"] = ((df_filtrado_longo["IDH"]*(85-20))+20)
df_filtrado_longo.head()

st.dataframe(df_filtrado_longo)

try:
    # Barra lateral
    st.sidebar.header("Filtros")

#     # Seleção de ano
    anos_disponives = sorted(df_filtrado_longo["Ano"].unique(), reverse=True)
    ano_selecionado = st.sidebar.selectbox("Selecione o ano:", anos_disponives)

#     # Seleção de localidades
    localidades_disponiveis = df_filtrado_longo["Estado"].unique().tolist()
    localidades_selecionadas = st.sidebar.multiselect(
        "Selecione as Regiões/UFs",
        options=localidades_disponiveis,
        default=["Maranhão","Pará","Bahia","Minas Gerais"]
    )

#     # Corpo da aplicação
    st.title("Indices que interferem no IDH")
    st.markdown("Análise de indices publicos que interferem na qualidade de vida do povo")

#     # Filtrar Dataframe com base nas seleções
    df_filtrado = df_filtrado_longo[(df_filtrado_longo["Ano"] == ano_selecionado) & (df_filtrado_longo["Estado"].isin(localidades_selecionadas))]

    if not df_filtrado.empty:
        # Visualização em tabela Titulo
        st.subheader(f"Dados em tabela ({ano_selecionado})")
        st.dataframe(df_filtrado[["Estado","IDH","Ano"]].reset_index(drop=True),use_container_width=True)

        st.markdown("---")
        st.subheader("Gráficos Comparativos")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.line_polar(
                df_filtrado,
                r="IDH",
                theta="Estado",
                line_close=True,
                markers=True
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Nenhuma localidade selecionada nos filtros da barra lateral.")

except Exception as e:
    st.error(f"Erro: {e}")
    st.info("Deu erro")


st.image("reportagens/rep1.png")
st.image("reportagens/rep2.png")