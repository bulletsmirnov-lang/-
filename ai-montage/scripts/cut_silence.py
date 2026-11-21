#!/usr/bin/env python3
"""Вырезает паузы. Использование: cut_silence.py in.mp4 out.mp4 [brand.json]"""
import json, re, subprocess, sys

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def main():
    src, dst = sys.argv[1], sys.argv[2]
    brand = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
    c = {"silence_db": -32, "min_silence_sec": 0.35, "padding_sec": 0.08, **brand.get("cuts", {})}
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", src]).stdout.strip())
    r = run(["ffmpeg", "-hide_banner", "-i", src, "-af",
             f"silencedetect=noise={c['silence_db']}dB:d={c['min_silence_sec']}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    pad = c["padding_sec"]
    keep, pos = [], 0.0
    for i, s in enumerate(starts):
        if s - pos > 0.1:
            keep.append((pos, min(s + pad, dur)))
        pos = max(ends[i] - pad, 0) if i < len(ends) else dur
    if dur - pos > 0.1:
        keep.append((pos, dur))
    if not keep:
        keep = [(0, dur)]
    parts, labels = [], ""
    for i, (a, b) in enumerate(keep):
        parts.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[a{i}]")
        labels += f"[v{i}][a{i}]"
    fc = ";".join(parts) + f";{labels}concat=n={len(keep)}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "20", "-c:a", "aac", dst], check=True)
    out = sum(b - a for a, b in keep)
    print(f"cut: {dur:.1f}s -> {out:.1f}s ({len(keep)} фрагментов)")

main()
