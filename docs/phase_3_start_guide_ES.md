# Guía en español — Fase 3: ingeniería de características y validación temporal

## Objetivo de este primer bloque

Crear exactamente las mismas variables predictivas para `train` y `test`, sin utilizar información que no esté disponible en el momento de hacer el forecast.

Este bloque todavía no entrena modelos. Primero comprueba que:

- todas las variables existen en train y test;
- no hay nulos en las columnas del modelo;
- los tipos de datos coinciden;
- `Sales` y `Customers` no entran como predictores;
- la validación es cronológica;
- el horizonte de validación tiene los mismos 48 días que el test de Kaggle.

## Archivos nuevos

Copia:

- `03_feature_engineering.ipynb` en `notebooks/`
- `features.py` en `src/`
- `__init__.py` en `src/`
- `phase_3_start_guide_ES.md` en `docs/`

## Principales variables creadas

### Calendario

- año, trimestre, mes, día y semana ISO;
- fin de semana;
- inicio y final de mes;
- días transcurridos desde el 1 de enero de 2013;
- codificaciones cíclicas de mes, semana y día de la semana.

### Competencia

- distancia imputada;
- logaritmo de la distancia;
- indicador de distancia ausente;
- fecha técnica de apertura;
- competidor activo;
- meses desde la apertura;
- indicador de fecha desconocida.

### Promo2

- fecha de inicio;
- mes incluido en el calendario Promo2;
- Promo2 activo;
- meses desde el inicio;
- indicador de fecha desconocida.

### Open

- `OpenMissingFlag` conserva la trazabilidad;
- `OpenFilled` completa como 1 los 11 valores ausentes de la tienda 622.

## Prevención de fuga de información

No se utilizarán como predictores:

- `Sales`, porque es el objetivo;
- `Customers`, porque no existe en test y se conoce después de la venta;
- `Date` directamente;
- `Id`;
- variables creadas a partir del resultado de ventas.

## Validación temporal

El test cubre 48 fechas. Por eso la validación utiliza los últimos 48 días del histórico:

- inicio: 14 de junio de 2015;
- final: 31 de julio de 2015.

La puntuación principal se calculará sobre las tiendas que también aparecen en test.

Las tiendas cerradas recibirán predicción cero. El modelo de ventas se entrenará con días abiertos.

## Qué ejecutar

Abre `notebooks/03_feature_engineering.ipynb` con el kernel `Python (rossmann-forecasting)` y ejecuta las celdas en orden hasta `Stop and review`.

No hagas todavía commit. Primero revisaremos juntos los controles y la población de validación.
