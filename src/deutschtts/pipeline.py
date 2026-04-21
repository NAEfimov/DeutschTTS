from __future__ import annotations

import json
from pathlib import Path

from .audio import normalize, stitch_audio, trim_silence, write_wav
from .config import TTSConfig
from .synthesizer import BackendError, build_backend
from .text import chunk_sentences, normalize_text, sentence_split


class TTSPipeline:
    def __init__(self, config: TTSConfig | None = None) -> None:
        self.config = config or TTSConfig.from_env()
        self.config.validate()
        self.backend = build_backend(self.config)

    def synthesize_to_file(self, text: str, output_path: Path) -> Path:
        clean = normalize_text(text)
        if not clean:
            raise ValueError("Input text is empty after normalization.")
        if len(clean) > self.config.max_chars:
            raise ValueError(
                f"Input text exceeds max_chars={self.config.max_chars}: got {len(clean)} chars"
            )
        self._validate_output_path(output_path)

        chunks = chunk_sentences(sentence_split(clean), self.config.chunk_size_chars)
        rendered: list[list[float]] = []
        for chunk in chunks:
            try:
                rendered.append(self.backend.synthesize(chunk, self.config))
            except Exception as exc:
                raise BackendError(f"Failed to synthesize chunk: {chunk[:80]}") from exc

        mixed = stitch_audio(rendered, fade_ms=self.config.fade_ms, sample_rate=self.config.sample_rate)
        if self.config.trim_silence:
            mixed = trim_silence(mixed)
        if self.config.normalize_audio:
            mixed = normalize(mixed)

        write_wav(output_path, mixed, sample_rate=self.config.sample_rate)
        self._write_metadata(output_path, text=clean, chunk_count=len(chunks), sample_count=len(mixed))
        return output_path

    @staticmethod
    def _validate_output_path(path: Path) -> None:
        if path.suffix.lower() != ".wav":
            raise ValueError("Only .wav output files are supported.")
        resolved = path.resolve()
        if resolved.is_dir():
            raise ValueError("Output path points to a directory, not a file.")

    def _write_metadata(self, wav_path: Path, text: str, chunk_count: int, sample_count: int) -> None:
        metadata = {
            "model": self.config.model_name,
            "device": self.config.device,
            "sample_rate": self.config.sample_rate,
            "chunk_size_chars": self.config.chunk_size_chars,
            "chunk_count": chunk_count,
            "samples": sample_count,
            "text_chars": len(text),
        }
        metadata_path = wav_path.with_suffix(".json")
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
