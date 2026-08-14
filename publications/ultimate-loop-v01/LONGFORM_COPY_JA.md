# Ultimate Loop v0.1 — Long-form Copy

Status: `READY_FOR_HUMAN_REVIEW / NOT_PUBLISHED`

## note向け

# AIにコードを書かせるだけでは足りなくなったので、「開発方法そのもの」をループにした

限界開発を続けているうちに、問題が変わりました。

最初は「スマホからAIへ指示して、必要なものを作れるか」が中心でした。ところが開発量が増えると、難しいのはコード生成ではなくなりました。

そもそも作る必要があるのか。既存サービスで済むのではないか。AIが古いコードを現行実装と勘違いしていないか。テストが通っただけで本番も正しいと言ってよいのか。より強いAIやOSSが出た時、作ったものに執着せず譲れるか。外部サービスが死んだ時、改善大会をせずまず復旧できるか。

ここを一本につなげたのが **Development Sequence Loop、通称 Ultimate Loop** です。

```text
問題 / 欲しいもの
→ Discovery Refresh
→ Raison d’être Destroy
→ 既存 / 構造抽出 / 新造候補
→ DA / Counter-DA
→ METEOR
→ 実装・Deploy
→ Deployment Identity
→ Post-Deploy Reality / Debug
→ STABLE / WATCH
→ material challenger が出たら DARWIN Knockout
→ 障害時は Emergency Recovery
→ PHOENIX で記憶と再構築可能性を残す
→ 繰り返す
```

一番大事なのは「作ること」ではなく、**今の条件で、その責任と実装が本当に残る価値があるか**を何度でも問い直すことです。

少なくとも7日ごとに外部を調べ直します。ただし、毎週コードを書き直すわけではありません。materialなチャレンジャーがいなければ `KEEP CURRENT` で終了です。より強い候補が出た時だけ、現在の王者と同じworkload・過去の死亡ケースを継承して戦わせます。

この方法自体もMovable Frameに入れています。将来、Ultimate Loopより明確に強い開発方法が出れば、その方法に席を譲ることも仕様に含めました。

公開導線も同じです。投稿文や記事は完成状態まで準備しますが、X APIによる投稿、連投、タイマー投稿はしません。最終Publishは人間の権限として残します。

---

限界開発: https://nobutakayamauchi.github.io/RS-AI-limit-development/

Ultimate Loop canonical: https://github.com/nobutakayamauchi/RTS/blob/main/thin-rts/ULTIMATE_LOOP_METHOD.md

---

## Qiita / Zenn向け

# Development Sequence Loop / Ultimate Loop v0.1 — AI支援開発の「必要性・実装・実Deployment・置換・復旧」を一つのループにする

Development Sequence Loop（Ultimate Loop）は、AI支援開発における「必要性」「実装選択」「実環境確認」「置換」「障害復旧」「再構築」を一つの循環として扱う開発方法です。

特徴は、実装を恒久資産として扱わず、責任とworkloadを基準にoccupantを入れ替え可能にする点です。

### 主要Invariant

- `NO CURRENT LANDSCAPE SWEEP -> NO SUPERIORITY CLAIM`
- `NO SURVIVAL, NO BUILD`
- `PROTOTYPE AUTHORIZED != PROMOTION AUTHORIZED`
- `DEPLOYED != OBSERVED_CORRECT`
- `CODE EXISTENCE != RUNTIME EVIDENCE`
- `EMERGENCY_USE != PROMOTION`
- `IMPLEMENTED != PERMANENT`

### 週次自己進化

7日ごとにDiscoveryを更新します。material challengerが無ければ変更しません。存在する場合だけ、既存workload・death cases・authority boundaryを引き継いでMETEOR/DARWIN比較を行います。

### 実装境界

Ultimate Loop自身はcrawler、scheduler、monitoring platform、deployment engine、SNS publisherを所有しません。外部機構をreplaceable occupantとして利用し、判断・証拠・権限境界を最小限保持します。

Canonical source: https://github.com/nobutakayamauchi/RTS/blob/main/thin-rts/ULTIMATE_LOOP_METHOD.md

Project context: https://nobutakayamauchi.github.io/RS-AI-limit-development/