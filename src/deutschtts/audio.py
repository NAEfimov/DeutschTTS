from __future__ import annotations

import math
import struct
import wave
from pathlib import Path


def stitch_audio(chunks: list[list[float]], fade_ms: int, sample_rate: int) -> list[float]:
    if not chunks:
        return []
    if len(chunks) == 1 or fade_ms <= 0:
        return [sample for chunk in chunks for sample in chunk]

    fade_samples = max(1, int((fade_ms / 1000) * sample_rate))
    merged = chunks[0][:]

    for chunk in chunks[1:]:
        overlap = min(fade_samples, len(merged), len(chunk))
        if overlap == 0:
            merged.extend(chunk)
            continue

        start = len(merged) - overlap
        denom = max(1, overlap - 1)
        for i in range(overlap):
            t = i / denom
            merged[start + i] = merged[start + i] * (1 - t) + chunk[i] * t
        merged.extend(chunk[overlap:])

    return merged


def normalize(samples: list[float], target_peak: float = 0.95) -> list[float]:
    if not samples:
        return samples
    peak = max(abs(s) for s in samples)
    if peak <= 0:
        return samples
    gain = target_peak / peak
    return [max(-1.0, min(1.0, s * gain)) for s in samples]


def trim_silence(samples: list[float], threshold: float = 0.005) -> list[float]:
    if not samples:
        return samples
    left = 0
    right = len(samples) - 1

    while left < len(samples) and abs(samples[left]) < threshold:
        left += 1
    while right >= 0 and abs(samples[right]) < threshold:
        right -= 1

    if left > right:
        return []
    return samples[left : right + 1]


def write_wav(path: Path, samples: list[float], sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for sample in samples:
            clamped = max(-1.0, min(1.0, sample))
            frames.extend(struct.pack("<h", int(clamped * 32767)))
        wav_file.writeframes(bytes(frames))


def generate_sine(duration_s: float, sample_rate: int, freq: float = 220.0) -> list[float]:
    samples = int(duration_s * sample_rate)
    return [math.sin(2 * math.pi * freq * n / sample_rate) * 0.15 for n in range(samples)]
