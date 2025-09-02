# gtimes library and timecalc program

Collection of modules to handle time related conversions and string formatting. Handles GPS-time

### gtimes provides two sets of time modules gpstime and timefunc

- [gpstime](http://software.ligo.org/docs/glue/glue.gpstime-module.html#GpsSecondsFromPyUTC) - A Python implementation of GPS related time conversions by Bud P. Bruegger released under [GNU LESSER GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/lgpl.html)
- timefunc - Collection of time manipulation/string-coding functions using gpstime and [python datetime](https://docs.python.org/3/library/datetime.html)
- timecalc - A simple command line program, somewhat similar to date implementing gpstime and timefunc for GPS specific time conversions
  as well as none GPS specific

## Getting Started

### Installation instructions

1. Run "pip install ." which will install the gtimes module in the python domain
   - For system wide install you must be used with a privileged user (sudo/root)

#### Prerequisites

    * pip
    * python pandas
    * python-dateutil

### Development

For development and testing:

```bash
# Install with development dependencies
pip install -e .[dev]

# Run tests
python run_tests.py

# Run tests with quality checks
python run_tests.py --quality

# Run all tests including slow ones
python run_tests.py --slow
```

### Running examples

    * timecalc -D 10 -l "/%Y/#gpsw/#b/VONC#Rin2D.Z " 1D  -d 2015-10-01
        -> /2015/1863/sep/VONC2650.15D.Z /2015/1863/sep/VONC2660.15D.Z /2015/1863/sep/VONC2670.15D.Z /2015/1863/sep/VONC2680.15D.Z /2015/1863/sep/VONC2690.15D.Z /2015/1864/sep/VONC2700.15D.Z /2015/1864/sep/VONC2710.15D.Z /2015/1864/sep/VONC2720.15D.Z /2015/1864/sep/VONC2730.15D.Z /2015/1864/oct/VONC2740.15D.Z

    * timecalc -wd
        -> 2001 002
    * timecalc -wd -d 2016-10-1
        -> 1864 004

## Author

- **Benedikt G. Ófeigsson** - _<bgo@vedur.is>_ - [Icelandic Meteorological Office](http://en.vedur.is)

## License

## Acknowledgments
