from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


def _auto_device() -> str:
    forced = os.getenv("DEUTSCHTTS_DEVICE")
    if forced:
        return forced
    try:
        import torch  # type: ignore

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


@dataclass(slots=True)
class VoiceConfig:
    speaker: str = "default"
    speed: float = 1.0
    pitch: float = 1.0
    style: str = "neutral"


@dataclass(slots=True)
class TTSConfig:
    model_name: str = "dummy-sine"
    model_path: Path | None = None
    sample_rate: int = 22050
    chunk_size_chars: int = 280
    max_chars: int = 12000
    device: str = field(default_factory=_auto_device)
    output_format: str = "wav"
    trim_silence: bool = True
    normalize_audio: bool = True
    fade_ms: int = 12
    voice: VoiceConfig = field(default_factory=VoiceConfig)

    @classmethod
    def from_env(cls) -> "TTSConfig":
        model_name = os.getenv("DEUTSCHTTS_MODEL", "dummy-sine")
        model_path = os.getenv("DEUTSCHTTS_MODEL_PATH")
        sample_rate = int(os.getenv("DEUTSCHTTS_SAMPLE_RATE", "22050"))
        chunk_size_chars = int(os.getenv("DEUTSCHTTS_CHUNK_SIZE", "280"))
        max_chars = int(os.getenv("DEUTSCHTTS_MAX_CHARS", "12000"))
        output_format = os.getenv("DEUTSCHTTS_OUTPUT_FORMAT", "wav")

        return cls(
            model_name=model_name,
            model_path=Path(model_path) if model_path else None,
            sample_rate=sample_rate,
            chunk_size_chars=chunk_size_chars,
            max_chars=max_chars,
            output_format=output_format,
        )

    def validate(self) -> None:
        if self.output_format.lower() != "wav":
            raise ValueError("Only WAV output is currently supported.")
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive.")
        if self.chunk_size_chars < 32:
            raise ValueError("chunk_size_chars must be >= 32.")
        if self.max_chars < self.chunk_size_chars:
            raise ValueError("max_chars must be >= chunk_size_chars.")
        if self.fade_ms < 0:
            raise ValueError("fade_ms must be non-negative.")
