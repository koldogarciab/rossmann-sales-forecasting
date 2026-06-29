# Diseño conceptual de producción y monitorización

## 1. Patrón de despliegue

La solución se desplegaría como un proceso batch. El negocio necesita renovar un horizonte de planificación de aproximadamente seis semanas, por lo que una API en tiempo real no aporta una ventaja material frente a un pipeline programado y auditable.

## 2. Flujo operativo propuesto

1. Ingesta de ventas reales, maestro de tiendas, aperturas y promociones.
2. Validación de esquema, claves, nulos, duplicados e integridad referencial.
3. Construcción de variables de calendario, competencia y Promo2.
4. Cálculo de medias históricas móviles de 365 días.
5. Scoring de todas las combinaciones tienda-fecha del horizonte.
6. Aplicación de reglas:
   - forecast cero para tiendas cerradas;
   - fallback cuando falta una combinación histórica;
   - trazabilidad de imputaciones.
7. Ejecución de controles y reconciliaciones.
8. Publicación de:
   - tabla de predicción detallada;
   - resúmenes de negocio;
   - metadata versionada;
   - modelo SQL;
   - dataset de Power BI.

## 3. Frecuencia

- Ingesta de ventas: diaria.
- Actualización del forecast: semanal, antes del ciclo de planificación.
- Evaluación con actuals: diaria o semanal, según disponibilidad.
- Revisión formal del modelo: mensual.
- Reentrenamiento extraordinario: cuando se active un umbral de rendimiento o drift.

## 4. Monitorización

### Calidad de datos

- filas esperadas y recibidas;
- tiendas y fechas cubiertas;
- duplicados `Store + Date`;
- valores ausentes de `Open`;
- tiendas desconocidas;
- valores negativos;
- continuidad del calendario;
- coherencia entre tiendas cerradas y forecast cero.

### Rendimiento del forecast

Cuando estén disponibles las ventas reales:

- RMSPE;
- WAPE;
- MAE;
- bias agregado;
- métricas por StoreType, weekday, Promo y deciles de tienda;
- porcentaje de tiendas con deterioro relevante.

### Data drift

Comparar la ventana reciente con la referencia de entrenamiento:

- distribución de ventas;
- porcentaje de días abiertos;
- porcentaje de días promocionales;
- mix de StoreType y Assortment;
- CompetitionDistance y antigüedad de competencia;
- número de tiendas nuevas o cerradas;
- cambios en el calendario Promo2.

Se pueden utilizar PSI, Jensen-Shannon distance o pruebas estadísticas simples, acompañadas de controles de negocio.

## 5. Umbrales orientativos

El modelo debe revisarse si ocurre alguno de estos casos:

- RMSPE móvil supera en más de un 10 % el benchmark de referencia;
- bias absoluto permanece por encima del 3 % durante varias ventanas;
- falla cualquier control crítico de población o integridad;
- aparecen categorías o tiendas no cubiertas por el fallback;
- el drift supera el umbral acordado para una variable crítica;
- cambia de forma estructural la política promocional o de aperturas.

Los umbrales deben calibrarse con experiencia real y no considerarse reglas universales.

## 6. Versionado

Cada ejecución debería registrar:

- versión de código o commit;
- fecha de corte de datos;
- ventana histórica;
- versión del modelo;
- parámetros y jerarquía de fallback;
- métricas de validación;
- controles de calidad;
- timestamp;
- ubicación de outputs.

`models/final_model_metadata.json` ya representa una primera versión de este registro.

## 7. Actualización y champion/challenger

El modelo actual actuaría como champion por su estabilidad y transparencia. Un challenger podría probar:

- residual boosting con una ventana de entrenamiento mayor;
- nuevos drivers externos;
- modelos jerárquicos;
- intervalos de predicción;
- calibración por segmentos.

El challenger solo sustituiría al champion si mejora el rendimiento en varios folds, mantiene el bias controlado y no introduce una variabilidad temporal excesiva.

## 8. Infraestructura posible

Una implementación real podría utilizar:

- almacenamiento cloud o base SQL para datos de entrada;
- Prefect, Airflow o Azure Data Factory para orquestación;
- contenedor Docker para reproducibilidad;
- GitHub Actions para tests y validaciones;
- MLflow o un registro equivalente para versiones y métricas;
- Power BI Service para publicación y refresh;
- alertas por email, Teams o Slack.

Estas herramientas son opcionales. La arquitectura lógica es más importante que una plataforma concreta.

## 9. Seguridad y gobierno

- acceso mínimo necesario a datos y dashboard;
- separación entre datos raw, processed y outputs;
- logs de ejecución;
- conservación de metadata;
- revisión de cambios mediante Git;
- documentación de imputaciones y reglas;
- rollback a la última versión estable.

## 10. Recuperación ante fallos

Si falla una fuente o un control crítico:

1. no publicar un nuevo forecast;
2. conservar la última versión aprobada;
3. registrar el error;
4. notificar al responsable;
5. corregir o completar la fuente;
6. reejecutar el pipeline;
7. validar reconciliaciones antes de publicar.
