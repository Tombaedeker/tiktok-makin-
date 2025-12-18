import glob
import json
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1920
BACKGROUND = (0, 0, 0)
FOREGROUND = (255, 255, 255)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SIZE = 84

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []

    for w in words:
        test = " ".join(current + [w])
        if draw.textlength(test, font=font) <= max_width:
            current.append(w)
        else:
            lines.append(" ".join(current))
            current = [w]

    if current:
        lines.append(" ".join(current))
    return lines

def render_slide(text, out_png):
    img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        font = ImageFont.load_default()

    max_width = int(WIDTH * 0.85)
    lines = wrap_text(draw, text, font, max_width)

    line_height = int(FONT_SIZE * 1.2)
    total_height = line_height * len(lines)
    y = (HEIGHT - total_height) // 2

    for line in lines:
        text_width = draw.textlength(line, font=font)
        x = (WIDTH - text_width) // 2
        draw.text((x, y), line, font=font, fill=FOREGROUND)
        y += line_height

    img.save(out_png)

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python render_video.py slides_dir out_videos_dir")

    slides_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    for path in sorted(glob.glob(os.path.join(slides_dir, "slides_*.json"))):
        base = os.path.splitext(os.path.basename(path))[0]
        vid = base.replace("slides_", "")
        work = os.path.join(out_dir, f"tmp_{vid}")
        os.makedirs(work, exist_ok=True)

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        inputs = []
        for i, slide in enumerate(data["slides"], start=1):
            png = os.path.join(work, f"{i:02d}.png")
            render_slide(slide["text"], png)
            inputs.append((png, int(slide["duration"])))

        cmd = ["ffmpeg", "-y"]
        for png, dur in inputs:
            cmd += ["-loop", "1", "-t", str(dur), "-i", png]

        n = len(inputs)
        filter_parts = []
        for i in range(n):
            filter_parts.append(f"[{i}:v]scale={WIDTH}:{HEIGHT},fps=30,format=yuv420p[v{i}]")
        concat_inputs = "".join([f"[v{i}]" for i in range(n)])
        filter_parts.append(f"{concat_inputs}concat=n={n}:v=1:a=0[v]")

        cmd += [
            "-filter_complex", ";".join(filter_parts),
            "-map", "[v]",
            "-t", "11",
            "-movflags", "+faststart",
            os.path.join(out_dir, f"tiktok_{vid}.mp4")
        ]

        subprocess.check_call(cmd)
        print(f"Rendered tiktok_{vid}.mp4")

if __name__ == "__main__":
    main()
