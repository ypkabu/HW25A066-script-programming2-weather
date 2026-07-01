# Jenkinsログの保存手順

1. Jenkinsの成功したビルドを開く。
2. 左側の「コンソール出力」を開く。
3. 右上のDownloadを押す。表示がない場合は「View as plain text」を開いて保存する。
4. ファイル名を `jenkins_console_HW25A066.txt` にする。
5. 最終行が `Finished: SUCCESS` になっていることを確認する。

ログ内で確認する文字列:

- `githubPush`
- `Unit tests`
- `Weather data output`
- `JavaScript dashboard extension`
- `[verify] success`
- `Archiving artifacts`
- `Finished: SUCCESS`
