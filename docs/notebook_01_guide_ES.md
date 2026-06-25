# Guía en español — `01_data_audit.ipynb`

El notebook está escrito en inglés porque formará parte del portfolio. Esta guía explica qué hace cada bloque.

## Celda 1 — Título y alcance
Define el propósito del notebook y deja claro que todavía no se limpiarán ni transformarán datos.

## Celda 2 — Marco de negocio
Registra la variable objetivo, la unidad de predicción y las decisiones iniciales sobre `Customers`, validación temporal y uso del test de Kaggle.

## Celda 3 — Importaciones y versiones
Carga únicamente las librerías necesarias para la auditoría y muestra sus versiones. Esto ayuda a reproducir el análisis.

## Celda 4 — Rutas del proyecto
Busca automáticamente la raíz del repositorio, construye la ruta `data/raw/` y comprueba que estén los cuatro CSV esperados. Si falta alguno, el notebook se detiene con un mensaje claro.

## Celda 5 — Inventario de archivos
Muestra el tamaño de cada CSV en bytes, KB y MB. Sirve para detectar archivos vacíos, incompletos o inesperadamente grandes.

## Celda 6 — Carga de datos
Lee los cuatro CSV sin modificar el contenido original. `low_memory=False` evita que pandas infiera tipos por fragmentos y genere resultados inconsistentes.

## Celda 7 — Resumen general
Muestra filas, columnas y memoria utilizada por cada DataFrame.

## Celda 8 — Columnas y muestras
Enseña los nombres de columnas y las primeras y últimas filas de cada archivo. Permite comprobar estructura, orden y contenido básico.

## Celda 9 — Tipos de datos
Presenta el tipo inferido por pandas para cada columna. En esta fase no se corrige nada; solo se identifica qué columnas necesitarán tratamiento posterior.

## Celda 10 — Valores nulos
Calcula número y porcentaje de valores faltantes por columna. No todos los nulos son errores: algunos pueden ser estructurales, por ejemplo variables de `Promo2` cuando la tienda no participa.

## Celda 11 — Duplicados exactos
Busca filas totalmente repetidas en cada archivo.

## Celda 12 — Granularidad y claves
Comprueba si `Store + Date` identifica de forma única las observaciones de train y test, si `Store` es único en la tabla de tiendas y si `Id` es único en test y submission.

## Celda 13 — Auditoría de fechas
Convierte una copia de `Date` a fecha, identifica fechas no válidas, muestra rangos temporales y comprueba que `DayOfWeek` coincida con la fecha.

## Celda 14 — Diferencias entre train y test
Compara columnas y tipos. Es especialmente importante para detectar variables presentes durante el entrenamiento pero no disponibles al realizar predicciones futuras.

## Celda 15 — Dominios categóricos
Muestra los valores y frecuencias de variables de calendario, promociones y tipología de tienda. Ayuda a detectar codificaciones inesperadas.

## Celda 16 — Reglas básicas de negocio
Comprueba ventas o clientes negativos, ventas en días cerrados, días abiertos con venta cero y valores de `Open` fuera de su dominio esperado. Los resultados no se corrigen todavía.

## Celda 17 — Integridad entre tablas
Verifica que todas las tiendas de train y test tengan una fila correspondiente en `store.csv`.

## Celda 18 — Alineación con la submission
Comprueba que el número de filas y los identificadores de `sample_submission.csv` coincidan con `test.csv`.

## Celda 19 — Diccionario estructural inicial
Crea una tabla por columna con dataset, tipo, valores no nulos, nulos, porcentaje de nulos y cardinalidad.

## Celda 20 — Resumen de auditoría
Concentra las comprobaciones principales en una tabla de controles con resultado y valor observado.

## Celda 21 — Guardado de outputs
Guarda el diccionario inicial y el resumen en `reports/tables/`. Son outputs generados y revisables. Podrán incluirse en Git después de comprobar que contienen resultados útiles y reproducibles.

## Celda 22 — Punto de parada
Indica exactamente qué resultados debes compartir antes de continuar con el EDA o tomar decisiones de limpieza.
