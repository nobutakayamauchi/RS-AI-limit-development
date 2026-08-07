# 限界開発 仕様テンプレート

## 0. Identity

- Project:
- Request / Idea ID:
- Branch / revision:
- Owner:
- Date:

## 1. 困りごと

- 何が詰まっているか:
- 誰が困っているか:
- 今日直す必要があるか:
- 生活・仕事への影響:

## 2. 目的

- Primary outcome:
- 成功条件:
- 非目的:
- 今回作らないもの:

## 3. 制約

- Smartphone-first制約:
- 時間:
- 金銭:
- サーバー / 計算資源:
- 既存システム:
- 安全上の制約:

## 4. Context Routing

- Target project:
- Target component:
- Timing:
- Related frozen knowledge:
- 必要な既存仕様:
- 今回読ませない文脈:
- Missing context:

## 5. Source of Truth

- 正式仕様:
- 正式コード:
- 現行branch:
- 完了済み / FREEZER:
- AI提案と区別すべき事実:

## 6. Human Decision Boundary

- Routing decision required: yes / no
- Implementation authorization required: yes / no
- Release decision required: yes / no
- 破壊的変更の確認:

## 7. Design

- Proposed architecture:
- Existing boundary to reuse:
- New boundary required:
- Side effects:
- Migration plan:
- Observability:
- Regression targets:

## 8. Deployment Identity

runtime classificationを行う場合に記入する。

- verified: true / false
- service / unit:
- working directory:
- entrypoint / loaded module:
- active route / surface:
- deployed revision:
- evidence:

> Deployment Identity MUST be established before runtime implementation classification.

> Code existence != runtime evidence.

## 9. Planned Nodes / Acceptance Criteria

| ID | Feature / Goal | Acceptance criteria | Evidence required |
|---|---|---|---|
| | | | |

## 10. Observation

各planned nodeを、実際に確認できた証拠だけで分類する。

| Node | Status | Evidence | Reason |
|---|---|---|---|
| | AS_BUILT / BROKEN / STALE / UNOBSERVED | | |

## 11. Test

- Unit:
- Integration:
- Regression:
- Real-project dogfood:
- Long-running / device-specific:
- 未実施テスト:

## 12. Release

- Known issues:
- STALE:
- UNOBSERVED:
- Blockers:
- Human release decision:
- implementation_executed:

## 13. Completion Record

- 完了したこと:
- 未完了:
- 次にやらないこと:
- 再開地点:
- 次の正当な一手:

### 原則

Observationは修復命令ではない。未確認を成功扱いしない。AI提案と人間承認を分ける。歴史記録へ現在仕様を後付けしない。
