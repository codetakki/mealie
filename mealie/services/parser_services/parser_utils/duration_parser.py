from datetime import datetime, timezone

import dateparser
import dateparser.search


class DurationParser:
    # Adapted from https://github.com/scrapinghub/dateparser/issues/213#issuecomment-1134750279

    _BASE = datetime(2024, 1, 20, 17, 0, 5, 55, tzinfo=timezone.utc)

    @classmethod
    def _get_duration_seconds_from_datetime(cls, dt: datetime) -> float:
        td = abs(dt - cls._BASE)
        return td.total_seconds()

    @classmethod
    def get_duration(cls, text: str) -> float | None:
        dt = dateparser.parse(
            text,
            settings={
                "RELATIVE_BASE": cls._BASE,
                "PARSERS": ["relative-time"],
                "TIMEZONE": "UTC",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
        )
        if not dt:
            return None

        return cls._get_duration_seconds_from_datetime(dt)

    @classmethod
    def get_all_durations(cls, text: str) -> list[float]:
        dts = dateparser.search.search_dates(
            text,
            settings={
                "RELATIVE_BASE": cls._BASE,
                "PARSERS": ["relative-time"],
                "TIMEZONE": "UTC",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
        )
        return [cls._get_duration_seconds_from_datetime(dt) for _, dt in dts] if dts else []
