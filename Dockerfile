FROM jupyter/datascience-notebook:latest

USER root

# Install requirements first
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Install JupyterHub with specific version
RUN pip install jupyterhub==5.3.0

# Install Elyra separately
RUN pip install elyra==3.15.0

# Return to jovyan user
USER jovyan
