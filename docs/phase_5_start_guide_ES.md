# Guía en español — Fase 5: mejora del modelo

## Objetivo

Mejorar el benchmark ganador de la Fase 4 sin perder su principal ventaja: el patrón histórico específico de cada tienda.

La fase introduce:

- medias históricas de largo plazo;
- medias recientes de 180 y 365 días;
- indicadores de tendencia;
- combinaciones entre media histórica y reciente;
- un modelo HGB que aprende una corrección residual;
- validación en tres periodos consecutivos de 48 días;
- métricas separadas para tiendas abiertas.

## Archivos nuevos

Copia:

- `05_model_improvement.ipynb` en `notebooks/`
- `history_features.py` en `src/`
- `phase_5_start_guide_ES.md` en `docs/`

No hace falta modificar `requirements.txt`.

## Por qué usamos tres folds

Un único periodo puede favorecer accidentalmente a un modelo.

Los tres bloques permiten comprobar si la mejora es estable y no depende únicamente del periodo 14 de junio–31 de julio de 2015.

Cada bloque:

- contiene 48 días;
- utiliza las 856 tiendas del test;
- se predice solo con información anterior a su fecha de inicio.

## Medias históricas

Para cada horizonte se calculan:

- media histórica por tienda;
- media por tienda y día;
- media por tienda, día y Promo;
- versiones de los últimos 180 y 365 días;
- número de observaciones disponibles;
- ratios de tendencia reciente frente al largo plazo.

Los cálculos se congelan al comienzo de cada horizonte. No utilizan ventas futuras.

## Modelo residual

El modelo no predice las ventas desde cero.

Primero obtiene el baseline y después aprende:

`log1p(ventas reales) - log1p(baseline)`

La predicción final se reconstruye sumando la corrección al baseline en escala logarítmica.

Para mantener la cronología, el residual se entrena con los 48 días inmediatamente anteriores a cada periodo de validación.

## Qué ejecutar

Abre `notebooks/05_model_improvement.ipynb` con el kernel:

`Python (rossmann-forecasting)`

Ejecuta las celdas en orden hasta `Stop and review`.

No hagas commit todavía.
