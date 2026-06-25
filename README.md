# diffchecker

A web-based text diff tool built with Flask. Paste two blocks of text and get a side-by-side HTML diff.

## Application

- **Framework:** Python / Flask
- **Port:** 5000
- **Endpoint:** `GET /` — renders the UI; `POST /compare` — returns HTML diff table

---

## Repository Structure

```
diffchecker/
├── app.py                        # Flask application
├── Dockerfile                    # Container image definition
├── requirements.txt              # Python dependencies
├── templates/
│   └── index.html                # Frontend UI
└── .github/
    └── workflows/
        └── build-push.yml        # CI/CD pipeline
```

---

## CI/CD Pipeline

### Overview

Every push to `main` triggers the following automated flow:

```
push to main
  → Build & push Docker image to GHCR
    → Update image tag in diffchecker_kind/values.yaml
      → ArgoCD detects git change
        → Syncs Kind cluster automatically
```

### Pipeline Steps (`build-push.yml`)

1. **Build & push image** — builds the Docker image and pushes it to `ghcr.io/RD-95/diffchecker` with a `sha-<commit>` tag
2. **Update image tag** — clones the [diffchecker_kind](https://github.com/RD-95/diffchecker_kind) infra repo, updates `charts/diffchecker/values.yaml` with the new SHA tag, and commits/pushes back

### Required Secret

| Secret | Description |
|--------|-------------|
| `DEPLOY_PAT` | GitHub Personal Access Token with `repo` scope — used to push the image tag update to `diffchecker_kind` |

---

## Infrastructure

Managed in a separate repo: [diffchecker_kind](https://github.com/RD-95/diffchecker_kind)

```
diffchecker_kind/
├── charts/
│   └── diffchecker/              # Helm chart
│       ├── Chart.yaml
│       ├── values.yaml           # Image tag updated automatically by CI
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           └── ...
└── argocd/
    └── app.yaml                  # ArgoCD Application manifest
```

### Kubernetes (Kind)

- **Cluster:** Kind (`diffchecker`)
- **Namespace:** `diffchecker`
- **Replicas:** 2
- **Service:** ClusterIP on port 80 → container port 5000

### ArgoCD

- Watches `diffchecker_kind` repo (`main` branch, `charts/diffchecker` path)
- Auto-sync enabled with self-heal and prune
- Access UI: `kubectl port-forward svc/argocd-server 8443:443 -n argocd`

---

## Local Development

```bash
pip install -r requirements.txt
python app.py
# open http://localhost:5000
```

## Docker

```bash
docker build -t diffchecker .
docker run -p 5000:5000 diffchecker
```

## Manual Helm Deploy

```bash
# Start Kind cluster
docker start diffchecker-control-plane
kind export kubeconfig --name diffchecker

# Deploy
helm upgrade --install diffchecker ~/repos/diffchecker_kind/charts/diffchecker/ --namespace diffchecker

# Access
kubectl port-forward svc/diffchecker-service 8080:80 -n diffchecker
# open http://localhost:8080
```