pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        timestamps()
    }
    
    environment {
        
    // ** Repository hiện đang có trên DockerHubp
        registry = 'ninhtdmorningstar/loan-prediction-ml' 
    // ** credential ID của Docker Hub đã được thêm vào Jenkinssss
        registryCredential = 'dockerhub-credential'
    
        APP_NAME = 'loan-prediction'
        NAMESPACE = 'default'
    }
    
    stages {
        stage('Environment Check') {
            steps {
                echo 'Checking available tools..'
                sh '''
                    echo "=== System Information ==="
                    uname -a
                    
                    echo "=== Available Commands ==="
                    which git || echo "Git not found"
                    which docker || echo "Docker not found"
                    
                    echo "=== Project Files ==="
                    ls -la
                    
                    echo "=== Requirements file ==="
                    cat requirements.txt || echo "No requirements.txt"
                '''
            }
        }
        
        
        
        stage('Test with Docker') {
            agent {
                docker {
                    image 'python:3.8-slim'
                    args '-v $PWD:/workspace -w /workspace'
                }
            }
            steps {
                echo 'Running tests in Python container..'
                sh '''
                    echo "=== Python Environment ==="
                    python --version
                    pip --version
                    
                    echo "=== Installing Dependencies ==="
                    pip install -r requirements.txt
                    
                    echo "=== Running Tests ==="
                    python -m pytest tests/test-py.py -v || echo "Tests completed"
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image..'
                    try {
                        dockerImage = docker.build registry + ":$BUILD_NUMBER"
                        echo 'Docker image built successfully!!'
                    } catch (Exception e) {
                        echo "Docker build failed: ${e.getMessage()}"
                        echo "This might be due to Docker not being properly installed"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                expression { 
                    return binding.hasVariable('dockerImage')
                }
            }
            steps {
                script {
                    echo 'Pushing to Docker registry..'
                    try {
                        docker.withRegistry('', registryCredential) {
                            dockerImage.push()
                            dockerImage.push('latest')
                        }
                        echo 'Image pushed successfully'
                    } catch (Exception e) {
                        echo "Docker push failed: ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        stage('Deploy to GKE') {
            steps {
                script {
                    // Tạo thư mục cục bộ cho kubectl
                    sh 'mkdir -p $HOME/k8s-tools'
            
                    // Tạo file deployment.yaml
                    writeFile file: 'deployment.yaml', text: """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP_NAME}-deployment
  namespace: ${NAMESPACE}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ${APP_NAME}
  template:
    metadata:
      labels:
        app: ${APP_NAME}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "5000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: ${APP_NAME}-container
        image: ${registry}:latest
        ports:
        - containerPort: 5000

"""
            
            // Tạo file service.yaml cho deployment
            writeFile file: 'service.yaml', text: """
apiVersion: v1
kind: Service
metadata:
  name: ${APP_NAME}-service
  namespace: ${NAMESPACE}
  labels:
    app: service-monitor ## match label của Service Monitor
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "5000"
    prometheus.io/path: "/metrics"
spec:
  selector:
    app: ${APP_NAME}
  ports:
    - name: http 
      protocol: TCP
      port: 80
      targetPort: 5000
      nodePort: 30080
  type: NodePort
"""
            
            // Cài đặt kubectl
            sh '''
                KUBECTL_VERSION=$(curl -L -s https://dl.k8s.io/release/stable.txt)
                curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
                ### Cài đặt vào thư mục home
                chmod +x kubectl
                mv kubectl $HOME/k8s-tools/
                ### Thêm vào PATH cho phiên làm việc hiện tại
                export PATH="$HOME/k8s-tools:$PATH"
            '''
            // Kiểm tra kubectl đã cài đặt
            sh '$HOME/k8s-tools/kubectl version --client'
            // Áp dụng lên cluster
            withKubeConfig([credentialsId: 'cloud-credential', serverUrl: 'https://34.124.251.86']) {
                sh '$HOME/k8s-tools/kubectl apply -f deployment.yaml'
                sh '$HOME/k8s-tools/kubectl apply -f service.yaml'
                
                // Kiểm tra
                sh '$HOME/k8s-tools/kubectl get pods'
                sh '$HOME/k8s-tools/kubectl get svc'
                   }
                }
            }
        }
    }  
}      