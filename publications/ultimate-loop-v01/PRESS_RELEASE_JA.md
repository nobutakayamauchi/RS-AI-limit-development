# プレスリリース案

Status: `READY_FOR_HUMAN_REVIEW / NOT_PUBLISHED`

## 限界開発から「Development Sequence Loop（通称 Ultimate Loop）v0.1」— 開発方法そのものを継続的に検証する開発シークエンスを暫定公開

2026年8月14日

「限界開発」は、スマートフォンを中心にAI・GitHub・クラウド等を使い、生活や仕事上の詰まりをその場で仕組みに変えていく社会実験です。今回、その開発過程から生まれた開発方法を **Development Sequence Loop（通称 Ultimate Loop）v0.1** として整理し、実案件へ投入できる暫定稼働版として公開準備しました。

## Ultimate Loopとは

Ultimate Loopは、単なるAIコーディング手順ではありません。

- **Discovery Refresh** — 現在の外部手段や既存実装を調べ直す
- **Raison d’être Destroy** — そもそも作る必要があるかを検証する
- **DA / Counter-DA** — 強い反証と反証への反証を作る
- **METEOR** — 既存・構造抽出・新造候補を同じ条件で比較する
- **Deployment Identity / Reality Gate** — 「コードがある」ではなく「今その実装が動いている」を証拠で確認する
- **WATCH / DARWIN** — 外部により強い候補が出たら現王者を再検証する
- **Emergency Recovery** — サービス障害時は改善より先に最小復旧を行い、正式昇格は後で判断する
- **PHOENIX** — 実装や提供者が失われても、重要な成果と再構築可能性を残す

## 「完成しているが、永久完成ではない」

v0.1は、現在の証拠では実案件を最初から最後まで通せる `PROVISIONAL_OPERATIONAL` 状態です。

一方でUltimate Loop自身も例外ではありません。少なくとも7日ごとに外部の開発手法・AI・OSS・サービス等を再確認し、materialなチャレンジャーが存在する場合だけ同じ条件でノックアウトマッチを行います。候補がなければ、何も変えないことが正しい結果です。

## 自動投稿・自動拡散は作らない

X等へのAPI自動投稿、連続投稿、タイマー投稿、投稿リトライの自動化は実装しません。作るのは「投稿文を完成状態にして、人間が内容を確認し、最後の投稿ボタンを押す直前まで持っていく」公開キットです。

## 公開上の配置

Ultimate Loopの一般向け説明は「限界開発」の公式ページに置きます。技術的な正本はRTSリポジトリに残します。公開ページは説明と導線を担い、正本を二重化しません。

## 関連リンク

- 限界開発: https://nobutakayamauchi.github.io/RS-AI-limit-development/
- 限界開発 GitHub: https://github.com/nobutakayamauchi/RS-AI-limit-development
- Ultimate Loop canonical method: https://github.com/nobutakayamauchi/RTS/blob/main/thin-rts/ULTIMATE_LOOP_METHOD.md