# 限界開発 テストレポートテンプレート

## Identity

- Project:
- Request / Idea ID:
- Branch / revision:
- Date:
- Tester:

## Deployment Identity

runtimeを評価する場合は先に確定する。

- verified:
- service / unit:
- working directory:
- entrypoint / module:
- active surface / routes:
- deployed revision:
- evidence:

> Code existence != runtime evidence.

## Test Scope

- 今回確認するもの:
- 今回確認しないもの:
- Planned nodes:
- Regression targets:

## Environment

- Smartphone / client:
- Server / runtime:
- Browser:
- Network:
- Relevant configuration:

## Results

| Node / Case | Expected | Actual | Status | Evidence |
|---|---|---|---|---|
| | | | AS_BUILT / BROKEN / STALE / UNOBSERVED | |

## Failure Record

- Symptom:
- Reproduction steps:
- Runtime evidence:
- Log / screenshot / route evidence:
- Cause confirmed / candidate:
- Human decision:
- Repair authorized: yes / no

## Regression

- Added / updated test:
- Result:
- Existing regression suite result:
- Remaining unobserved area:

## Summary

- AS_BUILT:
- BROKEN:
- STALE:
- UNOBSERVED:
- Blockers:
- Known issues:

## Release Boundary

- Human decision required:
- Implementation executed:
- Release executed:
- Next action:

### Rules

- 未実施テストはPASSにしない。
- 非稼働コードの不整合を現在runtimeのBROKENとして扱わない。
- ObservationとRepair Authorizationを分ける。
- 実測値とAI推測を分ける。
