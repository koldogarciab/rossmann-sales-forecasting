# Guía en español — Fase 4: modelos baseline y métricas

## Objetivo

Establecer referencias de rendimiento antes de optimizar modelos.

Este bloque compara:

1. media global de ventas en días abiertos;
2. media histórica por tienda;
3. media por tienda y día de la semana;
4. media por tienda, día de la semana y promoción;
5. Ridge con objetivo `Sales`;
6. Ridge con objetivo `log1p(Sales)`;
7. HistGradientBoosting con categorías codificadas mediante TargetEncoder;
8. el mismo boosting con objetivo logarítmico.

## Archivos nuevos

Copia:

- `04_baseline_models.ipynb` en `notebooks/`
- `metrics.py` en `src/`
- `phase_4_start_guide_ES.md` en `docs/`

No hay que modificar `requirements.txt`: todos los modelos pertenecen a scikit-learn.

## Métricas

### RMSPE

Es la métrica principal del proyecto:

`raíz de la media del cuadrado del error porcentual`

Las filas con ventas reales iguales a cero se excluyen porque el error porcentual no está definido.

### Métricas complementarias

- MAE: error absoluto medio.
- RMSE: penaliza más los errores grandes.
- WAPE: error absoluto total relativo a las ventas.
- Bias: indica sobreestimación o infraestimación agregada.

## Reglas de predicción

- Los modelos se entrenan únicamente con días en que la tienda estaba abierta.
- Las tiendas cerradas reciben predicción cero.
- Las predicciones negativas se recortan a cero.
- `Customers` no se utiliza.
- La validación mantiene los 48 días y las 856 tiendas del test.

## Modelos

### Medias históricas

Sirven como referencias transparentes. La versión más detallada utiliza:

`Store + DayOfWeek + Promo`

y aplica fallback a la media de la tienda y después a la media global.

### Ridge

Codifica las categorías con one-hot encoding y estandariza las variables numéricas.

Se prueba tanto con ventas directas como con `log1p(Sales)`.

### HistGradientBoosting

Utiliza TargetEncoder para convertir las categorías en variables numéricas compactas. Puede aprender relaciones no lineales e interacciones.

También se prueba con ventas directas y logarítmicas.

## Tiempo de ejecución

Ridge puede tardar varios minutos debido a la codificación de las 1.115 tiendas.

Los dos modelos de gradient boosting pueden tardar más. Deja terminar cada celda antes de continuar. Mientras aparezca `[*]`, el kernel sigue trabajando.

## Qué ejecutar

Abre:

`notebooks/04_baseline_models.ipynb`

con el kernel:

`Python (rossmann-forecasting)`

Ejecuta las celdas en orden hasta `Stop and review`.

No hagas commit todavía.

## Qué compartir

Envía:

- resultados de las medias históricas;
- resultados después de Ridge;
- tiempos de entrenamiento;
- tabla final de modelos;
- mejor modelo y RMSPE;
- diagnósticos por día, promoción y formato;
- ambos gráficos;
- cualquier error o warning.
