# Fase 0 — Guía de preparación local

## 1. Crear o registrar el repositorio en GitHub Desktop

1. Extrae la carpeta `rossmann-sales-forecasting`.
2. Abre GitHub Desktop.
3. Selecciona **File > Add local repository**.
4. Elige la carpeta extraída.
5. Si GitHub Desktop indica que todavía no es un repositorio Git, selecciona la opción para crear un repositorio en esa carpeta.
6. Mantén el repositorio privado mientras el proyecto está en construcción.
7. No publiques todavía los CSV.

## 2. Colocar los datos

Copia estos cuatro archivos dentro de `data/raw/`:

```text
data/raw/train.csv
data/raw/store.csv
data/raw/test.csv
data/raw/sample_submission.csv
```

No cambies sus nombres. La carpeta está configurada para que Git no suba los CSV.

## 3. Crear el entorno

Abre **Anaconda Prompt**, entra en la carpeta del proyecto y ejecuta:

```bash
conda env create -f environment.yml
conda activate rossmann-forecasting
python -m ipykernel install --user --name rossmann-forecasting --display-name "Python (rossmann-forecasting)"
jupyter lab
```

En el notebook, selecciona el kernel **Python (rossmann-forecasting)**.

## 4. Ejecutar el primer notebook

Abre:

```text
notebooks/01_data_audit.ipynb
```

Ejecuta las celdas de arriba abajo. No corrijas todavía los valores nulos, tipos o anomalías: esta fase solo debe observar y registrar el estado original.

## 5. Primer commit

Después de comprobar que la estructura y el notebook funcionan:

```text
Initial project structure and data audit notebook
```

Incluye código, documentación y archivos de configuración. Confirma en GitHub Desktop que los CSV no aparecen entre los cambios.
