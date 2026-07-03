def notifyDiscord(String status) {
    try {
        def credentialId = params.DISCORD_CREDENTIAL_ID?.trim()
        if (!credentialId) {
            echo '[discord] credential id is empty; notification skipped'
            return
        }
        withCredentials([string(credentialsId: credentialId, variable: 'DISCORD_WEBHOOK_URL')]) {
            if (isUnix()) {
                sh "python3 tools/notify_discord.py ${status} || true"
            } else {
                bat "python tools\\notify_discord.py ${status} || exit /b 0"
            }
        }
    } catch (err) {
        echo "[discord] notification skipped or failed without failing build: ${err.getMessage()}"
    }
}

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
        string(name: 'DISCORD_CREDENTIAL_ID', defaultValue: 'discord-webhook-url', description: 'Jenkins Secret text credential id。空なら通知をスキップ')
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
                    if (isUnix()) {
                        def command = "fetch_weather.py --location \"${params.LOCATION_NAME}\" --latitude ${params.LATITUDE} --longitude ${params.LONGITUDE} ${offlineFlag}"
                        sh "python3 ${command}"
                    } else {
                        // Windows batch can corrupt non-ASCII CLI arguments; the script default is the same location.
                        def command = "fetch_weather.py --latitude ${params.LATITUDE} --longitude ${params.LONGITUDE} ${offlineFlag}"
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
            echo 'Archiving artifacts'
            archiveArtifacts artifacts: 'output/**', fingerprint: true, allowEmptyArchive: false
        }
        success {
            script {
                notifyDiscord('SUCCESS')
            }
        }
        failure {
            script {
                notifyDiscord('FAILURE')
            }
        }
    }
}
