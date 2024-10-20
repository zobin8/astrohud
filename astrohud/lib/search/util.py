"""Utilities to search horoscopes"""

from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from astrohud.lib.ephemeris.models import EpheDate
from astrohud.lib.ephemeris.models import EpheSettings
from astrohud.lib.horoscope.models import Horoscope


def get_all_horoscopes(
    start_date: datetime,
    end_date: datetime,
    step: timedelta,
    settings: EpheSettings,
) -> List[Tuple[datetime, Horoscope]]:
    date = start_date
    out = []
    while date <= end_date:
        horo = Horoscope(EpheDate(date), settings)
        out.append((date, horo))
        date += step
    return out


def find_range(
    start_date: datetime,
    end_date: datetime,
    step: timedelta,
    filter: Dict[str, Any],
    settings: EpheSettings,
) -> List[Tuple[datetime, datetime, timedelta]]:
    all_horos = get_all_horoscopes(
        start_date=start_date,
        end_date=end_date,
        step=step,
        settings=settings,
    )

    match_ranges = []
    matched_last = False
    for date, horo in all_horos:
        matched = horo.match(filter)
        if matched:
            if matched_last:
                match_ranges[-1][1] = date
            else:
                match_ranges.append([date, date, step])

        matched_last = matched
        date += step
    return match_ranges


def find_datetime_range(
    start_date: datetime,
    end_date: datetime,
    day_filter: Dict[str, Any],
    time_filter: Dict[str, Any],
    settings: EpheSettings,
) -> List[Tuple[datetime, datetime, timedelta]]:
    day_ranges = find_range(
        start_date=start_date,
        end_date=end_date,
        step=timedelta(days=1),
        filter=day_filter,
        settings=settings,
    )

    day_filter.update(time_filter)

    time_ranges = []
    for day_range in day_ranges:
        time_ranges += find_range(
            start_date=day_range[0] - timedelta(days=1),
            end_date=day_range[1] + timedelta(days=1),
            step=timedelta(minutes=15),
            filter=day_filter,
            settings=settings
        )

    return time_ranges


def approx_filter(item: Any) -> Any:
    if isinstance(item, float):
        return 0.0
    elif isinstance(item, dict):
        out = '('
        for k in sorted(item.keys()):
            out += f'k={approx_filter(item[k])},'
        out += ')'
        return out
    return str(item)
