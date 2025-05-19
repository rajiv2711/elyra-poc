FROM jupyter/scipy-notebook:latest

USER root
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
USER jovyan
