# nikkei-daily-insight

日経新聞の音声議事録テキストを Gemini API に投げ、ハルシネーションのない分析レポートを自動生成する CLI ツール。

## 特徴

- **ステートレス実行**: 毎回コンテキストをリセットした状態で API を呼び出すため、文脈肥大化によるハルシネーションを防止
- **Markdown + PDF 出力**: 日付付きファイル名で `outputs/` に自動保存
- **プロンプト外部管理**: `src/system_prompt.md` を編集するだけで評価軸を変更可能
- **uv 完全対応**: 依存管理・実行を uv に統一

## ディレクトリ構成

```
.
├── inputs/                 # 議事録テキストを置く場所
│   └── sample.txt          # サンプル（ここにテキストを貼る）
├── outputs/                # 生成されたレポートの保存先（Git管理外）
├── src/
│   └── system_prompt.md    # Gemini に渡すシステムプロンプト（編集可）
├── main.py                 # CLIエントリポイント
├── pyproject.toml
└── .env.example            # 環境変数テンプレート
```

## セットアップ

### 1. 依存パッケージのインストール

```bash
uv sync
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# .env を開いて GEMINI_API_KEY を設定する
```

API キーは [Google AI Studio](https://aistudio.google.com/) で取得できます。

### 3. 議事録テキストを配置

`inputs/` フォルダに `.txt` ファイルを置きます。

## 実行方法

```bash
# デフォルト（inputs/sample.txt を使用）
uv run main.py

# ファイルを指定して実行
uv run main.py inputs/2024-01-15.txt

# モデルを変更して実行
uv run main.py inputs/2024-01-15.txt --model gemini-1.5-flash

# PDF出力をスキップ
uv run main.py inputs/2024-01-15.txt --no-pdf
```

実行後、`outputs/YYYY-MM-DD_<ファイル名>.md` と `.pdf` が生成されます。

## システムプロンプトのカスタマイズ

`src/system_prompt.md` を直接編集してください。  
現在は「プロのエコノミスト・Tier1戦コン」視点での株式動向分析フォーマットが設定されています。

## 開発ルール

- main への直接コミット禁止。必ず Issue → `feature/issue-{番号}` ブランチのフローを踏むこと。
- Issue/PR/コミットの書式は `.github/instructions/` の各規約に従う。
