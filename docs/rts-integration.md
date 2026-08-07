# RTSとの接続 — 限界開発の統制基盤

更新: 2026-08-07

## RTSの位置付け

RTSは限界開発の主役ではありません。

限界開発を続けるうちに、複数のAI、複数のプロジェクト、古い実装、仕様、観測、判断が混ざり始めたため、それらを分離して「どこまで分かっていて、誰が次を決めるのか」を保持するために生えた共通基盤です。

限界開発の定義自体は変わりません。

## 現在のVertical Slice

```text
Idea / Problem
    ↓
Idea Routing
    ↓
Human Routing Decision
    ↓
V1 Handoff
    ↓
Design Bundle
    ↓
Real Project Dogfood
    ↓
Deployment Identity Gate
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

## 1. Idea Routing

思いつきや困りごとを、そのまま実装命令にしません。

最低限、次のような情報へ変換します。

- idea identity
- classification
- target project
- target component
- timing
- routing action
- confidence
- missing context
- related FREEZER knowledge

目的は「AIが賢く推測する」ことより、**どの文脈へ運ぶべき情報なのかを分離すること**です。

## 2. Human Routing Decision

ルーティング候補が出ても、自動で別プロジェクトを書き換えません。

人間がAPPROVE等の判断を行い、その判断記録を残してからhandoffします。

ここで `implementation_executed = false` を維持できることが重要です。

## 3. Design Bundle

承認されたアイデアは、設計・議論用のBundleへ変換します。

Bundleには、要求、目標、feature、missing part、既存コンテキスト、挿入候補、human discussion questions等を持たせます。

設計候補が生成されても、この時点では実装しません。

## 4. Real Project Dogfood

設計上「あるはず」の機能と、現実に動いているものを分けるため、実プロジェクトで観測します。

観測対象は、コードの存在ではなくruntime realityです。

## 5. Deployment Identity Gate — V1.2

V1 dogfoodで、古いソースツリーを実稼働と誤認しかける問題が見つかりました。

V1.2では、runtime分類の前にDeployment Identityを要求します。

候補:

- `service` / unit
- `working_directory`
- `entrypoint` / loaded module
- `active_surface` / routes
- `revision` / deployed commit
- supporting evidence

不変条件:

> **Deployment Identity MUST be established before runtime implementation classification.**

> **Code existence != runtime evidence.**

runtime observationが存在するのにverified deployment identityがない場合、Debug Linkは分類を拒否します。

## 6. Observation

実プロジェクトの各planned nodeを次の状態で扱います。

- `AS_BUILT` — 実装・稼働を証拠で確認
- `BROKEN` — 対象runtimeで故障を確認
- `STALE` — 古い・非稼働・重複
- `UNOBSERVED` — まだ確認していない

観測がないものをAIの推測で埋めません。

Observationは**修復命令ではなく証拠**です。

## 7. Debug Link / Lifecycle

Design Bundleと実観測を接続し、「計画されたもの」と「現実に観測されたもの」をLifecycleへ変換します。

ここで重要なのは、正解率の演出ではなく、未観測やSTALEが残っていてもそのまま集計できることです。

V1.2の実dogfoodでは、Deployment Identityなしではruntime classificationを拒否し、identity確認後に同じ観測を正常にLifecycle化できました。

## 8. City Release

Lifecycleをもとに、次へ進めるか、人間判断を待つべきかを整理します。

City Releaseは自動リリース実行機ではありません。

例:

```text
decision = V1_SCOPE_COMPLETE_WITH_KNOWN_ISSUES
next_city = DOGFOODING
human_decision_required = true
implementation_executed = false
```

既知問題が残っていても、それを消したふりをせず、human release decisionへ渡します。

## 9. FREEZER / Obsidian / Knowledge Bridge

RTSは既存知識を毎回すべて巨大文脈として読み直すのではなく、関係する知識を候補として引き出し、設計やroutingへ接続します。

完了した仕様・判断は凍結し、必要な時だけ再利用します。

現時点での境界:

- full Obsidian rewriteは行わない
- Knowledge Bridgeは自動修復権限を持たない
- common UIはreview surface
- screenshot / sketchはadapter input
- approval / implementation / releaseはhuman boundaryを越えない

## 10. 限界開発との関係

RTSが高度化しても、限界開発を「RTSを作るプロジェクト」へ変えてはいけません。

RTSの価値は、スマホ1台で複数AI・複数案件を扱っても、

- 文脈を失わない
- 古い実装を現実と誤認しない
- 未確認を未確認のまま残す
- 中断しても再開できる
- 人間が最後の判断を持つ

状態を作ることにあります。

## 11. 実装境界

RTS側の最新仕様・テスト・completion recordを正本とし、本リポジトリでは限界開発から見た役割と運用原則を記録します。

RTSの内部実装をこのリポジトリへ複製しないことで、二重正本化を避けます。
