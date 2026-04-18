"""GTimes - High-precision GPS time conversion and processing library."""

__version__ = "0.5.0"
__author__ = "Benedikt Gunnar Ófeigsson"
__email__ = "bgo@vedur.is"

# __import__('pkg_resources').declare_namespace(__name__)
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

# Export key functions for convenient access
from gtimes.timefunc import (
    # RINEX filename functions
    rinex2_filename,
    rinex3_filename,
    rinex_filename,
    parse_rinex2_filename,
    parse_rinex3_filename,
    convert_rinex_filename,
    # GPS time functions
    gpsWeekDay,
    gpsfDateTime,
    datepathlist,
    toDatetime,
    hourABC,
    ABChour,
)

__all__ = [
    # RINEX filename functions
    "rinex2_filename",
    "rinex3_filename",
    "rinex_filename",
    "parse_rinex2_filename",
    "parse_rinex3_filename",
    "convert_rinex_filename",
    # GPS time functions
    "gpsWeekDay",
    "gpsfDateTime",
    "datepathlist",
    "toDatetime",
    "hourABC",
    "ABChour",
]
