# Kubernetes Deployment (Scaleway)

This folder contains Kubernetes manifests derived from the Compose setup. You
must push container images to a registry accessible by your Scaleway cluster.

## Prerequisites

- A Scaleway K8s cluster
- `kubectl` configured for the cluster
- Container images published for:
  - backend
  - delphes frontend
  - streamlit test client (optional)

## Quick Start

1) Update image names in the deployment manifests:

- `k8s/backend-deployment.yaml`
- `k8s/frontend-deployment.yaml`
- `k8s/streamlit-client-deployment.yaml` (optional)

2) Update secrets for Scaleway in `k8s/secrets.yaml`:

```bash
kubectl -n trusted-services apply -f k8s/namespace.yaml
kubectl -n trusted-services apply -f k8s/secrets.yaml
```

3) Apply the rest:

```bash
kubectl apply -k k8s/
```

## Notes

- The frontend service is `LoadBalancer` on port `3006` (maps to container 3000).
- The backend service is `ClusterIP` on port `8002`.
- Update `BACKEND_INTERNAL_URL` in `k8s/configmap.yaml` to the private API
  endpoint your frontend can reach.
- The runtime volume is backed by a PVC. Adjust the storage class if needed
  (see `k8s/runtime-pvc.yaml`).
- Streamlit test client is optional. Use it only for dev/integration scenarios.
