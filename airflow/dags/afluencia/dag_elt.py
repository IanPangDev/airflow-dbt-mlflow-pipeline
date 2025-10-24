from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd
from subprocess import run
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

dias_festivos = [
    [1, 1],    # Año Nuevo
    [2, 2],    # Día de la Candelaria
    [2, 3],    # Día de la Constitución (trasladado)
    [3, 17],   # Natalicio de Benito Juárez (trasladado)
    [4, 13],   # Domingo de Ramos
    [4, 14],   # Lunes Santo
    [4, 17],   # Jueves Santo
    [4, 18],   # Viernes Santo
    [4, 19],   # Sábado de Gloria
    [4, 20],   # Domingo de Resurrección
    [5, 1],    # Día del Trabajo
    [5, 5],    # Batalla de Puebla
    [9, 16],   # Día de la Independencia
    [11, 1],   # Día de Todos los Santos
    [11, 2],   # Día de Muertos
    [11, 17],  # Revolución Mexicana (trasladado)
    [12, 12],  # Día de la Virgen de Guadalupe
    [12, 24],  # Nochebuena
    [12, 25]   # Navidad
]

@dag(
    dag_id='afluencia_elt'
)
def afluencia_elt():
    
    urls = {
        'tren_ligero':'https://datos.cdmx.gob.mx/dataset/ee806dd2-c919-46f2-858f-6a55a05b8ee6/resource/c6f15e48-791d-4ed6-adc3-8d93ed80a055/download/afluencia_desglosada_tl_08_2025.csv',
        'cablebus':'https://datos.cdmx.gob.mx/dataset/ee806dd2-c919-46f2-858f-6a55a05b8ee6/resource/176c0d20-0111-43bc-903c-d7e807ff37c0/download/afluencia_desglosada_cb_08_2025.csv',
        'trolebus':'https://datos.cdmx.gob.mx/dataset/ee806dd2-c919-46f2-858f-6a55a05b8ee6/resource/48fdccd2-f910-4328-a018-df25b6a05b0b/download/afluencia_desglosada_trolebus_08_2025.csv'
    }
    
    @task
    def create_tables_raw():
        # Conexión a PostgreSQL
        hook = PostgresHook(postgres_conn_id='postgres')
        conn = hook.get_conn()
        cursor = conn.cursor()

        # Truncar la tabla raw
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.raw_cablebus (
            fecha text NULL,
            tipo_pago text NULL,
            afluencia text NULL,
            anio text NULL,
            mes text NULL,
            linea text NULL
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.raw_tren_ligero (
            fecha text NULL,
            tipo_pago text NULL,
            afluencia text NULL,
            anio text NULL,
            mes text NULL
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.raw_trolebus (
            fecha text NULL,
            tipo_pago text NULL,
            afluencia text NULL,
            anio text NULL,
            mes text NULL,
            linea text NULL
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.cat_dias_festivos (
            dia int NULL,
            mes int NULL
        );
        """)
        
        cursor.execute("TRUNCATE TABLE public.cat_dias_festivos")
        
        cursor.executemany(
            f"INSERT INTO public.cat_dias_festivos (mes, dia) VALUES (%s, %s)",
            dias_festivos
        )
        
        conn.commit()
        cursor.close()
        conn.close()
    
    @task
    def load_to_raw(url: str, table: str):
        # Leer CSV como string para evitar errores de tipo
        df = pd.read_csv(url, dtype=str, encoding='utf-8')

        # Reemplazar NaN por None (PostgreSQL lo interpreta como NULL)
        df = df.where(pd.notnull(df), None)

        # Conexión a PostgreSQL
        hook = PostgresHook(postgres_conn_id='postgres')
        conn = hook.get_conn()
        cursor = conn.cursor()

        # Truncar la tabla raw
        cursor.execute(f"TRUNCATE TABLE raw_{table}")
        conn.commit()

        # Preparar INSERT
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO raw_{table} ({columns}) VALUES ({placeholders})"

        # Insertar los datos
        cursor.executemany(insert_query, df.values.tolist())
        conn.commit()
        cursor.close()
        conn.close()
    
    @task
    def transform_to_stg():
        print(run(["dbt", "run", "--select", "stg_tren_ligero", "stg_cablebus", "stg_trolebus",
            "--profiles-dir", "/opt/airflow/dbt_project",
            "--project-dir", "/opt/airflow/dbt_project"], capture_output=True))
    
    @task.branch
    def evalua_stg() -> str:
        if run(["dbt", "run", "--select", "stg_tren_ligero", "stg_cablebus", "stg_trolebus",
            "--profiles-dir", "/opt/airflow/dbt_project",
            "--project-dir", "/opt/airflow/dbt_project"], capture_output=True).returncode != 0:
            return 'end'
        return 'vista_analytics'
    
    @task
    def vista_analytics():
        print(run([
            "dbt", "run", "--select", "vw_afluencia_transportes",
            "--profiles-dir", "/opt/airflow/dbt_project",
            "--project-dir", "/opt/airflow/dbt_project"], capture_output=True, text=True))
    
    @task
    def end():
        print("El proceso terminó sin ejecutar vistas.")
        
    
    trigger = TriggerDagRunOperator(
        task_id="trigger_dag_2",
        trigger_dag_id="afluencia_ml_train"
    )
    
    extract_load = [
        load_to_raw(urls['tren_ligero'],'tren_ligero'),
        load_to_raw(urls['cablebus'], 'cablebus'),
        load_to_raw(urls['trolebus'], 'trolebus')
    ]
    
    result_stg = evalua_stg()
    
    create_tables_raw() >> extract_load >> transform_to_stg() >> result_stg
    result_stg >> [trigger << vista_analytics(), end()]
    
afluencia_elt()