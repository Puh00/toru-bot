pipeline {
    agent any
    options {
        buildDiscarder logRotator(artifactDaysToKeepStr: '5', artifactNumToKeepStr: '5', daysToKeepStr: '5', numToKeepStr: '5')
    }
    triggers {
        pollSCM 'H/10 * * * *'
    }
    environment {
        DISCORD_TOKEN = credentials('discord-token')
        GIPHY_KEY = credentials('giphy-token')
        MONGODB_URL = 'localhost'
        DOCKER_HUB_URL = credentials('docker-hub-url')
        DOCKER_LOGIN = credentials('docker-login')
    }
    stages {
        stage('Compile test') {
            agent {
                dockerfile { filename 'Dockerfile.build' }
            }
            steps {
                echo 'Compiling in Python!'
                sh 'printf "DISCORD_TOKEN=${DISCORD_TOKEN}\nGIPHY_KEY=${GIPHY_KEY}\nMONGODB_URL=${MONGODB_URL}" >> .env'
                sh 'python -m compileall .'
            }
        }
        stage('Build Docker image') {
            steps {
                echo 'BUILDING!'
                sh 'docker build -t ${DOCKER_HUB_URL} .'
            }
        }
        stage('Publish Docker image') {
            steps {                
                sh 'docker login --username=$DOCKER_LOGIN_USR --password=$DOCKER_LOGIN_PSW'
                sh 'docker push ${DOCKER_HUB_URL}'
            }
        }
        stage('Deploy') {
            steps {
                sh 'printf "DISCORD_TOKEN=${DISCORD_TOKEN}\nGIPHY_KEY=${GIPHY_KEY}\nMONGODB_URL=${MONGODB_URL}" >> .env'
                sh 'docker-compose -f docker-compose-production.yml pull'
                sh 'docker-compose -f docker-compose-production.yml down'
                sh 'docker-compose -f docker-compose-production.yml up -d'
            }
        }
    }
}
