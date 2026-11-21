#!/usr/bin/env python3
"""Распознаёт речь по словам (Whisper). Использование: transcribe.py video.mp4 words.json [lang] [model]
Если нет доступа к модели, передайте готовый words.json: [{"w":"слово","s":0.0,"e":0.4}, ...]"""
import json, sys
from faster_whisper import WhisperModel

src, dst = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else None
model = sys.argv[4] if len(sys.argv) > 4 else "small"
segs, info = WhisperModel(model, compute_type="int8").transcribe(src, language=lang, word_timestamps=True)
words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)}
         for s in segs for w in s.words]
json.dump(words, open(dst, "w"), ensure_ascii=False, indent=1)
print(f"язык={info.language}, слов={len(words)}")
