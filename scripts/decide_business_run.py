#!/usr/bin/env python3
"""
decide_business_run.py
Business-management kategorisi icin "bugun yeni yazi uretilsin mi" kararini verir.
Cron gunune guvenmek yerine (Temmuz 2026 kesintisinde ogrenilen ders: GitHub Actions
zamanlanmis tetikleyicileri gecikebiliyor/kayabiliyor), gercek "kac tane business
yazisi yayinlandi" sayisina bakiyor:
  - Ilk 7 yayinlanan yazi tamamlanana kadar HER GUN calis (ilk hafta gunluk faz).
  - 7'den sonra sadece Pazartesi/Persembe (haftada 2) calis.
Workflow_dispatch ile manuel calistirmada her zaman "true" doner (force).
"""
import json
import os
import sys
from datetime import datetime, timezone

PUBLISHED_FILE = "_data/published_posts.json"
DAILY_PHASE_LIMIT = 7
# UTC haftanin gunleri: Monday=0 ... Sunday=6
WEEKLY_PHASE_DAYS = {0, 3}  # Pazartesi, Persembe


def count_business_published():
    if not os.path.exists(PUBLISHED_FILE):
        return 0
    with open(PUBLISHED_FILE) as f:
        data = json.load(f)
    return sum(1 for p in data.get("published", []) if p.get("category") == "business-management")


def main():
    forced = os.environ.get("FORCE_RUN", "false").lower() == "true"
    count = count_business_published()
    weekday = datetime.now(timezone.utc).weekday()

    if forced:
        decision = True
        reason = "workflow_dispatch manual force"
    elif count < DAILY_PHASE_LIMIT:
        decision = True
        reason = f"daily phase ({count}/{DAILY_PHASE_LIMIT} business posts published so far)"
    else:
        decision = weekday in WEEKLY_PHASE_DAYS
        reason = f"weekly phase (published={count}, utc_weekday={weekday}, run_days={sorted(WEEKLY_PHASE_DAYS)})"

    print(f"Decision: {'RUN' if decision else 'SKIP'} -- {reason}")

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"should_run={'true' if decision else 'false'}\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
