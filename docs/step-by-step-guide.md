# Step-by-Step Guide: Setting Up the Repository & Structure

### Prerequisites

* **Python 3.11+** installed locally.
* **`uv`** installed (`curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh`).
* **Docker** and **Docker Compose** installed and running.
* A **GitHub** account and a public or private repository named `devops-jenkins-demo`.

---

### Step 1: Initialize the Local Directory & Python Project

Create the project folder and use `uv` to initialize the workspace and install the application dependencies:

```bash
# Create and enter the project folder
mkdir devops-jenkins-demo
cd devops-jenkins-demo

# Initialize project with uv and add dependencies
uv init
uv add fastapi uvicorn pytest httpx

```

---

### Step 2: Create the Application & Tests

Create the directory structure for the app:

```bash
mkdir app tests

```

#### `app/main.py`

```python
from fastapi import FastAPI

app = FastAPI(title="Jenkins Demo API")

@app.get("/")
def read_root():
    return {"message": "CI/CD Pipeline Running Successfully!"}

@app.get("/health")
def health():
    return {"status": "ok"}

```

#### `tests/test_main.py`

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "CI/CD Pipeline Running Successfully!"}

```

---

### Step 3: Create the App Dockerfile & Jenkinsfile

#### `Dockerfile`

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

```

#### `Jenkinsfile`

```groovy
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "devops-jenkins-demo-app"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/your-username/devops-jenkins-demo.git'
            }
        }

        stage('Install & Test') {
            steps {
                sh '''
                    curl -LsSf https://astral.sh/uv/install.sh | sh
                    export PATH="$HOME/.local/bin:$PATH"
                    uv sync
                    uv run pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:latest .'
            }
        }

        stage('Deploy to Render') {
            steps {
                withCredentials([string(credentialsId: 'RENDER_DEPLOY_HOOK', variable: 'HOOK_URL')]) {
                    sh 'curl -X POST "$HOOK_URL"'
                }
            }
        }
    }
}

```

>[!Note]
> Replace `your-username` in the `Jenkinsfile` with your actual GitHub username to ensure the pipeline can access your repository.
> This `Jenkinsfile` defines a declarative pipeline that checks out the code, installs dependencies, runs tests, builds a Docker image, and triggers a deployment to Render using a deploy hook.

---

### Step 4: Configure Jenkins as Code (JCasC)

Create a dedicated `jenkins/` directory to manage Jenkins configuration declaratively.

```bash
mkdir jenkins

```

#### `jenkins/plugins.txt`

```text
git
workflow-aggregator
docker-workflow
configuration-as-code
git-client
job-dsl

```

>[!Note]
> The `plugins.txt` file lists the required Jenkins plugins for the CI/CD pipeline, including Git integration, Docker support, and Job DSL for pipeline creation.

#### `jenkins/jenkins.yaml`

```yaml
jenkins:
  systemMessage: "Jenkins server preconfigured for the class demonstration."
  numExecutors: 2
  scmCheckoutRetryCount: 2
  mode: NORMAL

unclassified:
  location:
    url: "http://localhost:8080/"

credentials:
  system:
    domainCredentials:
      - credentials:
          - string:
              scope: GLOBAL
              id: "RENDER_DEPLOY_HOOK"
              secret: "${RENDER_DEPLOY_HOOK}"
              description: "Render Deploy Hook Secret"

jobs:
  - script: |
      pipelineJob('fastapi-ci-cd-pipeline') {
        description('Main CI/CD Pipeline for FastAPI application')
        definition {
          cpsScm {
            scm {
              git {
                remote {
                  url('https://github.com/your-username/devops-jenkins-demo.git')
                }
                branches('main')
              }
            }
            scriptPath('Jenkinsfile')
          }
        }
      }

```

> [!Note]
> The `jenkins.yaml` file contains the declarative configuration for Jenkins, including system settings, credentials, and job definitions.

#### `jenkins/Dockerfile`

```dockerfile
FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg lsb-release && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

USER jenkins

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

```

---

### Step 5: Configure Docker Compose & Environment Variables

#### `docker-compose.yml`

```yaml
services:
  jenkins:
    build:
      context: ./jenkins
      dockerfile: Dockerfile
    container_name: jenkins_server
    privileged: true
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    environment:
      - CASC_JENKINS_CONFIG=/var/jenkins_home/jenkins.yaml
      - RENDER_DEPLOY_HOOK=${RENDER_DEPLOY_HOOK:-https://api.render.com/deploy/sample-hook}
    volumes:
      - ./jenkins/jenkins.yaml:/var/jenkins_home/jenkins.yaml
      - jenkins_data:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock

volumes:
  jenkins_data:

```

#### `.env.example`

```env
RENDER_DEPLOY_HOOK=https://api.render.com/deploy/srv-your-token-here

```

#### `.gitignore`

```text
.venv/
__pycache__/
.pytest_cache/
.env

```

---

### Step 6: Commit and Push to GitHub

```bash
git init
git add .
git commit -m "feat: initial project setup with FastAPI, Jenkins JCasC, and Docker"
git branch -M main
git remote add origin https://github.com/your-username/devops-jenkins-demo.git
git push -u origin main

```
