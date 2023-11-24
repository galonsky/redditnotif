from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class PostTime:
    def __init__(self, now: datetime):
        self.now = now

    @classmethod
    def as_of_now(cls, plus_hours: int) -> "PostTime":
        return cls((
                datetime.now(tz=ZoneInfo("America/New_York")) +
                timedelta(hours=plus_hours)
        ))

    def previous_day(self) -> "PostTime":
        return PostTime(self.now - timedelta(days=1))

    def __str__(self) -> str:
        return self.now.strftime("%m/%d/%Y")