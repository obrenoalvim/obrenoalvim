import json
import os
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "obrenoalvim")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    days = []
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None or level is None:
            continue
        days.append({"date": date, "level": int(level)})
    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = 0
    current_streak = 0
    longest_streak = 0
    running_streak = 0
    best_day = {"date": None, "level": -1}
    monthly = {}

    for day in days:
        level = day["level"]
        if level > best_day["level"]:
            best_day = {"date": day["date"], "level": level}
        month_key = day["date"][:7]
        monthly[month_key] = monthly.get(month_key, 0) + (1 if level > 0 else 0)

        if level > 0:
            running_streak += 1
            longest_streak = max(longest_streak, running_streak)
        else:
            running_streak = 0

    for day in reversed(days):
        if day["level"] > 0:
            current_streak += 1
        else:
            break

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
    }


def main():
    days = fetch_days()
    if not days:
        print("no contribution cells found, page layout may have changed", file=sys.stderr)
        sys.exit(1)

    stats = compute_stats(days)
    payload = {
        "username": USERNAME,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"wrote {len(days)} days to {OUT_PATH}")


if __name__ == "__main__":
    main()
