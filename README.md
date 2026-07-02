# 天気データ自動出力パイプライン

スクリプトプログラミング演習2 最終課題用プロジェクトです。

- 学籍番号: HW25A066
- 氏名: 嶋田一歩
- 必須要素: Jenkinsで天気データを出力
- GitHub/ngrok要素: GitHubのpushをWebhookでJenkinsへ通知し、自動ビルド
- 加点要素: JavaScriptでHTMLダッシュボードを生成、任意のDiscord通知、単体テスト、成果物検証

## 生成物

- `output/weather_data.json`: メタデータを含む7日分の集計データ
- `output/weather_data.csv`: Excel等で確認できるCSV
- `output/index.html`: JavaScriptで生成した静的ダッシュボード
- `output/build_summary.json`: 成果物検証結果

## ローカル確認

Python 3 と Node.js が必要です。外部Pythonパッケージは使いません。

```powershell
python run_local.py --offline
```

実データを取得できる環境では次を使用します。

```powershell
python run_local.py
```

## Jenkins

`Jenkinsfile` を利用する Pipeline from SCM として登録します。GitHub側のWebhook URLは次の形式です。

```text
https://<自分のngrokドメイン>/github-webhook/
```

詳しい設定と撮影順序は `submission/` を参照してください。

## セキュリティ

Discord Webhook URLやngrokのauthtokenはリポジトリへ書き込みません。Jenkins Credentialsまたは環境変数で設定します。

Webhook rehearsal note: Jenkins auto-build check on 2026-07-03 JST.
