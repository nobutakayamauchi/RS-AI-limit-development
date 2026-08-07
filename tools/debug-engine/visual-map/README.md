# 視覚ナビゲーションマップ

限界開発式デバッグエンジンの補助ツールです。画面、操作、遷移、到達可能性を人間がスマホでも把握しやすい形へ変換します。

## 役割

視覚マップは次を助けます。

- UI構成の把握
- 画面間の導線確認
- 重複UI候補の発見
- 操作起点の整理
- regression targetの発見
- デバッグ時の現在地共有

ただし、**視覚マップはruntime truthそのものではありません。**

静的ファイルやroute候補が存在しても、現在productionで配信されているとは限りません。

## Deployment Identityとの関係

現在の限界開発では、runtime UIを `AS_BUILT` / `BROKEN` と分類する前にDeployment Identityを確認します。

確認候補:

- service / unit
- working directory
- entrypoint / module
- active routes / served page
- deployed revision

> **Code existence != runtime evidence.**

視覚マップ上に旧UIが残っている場合、現在surfaceへ到達できないことが確認できれば `STALE` 候補です。現在runtimeの故障と混同しません。

## 推奨フロー

```text
Map / UI Candidate
    ↓
Deployment Identity
    ↓
Active Surface Verification
    ↓
User Flow Inspection
    ↓
Observation
AS_BUILT / BROKEN / STALE / UNOBSERVED
    ↓
Regression Target
```

## focused maps

`focused_maps.py` は大きなUI構成から、確認対象だけを切り出すために使います。

スマホ画面では全体マップを一度に読むより、

- save / export
- narration
- delete / restore
- output / render

など、目的ごとの小さなmapへ切る方が確認しやすくなります。

これは限界開発の文脈設計と同じ考え方です。**全部を見せるのではなく、今回必要な世界だけを見せる。**

## sample-map.json

サンプルはschemaや描画方法を示すためのfixtureです。

サンプル上のnodeやrouteを現行productionの証拠として扱わないでください。

## Test

visual mapのテストは、主に変換・描画・focused map生成のregressionを守ります。

実際のproduction UIの正しさは、別途real-project dogfoodとDeployment Identity確認が必要です。

## Human Boundary

このツールは画面関係を可視化しても、次を自動実行する権限を持ちません。

- UI削除
- route変更
- repair
- approval
- production release

Observationと変更権限を分けます。

## 成功条件

- スマホで「どの画面からどこへ行くか」が分かる
- 旧UIと現行UIを区別する調査起点になる
- 人間の再探索量が減る
- regression targetが見つけやすくなる
- map自体をruntime truthと誤認しない

視覚マップも、限界開発のために生えた生命維持設備の一つです。
