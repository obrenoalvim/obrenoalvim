import json
import os
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
LEFT_PAD = 28
TOP_PAD = 34
LEGEND_H = 20
FOOTER_H = 26
MONTH_LABEL_H = 16

MONTHS_PT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def load():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def to_weeks(days):
    if not days:
        return []
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    lead_blanks = (first.weekday() + 1) % 7  # week starts Sunday
    weeks = []
    week = [None] * lead_blanks
    for day in days:
        dow = (datetime.strptime(day["date"], "%Y-%m-%d").weekday() + 1) % 7
        week.append(day)
        if dow == 6:
            weeks.append(week)
            week = []
    if week:
        week += [None] * (7 - len(week))
        weeks.append(week)
    return weeks


def month_labels(weeks):
    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        for day in week:
            if day is None:
                continue
            month = int(day["date"][5:7])
            if month != last_month:
                labels.append((wi, MONTHS_PT[month - 1]))
                last_month = month
            break
    return labels


def render(data):
    days = data["days"]
    stats = data["stats"]
    weeks = to_weeks(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * (CELL + GAP)
    height = TOP_PAD + 7 * (CELL + GAP) + LEGEND_H + FOOTER_H

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Consolas, Menlo, monospace">'
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="#0d1117" rx="6"/>')
    parts.append(
        """
        <style>
          .cell { opacity: 0; transform: translate(-6px,-6px); animation: reveal 0.35s ease-out forwards; }
          @keyframes reveal { to { opacity: 1; transform: translate(0,0); } }
          .month { fill: #8b949e; font-size: 10px; }
          .legend-label { fill: #8b949e; font-size: 10px; }
          .footer { fill: #c9d1d9; font-size: 11px; }
        </style>
        """
    )

    for wi, month in month_labels(weeks):
        x = LEFT_PAD + wi * (CELL + GAP)
        parts.append(f'<text class="month" x="{x}" y="{TOP_PAD - 10}">{month}</text>')

    delay_step = 0.006
    idx = 0
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if day is None:
                continue
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + di * (CELL + GAP)
            color = PALETTE[min(day["level"], len(PALETTE) - 1)]
            delay = (wi + di) * delay_step
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{day["date"]}: {day["level"]}</title></rect>'
            )
            idx += 1

    legend_y = TOP_PAD + 7 * (CELL + GAP) + 12
    lx = LEFT_PAD
    parts.append(f'<text class="legend-label" x="{lx}" y="{legend_y + 9}">Less</text>')
    lx += 32
    for level, color in enumerate(PALETTE[:5]):
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
        lx += CELL + GAP
    parts.append(f'<text class="legend-label" x="{lx + 4}" y="{legend_y + 9}">More</text>')

    contrib_count = sum(1 for d in days if d)
    active_days = sum(1 for d in days if d["level"] > 0)
    footer_y = legend_y + CELL + 20
    footer_text = (
        f'{active_days} active days in the last year · '
        f'current streak {stats["current_streak"]} · longest {stats["longest_streak"]}'
    )
    parts.append(f'<text class="footer" x="{LEFT_PAD}" y="{footer_y}">{footer_text}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    data = load()
    svg = render(data)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
