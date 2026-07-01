pipeline {
    agent any

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        string(name: 'LOCATION_NAME', defaultValue: '宝塚市', description: '出力に表示する地点名')
        string(name: 'LATITUDE', defaultValue: '34.7990', description: '緯度')
        string(name: 'LONGITUDE', defaultValue: '135.3560', description: '経度')
        booleanParam(name: 'OFFLINE_MODE', defaultValue: false, description: 'APIを使わずサンプルデータで実行')
    }

    environment {
        PYTHONUTF8 = '1'
        PYTHONIOENCODING = 'utf-8'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Tool versions') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 --version && node --version && git --version'
                    } else {
                        bat 'python --version && node --version && git --version'
                    }
                }
            }
        }

        stage('Unit tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m unittest discover -s tests -v'
                    } else {
                        bat 'python -m unittest discover -s tests -v'
                    }
                }
            }
        }

        stage('Weather data output') {
            steps {
                script {
                    def offlineFlag = params.OFFLINE_MODE ? '--offline' : ''
                    def command = "fetch_weather.py --location \"${params.LOCATION_NAME}\" --latitude ${params.LATITUDE} --longitude ${params.LONGITUDE} ${offlineFlag}"
                    if (isUnix()) {
                        sh "python3 ${command}"
                    } else {
                        bat "python ${command}"
                    }
                }
            }
        }

        stage('JavaScript dashboard extension') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'node tools/generate_dashboard.js output/weather_data.json output/index.html'
                    } else {
                        bat 'node tools/generate_dashboard.js output/weather_data.json output/index.html'
                    }
                }
            }
        }

        stage('Verify outputs') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 tools/verify_outputs.py output'
                    } else {
                        bat 'python tools/verify_outputs.py output'
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'output/**', fingerprint: true, allowEmptyArchive: false
        }
        success {
            script {
                if (isUnix()) {
                    sh 'python3 tools/notify_discord.py SUCCESS || true'
                } else {
                    bat 'python tools\\notify_discord.py SUCCESS || exit /b 0'
                }
            }
        }
        failure {
            script {
                if (isUnix()) {
                    sh 'python3 tools/notify_discord.py FAILURE || true'
                } else {
                    bat 'python tools\\notify_discord.py FAILURE || exit /b 0'
                }
            }
        }
    }
}
