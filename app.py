"""
App de Streamlit: top hits de Spotify (2000-2019).

Cómo funciona Streamlit (resumen):
- Este archivo es un script de Python normal. Streamlit lo ejecuta de arriba abajo.
- Cada llamada que empieza por `st.` pinta algo en la página (título, texto, gráfico...).
- Cuando el usuario cambia un control (slider, casilla...), Streamlit vuelve a ejecutar
  el script entero con el nuevo valor. Por eso los gráficos se actualizan solos.

Para ejecutarla:   py -m streamlit run app.py
"""
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib.ticker import MaxNLocator

# ---------------------------------------------------------------------------
# 1) Configuración de la página y constantes
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Top hits de Spotify (2000-2019)", page_icon="🎵", layout="wide")
sns.set_theme(style="whitegrid")

AZUL, NARANJA = "#2a78d6", "#eb6834"
RUTA_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "songs_normalize.csv")


# ---------------------------------------------------------------------------
# 2) Carga de datos
# ---------------------------------------------------------------------------
@st.cache_data  # guarda el resultado en memoria: el CSV no se relee en cada cambio de control
def leer_csv(ruta):
    return pd.read_csv(ruta)


st.title("🎵 Top hits de Spotify (2000-2019)")
st.write(
    "Análisis visual de las 2000 canciones más exitosas de Spotify entre 2000 y 2019. "
    "Cada gráfico se puede ver con **matplotlib** o con **seaborn**."
)

if os.path.exists(RUTA_CSV):
    df = leer_csv(RUTA_CSV)
else:
    # Si el CSV no está en data/, dejamos que el usuario lo suba desde la propia app
    st.warning("No encuentro `data/songs_normalize.csv`. Sube el archivo aquí:")
    archivo = st.file_uploader("songs_normalize.csv", type="csv")
    if archivo is None:
        st.stop()  # detiene el script hasta que se suba el archivo
    df = pd.read_csv(archivo)

# Columna nueva: duración en minutos (el CSV la trae en milisegundos)
df["duracion_min"] = df["duration_ms"] / 60000


# ---------------------------------------------------------------------------
# 3) Controles de la barra lateral
# ---------------------------------------------------------------------------
st.sidebar.header("Controles")
anio_min, anio_max = st.sidebar.slider("Años a mostrar", 2000, 2019, (2000, 2019))
libreria = st.sidebar.radio("Librería de gráficos", ["matplotlib", "seaborn"])
sin_ceros = st.sidebar.checkbox(
    "Excluir canciones con popularidad 0",
    help="Hay canciones con popularidad 0 que probablemente no tienen dato (hipótesis sin verificar).",
)

# Datos filtrados según los controles
d = df[(df["year"] >= anio_min) & (df["year"] <= anio_max)]
if sin_ceros:
    d = d[d["popularity"] > 0]
if d.empty:
    st.warning("No hay canciones con esos filtros.")
    st.stop()

# Fila de métricas
c1, c2, c3, c4 = st.columns(4)
c1.metric("Canciones", len(d))
c2.metric("Popularidad media", f"{d['popularity'].mean():.1f}")
c3.metric("Duración media", f"{d['duracion_min'].mean():.2f} min")
c4.metric("Explícitas", f"{d['explicit'].mean() * 100:.1f} %")


# ---------------------------------------------------------------------------
# 4) Funciones que dibujan cada gráfico (devuelven la figura)
# ---------------------------------------------------------------------------
def grafico_generos(d, lib):
    generos = d["genre"].str.split(", ").explode()   # "rock, pop" -> dos filas
    generos = generos[generos != "set()"]            # fuera las canciones sin género
    conteo = generos.value_counts()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if lib == "matplotlib":
        ax.barh(conteo.index, conteo.values, color=AZUL)
    else:
        sns.barplot(x=conteo.values, y=conteo.index, color=AZUL, ax=ax)
    ax.bar_label(ax.containers[0], padding=3)
    ax.invert_yaxis()
    ax.set_xlim(0, conteo.max() * 1.12)
    ax.set_xlabel("Número de canciones (una canción puede tener varios géneros)")
    ax.set_ylabel("")
    ax.set_title("Canciones por género")
    fig.tight_layout()
    return fig


def grafico_linea(d, lib):
    fig, ax = plt.subplots(figsize=(9, 4))
    if lib == "matplotlib":
        por_anio = d.groupby("year")["popularity"].mean()
        ax.plot(por_anio.index, por_anio.values, marker="o", color=AZUL)
    else:
        sns.lineplot(data=d, x="year", y="popularity", estimator="mean",
                     errorbar=("ci", 95), marker="o", color=AZUL, ax=ax)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))   # años enteros (sin 2002.5)
    ax.set_xlabel("Año")
    ax.set_ylabel("Popularidad media (0-100)")
    ax.set_title("Popularidad media por año")
    fig.tight_layout()
    return fig


def grafico_dispersion(d, lib):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if lib == "matplotlib":
        ax.scatter(d["duracion_min"], d["popularity"], alpha=0.35, s=20, color=AZUL)
    else:
        sns.scatterplot(data=d, x="duracion_min", y="popularity", hue="explicit",
                        alpha=0.45, s=25, ax=ax)
        if len(d) > 2:
            sns.regplot(data=d, x="duracion_min", y="popularity", scatter=False,
                        color="black", line_kws={"linewidth": 1.5}, ax=ax)
    ax.set_xlabel("Duración (min)")
    ax.set_ylabel("Popularidad (0-100)")
    ax.set_title("Duración frente a popularidad")
    fig.tight_layout()
    return fig


def grafico_histograma(d, lib):
    media, mediana = d["duracion_min"].mean(), d["duracion_min"].median()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if lib == "matplotlib":
        ax.hist(d["duracion_min"], bins=30, color=AZUL, edgecolor="white")
    else:
        sns.histplot(data=d, x="duracion_min", bins=30, kde=True, color=AZUL, ax=ax)
    ax.axvline(media, color="black", linestyle="--", label=f"Media: {media:.2f} min")
    ax.axvline(mediana, color=NARANJA, linestyle="-", label=f"Mediana: {mediana:.2f} min")
    ax.set_xlabel("Duración (min)")
    ax.set_ylabel("Número de canciones")
    ax.set_title("Distribución de la duración")
    ax.legend()
    fig.tight_layout()
    return fig


def grafico_apilado(d, lib):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if lib == "matplotlib":
        tabla = pd.crosstab(d["year"], d["explicit"], normalize="index") * 100
        no_exp = tabla.get(False, 0)
        si_exp = tabla.get(True, 0)
        ax.bar(tabla.index, no_exp, color=AZUL, label="No explícita")
        ax.bar(tabla.index, si_exp, bottom=no_exp, color=NARANJA, label="Explícita")
        ax.set_ylim(0, 100)
        ax.set_ylabel("% de canciones del año")
        ax.legend(ncols=2, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
        ax.set_title("Canciones explícitas y no explícitas por año", pad=32)
    else:
        sns.histplot(data=d, x="year", hue="explicit", multiple="fill", discrete=True,
                     palette={False: AZUL, True: NARANJA}, shrink=0.8, ax=ax)
        ax.set_ylabel("Proporción de canciones del año")
        ax.set_title("Canciones explícitas y no explícitas por año")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))   # años enteros
    ax.set_xlabel("Año")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 5) Pestañas con los 5 gráficos
# ---------------------------------------------------------------------------
pestanas = st.tabs(["1. Géneros", "2. Popularidad por año", "3. Duración vs popularidad",
                    "4. Distribución de duración", "5. Explícitas por año"])

graficos = [
    (grafico_generos, "Barras: comparan el número de canciones por género. Una canción puede "
                      "tener varios géneros, así que la suma supera el total de canciones."),
    (grafico_linea, "Línea: evolución de la popularidad media. En seaborn, la banda sombreada es el "
                    "intervalo de confianza al 95 %: si dos años se solapan, la diferencia puede ser ruido."),
    (grafico_dispersion, "Dispersión: cada punto es una canción. En seaborn se añade la recta de "
                         "tendencia y se colorea por si la canción es explícita."),
    (grafico_histograma, "Histograma: cuántas canciones hay en cada intervalo de duración. "
                         "La media queda por encima de la mediana por las pocas canciones muy largas."),
    (grafico_apilado, "Barras apiladas al 100 %: cada barra suma el 100 %; compara el reparto, "
                      "no el número de canciones."),
]

for pestana, (funcion, texto) in zip(pestanas, graficos):
    with pestana:
        fig = funcion(d, libreria)
        st.pyplot(fig)
        plt.close(fig)  # liberar memoria
        st.caption(texto)

# ---------------------------------------------------------------------------
# 6) Notas sobre los datos
# ---------------------------------------------------------------------------
with st.expander("Notas sobre los datos"):
    st.markdown(
        "- **Fuente:** *Top Hits Spotify from 2000-2019* (Kaggle), `songs_normalize.csv`.\n"
        "- Se usan solo canciones de 2000 a 2019: otros años tienen muy pocas canciones.\n"
        "- En `genre`, el valor `set()` indica canciones sin género y se excluye del gráfico de géneros.\n"
        "- Hay canciones con popularidad 0 que se separan del resto; usa la casilla de la barra "
        "lateral para ver cómo cambian los gráficos sin ellas.\n"
        "- Las conclusiones completas están en el cuaderno `graficos_musica.ipynb`."
    )
    if st.checkbox("Mostrar la tabla de datos filtrados"):
        st.dataframe(d.drop(columns=["duracion_min"]))
