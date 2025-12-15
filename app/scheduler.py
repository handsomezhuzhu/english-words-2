from datetime import datetime, timedelta
import random
from typing import List

from sqlalchemy.orm import Session

from . import models

# Intervals in minutes: 5m, 30m, 12h, 1d, 2d, 4d, 7d, 15d
EBBINGHAUS_INTERVALS_MINUTES = [5, 30, 720, 1440, 2880, 5760, 10080, 21600]


def schedule_next(word: models.Word, grade: int):
    """
    grade: 0 (Don't know), 1 (Unclear), 2 (Know)
    """
    if grade == 2:
        word.interval_index = min(word.interval_index + 1, len(EBBINGHAUS_INTERVALS_MINUTES) - 1)
        word.success_streak += 1
    elif grade == 1:
        word.interval_index = max(0, word.interval_index - 1)
        word.success_streak = 0
    else:
        word.interval_index = 0
        word.success_streak = 0
    
    minutes = EBBINGHAUS_INTERVALS_MINUTES[word.interval_index]
    word.next_review_at = datetime.utcnow() + timedelta(minutes=minutes)
    word.last_reviewed_at = datetime.utcnow()


def get_due_words(db: Session, user_id: int) -> List[models.Word]:
    now = datetime.utcnow()
    return (
        db.query(models.Word)
        .filter(models.Word.owner_id == user_id, models.Word.next_review_at <= now)
        .order_by(models.Word.next_review_at.asc())
        .all()
    )


def pick_for_review(db: Session, user_id: int, count: int) -> List[models.Word]:
    due = get_due_words(db, user_id)
    if len(due) <= count:
        return due
    return random.sample(due, count)
