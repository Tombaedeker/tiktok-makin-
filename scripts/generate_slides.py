import csv
import json
import os
import sys
from openai import OpenAI

MODEL = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

SYSTEM = """Du bist ein Video-Skript-Editor für TikTok.
Ziel: 11 Sekunden, 9:16 Text-Slides, extrem knapp, klare Aussage.
Gib ausschließlich JSON zurück im Format:
{"slides":[{"text":"...","duration":2},{"text":"...","duration":3},{"text":"...","duration":3},{"text":"...","duration":3}]}"""

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python generate_slides.py inputs.csv out_dir")

    inp, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    client = OpenAI()

    with open(inp, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        vid = row["id"].strip()
        content = row["content"].strip()

        user = f"""Erstelle aus folgendem Inhalt ein 11-Sekunden-TikTok-Video.
Regeln:
- 4 Slides mit Dauer [2,3,3,3]
- Maximal 8 Wörter pro Slide
- Keine Hashtags, keine Emojis, kein Zusatztext
- Nur verständlicher Slide-Text

INHALT:
{content}
"""

        resp = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user},
            ],
        )

        text = resp.output_text.strip()
        data = json.loads(text)

        out_path = os.path.join(out_dir, f"slides_{vid}.json")
        with open(out_path, "w", encoding="utf-8") as o:
            json.dump(data, o, ensure_ascii=False, indent=2)

        print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
