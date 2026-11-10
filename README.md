# Top hits de Spotify (2000-2019): gráficos con matplotlib, seaborn y Streamlit

Ejercicio de visualización de datos del módulo *Sistemas de Big Data*. A partir de un conjunto de datos real de Kaggle se hacen **5 gráficos**, cada uno con **matplotlib** y con **seaborn**, y se presentan en una **aplicación de Streamlit**.

**Autor:** Daniel Meléndez Loreto

## Contenido del repositorio

| Archivo | Para qué sirve |
|---|---|
| `graficos_musica.ipynb` | Cuaderno de Colab con el análisis: limpieza de datos, los 5 gráficos (matplotlib y seaborn), resultados y conclusiones |
| `app.py` | Aplicación de Streamlit con los mismos gráficos, filtros por año y selector de librería |
| `requirements.txt` | Librerías necesarias |
| `data/` | Carpeta del conjunto de datos (ver más abajo) |

## Los 5 gráficos

1. **Barras:** canciones por género.
2. **Línea:** popularidad media por año.
3. **Dispersión:** duración frente a popularidad.
4. **Histograma:** distribución de la duración.
5. **Barras apiladas al 100 %:** porcentaje de canciones explícitas por año.

## Datos

Conjunto de datos *Top Hits Spotify from 2000-2019* (Kaggle): 2000 canciones y 18 columnas, archivo `songs_normalize.csv`. Descárgalo desde Kaggle y colócalo en `data/songs_normalize.csv`. Si no está, la app permite subirlo desde la propia página.

Decisiones de limpieza (explicadas en el cuaderno): se usan solo los años 2000-2019, se excluye el valor `set()` (canciones sin género) del gráfico de géneros y la duración se pasa de milisegundos a minutos.

## Cómo ejecutar la aplicación (Windows)

1. Instala Python 3 y abre una terminal en la carpeta del proyecto.
2. Instala las librerías:

   ```
   py -m pip install -r requirements.txt
   ```

3. Arranca la app:

   ```
   py -m streamlit run app.py
   ```

   Se abre en el navegador (normalmente en http://localhost:8501). Para pararla, pulsa `Ctrl+C` en la terminal.

## Resultados principales

- El pop aparece en el 81,65 % de las canciones (1633 de 2000); le siguen hip hop, R&B, Dance/Electronic y rock.
- La popularidad media se mueve entre unos 54 y 64 puntos casi todos los años, salvo un pico en 2018 (70,9) que estos datos no permiten explicar.
- La duración casi no influye en la popularidad (correlación de 0,051). La mayoría de canciones dura entre 3,4 y 4,1 minutos.
- Hay un grupo de canciones con popularidad 0, probablemente sin dato (hipótesis no verificada), que se puede excluir en la app con una casilla.

Las conclusiones completas y las limitaciones de cada gráfico están en el cuaderno.

## Tecnologías

Python, pandas, matplotlib, seaborn, Streamlit.
