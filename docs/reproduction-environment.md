# 限界開発 再現環境

更新: 2026-08-07

## この文書の目的

限界開発を再現するために必要なのは、作者とまったく同じサービス契約やサーバー構成ではありません。

再現すべきなのは、**スマートフォンを司令塔に、制約下でAIと外部計算資源を使い、実生活の問題を仕組みへ変え、証拠を残し、止まっても再開できること**です。

## 固定定義

> **スマートフォン1台しか持たず、精神・肉体・金銭・時間・生活上の問題を抱え、プログラム素人である人間が、AIと根性だけで生活をぶん回す仕組みを作る社会実験。**

再現環境はこの定義を支えるものであり、定義を置き換えません。

## 必須レイヤー

### 1. Human / Smartphone Layer

最低限:

- スマートフォン
- ブラウザ
- 文字入力または音声入力
- 対話AIへアクセスする手段

推奨:

- SSH/terminal client
- GitHub app / web
- ファイル閲覧・共有手段

スマホ本体で全処理を完結させる必要はありません。スマホから判断、指示、確認、復帰ができればよいとします。

### 2. AI Layer

一つ以上の対話・実装支援AIを使います。

AIには役割を分けてよいものとします。

例:

- 壁打ち・要求整理
- architecture / design discussion
- implementation
- review / audit
- research
- summarization

重要なのはAIの銘柄ではなく、**文脈を混ぜすぎないこと**です。

### 3. Source of Truth Layer

Git等、差分と履歴を保存できる場所を用意します。

最低限残すもの:

- definition / README
- specification
- current branch / revision
- tests
- completion record
- known issues

Chat historyだけを正本にしません。

### 4. Runtime Layer

必要ならクラウド、VPS、無料枠、ローカル外の計算資源を使います。

性能やサービス名は固定しません。

再現上重要なのは、**どのruntimeが本当に動いているかを識別できること**です。

### 5. Knowledge Layer

長期運用では、完了した知識を毎回全文読み直すのではなく、必要な情報を再利用できる層を持ちます。

実装例:

- Obsidian
- Markdown vault
- FREEZER相当の凍結知識
- GitHub docs
- search / routing layer

全面自動書き換えは必須ではありません。

## 現在の推奨構成

```text
iPhone / Smartphone
  ├─ ChatGPT / other AI
  ├─ GitHub
  ├─ SSH client
  └─ Browser
          ↓
GitHub / Source of Truth
          ↓
RTS / Context & Decision Layer
  ├─ Idea Routing
  ├─ FREEZER knowledge match
  ├─ Design Bundle
  ├─ Dogfood Observation
  ├─ Debug Link / Lifecycle
  └─ City Release
          ↓
Real Project / Cloud Runtime
          ↓
Deployment Identity Evidence
```

RTSは追試に必須ではありません。規模が小さい場合は、人間が同じ境界をMarkdownとチェックリストで再現しても構いません。

## 文脈設計の再現

次の情報を一つの巨大promptへ混ぜないことを推奨します。

- 正式仕様
- 過去の完成知識
- 今回の要求
- 実装候補
- runtime observation
- AIの推測
- human decision

最低限、「事実」と「提案」と「未確認」を分けます。

## Deployment Identityの再現

runtimeについて `AS_BUILT` / `BROKEN` のような判断をする前に、可能な範囲で次を確認します。

- service / process
- working directory
- executable / entrypoint / loaded module
- route / endpoint / active surface
- branch / revision / commit
- environment / deployment record

原則:

> **Deployment Identity MUST be established before runtime implementation classification.**

> **Code existence != runtime evidence.**

複数clone、古いbranch、未deployコードがある環境では特に重要です。

## Observationの再現

planned featureを次へ分けます。

```text
AS_BUILT   実稼働を証拠で確認
BROKEN     実稼働上の故障を証拠で確認
STALE      古い・非稼働・重複
UNOBSERVED まだ観測していない
```

`UNOBSERVED` を残せることを成功条件に含めます。

## Human Decision Boundaryの再現

AIや自動化へ次を無条件に任せないことを推奨します。

- どのprojectへroutingするか
- 実装してよいか
- repairを適用してよいか
- releaseしてよいか

自動化する場合も、どこまでがproposalでどこからがexecutionかを明示します。

## 弱い環境での考え方

サーバー性能が低い場合:

- 重い処理だけ外へ逃がす
- preview品質を落とす
- concurrencyを抑える
- 処理をjob化する
- 状態を保存して中断可能にする
- 完成品より復帰可能性を優先する

スマホ側のバッテリー・通信・画面保持が厳しい場合:

- 長い処理を端末セッションへ依存させない
- server-side jobとして継続させる
- statusを後から読めるようにする

## 再現に不要なもの

次は限界開発の成立条件ではありません。

- 同一機種のiPhone
- 同一AIプラン
- 同一クラウド事業者
- 同一RTS revision
- 同一Obsidian vault
- 同一デバッグUI

環境のブランドではなく、制約・判断境界・証拠・再開性を再現します。

## 最小追試

追試者は、次の一件だけでも限界開発を再現できます。

1. スマホから実生活の困りごとをAIへ相談する
2. 問題を最小単位へ切る
3. GitHub等へ仕様を残す
4. AI支援で最小ツールを作る
5. 実際に自分で使う
6. 失敗または成功の証拠を残す
7. 未確認事項を分ける
8. 次回の再開地点を書く

これが成立すれば、巨大なRTS環境をコピーしなくても限界開発の社会実験は成立します。

## 歴史との互換性

過去Episodeの環境は、その当時の再現条件です。現在のRTSやDeployment Identity Gateを過去の実験へ遡及適用して「当時も使った」ことにはしません。

新規Episodeは現在のプロトコルを基準とし、旧Episodeはhistorical snapshotとして保持します。
