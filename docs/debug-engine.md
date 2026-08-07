# 限界開発式デバッグエンジン

更新: 2026-08-07

## 位置付け

デバッグエンジンは限界開発の主役ではありません。

スマホ中心の開発では、一度踏んだ不具合を何度も人間が再操作して確認すること自体が大きな負荷になります。その負荷を減らすため、操作・症状・証拠・修正・回帰を再利用可能な形へ変換するために生えた生命維持設備です。

## 目的

不具合を次の形へ変えることを目的とします。

```text
人間が踏んだ問題
    ↓
再現条件
    ↓
対象runtimeのIdentity
    ↓
観測Evidence
    ↓
原因候補 / 修正
    ↓
回帰テスト
    ↓
再開可能な知識
```

「一度直った」だけで終わらせず、同じ問題に再遭遇した時の人間負荷を下げます。

## Evidence First

デバッグエンジンは、コードを見つけただけで故障と判定しません。

実観測は次を区別します。

- `AS_BUILT`
- `BROKEN`
- `STALE`
- `UNOBSERVED`

とくに `BROKEN` は、対象runtimeで壊れている証拠がある場合に使います。

## Deployment Identity

V1 dogfoodで、非稼働の古いコードをruntime realityと誤認しかける問題が見つかりました。

そのため現在は、runtime implementation classificationより先にDeployment Identityを確認します。

確認候補:

- service / unit
- working directory
- entrypoint / loaded module
- active route / surface
- revision / commit
- runtime evidence

原則:

> **Code existence != runtime evidence.**

古いファイルに不整合があっても、現在deployされていないなら「現在のruntimeがBROKEN」という証拠にはなりません。

## 観測と修復を分ける

Observationは証拠です。

デバッグエンジンが問題を発見しても、それだけで自動repair・自動approval・自動releaseを行うことを前提にしません。

```text
Observation
  ≠ Repair Authorization
  ≠ Release Authorization
```

修正候補を作る場合も、人間判断境界を別に持ちます。

## 視覚ナビゲーションマップ

視覚マップは、画面・操作・遷移・到達可能性を人間が把握しやすくする補助層です。

有効な用途:

- 画面構成確認
- 導線の重複確認
- 操作起点の整理
- expected pathの可視化
- 回帰対象の発見

ただし、静的HTMLや古い画面ファイルが存在するだけで「今のproduction UI」とは断定しません。Deployment Identity / active surfaceを先に確認します。

## 再現シナリオ

最低限、次を残します。

- 対象project
- Deployment Identity
- 事前状態
- 操作
- 期待結果
- 実結果
- screenshot / log / route / code evidence
- status classification
- 修正revision
- regression test

## スマホ中心での価値

スマホ1台では、長いログを何度も探したり、複数の画面を往復したりするコストが大きいです。

そのためデバッグエンジンは、

- 人間操作の再現回数を減らす
- どこまで確認したかを保存する
- AIへ渡す文脈を小さくする
- 次のチャット・次の日へ引き継ぐ

ことを優先します。

## RTSとの接続

RTS / Knowledge Bridgeを使う場合、デバッグ観測はDesign Bundleのplanned nodesへ接続され、Lifecycle判断の材料になります。

```text
Design Bundle
    +
Verified Deployment Identity
    +
Observation
    ↓
Debug Link
    ↓
Lifecycle
    ↓
City Release / Human Decision
```

デバッグエンジン単体がCity Releaseを決めるわけではありません。

## 完成条件

デバッグエンジンの価値は機能数ではなく、次で判断します。

- 同じバグを人間が何度も踏まなくてよい
- 古いコードと実稼働を区別できる
- 証拠と推測を区別できる
- regression testへ変換できる
- 中断後もどこまで調べたか分かる
- 修復権限と観測権限が混ざらない

## 非目的

- あらゆる不具合の完全自動修復
- AIによる無条件の自動承認
- productionへの無確認適用
- 静的コード存在だけからのruntime断定
- デバッグ基盤を育てること自体の目的化

限界開発では、デバッグエンジンも生活を回すための道具であり、社会実験そのものではありません。
