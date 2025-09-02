# ###############################
#
# timecalc 0.7
# Code made by bgo@vedur.is
# Iceland Met Office
# 2015
#
# ###############################
import argparse
import datetime
import re
import sys
from importlib.metadata import version
from typing import Optional, List, Union

from gtimes import timefunc as timefunc


def datestr(string: str) -> datetime.datetime:
    """
    Validate that the provided string is a correctly formatted date.

    This function checks if the input string is a datetime object. If not, it raises an
    error indicating that the string is not correctly formatted. This is typically used
    to validate date strings provided as command-line arguments.

    Args:
        string: The date string to validate.

    Returns:
        The validated date string as a datetime object.

    Raises:
        argparse.ArgumentTypeError: If the input string is not a valid datetime object.
    """
    if not isinstance(string, datetime.datetime):
        msg = "%r is not correctly formatted" % string
        raise argparse.ArgumentTypeError(msg)
    return string


def main() -> None:
    """Command-line interface for GPS time calculations and conversions.

    Provides a command-line tool for general time and date calculations with 
    support for GPS-specific time formats, RINEX filename generation, and 
    complex date manipulations commonly used in GNSS data processing.

    The tool supports:
    - GPS week and day-of-week calculations
    - UTC to GPS time conversions
    - RINEX filename pattern generation
    - Complex date range processing
    - Custom time formatting with GPS extensions

    Usage:
        timecalc -h                    # Show help
        timecalc -wd                   # Current GPS week/day
        timecalc -wd -d 2020-01-01     # GPS week/day for specific date
        timecalc -D 7 -l "file%j0.%yO" 1D -d 2020-01-01  # Generate file sequence

    Note:
        This is the main entry point for the 'timecalc' command installed
        with the gtimes package. Run 'timecalc -h' for complete usage help.
    """

    # date to use defaults to today ----
    dstr = "%Y-%m-%d"  # Default input string
    outpstr = "%a, %d. %b %Y"  # Default output string

    # today=datetime.date.today().strftime(dstr)
    today = datetime.datetime.utcnow()

    dD_parser = argparse.ArgumentParser(
        description="Time conversion program, can handle GPS time", add_help=False
    )
    dD_parser.add_argument(
        "-D",
        default=0,
        nargs="?",
        const=1,
        type=float,
        help="Number of days to shift the given day positive subracts, negativ adds",
    )
    dD_parser.add_argument(
        "--shift",
        nargs="?",
        type=str,
        help="works as -D exept works for more general shift "
        + "format is given by format letters"
        + "d for days, S for seconds,f for microseconds,"
        + "m for milliseconds, M for minutes, H for hours,"
        + "w for weeks.  with the shift as a number behind each letter"
        + "using : to separate the different fields , positive subracts,"
        + "negativ adds. Example: 'd1:S-3:H3'",
    )
    dD_parser.add_argument(
        "-d",
        default=today,
        help="Input date. The default format is "
        "%%Y-%%m-%%m"
        "." + " The format can be modifed through the -f flag",
    )
    dD_parser.add_argument(
        "-f",
        default=dstr,
        type=str,
        help="Format of the string passed to -d. If absent, -d defaults to "
        "%%Y-%%m-%%-%%m"
        "." + " Special formatting: " + " "
        "yearf"
        " -> fractional year " + " "
        "w-dow"
        " -> GPS Week-Day of Week. " + " "
        "w-sow"
        " -> GPS Week-Second of Week. " + " "
        "w-dow-sod"
        " -> GPS Week-Day of week-Second of day. "
        + "See datetime documentation for general formatting",
    )

    # parse what has -d, -f and -D to use as input for other options
    args, remaining_argv = dD_parser.parse_known_args()
    dstr = args.f

    # dealing with the input format.
    day = dday = timefunc.toDatetime(args.d, args.f)

    if args.shift:
        Shift = args.shift
    else:
        Shift = args.D

    day = day - datetime.timedelta(
        **timefunc.shifTime(Shift)
    )  # applying the Day offset
    # ----------------------------------------

    parser = argparse.ArgumentParser(
        parents=[dD_parser],
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Year flag -------------------
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v",
        "--version",
        action="version",
        version="0.3.3",  # Hardcoded version for development
        help="Show the version of the package",
    )
    group.add_argument(
        "-o",
        type=str,
        help=" Output format for general formatting defaults to "
        "%%a, %%d. %%b %%Y"
        "."
        + " See datetime documentation for the formatting."
        + " for special formatting see -f arguments",
    )
    group.add_argument(
        "-l",
        "--list",
        nargs="*",
        action="store",
        type=str,
        help="Return a list of strings according to the time formated string passed and the interval given"
        + "Special cases are: #b -> three letter lower case month %%b.lower() i.e. jan, "
        + "#gpsw -> gps week number in  wwww, "
        + "#Rin2 -> rinex 2 format %%j(session).%%y, "
        + "where session is a single character session identifier, "
        + "#8hRin2 -> special case of 8h rinex two files where Sessions are {0,1,2}) "
        + "Example:  /data/%%Y/#b/VONC/15s_24hr/rinex/VONC#Rin2O.Z -> "
        + "/data/2015/oct/VONC/15s_24hr/rinex/VONC2740.15O.Z \n"
        + "#datelist -> Specal case. list of dates one in a line. "
        + "Use -f to change the input format",
    )
    group.add_argument(
        "-p",
        type=str,
        help="Second input date, will calculate the number of days between the"
        + "input date from -d (or today) and the date given with -p."
        + "The default format is "
        "%%Y-%%m-%%m"
        "." + " The format can be modifed through the -f flag",
    )
    group.add_argument(
        "-y",
        type=int,
        nargs="?",
        const=timefunc.shlyear(yyyy=day.year, change=True),
        help="Returns the Year in "
        "YYYY"
        " form. Special case: If the year is passed directly"
        + "to -y it is converted to two/four digit form, depending on the input.",
    )
    group.add_argument(
        "-yy",
        action="store_true",
        help="Returns the Year from -d in two digit form ("
        "YY"
        "). " + "Current year is returned in two digit form if -d is omitted",
    )
    group.add_argument(
        "-yf",
        action="store_const",
        const=day,
        help="Return date from -d as fractional year. "
        + "Current date is returned if -d omitted",
    )
    group.add_argument(
        "-H",
        action="store_const",
        const=day,
        help="Return date from -d as an Hour of day ",
    )
    # flags for different output
    group.add_argument(
        "-t",
        action="store_const",
        const=day,
        help="Return a space seperated string of "
        + " (year, month, day of month, day of year, fractional year, GPS week,"
        + "day of week sunday = 0 ... 6 = saturday) -> "
        + "(YYYY MM DD DOY YYYY.ddd WWWW DOW) ",
    )
    group.add_argument(
        "-j", action="store_const", const=day, help="Return the day of year"
    )
    group.add_argument(
        "-ny",
        action="store_const",
        const=day,
        help="Return the number of days in thye year",
    )
    group.add_argument(
        "-w", "--week", action="store_const", const=day, help="Return GPS week"
    )
    group.add_argument(
        "-u",
        "--dayofw",
        action="store_const",
        const=day,
        help="Return day of GPS week sunday = 0 ... 6 = saturday ",
    )
    group.add_argument(
        "-wd",
        "--weekday",
        action="store_const",
        const=day,
        help="Return GPS week and day of GPS week sunday = 0 ... 6 = saturday ",
    )
    group.add_argument(
        "-ws",
        "--wsow",
        action="store_const",
        const=day,
        help="Return GPS week and Second of GPS week",
    )
    group.add_argument(
        "-i",
        "--datet",
        action="store_const",
        const=day,
        help="Returns the calendar date and time",
    )
    group.add_argument(
        "-r",
        "--rinex",
        const="d",
        nargs="?",
        choices=["H", "d"],
        help="return time part rinex standard hourly format format",
    )
    group.add_argument(
        "--GPST",
        const="all",
        nargs="?",
        choices=[
            "all",
            "w",
            "wdow",
            "dow",
            "wsow",
            "sow",
            "wdowsod",
            "dowsod",
            "dow",
            "sod",
        ],
        help="Return a different compinations of GPS time, GPS week (w), Second of week (sow)"
        + "Day of week (dow), Second of day (sod)",
    )
    args = parser.parse_args(args=remaining_argv)
    # ------------------------------

    # printing out stuff depending on args
    if args.y != None:
        print(timefunc.shlyear(yyyy=args.y, change=True))

    elif args.ny:
        print(timefunc.DaysinYear(day.year))

    elif args.yy:
        print(timefunc.shlyear(yyyy=day.year, change=True))

    elif args.yf:
        print(timefunc.currYearfDate(refday=day))

    elif args.H:
        print(day.hour)

    elif args.j:
        print(timefunc.currDate(refday=args.j, String="%j"))

    elif args.week:
        print(timefunc.gpsWeekDay(refday=args.week)[0])

    elif args.dayofw:
        print(timefunc.gpsWeekDay(refday=args.dayofw)[1])

    elif args.weekday:
        print("%04d %03d" % timefunc.gpsWeekDay(refday=args.weekday))

    elif args.GPST:
        (GPSW, SOW, DOW, SOD) = timefunc.gpsfDateTime(refday=day)

        if args.GPST == "all":
            print("{0:d} {1:.0f} {2:03d} {3:.0f}".format(GPSW, SOW, DOW, SOD))
        elif args.GPST == "w":
            print("{0:d}".format(GPSW, SOW, DOW, SOD))
        elif args.GPST == "wdow":
            print("{0:d} {2:03d}".format(GPSW, SOW, DOW, SOD))
        elif args.GPST == "dow":
            print("{2:03d}".format(GPSW, SOW, DOW, SOD))
        elif args.GPST == "wsow":
            print("{0:d} {1:.0f}".format(GPSW, SOW, DOW, SOD))
        elif args.GPST == "sow":
            print("{1:.0f}".format(GPSW, SOW, DOW, SOD))
        elif args.GPST == "wdowsod":
            print("{0:d} {2:03d} {3:.0f}".format(GPSW, SOW, DOW, SOD))
        elif args.GPST == "dowsod":
            print("{2:03d} {3:.0f}".format(GPSW, SOW, DOW, SOD))
        elif args.GPST == "sod":
            print("{3:.0f}".format(GPSW, SOW, DOW, SOD))

    elif args.wsow:
        print("{0:d}-{1:.0f}".format(*timefunc.gpsfDateTime(refday=day)[0:2]))

    elif args.datet:
        print(day.isoformat())

    elif args.t:
        print(
            "%d %02d %02d %03d %4.5f %04d %d %d %02d %s"
            % timefunc.dateTuple(refday=args.t)
        )

    elif args.o:
        print(day.strftime(args.o))

    elif args.list:
        # error check for argument --list
        if len(args.list) not in (2, 3):
            parser.error("Either give two or three arguments with --list")
        else:
            if len(args.list) == 2:  # the default for list[2]
                args.list.append("right")

            if args.list[2] not in {"left", "right"}:
                args.list[2] = None

            stringlist = timefunc.datepathlist(
                args.list[0], args.list[1], day, dday, closed=args.list[2]
            )

            datelistmatch = re.compile(r"\w*(#datelist)\w*").search(args.list[0])
            if datelistmatch:
                stringlist = [i.strftime("{0}\n".format(dstr)) for i in stringlist]

            [sys.stdout.write(item) for item in stringlist]
            sys.stdout.write("\n")  # to start with a newline after printing the list

    elif args.p:
        # dealing with the input format.
        day1 = timefunc.toDatetime(args.p, dstr)
        if dstr == "yearf":
            print((day - day1))
        else:
            print((day - day1).days)

    elif args.rinex:
        if args.rinex == "H":
            hour = timefunc.hourABC(day.hour)
        elif args.rinex == "d":
            hour = 0

        doy = int(day.strftime("%j"))
        yr = int(day.strftime("%y"))
        print("%.3d%s.%.2d" % (doy, hour, yr))

    else:
        print(day.strftime(outpstr))


if __name__ == "__main__":
    main()
