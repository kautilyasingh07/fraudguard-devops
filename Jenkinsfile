pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "kautilyasingh/fraudguard"
        PYTHON_VENV  = "${WORKSPACE}/venv"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse HEAD | cut -c1-8',
                        returnStdout: true
                    ).trim()
                }
                echo "Checked out commit: ${env.GIT_COMMIT_SHORT}"
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    python3 -m venv ${PYTHON_VENV}
                    ${PYTHON_VENV}/bin/pip install --upgrade pip
                    ${PYTHON_VENV}/bin/pip install -r app/requirements.txt
                    ${PYTHON_VENV}/bin/pip install -r tests/requirements-test.txt
                    ${PYTHON_VENV}/bin/pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=term-missing --cov-fail-under=70
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -f docker/Dockerfile -t ${DOCKER_IMAGE}:latest -t ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT} .
                    docker inspect ${DOCKER_IMAGE}:latest > /dev/null
                    docker inspect ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT} > /dev/null
                '''
            }
        }

        stage('Docker Push') {
            steps {
                // Implemented in Phase 3 — Vault + Docker Push
                sh 'echo "Stage 4 placeholder - skipping"'
            }
        }

        stage('Ansible Provision') {
            steps {
                // Implemented in Phase 4 — Ansible
                sh 'echo "Stage 5 placeholder - skipping"'
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                // Implemented in Phase 5 — Kubernetes
                sh 'echo "Stage 6 placeholder - skipping"'
            }
        }

        stage('Newman Smoke Test') {
            steps {
                // Implemented in Phase 5 — Newman
                sh 'echo "Stage 7 placeholder - skipping"'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        failure {
            echo "Pipeline FAILED. Check logs above."
        }
        success {
            echo "Build ${GIT_COMMIT_SHORT} completed successfully."
        }
    }
}
