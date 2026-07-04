"""
Period prediction service.
- Computes average cycle length from the last 3+ cycle entries
- Predicts next period date
- Determines current menstrual phase
- Returns phase-specific advisories
"""
from datetime import datetime, date, timedelta
from typing import List

from app.schemas.period import PeriodLogRequest, PeriodPredictionResponse, CycleEntry
from app.db.mongodb import get_period_logs_collection


PHASE_ADVISORIES = {
    "Menstrual": [
        "Rest and stay hydrated — your body is working hard.",
        "Gentle movement like yoga or walking can ease cramps.",
        "Iron-rich foods (spinach, lentils) help replenish blood loss.",
        "Use a heating pad for lower abdominal discomfort.",
    ],
    "Follicular": [
        "Energy levels are rising — great time to start new projects.",
        "Focus on strength training and high-intensity workouts.",
        "Eat plenty of fermented foods to support estrogen metabolism.",
        "Social and creative activities feel more natural this phase.",
    ],
    "Ovulatory": [
        "Peak energy and confidence — ideal for important meetings or events.",
        "Libido is naturally higher; this is your most fertile window.",
        "Stay hydrated and include anti-inflammatory foods.",
        "Great time for collaboration and communication.",
    ],
    "Luteal": [
        "Progesterone rises — you may feel calmer but more introspective.",
        "Magnesium-rich foods (dark chocolate, nuts) can ease PMS symptoms.",
        "Prioritise sleep and reduce caffeine and alcohol.",
        "Light exercise and journaling help manage mood shifts.",
    ],
}


def _parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _compute_avg_cycle(entries: List[CycleEntry]) -> float:
    starts = sorted([_parse_date(e.start_date) for e in entries])
    if len(starts) < 2:
        return 28.0  # default
    gaps = [(starts[i+1] - starts[i]).days for i in range(len(starts)-1)]
    return round(sum(gaps) / len(gaps), 1)


def _get_current_phase(last_start: date, avg_cycle: float) -> tuple[str, int]:
    today = date.today()
    day_of_cycle = (today - last_start).days % int(avg_cycle)

    if day_of_cycle <= 5:
        return "Menstrual", day_of_cycle
    elif day_of_cycle <= 13:
        return "Follicular", day_of_cycle
    elif day_of_cycle <= 16:
        return "Ovulatory", day_of_cycle
    else:
        return "Luteal", day_of_cycle


PHASE_DESCRIPTIONS = {
    "Menstrual":  "Your period phase (days 1–5). The uterine lining sheds.",
    "Follicular": "Post-period phase (days 6–13). Follicles mature and estrogen rises.",
    "Ovulatory":  "Ovulation phase (days 14–16). An egg is released — peak fertility.",
    "Luteal":     "Pre-period phase (days 17–28). Progesterone peaks; PMS may occur.",
}


async def predict_next_period(payload: PeriodLogRequest, user_id: str) -> PeriodPredictionResponse:
    entries = payload.cycle_entries
    avg_cycle = _compute_avg_cycle(entries)

    last_start = max(_parse_date(e.start_date) for e in entries)
    next_date  = last_start + timedelta(days=int(avg_cycle))

    ovulation_start = last_start + timedelta(days=int(avg_cycle) - 16)
    ovulation_end   = last_start + timedelta(days=int(avg_cycle) - 11)

    phase, day_num = _get_current_phase(last_start, avg_cycle)

    # Persist / update log
    col = get_period_logs_collection()
    doc = {
        "user_id": user_id,
        "cycle_entries": [e.dict() for e in entries],
        "avg_cycle_length": avg_cycle,
        "predicted_next_date": next_date.isoformat(),
        "updated_at": datetime.utcnow(),
    }
    await col.update_one({"user_id": user_id}, {"$set": doc}, upsert=True)

    return PeriodPredictionResponse(
        predicted_next_date=next_date.isoformat(),
        avg_cycle_length=avg_cycle,
        current_phase=phase,
        ovulation_window={
            "start": ovulation_start.isoformat(),
            "end":   ovulation_end.isoformat(),
        },
        advisories=PHASE_ADVISORIES[phase],
        phase_description=PHASE_DESCRIPTIONS[phase],
    )


async def get_period_log(user_id: str):
    col = get_period_logs_collection()
    log = await col.find_one({"user_id": user_id})
    if log:
        log["_id"] = str(log["_id"])
    return log or {}
