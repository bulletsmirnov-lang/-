#!/usr/bin/env python3
"""words.json -> ASS-субтитры (по 1-3 слова, подсветка текущего слова). subtitles.py words.json out.ass [brand.json]"""
import json, sys

def ass_color(hexc):
    h = hexc.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()

def ts(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

words = json.load(open(sys.argv[1]))
brand = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
cv, f, col, sub = brand.get("canvas", {}), brand.get("font", {}), brand.get("colors", {}), brand.get("subtitles", {})
W, H = cv.get("width", 1080), cv.get("height", 1920)
n = sub.get("words_per_chunk", 3)
mv = int(H * 0.30) if sub.get("position", "lower_third") == "lower_third" else int(H * 0.45)
base, hi = ass_color(col.get("text", "#FFFFFF")), ass_color(col.get("highlight", "#FF8A1F"))

out = [f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\n",
       "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
       f"Style: Default,{f.get('name','DejaVu Sans')},{f.get('size',78)},{base},{base},{ass_color(col.get('outline','#000000'))},&H80000000,{-1 if f.get('bold',True) else 0},0,0,0,100,100,0,0,1,{sub.get('outline',6)},0,2,60,60,{mv},1\n",
       "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text"]

for i in range(0, len(words), n):
    chunk = words[i:i + n]
    for j, w in enumerate(chunk):
        start = w["s"]
        end = chunk[j + 1]["s"] if j + 1 < len(chunk) else max(w["e"], start + 0.2)
        parts = []
        for k, x in enumerate(chunk):
            t = x["w"].upper() if sub.get("uppercase") else x["w"]
            parts.append(f"{{\\c{hi}}}{t}{{\\c{base}}}" if k == j and sub.get("karaoke_highlight", True) else t)
        out.append(f"Dialogue: 0,{ts(start)},{ts(end)},Default,,0,0,0,,{' '.join(parts)}")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"субтитры: {len(words)} слов")
