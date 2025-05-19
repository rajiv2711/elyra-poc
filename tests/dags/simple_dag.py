from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 19),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'simple_kubernetes_dag',
    default_args=default_args,
    description='A simple DAG with KubernetesPodOperator',
    schedule_interval=None,
)

task1 = KubernetesPodOperator(
    task_id='print_date',
    name='print-date',
    namespace='airflow',
    image='python:3.9-slim',
    cmds=["bash", "-c"],
    arguments=["date && echo 'Hello from Kubernetes!'"],
    dag=dag,
)
