"""
A Python implementation of GPS related time conversions.

Copyright 2002 by Bud P. Bruegger, Sistema, Italy
mailto:bud@sistema.it
http://www.sistema.it

Modifications for GPS seconds by Duncan Brown

PyUTCFromGpsSeconds added by Ben Johnson

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 2 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program; if not, write to the Free Software Foundation, Inc., 59
Temple Place, Suite 330, Boston, MA  02111-1307  USA

GPS Time Utility functions

This file contains a Python implementation of GPS related time conversions.

The two main functions convert between UTC and GPS time (GPS-week, time of
week in seconds, GPS-day, time of day in seconds).  The other functions are
convenience wrappers around these base functions.

A good reference for GPS time issues is:
http://www.oc.nps.navy.mil/~jclynch/timsys.html

Note that python time types are represented in seconds since (a platform
dependent Python) Epoch.  This makes implementation quite straight forward
as compared to some algorigthms found in the literature and on the web.
"""

__author__ = "Benedikt G. Ofeigsson <bgo@vedur.is> edited from Duncan Brown <duncan@gravity.phys.uwm.edu>"
__date__ = "$Date: 2012/03/6"
__version__ = "$Revision: 1.6 $"[11:-2]
# $Source: /usr/local/cvs/lscsoft/glue/glue/gpstime.py,v $

import time
import math
import datetime
import datetime as dt
import locale


# from sqlalchemy import Boolean

secsInWeek = 604800
secsInDay = 86400
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)
epochTuple = gpsEpoch + (-1, -1, 0)


def dayOfWeek(year: int, month: int, day: int) -> int:
    """
    This function returns the day of the week for a given date

    Examples:
        >>> dayOfWeek(2023, 1, 3)
        2
        >>> dayOfWeek(2023, 12, 4)
        1

    Args:
        year: Four digit year "yyyy". Example 2013
        month: Month in integer from 1-12
        day: Day of month as integer 1-(28-31) depending on month

    Returns:
        int: A number representing the day of the week (0=Sunday, 1=Monday, .., 6=Saturday)

    """
    hr = 12  # make sure you fall into right day, middle is save
    t = time.mktime((year, month, day, hr, 0, 0, 0, 0, -1))
    pyDow = time.localtime(t)[6]
    gpsDow = (pyDow + 1) % 7
    return gpsDow


def gpsWeek(year: int, month: int, day: int) -> int:
    """
    Function that calculates (full) gpsWeek for given date (in UTC)

    Args:
        year: int
        month:
        day:

    Returns:
        gpsWeek
    """
    hr = 12  # make sure you fall into right day, middle is save
    return gpsFromUTC(year, month, day, hr, 0, 0)[0]


def julianDay(year: int, month: int, day: int) -> int:
    """Function that calculates julian day=day since Jan 1 of year

    Args:
        year
        month
        day

    Returns:
        julian day

    """

    hr = 12  # make sure you fall into right day, middle is save
    t = time.mktime((year, month, day, hr, 0, 0.0, 0, 0, -1))
    julDay = time.localtime(t)[7]

    return julDay


def mkUTC(year: int, month: int, day: int, hour: int, min: int, sec: int) -> int:
    """
    Similar to python's mktime but for utc. Converts time list to time in utc

    Args:
        year:
        month:
        day:
        hour:
        min:
        sec:

    Returns:
        time tuple in UTC

    """
    spec = [year, month, day, hour, min, sec] + [0, 0, 0]
    utc = time.mktime(spec) - time.timezone
    return utc


def ymdhmsFromPyUTC(pyUTC) -> tuple:
    """
    Function that computes a tuple from a python time value in UTC

    Args:
        pyUTC:

    Returns:
        tuple from a python time
    """

    return time.gmtime(pyUTC)[:-3]


# def wtFromUTCpy(pyUTC, leapSecs=18):
#    """
#    Convenience function:
#    BGO 07.01.2013: changed the default leapsecond to 16
#    BGO 07.01.2019: changed the default leapsecond to 18
#         allows to use python UTC times and
#         returns only week and tow"""
#
#    ymdhms = ymdhmsFromPyUTC(pyUTC)
#    wSowDSoD = gpsFromUTC( *ymdhms)
#    return wSowDSoD[0:2]
#    #return ymdhms


def gpsFromUTC(
    year: int,
    month: int,
    day: int,
    hour: int,
    min: int,
    sec: int,
    leapSecs=None,
    gpst=True,
):
    """
    Converts UTC to: gpsWeek, secsOfWeek, gpsDay, secsOfDay

    a good reference is:  http://www.oc.nps.navy.mil/~jclynch/timsys.html

    This is based on the following facts (see reference above):

    GPS time is basically measured in (atomic) seconds since
    January 6, 1980, 00:00:00.0  (the GPS Epoch)

    The GPS week starts on Saturday midnight (Sunday morning), and runs
    for 604800 seconds.

    Currently, GPS time is 13 seconds ahead of UTC (see above reference).
    While GPS SVs transmit this difference and the date when another leap
    second takes effect, the use of leap seconds cannot be predicted.  This
    routine is precise until the next leap second is introduced and has to be
    updated after that.
    BGO 07.01.2013: changed the default leapsecond to 16
    BGO 07.01.2019: changed the default leapsecond to 18

    SOW = Seconds of Week
    SOD = Seconds of Day

    Note:  Python represents time in integer seconds, fractions are lost!!!
    """

    # Automatic or manually applyed leap seconds.
    if leapSecs is None:
        leapSecs = getleapSecs(
            dTime=dt.datetime(year, month, day, hour, min, sec), gpst=gpst
        )

    secFract = sec % 1
    t0 = time.mktime(epochTuple)
    t = time.mktime((year, month, day, hour, min, sec, -1, -1, 0))
    # Note: time.mktime strictly works in localtime and to yield UTC, it should be
    #       corrected with time.timezone
    #       However, since we use the difference, this correction is unnecessary.
    # Warning:  trouble if daylight savings flag is set to -1 or 1 !!!
    t = t + leapSecs
    tdiff = t - t0
    gpsSOW = (tdiff % secsInWeek) + secFract
    gpsWeek = int(math.floor(tdiff / secsInWeek))
    gpsDay = int(math.floor(gpsSOW / secsInDay))
    gpsSOD = gpsSOW % secsInDay

    return (gpsWeek, gpsSOW, gpsDay, gpsSOD)


def UTCFromGps(gpsWeek: int, SOW: int, leapSecs: int = None, dtimeObj: bool = False):
    """
    Function that converts gps week and seconds to UTC.
    BGO 07.01.2013: changed the default leapsecond to 16
    BGO 07.01.2019: changed the default leapsecond to 18

    see comments of inverse function!

    SOW = seconds of week
    gpsWeek is the full number (not modulo 1024)

    Args:
        gpsWeek:
        SOW:
        leapSecs:
        dtimeObj:

    Returns:
        datetime object in UTC time zone
    """

    # Automatic or manually applied leap seconds.
    if leapSecs is None:
        leapSecs = getleapSecs(dTime=(gpsWeek, SOW), gpst=True)

    secFract = SOW % 1
    epochTuple = gpsEpoch + (-1, -1, 0)
    t0 = time.mktime(epochTuple) - time.timezone  # mktime is localtime, correct for UTC
    tdiff = (gpsWeek * secsInWeek) + SOW - leapSecs
    t = t0 + tdiff
    if dtimeObj is True:
        # only deals with whole seconds
        return dt.datetime.fromtimestamp(t)
    else:
        (
            year,
            month,
            day,
            hh,
            mm,
            ss,
            dayOfWeek,
            julianDay,
            daylightsaving,
        ) = time.gmtime(t + secFract)
        # use gmtime since localtime does not allow to switch off daylighsavings correction!!!
        return (year, month, day, hh, mm, ss + secFract)


def GpsSecondsFromPyUTC(pyUTC, leapSecs=None):
    """
    Function that converts the python epoch to gps seconds
    BGO 07.01.2013: changed the default leapsecond to 16
    BGO 07.01.2019: changed the default leapsecond to 18

    pyEpoch = the python epoch from time.time()

    Args:
        pyUTC:
        leapSecs:

    Returns:
        Integer representing the number of leapSeconds in a python epoch

    """

    # Automatic or manually applied leap seconds.
    if leapSecs is None:
        leapSecs = getleapSecs(dTime=dt.datetime(*ymdhmsFromPyUTC(pyUTC)), gpst=True)

    t = gpsFromUTC(*ymdhmsFromPyUTC(pyUTC - leapSecs))

    return int(t[0] * 60 * 60 * 24 * 7 + t[1])


def PyUTCFromGpsSeconds(gpsseconds):
    """
    Converts gps seconds to the python epoch. That is, the time that would be returned from time.time() at gpsseconds.

    Args:
        gpsseconds:

    Returns:
        Python epoch equivalent from the gps seconds.

    """

    pyUTC


def getleapSecs(dTime=None, gpst=True):
    """
    Function that retreives the leap seconds for a given datetime.

    Args:
        dTime: A Time string can be a datetime object, string or integer (either seconds since Epoch or GPSs)
        gpst:


    Returns:
        leapsecs
    """

    # tdiff = (gpsWeek * secsInWeek) + SOW - leapSecs
    # t = t0 + tdiff

    leapsecdict = leapSecDict()
    leapSecs = 0

    if type(dTime) is datetime.datetime:
        pass
    elif (type(dTime) is int) or (type(dTime) is float):
        dTime = dt.datetime.fromtimestamp(dTime)
    elif type(dTime) is tuple:
        t0 = (
            time.mktime(epochTuple) - time.timezone
        )  # mktime is localtime, correct for UTC
        tdiff = dTime[0] * secsInWeek + dTime[1]
        dTime = dt.datetime.fromtimestamp(t0 + tdiff)
    elif dTime is None:
        dTime = dt.datetime.now()

    # print(dTime.strftime("%Y-%b-%d %H:%M:%S"))
    # print(time.mktime( dTime.timetuple()) )

    # making sure locale month format is correct by changing locale.
    syslocale = locale.getlocale()
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    for day in leapsecdict.keys():
        if dt.datetime.strptime(day, "%Y-%b-%d") <= dTime:
            leapSecs = leapsecdict[day]

    # changing back to system local.
    locale.setlocale(locale.LC_ALL, "{}.{}".format(*syslocale))

    if gpst is True:
        leapSecs = leapSecs - leapsecdict["1980-Jan-1"]
        # print( "ADDING: {0} s".format(leapSecs) )

    return leapSecs


def leapSecDict():
    leapSecDict = {
        "1972-Jan-1": 10,
        "1972-Jul-1": 11,
        "1973-Jan-1": 12,
        "1974-Jan-1": 13,
        "1975-Jan-1": 14,
        "1976-Jan-1": 15,
        "1977-Jan-1": 16,
        "1978-Jan-1": 17,
        "1979-Jan-1": 18,
        "1980-Jan-1": 19,
        "1981-Jul-1": 20,
        "1982-Jul-1": 21,
        "1983-Jul-1": 22,
        "1985-Jul-1": 23,
        "1988-Jan-1": 24,
        "1990-Jan-1": 25,
        "1991-Jan-1": 26,
        "1992-Jul-1": 27,
        "1993-Jul-1": 28,
        "1994-Jul-1": 29,
        "1996-Jan-1": 30,
        "1997-Jul-1": 31,
        "1999-Jan-1": 32,
        "2006-Jan-1": 33,
        "2009-Jan-1": 34,
        "2012-Jul-1": 35,
        "2015-Jul-1": 36,
        "2017-Jan-1": 37,
    }

    return leapSecDict


# def gpsTimeFromUTC()

# ===== Tests  =========================================


def testTimeStuff():
    print("-" * 20)
    print("The GPS Epoch when everything began (1980, 1, 6, 0, 0, 0, leapSecs=0)")
    (w, sow, d, sod) = gpsFromUTC(1980, 1, 6, 0, 0, 0, leapSecs=0)
    print("**** week: %s, sow: %s, day: %s, sod: %s" % (w, sow, d, sod))
    print("     and hopefully back:")
    print("**** %s, %s, %s, %s, %s, %s\n" % UTCFromGps(w, sow, leapSecs=0))

    print("The time of first Rollover of GPS week (1999, 8, 21, 23, 59, 47)")
    (w, sow, d, sod) = gpsFromUTC(1999, 8, 21, 23, 59, 47)
    print("**** week: %s, sow: %s, day: %s, sod: %s" % (w, sow, d, sod))
    print("     and hopefully back:")
    print("**** %s, %s, %s, %s, %s, %s\n" % UTCFromGps(w, sow, leapSecs=14))

    print("Today is GPS week 1186, day 3, seems to run ok (2002, 10, 2, 12, 6, 13.56)")
    (w, sow, d, sod) = gpsFromUTC(2002, 10, 2, 12, 6, 13.56)
    print("**** week: %s, sow: %s, day: %s, sod: %s" % (w, sow, d, sod))
    print("     and hopefully back:")
    print("**** %s, %s, %s, %s, %s, %s\n" % UTCFromGps(w, sow))


def testJulD():
    print("2002, 10, 11 -> 284  ==??== ", julianDay(2002, 10, 11))


def testGpsWeek():
    print("2002, 10, 11 -> 1187  ==??== ", gpsWeek(2002, 10, 11))


def testDayOfWeek():
    print("2002, 10, 12 -> 6  ==??== ", dayOfWeek(2002, 10, 12))
    print("2002, 10, 6  -> 0  ==??== ", dayOfWeek(2002, 10, 6))


def testPyUtilties():
    ymdhms = (2002, 10, 12, 8, 34, 12.3)
    print("testing for: ", ymdhms)
    pyUtc = apply(mkUTC, ymdhms)
    back = ymdhmsFromPyUTC(pyUtc)
    print("yields     : ", back)
    # *********************** !!!!!!!!
    # assert(ymdhms == back)
    # TODO:: this works only with int seconds!!! fix!!!
    (w, t) = wtFromUTCpy(pyUtc)
    print("week and time: ", (w, t))


# ===== Main =========================================
if __name__ == "__main__":
    pass
    testTimeStuff()
    testGpsWeek()
    testJulD()
    testDayOfWeek()
    testPyUtilties()
