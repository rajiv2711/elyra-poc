# Airflow 1.10.15 Deployment Guide - kubectl Commands

This guide provides the essential kubectl commands to deploy, verify, and interact with Airflow 1.10.15 in Kubernetes for integration with Elyra 3.15.0.

## Deployment Commands

### 1. Deploy Airflow 1.10.15

```bash
# Apply the Airflow deployment YAML
kubectl apply -f airflow-1.10.15-k8s.yaml
```

### 2. Verify Deployment Status

```bash
# Check the status of all resources
kubectl get all -n airflow-elyra

# Monitor pod creation in watch mode
kubectl get pods -n airflow-elyra -w

# Check if the initialization job completed successfully
kubectl get jobs -n airflow-elyra
```

Wait until all pods are in the `Running` state, and the initialization job shows `Completed`.

### 3. Check Logs (If Needed)

```bash
# Check logs of the initialization job
kubectl logs -n airflow-elyra job/airflow-init

# Check webserver logs
kubectl logs -n airflow-elyra $(kubectl get pods -n airflow-elyra -l app=airflow-webserver -o name)

# Check scheduler logs
kubectl logs -n airflow-elyra $(kubectl get pods -n airflow-elyra -l app=airflow-scheduler -o name)

# Check PostgreSQL logs
kubectl logs -n airflow-elyra $(kubectl get pods -n airflow-elyra -l app=postgresql -o name)
```

### 4. Access the Airflow UI

```bash
# Port-forward the Airflow webserver to your local machine
kubectl port-forward -n airflow-elyra svc/airflow-webserver 8080:8080
```

Then open your browser and navigate to: http://localhost:8080

## Integrating with Elyra

In Elyra, configure a new Runtime with these settings:

- **Display Name**: Airflow 1.10.15
- **Runtime Type**: Apache Airflow
- **Airflow URL**: http://airflow-webserver.airflow-elyra.svc.cluster.local:8080
- **API Endpoint**: http://airflow-webserver.airflow-elyra.svc.cluster.local:8080/api/v1
- **GitHub API Endpoint**: https://api.github.com
- **GitHub Repository**: your-github-username/your-repo-name
- **GitHub Branch**: main
- **GitHub Repository Token**: your-personal-access-token
- **Object Storage**: Configure your S3-compatible storage

## Troubleshooting Common Issues

### Database Connection Issues

If you see errors like `password authentication failed for user "airflow"`:

```bash
# Check PostgreSQL connectivity from another pod
kubectl exec -n airflow-elyra deploy/airflow-webserver -- psql -h postgresql -U postgres -d airflow -c "SELECT 1;"
```

### DAG Import Errors

If DAGs fail to load with errors like `ModuleNotFoundError: No module named 'airflow.providers'`:

The issue is that Airflow 1.10.x uses different import paths than Airflow 2.x. You need to modify DAGs to use:
- `airflow.contrib.operators` instead of `airflow.providers` 
- `airflow.contrib.kubernetes` instead of `airflow.providers.cncf.kubernetes`

### Restart Components

If you need to restart components:

```bash
# Restart the webserver
kubectl rollout restart -n airflow-elyra deployment/airflow-webserver

# Restart the scheduler
kubectl rollout restart -n airflow-elyra deployment/airflow-scheduler
```

## Cleaning Up

To remove the Airflow deployment:

```bash
# Delete everything in the namespace
kubectl delete namespace airflow-elyra

# Verify the namespace is gone
kubectl get namespace airflow-elyra
```