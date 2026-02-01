import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st 
import tmdbsimple as tmdb

# --- Configuração da página ---
st.set_page_config(page_title="🎬 Dashboard de Filmes", layout="wide")

# --- Estilo inicial ---
st.markdown(
    """
    <style>
    .main {
        background-color: #0d0d0d;
        color: #f5f5f5;
    }
    h1, h2, h3 {
        color: #ffcc00;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='text-align: center; color: #ffcc00;'>🎬 Dashboard de Filmes</h1>
    <p style='text-align: center;'>Projeto criado para aprendizado durante a <b>Imersão Alura</b>, com dados reais da API TMDb.</p>
    """,
    unsafe_allow_html=True
)

# --- Carregar chave da API ---
tmdb.API_KEY = st.secrets["TMDB_API_KEY"]

# --- Sidebar ---
st.sidebar.header("🎥 Filtros")
opcao = st.sidebar.radio("Selecione:", ["Populares", "Top Rated", "Por Gênero"])

# --- Buscar dados ---
movie = tmdb.Movies()
if opcao == "Populares":
    filmes = movie.popular(language="pt-BR")["results"]
elif opcao == "Top Rated":
    filmes = movie.top_rated(language="pt-BR")["results"]
else:
    genre = st.sidebar.selectbox("Escolha o gênero:", ["28 - Ação", "878 - Ficção Científica", "35 - Comédia", "18 - Drama", "10749 - Romance"])
    genre_id = int(genre.split(" - ")[0])
    filmes = tmdb.Discover().movie(with_genres=genre_id, language="pt-BR")["results"]

# --- Transformar em DataFrame ---
df = pd.DataFrame(filmes)[["title", "release_date", "vote_average", "vote_count", "poster_path", "overview"]]
df["release_year"] = pd.to_datetime(df["release_date"]).dt.year

# --- Renomear colunas para português ---
df = df.rename(columns={
    "title": "Título",
    "release_date": "Data de lançamento",
    "vote_average": "Nota média",
    "vote_count": "Número de votos",
    "release_year": "Ano de lançamento",
    "overview": "Sinopse",
    "poster_path": "Pôster"
})

# --- Filtros adicionais ---
anos = sorted(df["Ano de lançamento"].dropna().unique())
ano_range = st.sidebar.slider("Ano de lançamento", min_value=int(min(anos)), max_value=int(max(anos)), value=(int(min(anos)), int(max(anos))))
nota_min = st.sidebar.slider("Nota mínima", min_value=0.0, max_value=10.0, value=5.0)

df_filtrado = df[(df["Ano de lançamento"].between(*ano_range)) & (df["Nota média"] >= nota_min)]

# --- Mostrar pôsteres com sinopse em 2 colunas ---
st.subheader("🎞️ Catálogo de Filmes") 
st.markdown("<div style='margin-top: 20px'></div>", unsafe_allow_html=True)

# cria 2 colunas
cols = st.columns(2)

for i, row in enumerate(df_filtrado.head(10).itertuples()):
    col = cols[i % 2] 
    with col:
        st.markdown(
            f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 30px;">
                <img src="https://image.tmdb.org/t/p/w200{row.Pôster}" style="border-radius: 8px; margin-right: 20px;" />
                <div style="max-width: 300px;">
                    <h4 style="margin-bottom: 5px; color: #ffcc00;">{row.Título}</h4>
                    <div style="font-size: 14px; color: #ccc; max-height: 100px; overflow-y: auto;">
                        {row.Sinopse}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# --- Gráficos lado a lado ---
st.subheader("📊 Comparação de distribuições")
st.markdown("<div style='margin-top: 20px'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Contagem de filmes por faixa de nota**")
    fig_count = px.histogram(
        df_filtrado,
        x="Nota média",
        nbins=10,
        color="Ano de lançamento",
        title="Contagem de filmes",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_count, use_container_width=True)

with col2:
    st.markdown("**Soma de votos por faixa de nota**")
    fig_sum = px.histogram(
        df_filtrado,
        x="Nota média",
        y="Número de votos",
        nbins=10,
        color="Ano de lançamento",
        title="Soma de votos",
        histfunc="sum",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_sum, use_container_width=True)

# --- Gráfico 2: Notas por ano ---
st.subheader("🎞️ Notas por ano")
fig2 = px.scatter(df_filtrado, x="Ano de lançamento", y="Nota média", size="Número de votos",
                  hover_name="Título", title="Notas dos filmes",
                  color="Nota média", color_continuous_scale="viridis")
st.plotly_chart(fig2, use_container_width=True)

# --- Gráfico 3: Top 10 por votos ---
st.subheader("🔥 Filmes mais votados")
top_votados = df_filtrado.nlargest(10, "Número de votos")
fig3 = px.bar(top_votados, x="Título", y="Número de votos", color="Nota média",
              title="Top 10 filmes mais votados", color_continuous_scale="sunset")
st.plotly_chart(fig3, use_container_width=True)

# --- Gráfico 4: Média de notas por ano ---
st.subheader("📊 Média de notas por ano")
media_ano = df_filtrado.groupby("Ano de lançamento")["Nota média"].mean().reset_index()
fig4 = px.line(media_ano, x="Ano de lançamento", y="Nota média",
               title="Média de notas por ano", markers=True)
st.plotly_chart(fig4, use_container_width=True)

# --- Gráfico 5: Relação votos x notas ---
st.subheader("⚖️ Relação entre votos e notas")
fig5 = px.scatter(df_filtrado, x="Número de votos", y="Nota média",
                  size="Nota média", hover_name="Título",
                  title="Correlação entre votos e notas",
                  color="Ano de lançamento", color_discrete_sequence=px.colors.qualitative.Bold)
st.plotly_chart(fig5, use_container_width=True)
