# 限界開発式デバッグエンジン — Tool README

このディレクトリは、限界開発の社会実験を支えるデバッグ補助ツールを置く場所です。

デバッグエンジン自体を限界開発の主役にはしません。目的は、スマホ中心の開発で「人間が同じ不具合を何度も手で踏み直す」コストを減らすことです。

## 現在の原則

1. **Evidence First** — 推測より観測を優先する。
2. **Deployment Identity First** — runtime分類前に、どのdeploymentが動いているか確認する。
3. **Code existence != runtime evidence.**
4. **Observation != Repair Authorization.**
5. **UNOBSERVEDを許容する。** 分からないものをPASSにしない。
6. **Human Decision Boundaryを越えない。** 自動修復・承認・releaseを無条件で行わない。

## 推奨デバッグ単位

```text
Project / Request
    ↓
Deployment Identity
    ↓
Reproduction Scenario
    ↓
Observation Evidence
    ↓
AS_BUILT / BROKEN / STALE / UNOBSERVED
    ↓
Fix Proposal
    ↓
Human Authorization
    ↓
Regression Test
```

## Deployment Identity

runtime問題を扱う場合、可能な範囲で以下を記録してください。

- service / unit
- working directory
- entrypoint / loaded module
- active route / surface
- revision / commit
- evidence source

複数clone、旧UI、未deploy branchが存在する環境では特に重要です。

## `debug_engine.py`

軽量なデバッグ知識・再現情報を扱うための実装です。

このツールの出力だけでproduction realityを断定しないでください。runtime classificationが必要な場合は、対象deploymentのIdentityと実観測を別途確認します。

## `knowledge/`

再利用するデバッグ知識を置きます。

知識は次を区別できる形を推奨します。

- 症状
- 対象version / surface
- reproduction
- confirmed evidence
- fix
- regression
- historical / stale information

古い知識を現在runtimeへ無条件に適用しないでください。

## `visual-map/`

UIや操作経路を可視化する補助ツールです。

視覚マップは「存在する画面」を探す助けになりますが、「現在配信中の画面」を保証しません。現在surfaceの確定にはDeployment Identity / active routes等の証拠を使います。

## RTS / Knowledge Bridgeとの関係

RTSを利用する場合、実プロジェクトの観測はDesign BundleへDebug Linkされ、Lifecycle / City Releaseの判断材料になります。

```text
Design Bundle
+ Verified Deployment Identity
+ Observations
    ↓
Debug Link
    ↓
Lifecycle
    ↓
City Release
    ↓
Human Release Decision
```

本ツールはその一部を支えるもので、release authorityではありません。

## 開発時の注意

- 歴史的なfixtureや旧UIを削除する前に、現在runtimeで本当に不要か確認する。
- regression testがない場合は、その事実を明示する。
- screenshotだけでbackend状態を断定しない。
- code inspectionだけでruntime failureを断定しない。
- 人間が一度確認した情報を、次回再利用できる形へ残す。

## 成功条件

このデバッグエンジンの成功は、自動化率ではなく次で測ります。

- 人間の再操作回数が減る
- 誤診が減る
- 再現手順が残る
- regression testへ変換できる
- 古い知識と現在runtimeを区別できる
- 中断しても続きから再開できる
