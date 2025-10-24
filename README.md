
---

# 🚇 Proyecto de Pronóstico de Afluencia en Transporte Público

Este proyecto implementa un pipeline de datos para analizar y predecir la afluencia en tres sistemas de transporte público de la Ciudad de México: **Cablebús**, **Trolebús** y **Tren Ligero**.

El flujo completo incluye la orquestación de cargas, modelado de datos y entrenamiento de modelos de pronóstico, utilizando herramientas modernas del stack de datos.

---

## ⚙️ Arquitectura del Proyecto

**Tecnologías principales:**

* **Apache Airflow** → Orquestación de tareas ETL.
* **PostgreSQL** → Almacenamiento de datos brutos y transformados.
* **dbt (Data Build Tool)** → Creación de modelos *staging* y vistas analíticas.
* **scikit-learn (Random Forest)** → Modelo de pronóstico de afluencia.
* **MLflow** → Seguimiento y versionado de experimentos de *machine learning*.

---

## 🧩 Flujo de Trabajo

1. **Ingesta de datos**
   Airflow extrae datos de afluencia de las tres fuentes de transporte y los carga en PostgreSQL.

2. **Transformación de datos**
   dbt procesa las tablas *raw* para generar modelos *staging* y vistas limpias listas para análisis.

3. **Modelado predictivo**
   Se entrena un modelo de *Random Forest* para estimar la afluencia futura en cada servicio.

4. **Monitoreo de experimentos**
   MLflow registra métricas, versiones de modelos y parámetros de entrenamiento para facilitar el seguimiento.

---

## 📈 Objetivo

Desarrollar una solución reproducible y automatizada para:

* Integrar datos de diferentes sistemas de transporte.
* Generar vistas analíticas consistentes.
* Pronosticar la afluencia futura de pasajeros.
* Hacer seguimiento del rendimiento de modelos predictivos.

---

## 🧠 Estructura del Repositorio

```
├── airflow/             # DAGs de Airflow y modelos de DBT
├── dashboard/           # Dashboards con powerbi  
├── postgres-analytics/  # Warehouse
├── jupyters_modelos/    # Exploración y entrenamiento del modelo (pruebas)  
├── mlflow/              # Configuración de tracking MlFlow
├── init.bat             # Iniciador de todos los contenedores
└── README.md
```

---

## 🚀 Ejecución

1. init.bat

2. Establecer en airflow conexion con postgres

3. Ejecutar dag ELT

---

## 📊 Resultados Esperados

* Tablas analíticas con la afluencia diaria por sistema de transporte.
* Métricas del modelo de pronóstico (MAE, RMSE, etc.).
* Dashboard de seguimiento en MLflow con el historial de experimentos.

---