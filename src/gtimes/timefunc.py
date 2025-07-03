import os
import math
import calendar
import datetime
import string

import re
import pandas as pd
import numpy as np

# importing constants from gpstime.
from gtimes.gpstime import secsInDay, gpsFromUTC, UTCFromGps
from dateutil.tz import tzlocal


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


def TimetoYearf(year, month, day, hour=12, minute=0, sec=0):
    """
    Function that converts time cal+time of day into fractional year.

    Examples:
        >>>TimetoYearf(2008,03,29,hour=12,minute=15, sec=0)


    Args:
        date: as year, month, day
        time: as hour, minute, sec (defaults to the middle of the day at 12 am)

    Returns:
        returns fractional year

    """
    doy = DayofYear(0, year, month, day) - 1
    secofyear = doy * secsInDay + (hour * 60 + minute) * 60 + sec

    daysinyear = DaysinYear(year)
    secinyear = daysinyear * secsInDay

    yearf = year + secofyear / float(secinyear)

    return yearf


def TimefromYearf(yearf, String=None):
    """
    Function that returns a date and/or time according to a formated string derived from a fractional year.
    Intended to manipulate time format of gamit time series files which is in fractional years.

    Examples:
        >>>TimefromYearf(2023.97, String=None)

    Args:
        string:
            formated according to format codes that the C standard (1989 version) see documentation for
            datetime module. Example "%Y %m %d %H:%M:%S %f"
        year: fractional year. example 2012.55

    Returns:
        Returns time of the input year formated according to input string.
    """
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
    dt = datetime.datetime.strptime(
        timestr, "%Y %j %H:%M:%S %f"
    )  # Create datetime object from timestr
    if String:
        if String == "ordinalf":  # return a floating point ordinal day
            return dt.toordinal() + fofday
        else:
            return dt.strftime(String)
    else:  # just return the datetime instanse
        return dt


def currDatetime(days=0, refday=datetime.datetime.today(), String=None):
    """
    Function that returns a datetime object for the date, "days" from refday.

    Examples:
        >>> currDatetime(days=5, refday=datetime.datetime.today(), String=None)

    Args:
        days: integer, Defaults to 0
              days to offset
        refday: datetime object or a string, defaults to datetime.datetime.today()
              reference day
        string: formating string. defaults to None (infering refday as datetime object)
              If refday is a date string, this has to contain it's formating (i.e %Y-%m-%d %H:%M)

    Returns:
        A datetime object. Defaults to current day if ran without arguments
    """

    day = refday + datetime.timedelta(**shifTime(days))
    if String:
        return day.strftime(String)
    else:
        return day


def currDate(days=0, refday=datetime.date.today(), String=None, fromYearf=False):
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


def datepathlist(
    stringformat, lfrequency, starttime=None, endtime=None, datelist=[], closed="left"
):
    """

    Function that returns  a list of strings formated according to stringformat with
    frequency lfrequency for a given interval between starttime and endtime,
    can also accept a list of dates which will be converted according to
    stringformat. defaults to single element list with formated current date.

    Examples:
        >>> datepathlist(stringformat,...)

        Example the date 2015-10-01:
            stringformat -> "/data/%Y/#b/VONC/15s_24hr/rinex/VONCR2inexO.Z"
            output       -> "/data/2015/oct/VONC/15s_24hr/rinex/VONC2740.15O.Z"

    Args:
        stringformat: A String determinaning the output format of the input time
                      formated according to format codes that the C standard
                      (1989 version) requires, see documentation for datetime module
                      for details.                      Example, the date 2015-10-01
                      String = "/data/%Y/#b/VONC/15s_24hr/rinex/VONCR2inexO.Z" ->
                                /data/2015/oct/VONC/15s_24hr/rinex/VONC2740.15O.Z
                      Included are  some special case formating
                           #gpsw -> GPS week
                           #b -> %b converted to all lowercase.
                           #Rin2 -> %j(session).%y where session is a single character
                           reprecenting the session of the day. The coding depedepends
                           the (lfrequency).
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

        closed:     A string passed to pd.date_range, controls how interval
                    endpoints are treaded with given frequency "left", "right" or None,
                    See doc from pd.date_range
                    Defaults to "left"

    Returns:
        Returns list of strings with time codes formated according to input String.

    """

    today = datetime.datetime.now(datetime.timezone.utc)

    # special home made formating
    gpswmatch = re.compile(r"\w*(#gpsw)\w*").search(stringformat)  # use GPS week
    wrepl = ""
    rmatch = re.compile(r"\w*(#Rin2)\w*").search(
        stringformat
    )  # use GPS standard name RINEX2 name
    rrepl = ""
    r8hmatch = re.compile(r"\w*(#8hRin)\w*").search(
        stringformat
    )  # use GPS standard name RINEX2 name
    r8hrepl = ""
    bbbmatch = re.compile(r"\w*(#b)\w*").search(
        stringformat
    )  # use all lower case for 3 letter month
    bbbrepl = ""

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
            datelist = pd.date_range(
                starttime - mod, endtime - mod, freq=lfrequency, closed=closed
            ).tolist()
        else:
            datelist = [today - mod]

    else:
        hourshift = datetime.timedelta(hours=0)
        datelist = pd.date_range(
            starttime, endtime - hourshift, freq=lfrequency, inclusive="both"
        ).tolist()
        if not datelist:
            datelist = [endtime]

    if datelistmatch:
        return datelist

    stringlist = []
    for item in datelist:
        if rmatch or r8hmatch:  # form H or 8H rinex formating
            if rmatch:  # for rinex formating
                if lfrequency[-1] == "H":
                    hour = hourABC(item.hour)
                else:
                    hour = 0
            else:  # the specal case of 8H files
                hour = hour8hABC(item.hour)

            doy = int(item.strftime("%j"))
            yr = int(item.strftime("%y"))
            rrepl = "%.3d%s.%.2d" % (doy, hour, yr)

        if gpswmatch:  # for GPS week
            wrepl = "{0:04d}".format(gpsWeekDay(refday=item)[0])

        if bbbmatch:  # for lower case three letter month name Jan -> jan ...
            bbbrepl = "{:%b}".format(item).lower()

        # replacing special formating strings with the values
        pformat = re.sub("#gpsw", wrepl, stringformat)
        pformat = re.sub("#8hRin2", rrepl, pformat)
        pformat = re.sub("#Rin2", rrepl, pformat)
        pformat = re.sub("#b", bbbrepl, pformat)
        pformat = item.strftime(pformat)
        stringlist.append(pformat)

    return stringlist


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


# Temporary functions to deal with numpy arrays Will become apsolete when implementd directly in the main moduvls


def convfromYearf(yearf, String=None):
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
            tmp[i] = TimefromYearf(yearf[i], String)
        else:
            tmp[i] = TimefromYearf(yearf[i])

    return np.asarray(tmp)


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


def datefgpsWeekSOW(gpsWeek, SOW, String=None, leapSecs=None, mDay=False):
    """
    Function that calculates the date (time) converted from GPS Week and Second of week (SOW)

    Args:
        gpsWeek: An integer number of week since 1980-01-06 00:00:00

        SOW: Float Second of week (SOW) Then set

        String: output format See datetime for reference.
            None (Default), returns a python datetime object.
            For special formating:
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
    Function that converts date/time Strings to datetime objects accorting to formating rule defined in fStr

    Args:

        dStr: (list of) String(s)  holding a date and/or time

        fStr: formating rule constituding the  following input formats
            default: fStr formated according to standard rules see for example datetime documentation for formating
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
