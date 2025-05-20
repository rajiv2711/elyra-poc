# Keyward Elyra PoC

This project demonstrates deploying Apache Airflow 1.10.15 on Kubernetes for integration with Elyra 3.15.0, including DAG management and runtime orchestration.

## Project Purpose
- Deploy Airflow on Kubernetes for Elyra pipeline execution
- Provide configuration and deployment guides
- Enable reproducible data workflows using Elyra and Airflow

## Repository Structure
- `AIRFLOW.md`: Airflow deployment and management guide
- `Airflow DAG Info.md`: DAG troubleshooting and verification
- `airflow-1.10.15-k8s.yaml`: Airflow deployment manifest
- `airflow-3.0.1-values.yaml`: Helm values for Airflow
- `elyra-deployment.yaml`: Elyra deployment manifest
- `minio-deployment.yaml`: MinIO deployment manifest
- `pipelines/`: Example pipelines and DAGs
- `tests/`: Test DAGs and scripts

## Prerequisites
- Kubernetes cluster (v1.18+ recommended)
- `kubectl` configured for your cluster
- Helm (for Helm-based deployments)
- Docker (for building custom images, if needed)

## Deployment Instructions

### Deploy Airflow with kubectl
1. Apply the Airflow deployment YAML:
   ```bash
   kubectl apply -f airflow-1.10.15-k8s.yaml
   ```
2. Monitor deployment status:
   ```bash
   kubectl get pods -n airflow-elyra
   ```
3. Access Airflow UI (port-forward or service exposure as needed).

### Deploy Airflow with Helm
1. Customize `airflow-3.0.1-values.yaml` as needed.
2. Install Airflow:
   ```bash
   helm install airflow -n airflow-elyra -f airflow-3.0.1-values.yaml apache-airflow/airflow
   ```

### Deploy Elyra and MinIO
- Apply `elyra-deployment.yaml` and `minio-deployment.yaml` using `kubectl apply -f ...`

## DAG Management
- DAGs are managed via git-sync or direct volume mounts.
- See `Airflow DAG Info.md` for troubleshooting and verification steps.

## Cleaning Up
To remove the Airflow deployment:
```bash
kubectl delete namespace airflow-elyra
kubectl get namespace airflow-elyra
```

## Troubleshooting
- Check pod logs for errors: `kubectl logs <pod> -n airflow-elyra`
- Ensure all required Kubernetes resources are created
- Verify DAG synchronization and Airflow webserver status

## Further Documentation
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [Elyra Docs](https://elyra.readthedocs.io/)
- See `AIRFLOW.md` and `Airflow DAG Info.md` in this repo for detailed guides