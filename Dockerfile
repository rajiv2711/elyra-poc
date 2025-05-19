FROM jupyter/datascience-notebook:latest

USER root

# Install requirements first
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Install JupyterHub with specific version
RUN pip install jupyterhub==5.3.0

# Install Elyra with Airflow components
RUN pip install elyra==3.15.0
RUN pip install apache-airflow==2.10.5
RUN pip install apache-airflow-providers-cncf-kubernetes>=2.0.0

# Create the custom component catalog for Airflow
RUN mkdir -p /opt/conda/share/jupyter/metadata/runtime-images/
COPY airflow_component_catalog.json /opt/conda/share/jupyter/metadata/runtime-images/

# Add a patch to ensure DAGs are created in tests/dags subdirectory
RUN mkdir -p /opt/conda/lib/python3.*/site-packages/elyra/pipeline/airflow
COPY airflow_dag_patch.py /tmp/
RUN python /tmp/airflow_dag_patch.py

# Return to jovyan user
USER jovyan
