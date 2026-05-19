"""
nikkei-daily-insight: 日経新聞音声議事録 → Gemini API → Markdownレポート生成 CLI
"""

import sys
import argparse
from pathlib import Path
from datetime import date

from dotenv import load_dotenv
from google import genai
import os
import markdown as md_lib

load_dotenv()

PROMPT_FILE = Path(__file__).parent / "src" / "system_prompt.md"
OUTPUTS_DIR = Path(__file__).parent / "outputs"


def load_system_prompt() -> str:
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"システムプロンプトが見つかりません: {PROMPT_FILE}")
    return PROMPT_FILE.read_text(encoding="utf-8")


def load_transcript(input_path: Path) -> str:
    if not input_path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")
    return input_path.read_text(encoding="utf-8")


def call_gemini_streaming(system_prompt: str, transcript: str, model_name: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数 GEMINI_API_KEY が設定されていません。")

    client = genai.Client(api_key=api_key)

    # ステートレスな1ショット呼び出し: system_prompt + transcript を結合して送信
    full_prompt = f"{system_prompt}\n\n{transcript}"

    print("\n" + "=" * 60)
    chunks: list[str] = []
    # ストリーミングで受信しながらリアルタイム表示
    for chunk in client.models.generate_content_stream(model=model_name, contents=full_prompt):
        text = chunk.text
        print(text, end="", flush=True)
        chunks.append(text)
    print("\n" + "=" * 60 + "\n")

    return "".join(chunks)


def save_markdown(content: str, output_dir: Path, stem: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_path = output_dir / f"{today}_{stem}.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def save_pdf(markdown_content: str, md_path: Path) -> Path:
    try:
        import weasyprint

        html_body = md_lib.markdown(markdown_content, extensions=["extra", "toc"])
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: "Hiragino Sans", "Noto Sans CJK JP", sans-serif;
           font-size: 11pt; line-height: 1.7; margin: 2cm; }}
    h1,h2,h3 {{ border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
    code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
  </style>
</head>
<body>{html_body}</body>
</html>"""
        pdf_path = md_path.with_suffix(".pdf")
        weasyprint.HTML(string=html).write_pdf(pdf_path)
        return pdf_path
    except ImportError:
        print("[警告] weasyprint がインストールされていないため PDF 出力をスキップします。", file=sys.stderr)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="日経新聞音声議事録から Gemini API でレポートを生成する"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="inputs/sample.txt",
        help="議事録テキストファイルのパス (デフォルト: inputs/sample.txt)",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="使用する Gemini モデル名 (デフォルト: gemini-2.5-flash)",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="PDF出力をスキップする",
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    print(f"[1/3] 議事録を読み込み中: {input_path}")
    transcript = load_transcript(input_path)

    print(f"[2/3] Gemini API にリクエスト送信中... (model: {args.model})")
    system_prompt = load_system_prompt()
    try:
        report = call_gemini_streaming(system_prompt, transcript, args.model)
    except Exception as e:
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            print("\n[エラー] APIのクォータ上限に達しています。", file=sys.stderr)
            print("  → Google AI Studio でプロジェクトの課金を有効化してください。", file=sys.stderr)
            print("    https://ai.google.dev/gemini-api/docs/rate-limits", file=sys.stderr)
        elif "GEMINI_API_KEY" in msg:
            print("\n[エラー] APIキーが設定されていません。.env ファイルを確認してください。", file=sys.stderr)
        else:
            print(f"\n[エラー] {e}", file=sys.stderr)
        sys.exit(1)

    print("[3/3] レポートを保存中...")
    stem = input_path.stem
    md_path = save_markdown(report, OUTPUTS_DIR, stem)
    print(f"  Markdown: {md_path}")

    if not args.no_pdf:
        pdf_path = save_pdf(report, md_path)
        if pdf_path:
            print(f"  PDF:      {pdf_path}")

    print("完了！")


if __name__ == "__main__":
    main()
