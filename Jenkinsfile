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
                        script: "git rev-parse --short=8 HEAD",
                        returnStdout: true
                    ).trim()
                }
                echo "Building commit: ${GIT_COMMIT_SHORT}"
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    python3 -m venv ${PYTHON_VENV}
                    ${PYTHON_VENV}/bin/pip install -r app/requirements.txt -r tests/requirements-test.txt
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
                    export DOCKER_BUILDKIT=1
                    docker pull ${DOCKER_IMAGE}:latest || true
                    docker build --cache-from ${DOCKER_IMAGE}:latest -t ${DOCKER_IMAGE}:latest -t ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT} -f docker/Dockerfile .
                    docker inspect ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Docker Push') {
            steps {
                withVault([
                    configuration: [
                        vaultUrl: 'http://localhost:8200',
                        vaultCredentialId: 'vault-approle'
                    ],
                    vaultSecrets: [[
                        path: 'secret/dockerhub',
                        secretValues: [
                            [vaultKey: 'username', envVar: 'DOCKER_USER'],
                            [vaultKey: 'password', envVar: 'DOCKER_PASS']
                        ]
                    ]]
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_IMAGE}:latest
                        docker push ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT}
                    '''
                }
            }
            post {
                always {
                    sh 'docker logout || true'
                }
            }
        }

        stage('Ansible Provision') {
            steps {
                sh '''
                    if command -v ansible-playbook >/dev/null 2>&1; then
                        ansible-playbook ansible/site.yml -i ansible/inventory/hosts.ini --diff --extra-vars "docker_image=${DOCKER_IMAGE}:${GIT_COMMIT_SHORT}"
                    else
                        python3 -m ansible playbook ansible/site.yml -i ansible/inventory/hosts.ini --diff --extra-vars "docker_image=${DOCKER_IMAGE}:${GIT_COMMIT_SHORT}"
                    fi
                '''
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                withVault([
                    configuration: [
                        vaultUrl: 'http://localhost:8200',
                        vaultCredentialId: 'vault-approle'
                    ],
                    vaultSecrets: [[
                        path: 'secret/kubeconfig',
                        secretValues: [
                            [vaultKey: 'config', envVar: 'KUBE_CONFIG']
                        ]
                    ]]
                ]) {
                    sh '''
                        echo "$KUBE_CONFIG" | base64 -d > /tmp/kubeconfig_${BUILD_NUMBER}
                        export KUBECONFIG=/tmp/kubeconfig_${BUILD_NUMBER}
                        kubectl set image deployment/fraudguard-app fraudguard=${DOCKER_IMAGE}:${GIT_COMMIT_SHORT} -n fraudguard
                        if ! kubectl rollout status deployment/fraudguard-app -n fraudguard --timeout=120s; then
                            kubectl rollout undo deployment/fraudguard-app -n fraudguard
                            exit 1
                        fi
                    '''
                }
            }
            post {
                always {
                    sh 'rm -f /tmp/kubeconfig_${BUILD_NUMBER}'
                }
            }
        }

        stage('Newman Smoke Test') {
            steps {
                sh '''
                    MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "127.0.0.1")
                    for i in $(seq 1 12); do
                        if curl -sf http://${MINIKUBE_IP}:30080/health >/dev/null; then
                            break
                        fi
                        sleep 10
                    done
                '''
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "127.0.0.1")
                        newman run tests/postman/FraudGuard.postman_collection.json \
                          --env-var "baseUrl=http://${MINIKUBE_IP}:30080" \
                          --reporters cli,junit \
                          --reporter-junit-export newman-results.xml
                    '''
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'newman-results.xml'
                }
            }
        }
    }

    post {
        always {
            sh 'rm -f /tmp/kubeconfig_${BUILD_NUMBER} || true'
            cleanWs()
        }
        success {
            script {
                def minikubeIp = sh(script: 'minikube ip 2>/dev/null || echo "127.0.0.1"', returnStdout: true).trim()
                echo "SUCCESS: image=${DOCKER_IMAGE}:${GIT_COMMIT_SHORT}, minikube_ip=${minikubeIp}, kibana_url=http://${minikubeIp}:30001"
            }
        }
        failure {
            echo "Pipeline FAILED"
        }
        unstable {
            echo "Smoke tests need attention"
        }
    }
}
