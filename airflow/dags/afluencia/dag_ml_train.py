from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from subprocess import run
import pandas as pd
from os import getenv
from dotenv import load_dotenv

@dag(
    dag_id='afluencia_ml_train'
)
def afluencia_ml_train():
    
    load_dotenv()
    
    @task
    def create_view_train():
        print(run(["dbt", "run", "--select", "vw_afluencia_transportes_forecasting",
            "--profiles-dir", "/opt/airflow/dbt_project",
            "--project-dir", "/opt/airflow/dbt_project"], capture_output=True))
    
    @task
    def load_data() -> pd.DataFrame:
        hook = PostgresHook(postgres_conn_id='postgres')
        conn = hook.get_conn()
        return pd.read_sql(
            "SELECT * FROM vw_afluencia_transportes_forecasting",
            con=conn
        )
    
    @task.virtualenv(
        requirements=[
            'mlflow',
            'pandas',
            'numpy',
            'boto3'
            ],
        system_site_packages=False,
        env_vars={
            'MLFLOW_TRACKING_URI': 'http://mlflow:8080',
            'MLFLOW_S3_ENDPOINT_URL': 'http://minio:9000',
            'AWS_ACCESS_KEY_ID': getenv('AWS_ACCESS_KEY_ID'),
            'AWS_SECRET_ACCESS_KEY': getenv('AWS_SECRET_ACCESS_KEY')
        }
    )
    def train_model(df: pd.DataFrame):
        import sys, os
        dags_path = os.path.join(os.environ.get('AIRFLOW_HOME', '/opt/airflow'), 'dags')
        sys.path.append(dags_path)
        from afluencia.modelo_afluencia import train_and_log
        
        train_and_log(df)
    
    df = load_data()
    create_view_train() >> df >> train_model(df)

afluencia_ml_train()