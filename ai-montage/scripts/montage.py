#!/usr/bin/env python3
"""Полный монтаж: нарезка пауз -> речь -> субтитры -> 1080x1920 -> output/.
Использование: montage.py input/clip.mp4 [--words words.json] [--music track.mp3] [--lang uk] [--no-cut]"""
import argparse, json, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(D)
p = argparse.ArgumentParser()
p.add_argument("src"); p.add_argument("--words"); p.add_argument("--music")
p.add_argument("--lang"); p.add_argument("--no-cut", action="store_true"); p.add_argument("--no-subs", action="store_true")
a = p.parse_args()
brand_path = os.path.join(R, "brand.json"); brand = json.load(open(brand_path))
name = os.path.splitext(os.path.basename(a.src))[0]; W = os.path.join(R, "work")
cut, words, ass = f"{W}/{name}_cut.mp4", a.words or f"{W}/{name}_words.json", f"{W}/{name}.ass"
out = f"{R}/output/{name}_edit.mp4"
py = lambda s, *args: subprocess.run([sys.executable, f"{D}/{s}", *map(str, args)], check=True)

if a.no_cut: cut = a.src
else: py("cut_silence.py", a.src, cut, brand_path)
if not a.no_subs:
    if not a.words: py("transcribe.py", cut, words, *([a.lang] if a.lang else []))
    py("subtitles.py", words, ass, brand_path)

cv = brand["canvas"]; vf = (f"scale={cv['width']}:{cv['height']}:force_original_aspect_ratio=increase,"
                            f"crop={cv['width']}:{cv['height']},fps={cv['fps']}")
if not a.no_subs: vf += f",ass='{ass}'"
t = brand.get("title", {})
if t.get("text"):
    vf += (f",drawtext=text='{t['text']}':fontsize={t.get('size',96)}:fontcolor=white:borderw=6:"
           f"x=(w-text_w)/2:y=h*0.12:enable='lt(t,{t.get('duration_sec',3)})'")
cmd = ["ffmpeg", "-y", "-v", "error", "-i", cut]
af = "loudnorm=I=-16:TP=-1.5" if brand["audio"].get("loudnorm") else "anull"
if a.music:
    cmd += ["-stream_loop", "-1", "-i", a.music]
    fc = f"[0:v]{vf}[v];[0:a]{af}[v0];[1:a]volume={brand['audio']['music_volume']}[m];[v0][m]amix=inputs=2:duration=first[a]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]"]
else:
    cmd += ["-vf", vf, "-af", af]
cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out]
subprocess.run(cmd, check=True); print("готово:", out)
