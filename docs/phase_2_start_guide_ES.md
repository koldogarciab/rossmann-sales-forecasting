# Guía en español — Inicio de la Fase 2 (EDA)

## Objetivo de este primer bloque

Preparar una tabla analítica fiable antes de comenzar los gráficos de ventas.

Todavía no se estudian tendencias, promociones ni estacionalidad. Primero se comprueba que la unión entre ventas y tiendas:

- no pierde filas;
- no duplica registros;
- mantiene una fila por tienda y fecha;
- incorpora correctamente los atributos de tienda.

## Qué hace cada parte

1. **Importaciones y rutas**  
   Carga pandas y localiza automáticamente la raíz del proyecto.

2. **Carga de train y store**  
   Lee únicamente el histórico y la tabla maestra de tiendas.

3. **Conversión de Date y merge**  
   Convierte `Date` a fecha y une `train` con `store` mediante `Store`.  
   `validate="many_to_one"` impide que un error en la tabla maestra multiplique filas.

4. **Variables de calendario**  
   Crea año, trimestre, mes, semana, día y marcadores de fin de semana e inicio/final de mes.  
   Son transformaciones descriptivas derivadas exclusivamente de la fecha.

5. **Validación de granularidad**  
   Confirma que continúa existiendo una única fila por `Store + Date`.

6. **Cobertura histórica por tienda**  
   Calcula la primera y última fecha, número de registros y porcentaje de cobertura de cada tienda.

7. **Tiendas abiertas con ventas cero**  
   Aísla los 54 casos identificados en la auditoría para estudiar si se concentran en tiendas o fechas concretas.

8. **Guardado de tablas**  
   Genera:
   - `reports/tables/eda_store_history.csv`
   - `reports/tables/eda_open_zero_sales.csv`

## Qué ejecutar

Copia `02_eda.ipynb` dentro de la carpeta `notebooks/`, ábrelo con el kernel `Python (rossmann-forecasting)` y ejecuta todas las celdas hasta el apartado `Stop and review`.

No hagas todavía commit. Primero revisaremos juntos los resultados.
