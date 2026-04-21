from __future__ import annotations

import re
from typing import Iterable

_ABBREVIATIONS = {
    "z.B.": "zum Beispiel",
    "u.a.": "unter anderem",
    "bzw.": "beziehungsweise",
    "d.h.": "das heißt",
    "Dr.": "Doktor",
    "Prof.": "Professor",
}

_NUMBER_MAP = {
    "0": "null",
    "1": "eins",
    "2": "zwei",
    "3": "drei",
    "4": "vier",
    "5": "fünf",
    "6": "sechs",
    "7": "sieben",
    "8": "acht",
    "9": "neun",
}


def normalize_text(text: str) -> str:
    compact = " ".join(text.replace("\n", " ").split())
    expanded = _expand_abbreviations(compact)
    expanded = _expand_simple_numbers(expanded)
    return expanded.strip()


def _expand_abbreviations(text: str) -> str:
    out = text
    for short, long in _ABBREVIATIONS.items():
        out = out.replace(short, long)
    return out


def _expand_simple_numbers(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        return " ".join(_NUMBER_MAP[ch] for ch in token)

    return re.sub(r"\b\d{1,4}\b", repl, text)


def sentence_split(text: str) -> list[str]:
    parts = re.split(r"(?<=[\.!\?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_sentences(sentences: Iterable[str], max_chars: int) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        if len(sentence) > max_chars:
            if current:
                chunks.append(" ".join(current))
                current = []
                current_len = 0
            chunks.extend(_force_split(sentence, max_chars))
            continue

        sep = 1 if current else 0
        projected = current_len + sep + len(sentence)
        if projected <= max_chars:
            current.append(sentence)
            current_len = projected
        else:
            chunks.append(" ".join(current))
            current = [sentence]
            current_len = len(sentence)

    if current:
        chunks.append(" ".join(current))
    return chunks


def _force_split(text: str, max_chars: int) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
                current = word
            else:
                chunks.append(word[:max_chars])
                current = word[max_chars:]
    if current:
        chunks.append(current)
    return chunks
