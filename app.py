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
import geobr

st.set_page_config(page_title="IDH", layout="wide", page_icon="📈")

# Carregar arquivo
caminho_arquivo = "Tabela4.csv"

df_raw = pd.read_csv(
    caminho_arquivo,
    sep=";",
    encoding="latin-1",
    skiprows=1,
    decimal=","
)

# IMPORTANTE: manter todos os estados para permitir o mapa do Brasil
df_raw_filtrado = df_raw.copy()

# Transformar dados para formato longo
anos = [c for c in df_raw_filtrado.columns if str(c).isdigit()]

id_vars = [c for c in df_raw_filtrado.columns if c not in anos]

df_filtrado_longo = df_raw_filtrado.melt(
    id_vars=id_vars,
    value_vars=anos,
    var_name="Ano",
    value_name="IDH",
)

df_filtrado_longo["Ano"] = df_filtrado_longo["Ano"].astype(int)
df_filtrado_longo["IDH"] = pd.to_numeric(
    df_filtrado_longo["IDH"], errors="coerce"
)

df_filtrado_longo["KPI"] = (
    df_filtrado_longo["IDH"] * (85 - 20) + 20
)

try:
    # Barra lateral
    st.sidebar.header("Filtros")

    anos_disponiveis = sorted(
        df_filtrado_longo["Ano"].unique(),
        reverse=True
    )

    ano_selecionado = st.sidebar.selectbox(
        "Selecione o ano:",
        anos_disponiveis
    )

    localidades_disponiveis = sorted(
        df_filtrado_longo["Estado"].dropna().unique().tolist()
    )

    estados_padrao = [
        estado for estado in [
            "Maranhão", "Pará", "Bahia", "Minas Gerais"
        ]
        if estado in localidades_disponiveis
    ]

    localidades_selecionadas = st.sidebar.multiselect(
        "Selecione as Regiões/UFs",
        options=localidades_disponiveis,
        default=estados_padrao
    )

    # Corpo da aplicação
    st.title("Índices que interferem no IDH")

    st.markdown(
        "Análise de índices públicos que interferem na "
        "qualidade de vida da população."
    )

    # Filtrar dados
    df_filtrado = df_filtrado_longo[
        (df_filtrado_longo["Ano"] == ano_selecionado)
        & (df_filtrado_longo["Estado"].isin(localidades_selecionadas))
    ].dropna(subset=["IDH"])

    if not df_filtrado.empty:

        st.subheader(f"Dados em tabela ({ano_selecionado})")

        st.dataframe(
            df_filtrado[["Estado", "IDH", "Ano"]].reset_index(drop=True),
            use_container_width=True
        )

        st.markdown("---")
        st.subheader("Gráficos Comparativos")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.line_polar(
                df_filtrado,
                r="IDH",
                theta="Estado",
                line_close=True,
                markers=True,
                title="Comparação do IDH por estado"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig_bar = px.bar(
                df_filtrado,
                x="Estado",
                y="IDH",
                text="IDH",
                labels={
                    "IDH": "IDH",
                    "Estado": "Estado"
                },
                title="IDH por estado"
            )

            fig_bar.update_traces(
                texttemplate="%{text:.3f}",
                textposition="outside"
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        # NOVO GRÁFICO: BOXPLOT
        st.markdown("---")
        st.subheader("Dispersão dos índices de desenvolvimento")

        fig_box = px.box(
            df_filtrado,
            x="Estado",
            y="IDH",
            color="Estado",
            points="outliers",
            title="Boxplot - Distribuição do IDH por estado",
            labels={
                "Estado": "Estado",
                "IDH": "Índice de Desenvolvimento Humano"
            }
        )

        fig_box.update_layout(
            showlegend=False,
            yaxis_title="IDH",
            xaxis_title="Estados"
        )

        st.plotly_chart(fig_box, use_container_width=True)

    else:
        st.warning(
            "Nenhuma localidade selecionada nos filtros "
            "da barra lateral."
        )

    # NOVO GRÁFICO: MAPA DE CALOR DO BRASIL
    st.markdown("---")
    st.subheader(f"Mapa de calor do IDH no Brasil ({ano_selecionado})")

    # Pegar todos os dados do Brasil no ano selecionado
    df_mapa = df_filtrado_longo[
        df_filtrado_longo["Ano"] == ano_selecionado
    ].dropna(subset=["IDH"])

    # Calcular a média do IDH de cada estado
    df_mapa = (
        df_mapa.groupby("Sigla", as_index=False)
        ["IDH"].mean()
    )

    df_mapa.rename(
        columns={"IDH": "IDH_medio"},
        inplace=True
    )

    # Carregar mapa geográfico dos estados brasileiros
    estados_geo = geobr.read_state(year=2020)

    # Criar mapa de calor
    fig_mapa = px.choropleth(
        df_mapa,
        geojson=estados_geo.__geo_interface__,
        locations="Sigla",
        featureidkey="properties.abbrev_state",
        color="IDH_medio",
        color_continuous_scale="RdYlGn",
        range_color=(0, 1),
        hover_name="Sigla",
        hover_data={
            "IDH_medio": ":.3f",
            "Sigla": False
        },
        title="Distribuição do IDH médio por estado"
    )

    fig_mapa.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig_mapa.update_layout(
        height=650,
        coloraxis_colorbar={
            "title": "IDH",
            "tickformat": ".2f"
        }
    )

    st.plotly_chart(
        fig_mapa,
        use_container_width=True
    )

except Exception as e:
    st.error(f"Erro: {e}")
    st.info("Verifique os dados e as colunas do arquivo CSV.")

# Reportagens
st.markdown("---")
st.subheader("Reportagens e conteúdos adicionais")

st.image("reportagens/rep1.png")
st.image("reportagens/rep2.png")
