# MinIO Deployment and UI Access Guide

This guide provides step-by-step instructions to deploy MinIO using Kubernetes and access the MinIO web UI to manage buckets.

## Prerequisites
- Kubernetes cluster access (e.g., Minikube, Kind, or cloud provider)
- `kubectl` installed and configured

## 1. Deploy MinIO

Apply the provided MinIO deployment manifest:

```sh
kubectl apply -f minio-deployment.yaml
```

This manifest creates:
- A `minio-system` namespace
- MinIO credentials as a Kubernetes Secret
- MinIO Deployment
- PersistentVolumeClaim for storage
- Services for API and Console (including NodePort for external access)
- A Job to create and configure the `elyra-airflow` bucket

## 2. Expose MinIO Services

The manifest includes a `minio-nodeport` service that exposes:
- MinIO API on NodePort **30900**
- MinIO Console (UI) on NodePort **30901**

If running on Minikube or a local cluster, you can access the UI via:

```
http://<minikube-ip>:30901/
```

Find your Minikube IP:
```sh
minikube ip
```

If using a different Kubernetes setup, you may need to use `kubectl port-forward`:

```sh
kubectl port-forward -n minio-system svc/minio 9000:9000 9001:9001
```

Then access the UI at:
```
http://localhost:9001/
```

## 3. Login to MinIO Console

- **Username:** `minio`
- **Password:** `minio123`

These credentials are set in the `minio-credentials` secret in the manifest.

## 4. View and Manage Buckets

Once logged in, you can:
- View the `elyra-airflow` bucket (created by the setup Job)
- Create, delete, and manage additional buckets

## 5. Troubleshooting
- Ensure all pods in `minio-system` namespace are running:
  ```sh
  kubectl get pods -n minio-system
  ```
- Check logs for the MinIO pod if you encounter issues:
  ```sh
  kubectl logs -n minio-system deployment/minio
  ```

---

For more details, refer to the `minio-deployment.yaml` in this repository.