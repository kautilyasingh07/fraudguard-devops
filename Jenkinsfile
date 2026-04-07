pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root:root' // Run as root to install packages globally in the container
        }
    }

    environment {
        PYTHONUNBUFFERED = '1'
        PYTHONDONTWRITEBYTECODE = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    apt-get update && apt-get install -y gcc
                    python3 -m pip install --upgrade pip
                    pip3 install -r app/requirements.txt
                    pip3 install -r tests/requirements-test.txt
                '''
            }
        }

        stage('Unit Tests & Coverage') {
            steps {
                sh '''
                    # FR-119: Run tests with 70% coverage requirement
                    python3 -m pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml --cov-report=term-missing --cov-fail-under=70
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
    }

    post {
        success {
            echo "CI Pipeline completed successfully. All tests passed and code coverage is above 70%."
        }
        failure {
            echo "CI Pipeline failed. Check the logs for test or coverage failures."
        }
    }
}
