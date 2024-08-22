from airflow import DAG
from datetime import datetime
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from api_pokemon import extrair_pokemon


default_args = {
    "owner": "Manoel",
    "start_date": datetime(2024, 8, 21),
}
with DAG(
    dag_id="pokemon_extraction",
    default_args = default_args,
    schedule = None,
    max_active_runs = 1,
) as dag:
    start_pipeline = EmptyOperator(
        task_id = "start_pipeline",
    )
    extract_pokemon = PythonOperator(
        task_id = "extract_pokemon",
        python_callable = extrair_pokemon,
    )
    done_pipeline = EmptyOperator(
        task_id = "done_pipeline",
    )
    start_pipeline >> extract_pokemon >> done_pipeline