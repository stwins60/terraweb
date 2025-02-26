pipeline {
    agent any

    environment {
        // Define environment variables
        DOCKER_IMAGE = 'idrisniyi94/terraweb'
        BRANCH_NAME = "${GIT_BRANCH.split('/')[1]}"
        BUILD_NUMBER = "v.0.${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from the repository
                checkout scmGit(branches: [[name: '*/master'], [name: '*/dev']], extensions: [], \
                userRemoteConfigs: [[url: 'https://github.com/stwins60/terraweb.git']])
            }
        }
        stage('Build') {
            steps {
                // Build the project
                script {
                    sh "docker build -t ${DOCKER_IMAGE}:${BRANCH_NAME}-${BUILD_NUMBER} ."
                }
            }
        }
    }
}