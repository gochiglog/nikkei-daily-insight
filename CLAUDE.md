# CLAUDE.md — nikkei-daily-insight

## プロジェクト概要

日経新聞の音声テキスト（議事録）を Gemini API に投げ、株式動向の分析レポートを自動生成する Python CLI ツール。
Gemini の Web チャットでは文脈肥大化によるハルシネーションが発生していたため、毎回ステートレスな API 呼び出しで解決する。

## 技術スタック

| 用途 | ライブラリ / サービス |
|---|---|
| パッケージ管理 | uv |
| LLM API | Google Gemini API (`google-genai`) |
| 環境変数 | python-dotenv |
| Markdown → HTML | markdown |
| HTML → PDF | weasyprint |

## ディレクトリ構成

```
.
├── .github/
│   └── instructions/       # Issue/PR/Commit/Reviewのルール定義
├── inputs/                 # 議事録テキスト (.txt) を置く場所
├── outputs/                # 生成レポート置き場（Git管理外）
├── src/
│   └── system_prompt.md    # Geminiに渡すシステムプロンプト
├── main.py                 # CLIエントリポイント
├── pyproject.toml          # uv 依存定義
└── .env                    # APIキー等（Git管理外）
```

## 開発ルール

- **main への直接コミット禁止。** 必ず GitHub Issue を作成し、`feature/issue-{番号}` ブランチを切ること。
- Issue のタイトル・本文は `.github/instructions/issue.instructions.md` に従う。
- PR は `.github/instructions/pr.instructions.md` に従う。
- コミットメッセージは `.github/instructions/commit.instructions.md` に従う。

## コーディング規約

- Python 3.13+ の型ヒントを活用する。
- 変数名・関数名はスネークケース (`snake_case`)、クラス名はパスカルケース (`PascalCase`)。
- コメントは日本語で可。

## よく使うコマンド

```bash
# 依存パッケージのインストール
uv sync

# CLIの実行（デフォルト: inputs/sample.txt）
uv run main.py

# ファイル指定で実行
uv run main.py inputs/YYYYMMDD.txt

# PDF出力なし
uv run main.py inputs/YYYYMMDD.txt --no-pdf
```

## 重要な設計上の注意点

- **ステートレス呼び出し必須**: `generate_content()` を毎回新しい `GenerativeModel` インスタンスで呼び出し、チャット履歴を持たせないこと。
- **プロンプトの外部管理**: システムプロンプトは `src/system_prompt.md` に集約し、コードに埋め込まない。
- **出力ファイルのGit除外**: `outputs/` は `.gitignore` で除外済み。機密性の高い議事録を誤ってコミットしないこと。
