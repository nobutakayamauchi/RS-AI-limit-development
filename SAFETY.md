# 限界開発 安全基準

更新: 2026-08-07

## 目的

限界開発は、厳しい制約下でも生活を回す方法を検証する社会実験です。

**危険な状態、苦痛、睡眠不足、医療アクセスの不足、金銭的困窮を美化したり、継続条件として要求する企画ではありません。**

安全のために停止・中断・縮小することも、限界開発の正しい判断です。

## 1. 限界は開始条件であって目標ではない

「もっと限界まで追い込めば良い成果が出る」という思想を採用しません。

制約が既に存在する場合、それを設計条件として扱い、可能なら負荷を減らします。

## 2. 再開可能性を優先する

体力、集中、通信、電源、資金等が不足した場合、無理に完遂するより現在地を保存します。

残すもの:

- 何をしていたか
- どこまで確認したか
- 何が未確認か
- 次の一手
- 対象branch / revision
- 必要ならDeployment Identity

「止まっても戻れる」を安全機構として扱います。

## 3. AIの提案と人間の判断を分ける

AIが生成した提案は、事実・許可・承認ではありません。

次は人間判断境界として分離します。

- routing decision
- approval
- implementation authorization
- release decision
- 外部への送信・公開
- 破壊的変更

Observationは自動修復命令ではありません。

## 4. Evidence First

不明な状態を無理に確定しません。

- 確認済み → `AS_BUILT`
- 故障を確認 → `BROKEN`
- 古い / 非稼働 → `STALE`
- 未確認 → `UNOBSERVED`

未確認を成功扱いすると、後で人間がより危険な状態で再調査することになります。

## 5. Deployment Identity

runtimeの障害判定やproduction判断を行う前に、対象が本当に現在稼働中のdeploymentか確認します。

確認候補:

- service / unit
- working directory
- entrypoint / loaded module
- active route / surface
- revision / commit

> **Code existence != runtime evidence.**

古いcloneや未deploy branchを誤って修正・削除・release対象にしないための安全境界です。

## 6. 破壊的操作

削除、上書き、production反映、権限変更、データ移行等は、可能な範囲で次を優先します。

- soft delete
- backup / snapshot
- branch分離
- dry-run
- rollback path
- explicit human confirmation

スマホ操作では誤タップ・貼り付けミスも起こり得るため、一発で不可逆になる設計を避けます。

## 7. 秘密情報

公開リポジトリ、GitHub Pages、スクリーンショット、ログへ次を含めないよう注意します。

- password
- private key
- access token
- session cookie
- 個人情報
- 非公開の契約・顧客情報
- 公開不要な内部IPや認証情報

公開前に秘密情報を確認します。

## 8. 実生活と実験を混同しない

生活上の判断、医療、安全、法的判断等を、ソフトウェア実験の成功条件へ従属させません。

開発継続より休息・安全確保・専門家への相談等が優先される場面があります。

このリポジトリは、それらの専門的判断を代替するものではありません。

## 9. 自動化の境界

現行の限界開発では、次を無条件で自動化しません。

- production-grade automatic repair
- automatic approval
- automatic release
- Obsidian / knowledge baseの全面自動書き換え
- runtime identity未確認の自動故障判定

自動化を追加する場合、監査可能性・rollback・human gateを先に設計します。

## 10. 公開時の表現

「限界開発」は挑発的な名前ですが、危険行為を推奨する意味ではありません。

公開コンテンツでは、

- 苦痛を英雄化しない
- 危険を再現条件にしない
- 失敗を隠さない
- 停止判断を敗北扱いしない
- 技術を生活の目的より上に置かない

ことを原則とします。

## 11. 歴史記録

過去Episodeは当時の事実として保持します。

安全基準やRTSが後から進化した場合も、過去の実験が当時その仕組みを備えていたかのように書き換えません。

必要なら「現在の基準ではこう扱う」という注記を追加し、事実と現在評価を分離します。

## 12. 最優先原則

限界開発のインフラは、人間を支えるためにあります。

**人間がインフラを維持するために限界へ追い込まれる状態になったら、設計を縮小・停止・見直します。**
