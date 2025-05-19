from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.kubernetes.volume import Volume
from airflow.kubernetes.volume_mount import VolumeMount
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
    'simple_test_dag',
    default_args=default_args,
    description='A simple test DAG with correct imports',
    schedule_interval=None,
)

# Define a volume and volume mount
volume = Volume(
    name='example-volume',
    configs={
        'emptyDir': {}
    }
)

volume_mount = VolumeMount(
    name='example-volume',
    mount_path='/data',
    sub_path=None,
    read_only=False
)

# Task 1: Print date
task1 = KubernetesPodOperator(
    task_id='print_date',
    name='print-date',
    namespace='airflow',
    image='python:3.9-slim',
    cmds=["bash", "-c"],
    arguments=["date > /data/date.txt && echo 'Date saved to /data/date.txt'"],
    volumes=[volume],
    volume_mounts=[volume_mount],
    dag=dag,
)

# Set task dependencies
task1
