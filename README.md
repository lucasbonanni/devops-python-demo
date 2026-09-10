# FastAPI Jenkins CI/CD & Observability Demo

This repository contains a full hands-on demonstration of a modern CI/CD pipeline using **Jenkins (JCasC)**, **Python (uv + FastAPI)**, **Docker**, and **Render**, along with local and cloud observability using **OpenTelemetry** and **Grafana**.

---

## Project Architecture


```


                             ┌────────────────────────┐
                             │     GitHub Repo        │
                             └───────────┬────────────┘
                                         │
                                         ▼


┌───────────────────────────────────────────────────────────────────────────┐
│ Docker Environment (Local)                                                │
│                                                                           │
│   ┌──────────────────┐    Executes    ┌───────────────────────────────┐   │
│   │  Jenkins Server  │ ──────────────► │  FastAPI App (Docker Build)   │   │
│   │    (JCasC)       │                └───────────────┬───────────────┘   │
│   └────────┬─────────┘                                │                   │
└────────────┼──────────────────────────────────────────┼───────────────────┘
│ Triggers Deploy Hook                     │ Sends Metrics/Traces
▼                                          ▼
┌──────────────────┐                        ┌─────────────────┐
│ Render Platform  │                        │ OTEL Collector  │
└──────────────────┘                        └────────┬────────┘
│
▼
┌─────────────────┐
│ Grafana (Cloud) │
└─────────────────┘

```

---

## Project Structure

```text
devops-jenkins-demo/
├── app/
│   └── main.py              # FastAPI application entry point
├── jenkins/
│   ├── Dockerfile           # Custom Jenkins image with Docker CLI & preinstalled plugins
│   ├── jenkins.yaml         # Jenkins Configuration as Code (JCasC) definition
│   └── plugins.txt          # Required Jenkins plugins list (JCasC, Job-DSL, Docker, Git)
├── tests/
│   └── test_main.py         # Pytest suite
├── .env.example             # Template for environment variables
├── Dockerfile               # Multi-stage Dockerfile for FastAPI using `uv`
├── docker-compose.yml       # Docker Compose setup for Jenkins
├── Jenkinsfile              # Declarative pipeline definition
├── pyproject.toml           # Project dependencies managed by `uv`
└── uv.lock                  # Lockfile for reproducible python environments

```

---

## Prerequisites

* [Docker Desktop](https://www.docker.com/) installed and running.
* [uv](https://www.google.com/search?q=https://astral.sh/uv/) for local Python dependency management.
* A [Render](https://render.com/) account with a Web Service configured.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/devops-jenkins-demo.git](https://github.com/your-username/devops-jenkins-demo.git)
cd devops-jenkins-demo

```

### 2. Configure Environment Variables

Copy the example environment file and add your Render Deploy Hook URL:

```bash
cp .env.example .env

```

Edit `.env`:

```env
RENDER_DEPLOY_HOOK=[https://api.render.com/deploy/srv-your-actual-token](https://api.render.com/deploy/srv-your-actual-token)

```

### 3. Run the Local Development Environment

Install dependencies and run unit tests locally with `uv`:

```bash
uv sync
uv run pytest

```

---

## Running Jenkins CI/CD

Start Jenkins in a containerized environment using Docker Compose:

```bash
docker compose up --build -d

```

> [!Warning]
> In order to obtain the initial Jenkins admin password, run the following command:
> docker exec -it jenkins_server cat /var/jenkins_home/secrets/initialAdminPassword

### Accessing Jenkins

1. Open your browser and navigate to `http://localhost:8080`.
2. Notice that **no initial setup wizard is required**.
3. The job `fastapi-ci-cd-pipeline` is automatically created via **Job-DSL**.
4. The credential `RENDER_DEPLOY_HOOK` is injected automatically via **JCasC**.

### Triggering a Build

* Open the `fastapi-ci-cd-pipeline` job and click **Build Now**.
* The pipeline will execute the following stages:
1. **Checkout:** Pulls the code from GitHub.
2. **Install & Test:** Installs `uv` and executes tests using `pytest`.
3. **Build Docker Image:** Builds the application container image using the host Docker daemon.
4. **Deploy to Render:** Triggers the Render Deploy Hook via `curl`.



---

## Troubleshooting

If Jenkins fails to boot, verify that the `job-dsl` plugin is listed in `jenkins/plugins.txt` and rebuild with clean volumes:

```bash
docker compose down -v
docker compose up --build

```
