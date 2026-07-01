# GitHub - ngrok - Jenkins 設定手順

## 1. GitHubへ配置

1. GitHubで新規リポジトリを作成する。
2. このフォルダの内容をリポジトリ直下へpushする。
3. `Jenkinsfile` がリポジトリ直下にあることを確認する。

## 2. Jenkinsジョブ

1. Jenkinsで「新規ジョブ作成」を開く。
2. ジョブ名を `HW25A066-weather-dashboard` とする。
3. 「パイプライン」を選ぶ。
4. Pipeline definitionを `Pipeline script from SCM` にする。
5. SCMをGit、Repository URLを自分のGitHubリポジトリURLにする。
6. Script Pathを `Jenkinsfile` にする。
7. GitHub pluginが利用できる場合、「GitHub hook trigger for GITScm polling」にチェックする。
8. 保存する。

## 3. ngrok

PowerShellでJenkinsのポート8080を公開する。

```powershell
ngrok config add-authtoken <自分のトークン>
ngrok http 8080
```

固定ドメインを使う場合:

```powershell
ngrok http --url=<自分の固定ドメイン>.ngrok-free.app 8080
```

## 4. GitHub Webhook

GitHubリポジトリの Settings > Webhooks > Add webhook で設定する。

- Payload URL: `https://<ngrokのURL>/github-webhook/`
- Content type: `application/json`
- Event: `Just the push event`
- Active: ON

Recent DeliveriesでHTTP 200になれば接続成功。

## 5. 動作確認

READMEの末尾へ1行追加してcommit/pushする。手動でJenkinsの「ビルド実行」を押さずに、自動で新しいビルドが開始されることを確認する。
