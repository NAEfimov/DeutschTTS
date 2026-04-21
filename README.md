# DeutschTTS

Local-first German text-to-speech pipeline that runs on your machine and can use CUDA when available.

## Features

- German text normalization (abbreviations, basic number expansion)
- Sentence splitting and chunked synthesis for long inputs
- Pluggable synthesis backend:
  - `dummy-sine` (default, dependency-free development backend)
  - `coqui:<model-id>` (optional Coqui TTS backend if installed)
- Audio chunk stitching with crossfade
- Post-processing (trim silence + normalize)
- WAV output + JSON metadata sidecar
- CLI for direct text or text-file input

## Requirements

- Python 3.10+
- Optional CUDA-capable GPU (used only when selected backend supports it)
- Optional Coqui TTS package for real voice generation

## Quickstart

```bash
python -m pip install -e .
```

Generate speech from direct text:

```bash
deutschtts --text "Hallo, dies ist ein Test." --output ./out.wav
```

Generate from file:

```bash
deutschtts --input-file ./input.txt --output ./out.wav
```

Use optional Coqui backend (requires manual install of Coqui-TTS and model assets):

```bash
deutschtts \
  --model "coqui:tts_models/de/thorsten/tacotron2-DDC" \
  --text "Guten Tag!" \
  --output ./coqui.wav
```

## Configuration

Runtime config defaults can be overridden with environment variables:

- `DEUTSCHTTS_MODEL`
- `DEUTSCHTTS_MODEL_PATH`
- `DEUTSCHTTS_DEVICE`
- `DEUTSCHTTS_SAMPLE_RATE`
- `DEUTSCHTTS_CHUNK_SIZE`
- `DEUTSCHTTS_MAX_CHARS`
- `DEUTSCHTTS_OUTPUT_FORMAT`

CLI flags override environment values.

## Development

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Troubleshooting

- **"Only WAV output is currently supported"**: output file must end in `.wav`.
- **Coqui backend unavailable**: install `TTS` package and required model dependencies.
- **CUDA not used**: set `--device cuda` (or `DEUTSCHTTS_DEVICE=cuda`) and ensure your backend supports GPU execution.
- **Input too long**: increase `--max-chars` or split text before synthesis.

## Architecture

- `src/deutschtts/text.py`: normalization and chunking
- `src/deutschtts/synthesizer.py`: backend abstraction and model adapters
- `src/deutschtts/audio.py`: stitching + post-processing + WAV writer
- `src/deutschtts/pipeline.py`: orchestration and metadata emission
- `src/deutschtts/cli.py`: command-line interface

## Status

This repository now provides a production-shaped MVP with a dependency-free backend for development and testability.
For high-quality natural voice output, configure a real local backend (for example Coqui model variants) and tune model/voice settings for your hardware.
