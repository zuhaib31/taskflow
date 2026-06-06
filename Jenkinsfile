pipeline {
    agent any

    environment {
        APP_DIR = '/home/ubuntu/taskflow'
    }

    options {
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Sync to Deploy Directory') {
            steps {
                echo 'Updating the deployment directory with latest code...'
                sh '''
                    cd ${APP_DIR}
                    git fetch origin main
                    git reset --hard origin/main
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running automated tests...'
                sh '''
                    docker run --rm \
                      -v ${APP_DIR}:/app \
                      -w /app \
                      python:3.11-slim \
                      bash -c "pip install --quiet -r requirements-test.txt && pytest --tb=short"
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Building the Docker image...'
                sh '''
                    cd ${APP_DIR}
                    docker compose build web
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying the updated stack...'
                sh '''
                    cd ${APP_DIR}
                    docker compose up -d
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo 'Verifying the application is healthy...'
                sh '''
                    for i in $(seq 1 12); do
                        STATUS=$(docker inspect --format='{{.State.Health.Status}}' taskflow-web 2>/dev/null || echo "unknown")
                        echo "Attempt $i: taskflow-web health = $STATUS"
                        if [ "$STATUS" = "healthy" ]; then
                            echo "Application is healthy."
                            exit 0
                        fi
                        sleep 5
                    done
                    echo "Health check failed - container did not become healthy."
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully. App is deployed and healthy.'
        }
        failure {
            echo 'Pipeline failed. Check the logs above for details.'
        }
        always {
            sh '''
                cd ${APP_DIR}
                docker compose ps
            '''
        }
    }
}
