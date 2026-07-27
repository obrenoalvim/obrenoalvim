import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

WIDTH = 490
LINE_H = 22
PAD_X = 20
TITLE_H = 34

ROWS = [
    ("user", "obrenoalvim@github"),
    ("---", ""),
    ("Now", "Movida"),
    ("Stack", "TypeScript, Next.js, React, PHP, Laravel, Node.js, PostgreSQL, Docker"),
    ("Highlights", "zero-drift, findable, spoti-paper, linkedin-insights"),
]

ACCENT = "#39d353"
LABEL_COLOR = "#7ee787"
TEXT_COLOR = "#c9d1d9"
DIM = "#6e7681"


def wrap(text, max_chars):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def build_lines():
    lines = []
    for label, value in ROWS:
        if label == "---":
            lines.append(("rule", "", ""))
            continue
        if not value:
            lines.append(("line", label, ""))
            continue
        wrapped = wrap(value, 46)
        lines.append(("line", label, wrapped[0]))
        for extra in wrapped[1:]:
            lines.append(("line", "", extra))
    return lines


def render():
    lines = build_lines()
    height = TITLE_H + len(lines) * LINE_H + 24

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="Consolas, Menlo, monospace">',
        f'<rect width="{WIDTH}" height="{height}" fill="#0d1117" rx="6"/>',
        f'<rect width="{WIDTH}" height="{TITLE_H}" fill="#161b22" rx="6"/>',
        f'<rect y="{TITLE_H - 6}" width="{WIDTH}" height="6" fill="#161b22"/>',
        '<circle cx="18" cy="17" r="5" fill="#ff5f56"/>',
        '<circle cx="36" cy="17" r="5" fill="#ffbd2e"/>',
        '<circle cx="54" cy="17" r="5" fill="#27c93f"/>',
        f'<text x="{WIDTH/2}" y="21" text-anchor="middle" fill="{DIM}" font-size="12">neofetch</text>',
    ]

    if not STATIC:
        parts.append(
            "<style>"
            ".ln { opacity: 0; transform: translateX(-8px); animation: fadein 0.3s ease-out forwards; }"
            "@keyframes fadein { to { opacity: 1; transform: translateX(0); } }"
            "</style>"
        )

    y = TITLE_H + 22
    delay = 0.0
    for kind, label, value in lines:
        cls = "" if STATIC else ' class="ln"'
        style = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        if kind == "rule":
            parts.append(
                f'<line{cls}{style} x1="{PAD_X}" y1="{y - 14}" x2="{WIDTH - PAD_X}" y2="{y - 14}" '
                f'stroke="{DIM}" stroke-width="1"/>'
            )
        elif not value:
            parts.append(
                f'<text{cls}{style} x="{PAD_X}" y="{y}" fill="{ACCENT}" font-size="13" font-weight="bold">{label}</text>'
            )
        elif not label:
            parts.append(f'<text{cls}{style} x="{PAD_X + 92}" y="{y}" fill="{TEXT_COLOR}" font-size="13">{value}</text>')
        else:
            parts.append(f'<text{cls}{style} x="{PAD_X}" y="{y}" fill="{LABEL_COLOR}" font-size="13">{label}</text>')
            parts.append(f'<text{cls}{style} x="{PAD_X + 92}" y="{y}" fill="{TEXT_COLOR}" font-size="13">{value}</text>')
        y += LINE_H
        delay += 0.09

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    svg = render()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
