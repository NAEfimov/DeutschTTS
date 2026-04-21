from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

from .config import TTSConfig
from .pipeline import TTSPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DeutschTTS local German text-to-speech")
    parser.add_argument("--text", help="Direct text to synthesize")
    parser.add_argument("--input-file", type=Path, help="Path to UTF-8 text file")
    parser.add_argument("--output", type=Path, required=True, help="Output .wav file path")
    parser.add_argument("--model", default="dummy-sine", help="Backend model name")
    parser.add_argument("--sample-rate", type=int, default=22050)
    parser.add_argument("--chunk-size", type=int, default=280)
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument("--device", default=None, help="Override device (cpu/cuda)")
    parser.add_argument("--verbose", action="store_true")
    return parser


def _load_text(args: argparse.Namespace) -> str:
    if (args.text is not None) == (args.input_file is not None):
        raise ValueError("Provide exactly one of --text or --input-file.")
    if args.text:
        return args.text
    assert args.input_file is not None
    return args.input_file.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        text = _load_text(args)
        cfg = TTSConfig.from_env()
        cfg.model_name = args.model
        cfg.sample_rate = args.sample_rate
        cfg.chunk_size_chars = args.chunk_size
        cfg.max_chars = args.max_chars
        if args.device:
            cfg.device = args.device

        pipeline = TTSPipeline(config=cfg)
        out = pipeline.synthesize_to_file(text=text, output_path=args.output)
        logging.info("Generated %s", out)
        return 0
    except Exception as exc:
        logging.error("Synthesis failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
