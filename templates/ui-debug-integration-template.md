# UI / デバッグ統合テンプレート

## Target Identity

- Project:
- Request ID:
- UI surface:
- Branch / revision:

## Deployment Identity

UIを「現行production」として評価する前に確認する。

- verified:
- service / unit:
- working directory:
- entrypoint / module:
- active route / served page:
- deployed revision:
- evidence:

> 静的HTMLが存在することと、現在その画面が配信されていることは別。

## Expected User Flow

```text
Start
  ↓
[screen / action]
  ↓
[save / processing]
  ↓
[next screen]
  ↓
[completion / failure]
```

## Observed Flow

- Start URL / route:
- 操作:
- 実際の遷移:
- 完了表示:
- 失敗表示:
- 復帰導線:

## UI Inventory

| Surface | Active / stale / unknown | Evidence | Notes |
|---|---|---|---|
| | | | |

## API Contract

| UI action | Frontend request | Active backend route | Match |
|---|---|---|---|
| | | | yes / no / unobserved |

## Classification

| Planned node | Status | Evidence | Reason |
|---|---|---|---|
| | AS_BUILT / BROKEN / STALE / UNOBSERVED | | |

## Regression Targets

- Navigation:
- Save / write-out:
- Status display:
- Error handling:
- Old UI reachability:
- Long-running behavior:

## Human Boundary

- Observation recorded:
- Repair proposal:
- Repair authorized:
- Release authorized:

### Rules

1. Code existence != runtime evidence.
2. Deployment Identityを確定してからruntime classificationする。
3. Observationは自動repair命令ではない。
4. 到達できない旧UIはSTALE候補として扱い、現在runtimeのBROKENと混同しない。
5. UNOBSERVEDを無理に埋めない。
