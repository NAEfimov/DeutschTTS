from __future__ import annotations

from dataclasses import dataclass

from .audio import generate_sine
from .config import TTSConfig


class BackendError(RuntimeError):
    """Raised when synthesis backend fails."""


class SynthesisBackend:
    def synthesize(self, text: str, cfg: TTSConfig) -> list[float]:
        raise NotImplementedError


@dataclass(slots=True)
class DummySineBackend(SynthesisBackend):
    def synthesize(self, text: str, cfg: TTSConfig) -> list[float]:
        words = max(1, len(text.split()))
        duration_s = min(12.0, 0.22 + words * 0.13)
        base_freq = 180.0 + (len(text) % 80)
        return generate_sine(duration_s=duration_s, sample_rate=cfg.sample_rate, freq=base_freq)


@dataclass(slots=True)
class CoquiBackend(SynthesisBackend):
    model_name: str

    def synthesize(self, text: str, cfg: TTSConfig) -> list[float]:
        try:
            from TTS.api import TTS  # type: ignore
        except Exception as exc:
            raise BackendError(
                "Coqui backend requested but package 'TTS' is unavailable. "
                "Install Coqui-TTS to use this backend."
            ) from exc

        tts = TTS(model_name=self.model_name, progress_bar=False).to(cfg.device)
        wav = tts.tts(text=text)
        if not isinstance(wav, list):
            wav = list(wav)
        return [float(v) for v in wav]


def build_backend(cfg: TTSConfig) -> SynthesisBackend:
    if cfg.model_name == "dummy-sine":
        return DummySineBackend()
    if cfg.model_name.startswith("coqui:"):
        return CoquiBackend(model_name=cfg.model_name.split(":", 1)[1])
    raise BackendError(
        f"Unsupported model_name '{cfg.model_name}'. Use 'dummy-sine' or 'coqui:<model-id>'."
    )
