import calendar
import datetime
import math
import os
import re
import string
from typing import Union, List, Dict, Any, Optional, Tuple

# Removed numpy and pandas dependencies - using Python standard library instead
from dateutil.tz import tzlocal

# importing constants from gpstime.
from gtimes.gpstime import UTCFromGps, gpsFromUTC, secsInDay
from .exceptions import (
    FractionalYearError,
    DateRangeError,
    FormatError,
    ValidationError,
    validate_fractional_year,
)


# Core functions ---------------------------
def shifTime(String: str = "d0") -> dict:
    """
    Function to shift time.


    Examples:
        >>> shifTime("d0")

    Args:
        String: String to shift time. Default is "d0"

    Returns:
        dict: Shifted time

    """

    Unitdict = {
        "d": "days",
        "S": "seconds",
        "f": "microseconds",
        "m": "milliseconds",
        "M": "minutes",
        "H": "hours",
        "w": "weeks",
    }

    Shiftdict = {
        "days": 0.0,
        "seconds": 0.0,
        "microseconds": 0.0,
        "milliseconds": 0.0,
        "minutes": 0.0,
        "hours": 0.0,
        "weeks": 0.0,
    }

    if type(String) is not str:
        String = "d" + str(String)

    for i in String.split(":"):
        Shiftdict[Unitdict[i[0]]] = float(i[1:])

    return Shiftdict


def dTimetoYearf(dtime: datetime.datetime) -> float:
    """Convert datetime object to fractional year representation.

    Converts a datetime object to fractional year format commonly used in
    GAMIT time series analysis and geodetic applications.

    Args:
        dtime: Datetime object to convert

    Returns:
        float: Fractional year (e.g., 2008.245 for March 29, 2008)

    Example:
        >>> import datetime
        >>> dt = datetime.datetime(2008, 3, 29, 12, 15, 0)
        >>> yearf = dTimetoYearf(dt)
        >>> print(f"Fractional year: {yearf:.6f}")
        Fractional year: 2008.245205
    """
    return TimetoYearf(*dtime.timetuple()[0:6])


def TimetoYearf(year: int, month: int, day: int, hour=12, minute=0, sec=0) -> float:
    """Convert date and time components to fractional year representation.

    Converts individual date and time components to fractional year format
    commonly used in GAMIT time series analysis and geodetic applications.

    Args:
        year: Year (4 digits, e.g., 2008)
        month: Month (1-12)
        day: Day of month (1-31)
        hour: Hour (0-23, default: 12 for noon)
        minute: Minute (0-59, default: 0)
        sec: Second (0-59, can include fractional seconds, default: 0)

    Returns:
        float: Fractional year representation

    Example:
        >>> yearf = TimetoYearf(2008, 3, 29, hour=12, minute=15, sec=0)
        >>> print(f"Fractional year: {yearf:.6f}")
        Fractional year: 2008.245763

        >>> # Beginning of year
        >>> yearf_start = TimetoYearf(2020, 1, 1, hour=0, minute=0, sec=0)
        >>> print(f"Year start: {yearf_start:.6f}")
        Year start: 2020.000000
    """
    doy = DayofYear(0, year, month, day) - 1
    secofyear = doy * secsInDay + (hour * 60 + minute) * 60 + sec

    daysinyear = DaysinYear(year)
    secinyear = daysinyear * secsInDay

    yearf = year + secofyear / float(secinyear)

    return yearf


def TimefromYearf(
    yearf: float, String: Optional[str] = None, rhour: bool = False
) -> Union[datetime.datetime, str, float]:
    """Convert fractional year to datetime object or formatted string.

    Converts fractional year representation (commonly used in GAMIT time series)
    back to datetime object or formatted string. Inverse operation of dTimetoYearf().

    Args:
        yearf: Fractional year (e.g., 2023.97 for late December 2023)
        String: Output format string. Options:
            - None: Return datetime object (default)
            - "ordinalf": Return ordinal day as float
            - Standard strftime format (e.g., "%Y-%m-%d %H:%M:%S")
        rhour: If True, round result to nearest hour (default: False)

    Returns:
        If String is None:
            datetime.datetime: Datetime object
        If String is "ordinalf":
            float: Ordinal day representation
        Otherwise:
            str: Formatted date/time string

    Example:
        >>> # Convert to datetime
        >>> dt = TimefromYearf(2023.97)
        >>> print(dt)
        2023-12-20 20:48:00

        >>> # Convert to formatted string
        >>> date_str = TimefromYearf(2023.97, String="%Y-%m-%d")
        >>> print(date_str)
        2023-12-20

        >>> # Round to nearest hour
        >>> dt_rounded = TimefromYearf(2023.97, rhour=True)
        >>> print(dt_rounded)
        2023-12-20 21:00:00
    """
    # Validate input
    try:
        yearf = validate_fractional_year(yearf)
    except ValidationError as e:
        raise FractionalYearError(f"Invalid fractional year: {e}") from e

    # to integer year
    year = int(math.floor(yearf))

    # converting to doy, hour, min, sec, microsec
    daysinyear = DaysinYear(year)
    dayf = (yearf - year) * daysinyear + 1
    doy = int(math.floor(dayf))  # day of year)
    fofday = dayf - doy
    Hour = int(math.floor((fofday) * 24))  # hour of day
    Min = int(math.floor((fofday) * 24 * 60 % 60))  # minute of hour
    fsec = fofday * 24 * 60 * 60 % 60
    Sec = int(math.floor(fsec))  # second of minute
    musec = int(math.floor((fsec - Sec) * 1000000))  # microsecond 0 - 1000000

    timestr = "%d %.3d %.2d:%.2d:%.2d %s" % (year, doy, Hour, Min, Sec, musec)
    # Create datetime object from timestr
    dt = datetime.datetime.strptime(timestr, "%Y %j %H:%M:%S %f")
    if rhour:
        dt = round_to_hour(dt)

    if String:
        if String == "ordinalf":  # return a floating point ordinal day
            return dt.toordinal() + fofday
        else:
            return dt.strftime(String)
    else:  # just return the datetime instanse
        return dt


def currDatetime(
    days: Union[int, float, str] = 0,
    refday: Union[datetime.datetime, str] = datetime.datetime.today(),
    String: Optional[str] = None,
) -> Union[datetime.datetime, str]:
    """
    Function that returns a datetime object for the date, "days" from refday.

    Examples:
        >>> currDatetime(days=5, refday=datetime.datetime.today(), String=None)

    Args:
        days: integer, Defaults to 0
              days to offset
        refday: datetime object or a string, defaults to datetime.datetime.today()
              reference day
        string: formatting string. defaults to None (inferring refday as datetime object)
              If refday is a date string, this has to contain its formatting (i.e %Y-%m-%d %H:%M)

    Returns:
        A datetime object. Defaults to current day if ran without arguments
    """

    day = refday + datetime.timedelta(**shifTime(days))
    if String:
        return day.strftime(String)
    else:
        return day


def currDate(
    days: Union[int, float, str] = 0,
    refday: Union[datetime.date, float] = datetime.date.today(),
    String: Optional[str] = None,
    fromYearf: bool = False,
) -> Union[datetime.date, str]:
    """
    Function that returns a datetime object for the date, "days" from refday.

    Examples:
        >>> currDate()

    Args:
        days: int. Number of days
        refday: date object
        String:
        fromYearf: bool, if true, the reference date is in yearf format.

    Returns:
        date object. Defaults to current day


    """

    if fromYearf and type(refday) == float or type(refday) == int:
        refday = TimefromYearf(refday)

    day = refday + datetime.timedelta(**shifTime(days))
    if String == "yearf":
        return TimetoYearf(*day.timetuple()[0:3])
    elif String:
        return day.strftime(String)
    else:
        return day


def gpsfDateTime(
    days=0, refday=currDatetime(), fromYearf=False, mday=False, leapSecs=None, gpst=True
):
    """
    Function that returns GPS time tuple (GPSWeek, SOW, DOW, SOD)
                            (GPS week, Second of week, Day of week 0...6, Second of day))

    Examples:
        >>> gpsfDateTime()

    Args:
        days: Int
        refday: Datetime
        fromYearf: Boolean
        mday: Boolean
        leapSecs:
        gpst: Boolean

    Returns:
        gps time tuple (GPSWeek, Second of Week, Day of Week, Second of Day)
    """

    if fromYearf:
        refday = TimefromYearf(
            refday,
        )

    refdayt = refday + datetime.timedelta(**shifTime(days))
    tmp = refdayt.timetuple()[0:6]

    if mday:
        return gpsFromUTC(
            *tmp[0:3], hour=12, min=0, sec=0, leapSecs=leapSecs, gpst=gpst
        )
    else:
        return gpsFromUTC(*tmp, leapSecs=leapSecs, gpst=gpst)


def gpsWeekDay(days=0, refday=currDate(), fromYearf=False):
    """
    Convenience function to convert date into gpsWeekDay

    Examples:
        >>> gpsWeekDay()

    Args:
        days:
        refday:
            fromYearf

    Returns:
        Tuple gps Week and day of Week
    """
    return gpsfDateTime(days=0, refday=refday, fromYearf=False, mday=False)[0:3:2]


def _parse_frequency_to_timedelta(lfrequency: str) -> datetime.timedelta:
    """Parse frequency string to timedelta object.

    Converts pandas/gtimes-style frequency strings to Python timedelta objects.
    Supports hour-based and day-based frequencies.

    Args:
        lfrequency: Frequency string like "1H", "H", "1D", "D", "3H", "24H", etc.

    Returns:
        datetime.timedelta object representing the frequency

    Raises:
        ValueError: If frequency format is not recognized

    Examples:
        >>> _parse_frequency_to_timedelta("H")
        datetime.timedelta(hours=1)
        >>> _parse_frequency_to_timedelta("1H")
        datetime.timedelta(hours=1)
        >>> _parse_frequency_to_timedelta("3H")
        datetime.timedelta(hours=3)
        >>> _parse_frequency_to_timedelta("D")
        datetime.timedelta(days=1)
        >>> _parse_frequency_to_timedelta("1D")
        datetime.timedelta(days=1)
    """
    if not lfrequency:
        # Default to daily if not specified
        return datetime.timedelta(days=1)

    # Extract number and unit
    # Format: [number]unit where unit is H, D, etc.
    match = re.match(r'^(\d+)?([A-Za-z]+)$', lfrequency)
    if not match:
        raise ValueError(f"Invalid frequency format: {lfrequency}")

    number_str, unit = match.groups()
    number = int(number_str) if number_str else 1

    # Map unit to timedelta parameter
    unit_upper = unit.upper()
    if unit_upper in ('H', 'HOUR', 'HOURS'):
        return datetime.timedelta(hours=number)
    elif unit_upper in ('D', 'DAY', 'DAYS'):
        return datetime.timedelta(days=number)
    elif unit_upper in ('W', 'WEEK', 'WEEKS'):
        return datetime.timedelta(weeks=number)
    elif unit_upper in ('M', 'MIN', 'MINUTE', 'MINUTES'):
        return datetime.timedelta(minutes=number)
    elif unit_upper in ('S', 'SEC', 'SECOND', 'SECONDS'):
        return datetime.timedelta(seconds=number)
    else:
        raise ValueError(f"Unsupported frequency unit: {unit}")


def datepathlist(
    stringformat, lfrequency, starttime=None, endtime=None, datelist=[], closed="left"
):
    """Generate list of formatted date/time strings for GPS data processing.

    Creates a list of strings formatted according to stringformat with specified
    frequency. Commonly used for generating RINEX filenames, data paths, and
    processing sequences in GPS analysis workflows.

    Args:
        stringformat: Format string for output. Supports standard strftime codes
            plus GPS-specific extensions:
            - Standard: %Y (year), %m (month), %d (day), %j (day of year), etc.
            - GPS extensions:
                - #gpsw: GPS week number
                - #b: Lowercase month name (jan, feb, etc.)
                - #Rin2: RINEX 2 format (%j + session).%y (e.g., "2740.15")
                - #8hRin2: 8-hour RINEX format with session letters
                - #hourl: Hour of day as letter (0→a, 1→b, ..., 23→x)
        lfrequency: Time frequency/interval:
            - "1D": Daily intervals
            - "1H": Hourly intervals
            - "8H": 8-hour intervals (for RINEX sessions)
            - pandas frequency strings supported
        starttime: Start datetime (default: current time)
        endtime: End datetime (default: same as starttime for single entry)
        datelist: Explicit list of datetime objects to format
        closed: Interval closure ("left" or "right", default: "left")

    Returns:
        list[str]: List of formatted strings

    Example:
        >>> # Generate daily RINEX filenames for a week
        >>> import datetime
        >>> start = datetime.datetime(2015, 10, 1)
        >>> filenames = datepathlist(
        ...     stringformat="VONC%j0.%yO",
        ...     lfrequency="1D",
        ...     starttime=start,
        ...     periods=7
        ... )
        >>> print(filenames[0])
        VONC2740.15O

        >>> # Complex path with GPS-specific formatting
        >>> paths = datepathlist(
        ...     stringformat="/data/%Y/#b/VONC/VONC#Rin2D.Z",
        ...     lfrequency="1D",
        ...     starttime=datetime.datetime(2015, 10, 1)
        ... )
        >>> print(paths[0])
        /data/2015/oct/VONC/VONC2740.15D.Z

    Note:
        This function is essential for GPS data processing workflows at
        Veðurstofan Íslands, particularly for RINEX file management and
        automated processing sequences.
                           #8hRin2 -> special case of 8h rinex files will overite lfrequency
                           by padding session parameter to {1, 2, 3}
                           #datelist -> returns a list of datetimeobjects instead of a string


        lfrequency: A string defining the frequency of the datetime list created. uses
                    pandas.date_range to create the list (See pandas date_range function
                    for parameters but most common converion letters are
                    frequency letters, H -> hour, D -> day  A -> year
                    (and Y for newer versions of pandas)
                    precead  with a number to specify number of units.
                    examples. 3H -> 3 hours, 4D -> 4 days, 2A -> 2 years
                    The session parameter in stringformat are treated
                    differently depending lfrequency,
                                  lfrequency >= day -> session = 0
                                  lfrequency < day  -> session = {a,b,c ... x}
                                  lfrequency = 8H   -> session = {a, i, q}

        starttime:  datetime object reprecenting the start of the period
                    defaults to None, is set to datetime.datetime.utcnow()
                    if datelist is empty

        endtime:    datetime object reprecenting the end of the period
                    defaults to None , is set to datetime.datetime.utcnow()
                    if datelist is empty

        datelist:   Optional list of datetime object can be passed then
                    starttime and endtime are ignored.

        closed:     Controls how interval endpoints are treated with given frequency
                    "left", "right" or None
                    Defaults to "left"

    Returns:
        Returns list of strings with time codes formated according to input String.

    """

    today = datetime.datetime.now(datetime.timezone.utc)

    # special home made formatting
    gpswmatch = re.compile(r"\w*(#gpsw)\w*").search(stringformat)  # use GPS week
    wrepl = ""
    rmatch = re.compile(r"\w*(#Rin2)\w*").search(
        stringformat
    )  # use GPS standard name RINEX2 name
    rrepl = ""
    # #Rin3 - RINEX 3 long naming format: SSSS00CCC_R_YYYYDDDHHMM_PPU_FFS_TT
    # Parameters can be passed as #Rin3 or #Rin3{options}
    # Options: country=XXX, period=PPU, freq=FFS, type=TT, source=R/S/U
    r3match = re.compile(r"#Rin3(\{[^}]*\})?").search(stringformat)
    r3repl = ""
    r8hmatch = re.compile(r"\w*(#8hRin)\w*").search(
        stringformat
    )  # use GPS standard name RINEX2 name
    r8hrepl = ""
    bbbmatch = re.compile(r"\w*(#b)\w*").search(
        stringformat
    )  # use all lower case for 3 letter month
    bbbrepl = ""

    hmatch = re.compile(r"\w*(#hourl)\w*").search(
        stringformat
    )  # #hourl: Convert hours of day (0,1,2...23) to letters (a,b,c...x)
    # Used for non-standard GNSS receiver filename formats like Leica
    hrepl = ""

    datelistmatch = re.compile(r"\w*(#datelist)\w*").search(
        stringformat
    )  # Return a list of datetime objects

    # -----------

    if (endtime is None) and not datelist:
        endtime = today
    elif (starttime is None) and not datelist:
        starttime = endtime = today
        datelist = [today]

    if datelist:
        pass
    elif lfrequency == "8H" or r8hmatch:
        mod = endtime - datetime.datetime.combine(endtime.date(), datetime.time(0))

        if mod > datetime.timedelta(16):
            mod += datetime.timedelta(16)
        elif mod > datetime.timedelta(8):
            mod += datetime.timedelta(8)

        if today - starttime > datetime.timedelta(hours=8):
            # Simple date range generation using standard library
            current = starttime - mod
            end_time = endtime - mod
            # For 8H sessions, generate daily intervals (3 sessions per day: 0-8, 8-16, 16-24)
            delta = datetime.timedelta(days=1)
            datelist = []

            if closed == "left":
                while current < end_time:
                    datelist.append(current)
                    current += delta
            elif closed == "right":
                current += delta
                while current <= end_time:
                    datelist.append(current)
                    current += delta
            else:  # both or None
                while current <= end_time:
                    datelist.append(current)
                    current += delta
        else:
            datelist = [today - mod]

    else:
        # Parse lfrequency to get correct time delta
        # Supports formats like: "1H", "H", "1D", "D", "3H", "24H", etc.
        delta = _parse_frequency_to_timedelta(lfrequency)

        hourshift = datetime.timedelta(hours=0)
        # Simple date range generation using standard library
        current = starttime
        end_time = endtime - hourshift
        datelist = []

        while current <= end_time:
            datelist.append(current)
            current += delta
        if not datelist:
            datelist = [endtime]

    if datelistmatch:
        return datelist

    stringlist = []
    for item in datelist:
        if rmatch or r8hmatch:  # form H or 8H rinex formatting
            if rmatch:  # for rinex formatting
                if lfrequency[-1] == "H":
                    hour = hourABC(item.hour)
                else:
                    hour = 0
            else:  # the specal case of 8H files
                hour = hour8hABC(item.hour)

            doy = int(item.strftime("%j"))
            yr = int(item.strftime("%y"))
            rrepl = "%.3d%s.%.2d" % (doy, hour, yr)

        if r3match:  # #Rin3 - RINEX 3 long naming format
            # Parse optional parameters from #Rin3{param=value,...}
            r3_opts = {"country": "ISL", "period": None, "freq": "15S", "type": "MO", "source": "R", "monument": "00"}
            if r3match.group(1):
                opts_str = r3match.group(1)[1:-1]  # Remove { and }
                for opt in opts_str.split(","):
                    if "=" in opt:
                        k, v = opt.split("=", 1)
                        r3_opts[k.strip()] = v.strip()

            # Determine file period from frequency if not specified
            if r3_opts["period"] is None:
                if lfrequency[-1] == "H":
                    r3_opts["period"] = "01H"
                else:
                    r3_opts["period"] = "01D"

            # Build RINEX 3 naming components
            doy = int(item.strftime("%j"))
            year = item.year
            hour = item.hour
            minute = item.minute

            # Format: YYYYDDDHHMM_PPU_FFS_TT
            r3repl = (
                f"{year:04d}{doy:03d}{hour:02d}{minute:02d}_"
                f"{r3_opts['period']}_"
                f"{r3_opts['freq']}_"
                f"{r3_opts['type']}"
            )

        if gpswmatch:  # for GPS week
            wrepl = "{0:04d}".format(gpsWeekDay(refday=item)[0])

        if hmatch:  # #hourl: Convert hour to letter (0→a, 1→b, ..., 23→x)
            hrepl = hourABC(item.hour)

        if bbbmatch:  # for lower case three letter month name Jan -> jan ...
            bbbrepl = "{:%b}".format(item).lower()

        # replacing special formatting strings with the values
        pformat = re.sub("#gpsw", wrepl, stringformat)
        pformat = re.sub("#8hRin2", rrepl, pformat)
        pformat = re.sub("#Rin2", rrepl, pformat)
        # Handle #Rin3 with optional parameters
        pformat = re.sub(r"#Rin3(\{[^}]*\})?", r3repl, pformat)
        pformat = re.sub("#hourl", hrepl, pformat)
        pformat = re.sub("#b", bbbrepl, pformat)
        pformat = item.strftime(pformat)
        stringlist.append(pformat)

    return stringlist


def previous_complete_period(
    period: Union[str, datetime.timedelta],
    now: Optional[datetime.datetime] = None,
) -> datetime.datetime:
    """Return the start of the most recently completed period (UTC).

    Used as the exclusive upper bound for "give me the last N periods of
    complete data" queries, so the currently-being-written period isn't
    pulled mid-file.

    - period = 1 day → start of today (00:00:00 UTC); last complete day is yesterday.
    - period = 1 hour → start of current hour; last complete hour is the one before.
    - Any other timedelta returns ``now`` truncated to a multiple of ``period``
      counted from midnight UTC of the reference day.

    Args:
        period: Period as a timedelta or a frequency string ("1H", "1D", ...).
        now: Reference time (UTC). Defaults to ``datetime.now(timezone.utc)``.

    Returns:
        Aligned datetime marking the start of the most recent complete period.

    Examples:
        >>> ref = datetime.datetime(2026, 4, 17, 22, 41, tzinfo=datetime.timezone.utc)
        >>> previous_complete_period("1H", now=ref).hour
        22
        >>> previous_complete_period("1D", now=ref).hour
        0
    """
    if isinstance(period, str):
        delta = _parse_frequency_to_timedelta(period)
    else:
        delta = period

    ref = now if now is not None else datetime.datetime.now(datetime.timezone.utc)

    # Day-aligned period
    if delta >= datetime.timedelta(days=1):
        return ref.replace(hour=0, minute=0, second=0, microsecond=0)

    # Sub-day: truncate to a multiple of delta counted from midnight
    midnight = ref.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed = ref - midnight
    whole_periods = int(elapsed.total_seconds() // delta.total_seconds())
    return midnight + delta * whole_periods


def generate_time_range(
    period: Union[str, datetime.timedelta],
    lookback_periods: int,
    now: Optional[datetime.datetime] = None,
) -> Tuple[datetime.datetime, datetime.datetime]:
    """Compute ``(start, end)`` covering the last ``lookback_periods`` complete periods.

    The ``end`` is the start of the most recently completed period (from
    :func:`previous_complete_period`) and is exclusive — the currently-being-
    written period is deliberately not included, so callers don't pull
    mid-file data.

    Args:
        period: Period as a timedelta or frequency string ("1H", "1D", ...).
        lookback_periods: Number of complete periods to include.
        now: Reference time (UTC). Defaults to current UTC time.

    Returns:
        ``(start, end)`` — ``end`` is exclusive.

    Examples:
        >>> ref = datetime.datetime(2026, 4, 17, 22, 41, tzinfo=datetime.timezone.utc)
        >>> start, end = generate_time_range("1H", 24, now=ref)
        >>> end.hour, start.day
        (22, 16)
    """
    if isinstance(period, str):
        delta = _parse_frequency_to_timedelta(period)
    else:
        delta = period
    end = previous_complete_period(delta, now=now)
    start = end - delta * lookback_periods
    return start, end


def generate_datetime_list(
    start: datetime.datetime,
    end: datetime.datetime,
    period: Union[str, datetime.timedelta],
    reverse: bool = False,
) -> List[datetime.datetime]:
    """Generate a list of datetimes at ``period`` intervals in ``[start, end)``.

    Args:
        start: Inclusive start.
        end: Exclusive end.
        period: Step between datetimes (timedelta or frequency string).
        reverse: If True, return newest-first order.

    Returns:
        List of datetimes; empty if ``start >= end``.

    Examples:
        >>> a = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        >>> b = datetime.datetime(2026, 1, 4, tzinfo=datetime.timezone.utc)
        >>> [d.day for d in generate_datetime_list(a, b, "1D")]
        [1, 2, 3]
    """
    if isinstance(period, str):
        delta = _parse_frequency_to_timedelta(period)
    else:
        delta = period

    out: List[datetime.datetime] = []
    current = start
    while current < end:
        out.append(current)
        current += delta
    if reverse:
        out.reverse()
    return out


def generate_period_ranges(
    start: datetime.datetime,
    end: datetime.datetime,
    period: Union[str, datetime.timedelta],
    reverse: bool = False,
) -> List[Tuple[datetime.datetime, datetime.datetime]]:
    """Generate ``(period_start, period_end)`` tuples covering ``[start, end)``.

    The final tuple's end is clamped to ``end`` if the last period would
    otherwise overrun it.

    Args:
        start: Inclusive start.
        end: Exclusive end.
        period: Length of each sub-range (timedelta or frequency string).
        reverse: If True, return newest-first order.

    Returns:
        List of ``(period_start, period_end)`` tuples.

    Examples:
        >>> a = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        >>> b = datetime.datetime(2026, 1, 4, tzinfo=datetime.timezone.utc)
        >>> [(s.day, e.day) for s, e in generate_period_ranges(a, b, "1D")]
        [(1, 2), (2, 3), (3, 4)]
    """
    if isinstance(period, str):
        delta = _parse_frequency_to_timedelta(period)
    else:
        delta = period

    out: List[Tuple[datetime.datetime, datetime.datetime]] = []
    current = start
    while current < end:
        period_end = min(current + delta, end)
        out.append((current, period_end))
        current += delta
    if reverse:
        out.reverse()
    return out


############################################
# derived functions


def currTime(String):
    """
    Function that returns the current local time in a format determined by String

    Examples:
        >>>currTime("%Y %j %H:%M:%S %f")

    Args:
        String: A String determinaning the output format of the current time
                formated according to format codes that the C standard (1989 version) requires,
                see documentation for datetime module. Example
                Example,  String = "%Y %j %H:%M:%S %f" -> '2013 060 16:03:54 970424'
                See datetime documentation for details

    Returns:
                Returns the current time formated according to input String.

    """

    return datetime.datetime.now(tzlocal()).strftime(String)


def DayofYear(days=0, year=None, month=None, day=None):
    """
    Returns the day of year, "days" (defaults to 0) relative to the date given
    i.e. (year,month,day) (defaults to today)
    No argument returns the day of today

    Examples:
        >>> DayofYear(days=0, year=None, month=None, day=None)

    Args:
        days: Day relative to (year,month,day) or today if (year,month,day) not given
        year: Four digit year "yyyy". Example 2013
        month: Month in integer from 1-12
        day: Day of month as integer 1-(28-31) depending on month

    Returns:
        doy: Integer containing day of year. Exampls (2013,1,3) -> 60
                spans 1 -365(366 if leap year)
    """

    # if type(days) is int:
    #    tmp = {'days':days}
    #    days = tmp

    if year and month and day:
        nday = datetime.date(year, month, day) + datetime.timedelta(**shifTime(days))
        doy = nday.timetuple()[7]
    else:
        nday = datetime.date.today() + datetime.timedelta(**shifTime(days))
        doy = nday.timetuple()[7]

    return doy


def DaysinYear(year=None):
    """
    Returns the last day of year 365 or 366, (defaults to current year)

    Args:
        year: Integer or floating point year (defaults to current year)

    Returns:
        daysinyear: Returns and integer value, the last day of the year  365 or 366
    """

    if year == None:  # defaults to current year
        year = datetime.date.today().year

    year = int(math.floor(year))  # allow for floating point year
    daysinyear = (
        366 if calendar.isleap(year) else 365
    )  # checking if it is leap year and assigning the correct day number

    return daysinyear


def yearDoy(yearf):
    """
    Simple wrapper that calls TimefromYearf, to return a date in the form "year-doyT" from fractional year.
    convenient for fancy time labels in GMT hence the T.

    Args:
        yearf: float

    Returns:
        year-doyT
    """
    return TimefromYearf(
        yearf,
        "%Y-%jT",
    )


def currYearfDate(days=0, refday=datetime.date.today(), fromYearf=True):
    """
    Wrapper for currDate() to return the date, "days" from "refday"
    in decimal year, defaults to current day
    """

    return currDate(days=days, refday=refday, String="yearf", fromYearf=fromYearf)


def currYear():
    """
    Function to calculate Current year in YYYY
    """
    return datetime.date.today().year


def shlyear(yyyy=currYear(), change=True):
    """
    Function that changes a year from two digit format to four and vice versa.

    Args:
        YYYY: Year in YYYY or YY (defaults to current year)
        change: True of False convinies in case we want to pass YYYY unchanged through the function

    Returns:
        Year converted from two->four or four->two digit form.
        returns current year in two digit form in the apsence of input
    """
    if len(str(abs(yyyy))) == 4 and change is True:
        yyyy = datetime.datetime.strptime(str(yyyy), "%Y")
        return yyyy.strftime("%y")
    elif len(str(abs(yyyy))) <= 2 and change is True:
        yyyy = datetime.datetime.strptime("%02d" % yyyy, "%y")
        return yyyy.strftime("%Y")
    elif change is False:
        return yyyy


def dateTuple(days=0, refday=datetime.datetime.today(), String=None, fromYearf=False):
    """
    Function that calculates a tuple with different elements of a given date.
    Examples:
        >>>dateTuple()

    Args:
        days:
        refday:
        String:
        fromYearf:

    Returns:
        Tuple of different elements of a given date (year, month, day of month, day of year, fractional year, gps week, gps day of week)


    """

    # (Week,dow) = gpsWeekDay(days,refday,fromYearf)
    day = currDatetime(days, refday, String=String)
    month = day.strftime("%b")
    day = day.timetuple()
    return (
        day[0:3]
        + day[7:8]
        + (currYearfDate(days, refday),)
        + gpsWeekDay(days, refday, fromYearf)
        + (int(str(day[0])[-1]),)
        + (int(shlyear(day[0])),)
        + (month,)
    )


def hourABC(Hour=datetime.datetime.now().hour):
    """
    Function that calculates the hour as an alphabetica letter i.e. 00 -> a, 01 -> b ... 23 -> x

    Examples:
        >>> hourABC()

    Args:
        Hour: datetime hour object

    Returns:
        alphabetical letter representing the hour of the Args in the form of dictionary


    """

    hourdict = dict(enumerate(string.ascii_lowercase, 0))

    return hourdict[Hour]


def ABChour(HourA):
    """
    Function that returns the inverse of hourABC and hour8hABC

    Examples:
        >>>ABChour(HourA=2)

    Args:
        HourA:

    Returns:
        key of the hourdict for HourA (Args)

    """

    hourdict = dict(enumerate(string.ascii_lowercase, 0))
    if HourA == "0":
        return 0
    if HourA == "1":
        return 8
    if HourA == "2":
        return 16

    for key, value in hourdict.items():
        if value == HourA.lower():
            return key

    return ""


def hour8hABC(Hour=0):
    """
    Function that returns hour 0, 8 and 16 as 0, 1 and 2
    IMO special case for 8hr rinex sessions.

    Examples:
        >>>hour8hABC(Hour=8)
        1

    Args:
        Hour: 0, 8 or 16

    Returns:
        Value equivalent to the Args. If 0, 0; if 8, 1; and if 16, 2.

    """

    hourdict = {
        0: 0,
        8: 1,
        16: 2,
    }

    return hourdict[Hour]


# Vectorization functions for numpy arrays


def convfromYearf(yearf, String=None, rhour=False):
    """
    Function that calculates an array of dates in the form "year-doyT" from fractional year array.

    Args:
        yearf: float

    Returns:
        year-doyT
    """

    # from floating point year to floating point ordinal

    tmp = list(range(len(yearf)))

    for i in range(len(yearf)):
        if String:
            tmp[i] = TimefromYearf(yearf[i], String=String, rhour=rhour)
        else:
            tmp[i] = TimefromYearf(yearf[i], rhour=rhour)

    return tmp  # Return Python list instead of numpy array


def round_to_hour(dt: datetime.datetime) -> datetime.datetime:
    minutes = dt.minute
    if minutes >= 30:
        return dt.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(
            hours=1
        )
    else:
        return dt.replace(minute=0, second=0, microsecond=0)


# functions using gps week and day of week ----------------


def datefRinex(rinex_list):
    """
    Function that calculates datetime object from rinex format

    Args:
        rinex_list: list of rinex files

    Returns:
        list of datetime objects
    """

    date_list = []

    for rinex in rinex_list:
        basename = os.path.basename(rinex)
        doy = basename[4:7]
        yy = basename[9:11]
        session = ABChour(basename[7:8])
        date_list.append(
            datetime.datetime.strptime(
                "{0}-{1}:{2:02d}".format(yy, doy, session), "%y-%j:%H"
            )
        )

    return date_list


# RINEX naming conventions ----------------------------------------

# RINEX 3/4 Long format constants
RINEX3_COUNTRY_CODES = {
    "IS": "ISL",  # Iceland
    "NO": "NOR",  # Norway
    "SE": "SWE",  # Sweden
    "DK": "DNK",  # Denmark
    "FI": "FIN",  # Finland
    "GL": "GRL",  # Greenland
    "US": "USA",  # United States
    "DE": "DEU",  # Germany
    "FR": "FRA",  # France
    "GB": "GBR",  # Great Britain
    "JP": "JPN",  # Japan
    "AU": "AUS",  # Australia
}

RINEX3_DATA_SOURCES = {
    "R": "Receiver",     # Directly from receiver
    "S": "Stream",       # NTRIP stream
    "U": "Unknown",      # Unknown source
}

RINEX3_FILE_TYPES = {
    # Observation files
    "MO": "Mixed Observation",
    "GO": "GPS Observation",
    "RO": "GLONASS Observation",
    "EO": "Galileo Observation",
    "JO": "QZSS Observation",
    "CO": "BeiDou Observation",
    "IO": "IRNSS Observation",
    "SO": "SBAS Observation",
    # Navigation files
    "MN": "Mixed Navigation",
    "GN": "GPS Navigation",
    "RN": "GLONASS Navigation",
    "EN": "Galileo Navigation",
    "JN": "QZSS Navigation",
    "CN": "BeiDou Navigation",
    "IN": "IRNSS Navigation",
    "SN": "SBAS Navigation",
    # Meteorological
    "MM": "Meteorological",
}

# RINEX 2 file type characters
RINEX2_FILE_TYPES = {
    "o": "Observation",
    "n": "GPS Navigation",
    "g": "GLONASS Navigation",
    "l": "Galileo Navigation",
    "m": "Meteorological",
    "h": "SBAS Payload",
}


def rinex2_filename(
    station: str,
    dt: datetime.datetime,
    file_type: str = "o",
    session: Optional[str] = None,
    sequence: int = 0,
) -> str:
    """Generate RINEX 2 short format filename.

    Format: SSSS0DDS.YYt
        - SSSS: 4-char station marker (uppercase)
        - 0DD: 3-digit day of year (001-366)
        - S: Session indicator (0 for daily, a-x for hourly)
        - YY: 2-digit year
        - t: File type (o=obs, n=nav, g=glonass nav, etc.)

    Args:
        station: 4-character station identifier (e.g., "ELDC")
        dt: Datetime for the file
        file_type: File type character (o, n, g, l, m, h) or RINEX 3 code (MO, GN, etc.)
        session: Session letter (None=auto from frequency, "0"=daily, "a"-"x"=hourly)
        sequence: File sequence number (0 for first file)

    Returns:
        RINEX 2 format filename (e.g., "ELDC0150.26o")

    Example:
        >>> import datetime
        >>> rinex2_filename("ELDC", datetime.datetime(2026, 1, 15))
        'ELDC0150.26o'
        >>> rinex2_filename("ELDC", datetime.datetime(2026, 1, 15, 10, 0), session="k")
        'ELDC015k.26o'
    """
    # Ensure station is 4 chars, uppercase
    station = station.upper()[:4].ljust(4)

    # Get day of year and 2-digit year
    doy = dt.timetuple().tm_yday
    year_2digit = dt.year % 100

    # Determine session indicator
    if session is None:
        # Default to daily (0) if not specified
        session_char = str(sequence) if sequence < 10 else "0"
    elif session == "0" or session.isdigit():
        session_char = session
    else:
        session_char = session.lower()

    # Map RINEX 3 file types to RINEX 2 characters
    type_mapping = {
        "MO": "o", "GO": "o", "RO": "o", "EO": "o",  # Observation
        "MN": "n", "GN": "n",  # GPS Navigation
        "RN": "g",  # GLONASS Navigation
        "EN": "l",  # Galileo Navigation
        "MM": "m",  # Meteorological
    }

    if len(file_type) == 2 and file_type.upper() in type_mapping:
        type_char = type_mapping[file_type.upper()]
    else:
        type_char = file_type[0].lower()

    return f"{station}{doy:03d}{session_char}.{year_2digit:02d}{type_char}"


def rinex3_filename(
    station: str,
    dt: datetime.datetime,
    country_code: str = "ISL",
    data_source: str = "R",
    file_period: str = "01D",
    data_frequency: str = "15S",
    file_type: str = "MO",
    monument_number: str = "00",
    uppercase: bool = False,
) -> str:
    """Generate RINEX 3/4 long format filename.

    Format: SSSS00CCC_R_YYYYDDDHHMM_PPU_FFS_TT.rnx
        - SSSS: 4-char station marker (lowercase by default for RINEX 3+)
        - 00: 2-digit monument number
        - CCC: 3-char ISO country code
        - R: Data source (R=receiver, S=stream, U=unknown)
        - YYYY: 4-digit year
        - DDD: 3-digit day of year
        - HH: Start hour (00-23)
        - MM: Start minute (00-59)
        - PP: File period value (01, 15, etc.)
        - U: Period unit (D=day, H=hour, M=minute)
        - FF: Data frequency value (01, 15, 30, etc.)
        - S: Frequency unit (S=second, M=minute, H=hour)
        - TT: File type (MO, GO, MN, etc.)

    Args:
        station: 4-character station identifier
        dt: Datetime for the file start
        country_code: 3-char ISO country code (default: "ISL" for Iceland)
        data_source: Data source code (R, S, or U)
        file_period: File period (e.g., "01D", "01H", "15M")
        data_frequency: Data frequency (e.g., "15S", "01S", "30S")
        file_type: RINEX 3 file type code (MO, GO, MN, etc.)
        monument_number: 2-digit monument marker number
        uppercase: Use uppercase station ID (default: False for RINEX 3+ standard)

    Returns:
        RINEX 3 format filename (e.g., "eldc00ISL_R_20260150000_01D_15S_MO.rnx")

    Example:
        >>> import datetime
        >>> rinex3_filename("ELDC", datetime.datetime(2026, 1, 15))
        'eldc00ISL_R_20260150000_01D_15S_MO.rnx'
        >>> rinex3_filename("ELDC", datetime.datetime(2026, 1, 15), uppercase=True)
        'ELDC00ISL_R_20260150000_01D_15S_MO.rnx'
        >>> rinex3_filename("ELDC", datetime.datetime(2026, 1, 15, 10, 0),
        ...                 file_period="01H", data_frequency="01S")
        'eldc00ISL_R_20260151000_01H_01S_MO.rnx'
    """
    # Station case: lowercase by default for RINEX 3+, uppercase if requested
    if uppercase:
        station = station.upper()[:4].ljust(4)
    else:
        station = station.lower()[:4].ljust(4)

    # Ensure monument number is 2 digits
    monument_number = str(monument_number).zfill(2)[:2]

    # Country code uppercase, 3 chars
    country_code = country_code.upper()[:3]

    # Date components
    year = dt.year
    doy = dt.timetuple().tm_yday
    hour = dt.hour
    minute = dt.minute

    # Data source
    data_source = data_source.upper()[:1]

    # File type uppercase
    file_type = file_type.upper()[:2]

    return (
        f"{station}{monument_number}{country_code}_"
        f"{data_source}_"
        f"{year:04d}{doy:03d}{hour:02d}{minute:02d}_"
        f"{file_period}_"
        f"{data_frequency}_"
        f"{file_type}.rnx"
    )


def parse_rinex2_filename(filename: str) -> Optional[Dict[str, Any]]:
    """Parse RINEX 2 short format filename into components.

    Args:
        filename: RINEX 2 filename (e.g., "ELDC0150.26o")

    Returns:
        Dictionary with parsed components or None if parsing fails:
        - station: 4-char station code
        - doy: Day of year (1-366)
        - session: Session character (0-9 or a-x)
        - year: Full 4-digit year
        - file_type: File type character
        - datetime: Parsed datetime object

    Example:
        >>> parse_rinex2_filename("ELDC015k.26o")
        {'station': 'ELDC', 'doy': 15, 'session': 'k', 'year': 2026,
         'file_type': 'o', 'datetime': datetime.datetime(2026, 1, 15, 10, 0)}
    """
    # Remove path and extension variations
    basename = os.path.basename(filename)

    # Pattern: SSSS0DDS.YYt
    pattern = r'^([A-Za-z0-9]{4})(\d{3})([0-9a-z])\.(\d{2})([ongmlh])$'
    match = re.match(pattern, basename, re.IGNORECASE)

    if not match:
        return None

    station = match.group(1).upper()
    doy = int(match.group(2))
    session = match.group(3).lower()
    year_2digit = int(match.group(4))
    file_type = match.group(5).lower()

    # Convert 2-digit year to 4-digit (80-99 = 1980-1999, 00-79 = 2000-2079)
    year = 2000 + year_2digit if year_2digit < 80 else 1900 + year_2digit

    # Convert session to hour
    if session.isdigit():
        hour = 0  # Daily file
    else:
        hour = ABChour(session)

    # Create datetime
    try:
        dt = datetime.datetime.strptime(f"{year}-{doy}:{hour:02d}", "%Y-%j:%H")
    except ValueError:
        dt = None

    return {
        "station": station,
        "doy": doy,
        "session": session,
        "year": year,
        "file_type": file_type,
        "datetime": dt,
    }


def parse_rinex3_filename(filename: str) -> Optional[Dict[str, Any]]:
    """Parse RINEX 3/4 long format filename into components.

    Args:
        filename: RINEX 3 filename (e.g., "eldc00ISL_R_20260150000_01D_15S_MO.rnx")

    Returns:
        Dictionary with parsed components or None if parsing fails:
        - station: 4-char station code (uppercase)
        - monument_number: 2-char monument marker
        - country_code: 3-char country code
        - data_source: Data source code
        - year: 4-digit year
        - doy: Day of year
        - hour: Hour (0-23)
        - minute: Minute (0-59)
        - file_period: File period (e.g., "01D")
        - data_frequency: Data frequency (e.g., "15S")
        - file_type: File type code
        - datetime: Parsed datetime object

    Example:
        >>> parse_rinex3_filename("eldc00ISL_R_20260151000_01H_01S_MO.rnx")
        {'station': 'ELDC', 'monument_number': '00', 'country_code': 'ISL',
         'data_source': 'R', 'year': 2026, 'doy': 15, 'hour': 10, 'minute': 0,
         'file_period': '01H', 'data_frequency': '01S', 'file_type': 'MO',
         'datetime': datetime.datetime(2026, 1, 15, 10, 0)}
    """
    # Remove path
    basename = os.path.basename(filename)

    # Pattern: SSSS00CCC_R_YYYYDDDHHMM_PPU_FFS_TT.rnx
    pattern = (
        r'^([a-zA-Z0-9]{4})(\d{2})([A-Z]{3})_'
        r'([RSU])_'
        r'(\d{4})(\d{3})(\d{2})(\d{2})_'
        r'(\d{2}[DHMS])_'
        r'(\d{2}[SHMU])_'
        r'([A-Z]{2})'
        r'\.rnx'
    )
    match = re.match(pattern, basename, re.IGNORECASE)

    if not match:
        return None

    station = match.group(1).upper()
    monument_number = match.group(2)
    country_code = match.group(3).upper()
    data_source = match.group(4).upper()
    year = int(match.group(5))
    doy = int(match.group(6))
    hour = int(match.group(7))
    minute = int(match.group(8))
    file_period = match.group(9).upper()
    data_frequency = match.group(10).upper()
    file_type = match.group(11).upper()

    # Create datetime
    try:
        dt = datetime.datetime.strptime(f"{year}-{doy}:{hour:02d}:{minute:02d}", "%Y-%j:%H:%M")
    except ValueError:
        dt = None

    return {
        "station": station,
        "monument_number": monument_number,
        "country_code": country_code,
        "data_source": data_source,
        "year": year,
        "doy": doy,
        "hour": hour,
        "minute": minute,
        "file_period": file_period,
        "data_frequency": data_frequency,
        "file_type": file_type,
        "datetime": dt,
    }


def rinex_filename(
    station: str,
    dt: datetime.datetime,
    version: int = 2,
    frequency: str = "1D",
    file_type: str = "o",
    **kwargs
) -> str:
    """Generate RINEX filename in either short (v2) or long (v3/4) format.

    This is a convenience wrapper that calls either rinex2_filename or
    rinex3_filename based on the version parameter.

    Args:
        station: 4-character station identifier
        dt: Datetime for the file
        version: RINEX version (2, 3, or 4)
        frequency: File frequency ("1D" for daily, "1H" for hourly)
        file_type: File type (RINEX 2: "o", "n", etc. or RINEX 3: "MO", "MN", etc.)
        **kwargs: Additional arguments passed to the specific function

    Returns:
        RINEX filename in appropriate format

    Example:
        >>> import datetime
        >>> dt = datetime.datetime(2026, 1, 15)
        >>> rinex_filename("ELDC", dt, version=2)
        'ELDC0150.26o'
        >>> rinex_filename("ELDC", dt, version=3)
        'eldc00ISL_R_20260150000_01D_15S_MO.rnx'
    """
    if version == 2:
        # Map frequency to session
        if frequency.upper() in ("1H", "H"):
            session = hourABC(dt.hour)
        else:
            session = "0"

        return rinex2_filename(
            station=station,
            dt=dt,
            file_type=file_type,
            session=session,
            sequence=kwargs.get("sequence", 0),
        )
    else:
        # RINEX 3/4
        # Map file_type from RINEX 2 to RINEX 3 if needed
        type_mapping = {
            "o": "MO",
            "n": "GN",
            "g": "RN",
            "l": "EN",
            "m": "MM",
        }
        if len(file_type) == 1:
            file_type = type_mapping.get(file_type.lower(), "MO")

        # Map frequency to file_period
        if frequency.upper() in ("1H", "H"):
            file_period = "01H"
        elif frequency.upper() in ("1D", "D"):
            file_period = "01D"
        else:
            file_period = kwargs.get("file_period", "01D")

        return rinex3_filename(
            station=station,
            dt=dt,
            country_code=kwargs.get("country_code", "ISL"),
            data_source=kwargs.get("data_source", "R"),
            file_period=file_period,
            data_frequency=kwargs.get("data_frequency", "15S"),
            file_type=file_type,
            monument_number=kwargs.get("monument_number", "00"),
        )


def convert_rinex_filename(
    filename: str,
    target_version: int,
    **kwargs
) -> Optional[str]:
    """Convert RINEX filename between version 2 and version 3/4 formats.

    Args:
        filename: Input RINEX filename (either v2 or v3 format)
        target_version: Target RINEX version (2, 3, or 4)
        **kwargs: Additional arguments for target format (country_code, etc.)

    Returns:
        Converted filename or None if parsing fails

    Example:
        >>> convert_rinex_filename("ELDC0150.26o", target_version=3)
        'eldc00ISL_R_20260150000_01D_15S_MO.rnx'
        >>> convert_rinex_filename("eldc00ISL_R_20260151000_01H_01S_MO.rnx", target_version=2)
        'ELDC015k.26o'
    """
    # Try parsing as RINEX 2
    parsed = parse_rinex2_filename(filename)
    source_version = 2

    if parsed is None:
        # Try parsing as RINEX 3
        parsed = parse_rinex3_filename(filename)
        source_version = 3

    if parsed is None:
        return None

    dt = parsed.get("datetime")
    if dt is None:
        return None

    station = parsed["station"]

    if target_version == 2:
        # Convert to RINEX 2
        session = parsed.get("session")
        if session is None:
            # Derive from hour
            hour = parsed.get("hour", 0)
            if hour == 0:
                session = "0"
            else:
                session = hourABC(hour)

        file_type = parsed.get("file_type", "o")
        if len(file_type) == 2:
            # Map RINEX 3 type to RINEX 2
            type_mapping = {"MO": "o", "GO": "o", "MN": "n", "GN": "n", "RN": "g", "EN": "l", "MM": "m"}
            file_type = type_mapping.get(file_type.upper(), "o")

        return rinex2_filename(station, dt, file_type=file_type, session=session)

    else:
        # Convert to RINEX 3
        file_period = parsed.get("file_period")
        if file_period is None:
            # Derive from session
            session = parsed.get("session", "0")
            if session.isdigit():
                file_period = "01D"
            else:
                file_period = "01H"

        data_frequency = parsed.get("data_frequency", kwargs.get("data_frequency", "15S"))

        file_type = parsed.get("file_type", "o")
        if len(file_type) == 1:
            type_mapping = {"o": "MO", "n": "GN", "g": "RN", "l": "EN", "m": "MM"}
            file_type = type_mapping.get(file_type.lower(), "MO")

        return rinex3_filename(
            station=station,
            dt=dt,
            country_code=kwargs.get("country_code", parsed.get("country_code", "ISL")),
            data_source=kwargs.get("data_source", parsed.get("data_source", "R")),
            file_period=file_period,
            data_frequency=data_frequency,
            file_type=file_type,
            monument_number=kwargs.get("monument_number", parsed.get("monument_number", "00")),
        )


def datefgpsWeekSOW(gpsWeek, SOW, String=None, leapSecs=None, mDay=False):
    """
    Function that calculates the date (time) converted from GPS Week and Second of week (SOW)

    Args:
        gpsWeek: An integer number of week since 1980-01-06 00:00:00

        SOW: Float Second of week (SOW) Then set

        String: output format See datetime for reference.
            None (Default), returns a python datetime object.
            For special formatting:
            "yearf", will return date (time) in fractional year
            "tuple", will return a tuple with date (time)

        leapSecs: number of leap seconds to take into acount.


        mDay: Boolean Defaulsts to False returns date at 12 PM (noon),
               False return input time in second accuracy

    Returns:
        date (time)

    """

    print("SOW: {}".format(SOW))
    print("gpsWeek: {}".format(gpsWeek))
    day = datetime.datetime(*UTCFromGps(gpsWeek, SOW, leapSecs=leapSecs))

    if mDay:
        day = day.replace(hour=12, minute=0, second=0)

    if String == "yearf":
        return TimetoYearf(*day.timetuple()[0:6])
    elif String == "tuple":
        return day.timetuple()[0:6]
    elif String:
        return day.strftime(String)
    else:
        return day


def datefgpsWeekDOW(gpsWeek, DOW, String=None, leapSecs=None, mDay=True):
    """
    Function that calculates date (time) converted from GPS Week and Day of week (DOW)

    Args:

        DOW: integer Day of week

        See datefgpsWeekSOW for other arguments

    Returns:
    date (time)

    """

    SOW = (DOW + 1) * secsInDay
    return datefgpsWeekSOW(gpsWeek, SOW, String=String, leapSecs=leapSecs, mDay=mDay)


def datefgpsWeekDOWSOD(gpsWeek, DOW, SOD, String=None, leapSecs=None, mDay=False):
    """
    Function that calculates date (time) converted from GPS Week and Day of week (DOW)

    Args:

        DOW: integer Day of week
        SOD: float second of day

        See datefgpsWeekSOW for other arguments

    Returns:
    date (time)

    """

    SOW = DOW * secsInDay + SOD
    return datefgpsWeekSOW(gpsWeek, SOW, String=String, leapSecs=leapSecs, mDay=mDay)


def datefgpsWeekDoy(gpsWeek, Doy, String=None, leapSecs=None):
    """
    Function that calculates date converted from GPS Week and Day of year

    Args:
        gpsWeek
        Doy: Day of year
        String
        leapSecs

    Returns:
        date converted from GPS Week and Day of the year.
    """
    SOW = 1 * secsInDay
    day = datetime.datetime(*UTCFromGps(gpsWeek, SOW, leapSecs=leapSecs)[0:3])
    year0 = day.timetuple()[0]
    doy0 = day.timetuple()[7]

    daysinyear0 = DaysinYear(year0)
    daystoYend = daysinyear0 - doy0

    if doy0 <= Doy < doy0 + 7:  # check if doy is in the given week
        DOW = Doy - doy0
    elif (
        daystoYend < 6 and daysinyear0 + Doy - doy0 < 7
    ):  # in case it is the end of year
        DOW = daysinyear0 + Doy - doy0
    else:
        DOW = 0
        print(
            "ERROR: Doy %s is not in week %s returning date of day 0 of week %s"
            % (Doy, gpsWeek, gpsWeek)
        )

    day = day + datetime.timedelta(DOW)

    if String == "yearf":
        return TimetoYearf(*day.timetuple()[0:3])
    elif String == "tuple":
        return day.timetuple()[0:3]
    elif String:
        return day.strftime(String)
    else:
        return day


def toDatetime(dStr, fStr):
    """
    Function that converts date/time Strings to datetime objects according to formatting rule defined in fStr

    Args:

        dStr: (list of) String(s)  holding a date and/or time

        fStr: formatting rule constituting the following input formats
            default: fStr formatted according to standard rules see for example datetime documentation for formatting
            (i.e dStr=20150120 entailes fStr=%Y%m%d )

            yearf: decimal year
            w-dow: GPS week and day of week on the form WWWW-DOW (example 1820-3, where DOW is sunday = 0 ... 6 = saturday)
            w-dow-sod: GPS week and day of week on the form WWWW-DOW-SOD (example 1820-3-100, where DOW is sunday = 0 ... 6 = saturday)
            w-sow: GPS week and second of week on the form WWWW-SOW (example 1820-3000, where SOW is number of seconds since week started)
            w-dow-sod: GPS week - day of week - second of daym on the form WWWW-DOW-SOD (example 1820-1-18)
            w-doy: GPS week and day of year on the form WWWW-DOY
            Rinex: converts rinex format to rinex

    Returns:
        datetime object.

    """

    if type(dStr) == datetime.datetime:
        day = dStr

    elif fStr == "yearf":
        day = TimefromYearf(float(dStr))

    elif fStr == "w-dow":
        wdow = tuple([int(i) for i in dStr.split("-")])
        day = datefgpsWeekDOW(*wdow)

    elif fStr == "w-dow-sod":
        wdowsod = tuple([int(i) for i in dStr.split("-")])
        day = datefgpsWeekDOWSOD(*wdowsod)

    elif fStr == "w-sow":
        wsow = tuple([int(i) for i in dStr.split("-")])
        day = datefgpsWeekSOW(*wsow)

    elif fStr == "w-doy":
        wdoy = tuple([int(i) for i in dStr.split("-")])
        day = datefgpsWeekDoy(*wdoy)

    elif fStr == "Rinex":
        day = datefRinex(dstr)

    else:
        day = datetime.datetime.strptime(dStr, fStr)

    # returning datetime object
    return day


def toDatetimel(dStrlist, fStr):
    """
    A simple wrapper around toDatetime to allow for list input works like toDatetime if dStrlist is a single object.

    Args:

        dStr: (list of) String(s)  holding a date and/or time

        fStr: See docstring of toDatetime

    Returns:
        list of datetime objects.

    """

    # To allow for single object input as well, otherwise python will treat a string as a list in the for loop
    if type(dStrlist) is not list:
        dStrlist = [dStrlist]

    dStrlist = [
        toDatetime(dStr, fStr) for dStr in dStrlist
    ]  # converting to a list of datetime strings

    if len(dStrlist) == 1:  # toDatetimel can be replaced by toDatetime
        return dStrlist[0]
    else:
        return dStrlist


HOURS_PER_DAY = 24.0
MINUTES_PER_DAY = 60.0 * HOURS_PER_DAY
SECONDS_PER_DAY = 60.0 * MINUTES_PER_DAY
MUSECONDS_PER_DAY = 1e6 * SECONDS_PER_DAY
SEC_PER_MIN = 60
SEC_PER_HOUR = 3600
SEC_PER_DAY = SEC_PER_HOUR * 24
SEC_PER_WEEK = SEC_PER_DAY * 7


def _to_ordinalf(dt):
    """
    Function that converts :mod:`datetime` to the Gregorian date as UTC float days,
    preserving hours, minutes, seconds and microseconds.

    Args:
        df: datetime object

    Returns:
        ordinal equivalent of dt, in float format.
    """

    if hasattr(dt, "tzinfo") and dt.tzinfo is not None:
        delta = dt.tzinfo.utcoffset(dt)
        if delta is not None:
            dt -= delta

    base = float(dt.toordinal())
    if hasattr(dt, "hour"):
        base += (
            dt.hour / HOURS_PER_DAY
            + dt.minute / MINUTES_PER_DAY
            + dt.second / SECONDS_PER_DAY
            + dt.microsecond / MUSECONDS_PER_DAY
        )
    return base
