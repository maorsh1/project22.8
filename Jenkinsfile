pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-maorsh6-credentials')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    bat 'docker build -t maorsh6/my-python-app .'
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    bat 'echo "Running tests..."'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    bat 'docker login -u %DOCKERHUB_CREDENTIALS_USR% -p %DOCKERHUB_CREDENTIALS_PSW%'
                    bat 'docker push maorsh6/my-python-app:latest'
                    bat 'kubectl apply -f deployment.yaml'
                    bat 'kubectl apply -f service.yaml'
                }
            }
        }
    }
}
