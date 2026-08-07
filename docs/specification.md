# 限界開発 仕様書

更新: 2026-08-07

## 1. 定義

限界開発とは、

> **スマートフォン1台しか持たず、精神・肉体・金銭・時間・生活上の問題を抱え、プログラム素人である人間が、AIと根性だけで生活をぶん回す仕組みを作る社会実験。**

この定義は固定する。開発環境・ツール・AI・サーバー・RTSが進化しても、限界開発の主語を技術へ移さない。

## 2. 目的

限界状態を美化することではない。

制約がある人間でも、AIと外部サービスを組み合わせることで、生活上の詰まりを小さな仕組みに変え、中断・失敗を経ても再開し、仕事・収入・生存へ接続できるかを検証する。

## 3. 基本条件

- 実質スマートフォン1台を司令塔とする
- PC、高額機材、大きな初期投資を必須にしない
- 体力・集中・時間・生活環境が安定しているとは仮定しない
- 弱いサーバーや無料枠でも始められる
- プログラム素人からの開始を許容する
- AIを単なるコード生成器ではなく、相談・設計・実装・監査・記録補助として扱う
- 中断しないことではなく、再開可能であることを重視する

## 4. 開発原則

### 4.1 限界は開始条件

「十分な時間・金・体力・機材が揃ったら始める」を前提にしない。現に存在する制約を入力として設計する。

### 4.2 最小の詰まりを潰す

人生全体を一度に自動化しない。今日の詰まりを一つ減らす仕組みから作る。

### 4.3 実プロジェクトでDogfoodする

デモやコード存在だけで完成扱いしない。実際の生活・制作・運用で使い、証拠を得る。

### 4.4 文脈を設計する

AIへ全履歴・全コード・全知識を毎回投入しない。

以下を分離する。

- source of truthとなる仕様
- 完了して凍結した知識
- 現在の差分
- 実世界の観測
- AIの提案
- 人間の判断
- 未確認事項

目的はAIを「何でも知っている状態」にすることではなく、**今回判断するために必要な世界だけを読ませること**である。

### 4.5 Evidence First

観測対象は次のように分類する。

- `AS_BUILT` — 実装・稼働を証拠で確認した
- `BROKEN` — 対象runtimeで故障を確認した
- `STALE` — 古い・非稼働・重複した実装である
- `UNOBSERVED` — まだ観測していない

未確認を成功扱いしない。

### 4.6 Deployment Identity First

runtime実装を分類する前にDeployment Identityを確定する。

確認候補:

- service / unit
- working directory
- entrypoint / loaded module
- active route / runtime surface
- deployed revision / commit when available
- supporting evidence

不変条件:

> **Deployment Identity MUST be established before runtime implementation classification.**

> **Code existence != runtime evidence.**

### 4.7 Human Decision Boundary

AI・RTS・デバッグエンジンは、証拠や候補を提示しても次を自動越境しない。

- routing decision
- approval
- implementation authorization
- release decision

Observationは自動修復命令ではない。

## 5. 現行プロトコル

```text
Problem / Idea
    ↓
Context Routing
    ↓
Human Routing Decision
    ↓
Design Bundle
    ↓
Real Project Dogfood
    ↓
Deployment Identity
    ↓
Observation
    ↓
Debug Link
    ↓
Lifecycle
    ↓
City Release
    ↓
Human Release Decision
```

このプロトコルの詳細は `current-development-architecture.md` と `rts-integration.md` を参照する。

## 6. RTSの位置付け

RTSは限界開発そのものではない。限界開発を長期継続するために生まれた共通統制基盤である。

現在の役割:

- アイデアと対象プロジェクトのルーティング
- FREEZER / Obsidian等の既存知識照合
- Design Bundle生成
- 実プロジェクトDogfoodの観測枠
- Debug Link / Lifecycle
- City Release判断材料
- 人間判断境界の保持

## 7. Knowledge Bridge / Obsidian / FREEZER

知識層は、全情報を一つの巨大文書へまとめるために使わない。

完了した仕様・判断・学習を凍結し、必要な時だけ関連文脈へ戻す。

現時点では、全面自動書き換え・自動承認・自動修復を目的としない。

## 8. デバッグ

一度人間が踏んだ不具合を、可能な限り次へ変換する。

- 再現条件
- 入力
- 期待結果
- 実結果
- 原因候補
- 修正
- 回帰テスト
- 再開手順

「また人間が同じ場所を触って確認する」回数を減らす。

## 9. スマートフォンの役割

スマホはすべての重処理を実行する端末ではなく、司令塔である。

スマホから必要に応じて次を使う。

- 対話AI
- GitHub
- SSH / terminal
- browser
- cloud / server
- Obsidian / knowledge store
- GitHub Pages / publication surfaces

重要なのは処理を端末内へ閉じることではなく、**スマホだけで現在地・判断・操作・確認へ到達できること**である。

## 10. 成功条件

限界開発の成功は「大きな製品が完成した」だけでは判定しない。

成功例:

- 今日の作業が一つ減った
- 同じ失敗を二度踏まなくてよくなった
- 中断後に現在地へ戻れた
- 実稼働と古いコードを区別できた
- 未確認事項を未確認のまま保持できた
- 他人が同じ条件で追試できた
- 仕事・収入・生活へ接続した
- 安全に停止できた

## 11. 非目的

限界開発は次を目的としない。

- 苦痛・睡眠不足・危険な生活状態の美化
- AIによる人間判断の全面置換
- 自動修復・自動承認を無条件で拡大すること
- 技術インフラを育てること自体を目的化すること
- 過去の実験記録を現在の仕組みに合わせて改竄すること
- 「全部入り」の巨大システムを完成条件にすること

## 12. 歴史記録の扱い

Episodeや公開済み記録は、その時点の事実として保存する。

現在のRTS、Knowledge Bridge、Deployment Identity Gate等を、当時使っていなかった記録へ後付けで「実施済み」と記載しない。

現在仕様と歴史資料を分ける。

## 13. 変更管理

限界開発の**定義**と、限界開発を支える**現行開発環境**は別物として管理する。

- 定義変更: 原則行わない
- 開発環境更新: 実dogfoodの証拠に応じて更新する
- 新しい不変条件: 実際に踏んだ失敗から追加する
- 不明点: 未確認として保持する

この区別により、システムが巨大化しても社会実験の主語を失わない。
