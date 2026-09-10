pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "devops-jenkins-demo-app"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/lucasbonanni/devops-python-demo.git'
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
