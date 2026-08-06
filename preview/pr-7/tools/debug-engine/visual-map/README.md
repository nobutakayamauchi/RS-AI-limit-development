# Visual Navigation Map

画面ごとのスクリーンショットと、各ボタンの接続先を視覚マップへ変換するための補助ツールです。

全体構造を確認する**全体マップ**と、1画面を起点に直接つながる画面だけを表示する**画面別マップ**の二層で出力します。線が密集した場合は、一枚絵だけで判断せず画面別マップへ自動分割します。

## 目的

- どの画面から、どの操作で、どの画面へ移動するかを確認する
- 想定接続先と実測接続先の不一致を赤線で可視化する
- 接続先が未確認のボタンを黄色で残す
- バグ報告、再現テスト、回帰テストの対象画面を視覚的に特定する
- リリース前に「画面は存在するが到達不能」「戻り道がない」「誤った画面へ遷移する」を検出する
- 線の重なりによる見落としを、画面別マップで防止する

## 出力レイヤー

### 1. 全体マップ

すべての画面と接続を一枚で表示します。全体像の把握、孤立画面、戻り道の欠如、主要導線の確認に使用します。

### 2. 画面別マップ

起点画面を1枚だけ左側へ置き、その画面のボタンから直接つながる画面だけを右側へ並べます。

- 1ページにつき起点画面は1つ
- 他画面から出る線は表示しない
- 同一ボタンの期待接続先と実測接続先を比較できる
- トップ画面など接続数の多い画面でも、別画面の線と混ざらない
- `index.html` から画面単位で開ける

## 自動分割の発火条件

次のいずれかを満たした時点で、全体マップだけでは判定困難とみなし、画面別マップを生成します。

- 接続総数が8本以上
- 1画面から出る接続が3本以上
- 画面配置上の推定線交差が2か所以上
- `--focused` が明示された

閾値はコマンドラインで変更できます。線の重なりを完全に幾何学判定するのではなく、**読みづらくなる前に早めに分割する安全側の判定**です。

## 発火地点

Visual Navigation Map は以下で生成・更新します。

1. `SCREEN_CAPTURE` — 新しい画面または状態のスクリーンショットを取得した時
2. `INTERACTION_DISCOVERY` — ボタン、リンク、戻る操作などの接続先を確認した時
3. `BUG_REPRODUCTION` — 想定と異なる画面へ遷移した時
4. `REGRESSION` — 修正後に接続先を再確認した時
5. `MAP_COMPLEXITY_GATE` — 線の密集または交差を検出した時
6. `RELEASE_GATE` — リリース前に全主要導線を監査する時

## 入力

`sample-map.json` と同じ形式のJSONを使用します。

- `screens`: 画面または画面状態
- `actions`: 画面上のボタン・リンク・戻る操作
- `expected_target`: 仕様上の接続先
- `observed_target`: 実際の操作で到達した接続先
- `status`: `confirmed` / `mismatch` / `unknown` / `blocked`

スクリーンショットはリポジトリ内または生成先HTMLから参照可能な相対パスを指定します。

## 線の意味

- 緑: 想定どおりの接続
- 赤: 想定と実測が異なる
- 黄: 接続先未確認
- 灰: 操作不能、無反応、到達不能
- 青い点線: 戻る・復帰などの逆方向操作

## 実行

### 全体マップだけ生成

```bash
python tools/debug-engine/visual-map/visual_map.py \
  tools/debug-engine/visual-map/sample-map.json \
  --output artifacts/navigation-map.html
```

### 全体マップ＋必要時に画面別マップを生成

```bash
python tools/debug-engine/visual-map/focused_maps.py \
  tools/debug-engine/visual-map/sample-map.json \
  --output-dir artifacts/navigation-maps
```

### 必ず画面別マップを生成

```bash
python tools/debug-engine/visual-map/focused_maps.py \
  tools/debug-engine/visual-map/sample-map.json \
  --output-dir artifacts/navigation-maps \
  --focused
```

生成物は次の形になります。

```text
artifacts/navigation-maps/
├── index.html
├── navigation-map-overview.html
├── navigation-map-top.html
├── navigation-map-editor.html
└── navigation-map-preview.html
```

各線をクリックすると、操作名、期待接続先、実測接続先、状態、メモが表示されます。

## デバッグエンジンとの接続

不具合報告から再現シナリオを生成した後、各操作結果を `observed_target` として追記します。

```text
報告文
  ↓
意図・操作列を抽出
  ↓
自動操作
  ↓
現在画面IDを観測
  ↓
expected_target と比較
  ↓
全体マップを更新
  ↓
複雑度を判定
  ├─ 閾値未満: 全体マップで監査
  └─ 閾値以上: 画面別マップも生成
  ↓
不一致線を回帰テストへ登録
```

## 人間が行う確認

自動生成後も、次は人間が確認します。

- スクリーンショット上のボタン位置とラベルが実物と一致しているか
- 同じ画面でも状態違いを別ノードにすべきか
- モーダル、処理中表示、エラー表示が隠れていないか
- 全体マップで線が読めない場合、画面別マップで接続を一つずつ確認できるか
- 正しい遷移でも、利用者が意図を理解できる導線になっているか

画面単位だけでなく、`編集中`、`書き出し中`、`エラー後`、`復帰後`のような状態単位でノードを分けることを推奨します。
