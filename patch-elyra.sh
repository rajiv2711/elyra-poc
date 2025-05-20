#!/bin/bash
set -e

# Downgrade problematic packages first
pip install protobuf==3.20.3 --force-reinstall

# Set environment variable for protobuf implementation
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Install Airflow dependencies with versions for Airflow 3.0 compatibility
pip install apache-airflow==3.0.1 \
    apache-airflow-providers-cncf-kubernetes>=6.0.0 \
    pendulum>=2.0.0 \
    --no-deps

# Create Jupyter config directory
mkdir -p /home/jovyan/.jupyter

# Create configuration file for Airflow processor
cp /elyra-config/jupyter_config.py /home/jovyan/.jupyter/jupyter_config.py

# Fix permissions for the config file
chmod 644 /home/jovyan/.jupyter/jupyter_config.py
chown jovyan:users /home/jovyan/.jupyter/jupyter_config.py

# Create directories for metadata
mkdir -p /home/jovyan/.local/share/jupyter/metadata/runtimes/
mkdir -p /home/jovyan/.local/share/jupyter/metadata/component-catalogs/
mkdir -p /home/jovyan/.local/share/jupyter/metadata/templates/airflow3/

# Create Airflow 3.0 compatible template file
cat > /home/jovyan/.local/share/jupyter/metadata/templates/airflow3/airflow3_template.jinja2 << 'EOF'
import pendulum
from airflow import DAG
{% for import_statement in imports %}
{{ import_statement }}
{% endfor %}

args = {
    "project_id": "{{ pipeline_name }}",
}

dag = DAG(
    "{{ pipeline_name }}",
    default_args=args,
    schedule="{{ schedule }}",
    start_date=pendulum.datetime(2025, 5, 19, tz="UTC"),
    description="""
Created with Elyra {{ elyra_version }} pipeline editor using `{{ pipeline_path }}`.
    """,
    is_paused_upon_creation=False,
)

{% for node in nodes %}

# Operator source: {{ node.filename }}

{{ node.id }} = {{ node.component_source }}(
    name="{{ node.name }}",
    namespace="airflow-new",
    image="{{ node.image }}",
{% if node.env_vars %}
    env_vars={{ node.env_vars }},
{% endif %}
{% if node.include_workflow_name %}
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow-new",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "{{ pipeline_name }}-{{ '{{' }} ts_nodash {{ '}}' }}",
    },
{% endif %}
{% if 'KubernetesPodOperator' in node.component_source %}
    cmds=["sh", "-c"],
    arguments=[
        "{{ node.command_line }}"
    ],
    task_id="{{ node.task_id }}",
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={},
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file=None,
{% else %}
    task_id="{{ node.task_id }}",
{% endif %}
    dag=dag,
)

{% for parent in node.parent_nodes %}
{{ node.id }} << {{ parent.id }}
{% endfor %}
{% endfor %}
EOF

# Create the Airflow runtime configuration with fixed properties
cat > /home/jovyan/.local/share/jupyter/metadata/runtimes/airflow-runtime.json << 'EOF'
{
  "display_name": "Apache Airflow 3.0",
  "metadata": {
    "runtime_type": "APACHE_AIRFLOW",
    "airflow_version": "3.0.1",
    "airflow_url": "http://airflow-webserver.airflow.svc.cluster.local:8080",
    "api_endpoint": "http://airflow-webserver.airflow.svc.cluster.local:8080/api/v1",
    "github_api_endpoint": "https://api.github.com",
    "github_repo": "victorfonseca/elyra-poc",
    "github_branch": "main",
    "github_repo_token": "YOUR_TOKEN",
    "cos_endpoint": "http://minio.minio-system.svc.cluster.local:9000",
    "cos_bucket": "elyra-airflow",
    "cos_username": "minio",
    "cos_password": "minio123",
    "template_directory": "/home/jovyan/.local/share/jupyter/metadata/templates/airflow3/",
    "template_file": "airflow3_template.jinja2",
    "namespace": "airflow-new"
  },
  "schema_name": "airflow"
}
EOF

# Create the component catalog
cat > /home/jovyan/.local/share/jupyter/metadata/component-catalogs/airflow-k8s-components.json << EOF
{
  "display_name": "Kubernetes Airflow 3.0 Components",
  "metadata": {
    "runtime_type": "APACHE_AIRFLOW",
    "categories": ["Kubernetes"],
    "paths": ["/tmp/airflow_components.json"],
    "base_path": ""
  },
  "schema_name": "local-file-catalog"
}
EOF

# Copy components file
cp /elyra-config/airflow_component_catalog.json /tmp/airflow_components.json

# Fix permissions
chown -R jovyan:users /home/jovyan/.local/share/jupyter/metadata/
chown -R jovyan:users /home/jovyan/.jupyter/

echo "Elyra configuration completed successfully"