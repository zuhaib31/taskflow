pipeline {
    agent any

    environment {
        APP_DIR = '/home/ubuntu/taskflow'
        HEALTH_URL = 'http://localhost:5000/health'
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
                    sleep 10
                    for i in $(seq 1 6); do
                        if curl -fs ${HEALTH_URL} > /dev/null; then
                            echo "Application is healthy."
                            exit 0
                        fi
                        echo "Waiting for app to respond... attempt $i"
                        sleep 5
                    done
                    echo "Health check failed."
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
