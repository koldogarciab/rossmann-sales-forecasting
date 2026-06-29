# Especificación del dashboard — Fase 8

## Principio de diseño

El informe debe responder primero a las preguntas de negocio y después mostrar el detalle técnico. Se usará una estructura de cuatro páginas, con fondo claro, alto contraste, pocas categorías por gráfico y una jerarquía visual consistente.

## Página 1 — Executive Forecast

**Pregunta principal:** ¿cuánto se prevé vender, cuándo y con qué perfil operativo?

### KPIs

- Forecast Sales
- Forecast Sales per Open Store Day
- Forecast Stores
- Forecast Promo Uplift %

### Visuales

1. Gráfico de líneas con `dim_date[Date]` y las medidas `Actual Sales` y `Forecast Sales`.
2. Columnas con `dim_date[DayName]` y `Forecast Sales`.
3. Barras con `dim_store[StoreType]` y `Forecast Sales`.
4. Matriz por `StoreType` y `Assortment` con ventas, días abiertos y venta media.

### Segmentadores

- StoreType
- Assortment
- Promo2
- Date

Para el gráfico temporal, aplicar inicialmente un filtro desde `2015-01-01` hasta `2015-09-17` para que la transición entre histórico y forecast sea legible.

## Página 2 — Store Performance

**Pregunta principal:** ¿qué tiendas y formatos concentran el forecast?

### KPIs

- Top Store Forecast Sales
- Forecast Sales per Open Store Day
- Forecast Open Store Days
- Forecast Closed Store Days

### Visuales

1. Barras horizontales: Top 10 stores por `Forecast Sales`.
2. Dispersión:
   - X: `dim_store[CompetitionDistance]`
   - Y: `Forecast Sales per Open Store Day`
   - Size: `Forecast Sales`
   - Legend: `dim_store[StoreType]`
   - Details: `dim_store[Store]`
3. Tabla de tiendas con Store, StoreType, Assortment, Forecast Sales, Open Store Days, Promo Store Days, Average Sales y Rank.
4. Matriz StoreType × Assortment.

## Página 3 — Promotion & Calendar

**Pregunta principal:** ¿cómo cambia el rendimiento previsto con las promociones y el calendario?

### KPIs

- Forecast Promo Sales
- Forecast Non-Promo Sales
- Forecast Promo Average
- Forecast Promo Uplift %

### Visuales

1. Columnas agrupadas por `DayName` con `Forecast Promo Average` y `Forecast Non-Promo Average`.
2. Gráfico combinado por Date:
   - columnas: Forecast Promo Store Days;
   - línea: Forecast Sales.
3. Barras por StateHoliday con Forecast Sales.
4. Matriz DayName × Promo con Forecast Sales per Open Store Day.

Mantener `DayName` ordenado por `DayOfWeek`.

## Página 4 — Model & Data Quality

**Pregunta principal:** ¿es fiable el forecast y están controlados los datos?

### KPIs

- Mean RMSPE
- RMSPE Standard Deviation
- Kaggle Public RMSPE
- Kaggle Private RMSPE
- Controls Status

### Visuales

1. Tabla de controles: Area, ControlName, Passed, ObservedValue, ExpectedValue y Tolerance.
2. Tabla o tarjetas de metadata: ModelName, HistoryWindowDays, ForecastStart, ForecastEnd y MissingOpenValues.
3. Texto explicativo breve:
   - modelo final basado en los 365 días recientes;
   - validación temporal de tres folds de 48 días;
   - Private Score prácticamente alineado con el backtest;
   - tiendas cerradas con forecast cero.

## Formatos recomendados

- Sales: moneda sin decimales o display units en millones.
- Sales per Open Store Day: moneda con cero decimales.
- RMSPE y uplift: porcentaje con dos decimales.
- Counts: entero con separador de miles.
- Títulos y etiquetas del informe: inglés.
