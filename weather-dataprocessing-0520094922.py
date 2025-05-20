from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "weather-dataprocessing-0520094922",
}

dag = DAG(
    "weather-dataprocessing-0520094922",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `weather-dataprocessing.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: 01-generate-data-simple.py

op_1bfb1881_65a3_496b_9110_2460c2a2ceb8 = KubernetesPodOperator(
    name="01_generate_data_simple",
    namespace="airflow",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'weather-dataprocessing' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'weather-dataprocessing-0520094922' --cos-dependencies-archive '01-generate-data-simple-1bfb1881-65a3-496b-9110-2460c2a2ceb8.tar.gz' --file '01-generate-data-simple.py' "
    ],
    task_id="01_generate_data_simple",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "weather-dataprocessing-{{ ts_nodash }}",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={},
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file="None",
    dag=dag,
)


# Operator source: 02-process-data-simple.py

op_83bd05aa_fa6a_4598_a3fb_f21dcb77e3e0 = KubernetesPodOperator(
    name="02_process_data_simple",
    namespace="airflow",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'weather-dataprocessing' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'weather-dataprocessing-0520094922' --cos-dependencies-archive '02-process-data-simple-83bd05aa-fa6a-4598-a3fb-f21dcb77e3e0.tar.gz' --file '02-process-data-simple.py' "
    ],
    task_id="02_process_data_simple",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "weather-dataprocessing-{{ ts_nodash }}",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={},
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file="None",
    dag=dag,
)

op_83bd05aa_fa6a_4598_a3fb_f21dcb77e3e0 << op_1bfb1881_65a3_496b_9110_2460c2a2ceb8


# Operator source: 03-visualize-data-simple.py

op_d566e5e5_7c69_482b_a582_ff53057ffee5 = KubernetesPodOperator(
    name="03_visualize_data_simple",
    namespace="airflow",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'weather-dataprocessing' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'weather-dataprocessing-0520094922' --cos-dependencies-archive '03-visualize-data-simple-d566e5e5-7c69-482b-a582-ff53057ffee5.tar.gz' --file '03-visualize-data-simple.py' "
    ],
    task_id="03_visualize_data_simple",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "weather-dataprocessing-{{ ts_nodash }}",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={},
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file="None",
    dag=dag,
)

op_d566e5e5_7c69_482b_a582_ff53057ffee5 << op_83bd05aa_fa6a_4598_a3fb_f21dcb77e3e0
