# GPS Time Concepts and Coordinate Systems

This document explains the fundamental GPS/GNSS concepts used in the gtimes library for geodetic and meteorological applications at Veðurstofan Íslands (Icelandic Met Office).

## GPS Time System

### GPS Epoch and Time Representation

**GPS Epoch**: January 6, 1980, 00:00:00 UTC

GPS time is a continuous time scale that started at the GPS epoch and is maintained by atomic clocks. Unlike UTC, GPS time does not include leap seconds, making it a uniform time scale ideal for precise positioning and timing applications.

### Key GPS Time Formats

#### 1. GPS Week and Seconds of Week (SOW)
- **GPS Week**: Integer weeks since GPS epoch (0 = January 6-12, 1980)
- **Seconds of Week**: 0-604799 seconds within the current GPS week
- **Week Start**: Saturday midnight (Sunday 00:00:00)

#### 2. GPS Day and Seconds of Day (SOD)
- **GPS Day**: Days since GPS epoch
- **Seconds of Day**: 0-86399 seconds within the current GPS day

#### 3. Fractional Year Format
- **Format**: YYYY.FFFFFFF (e.g., 2020.5 = middle of 2020)
- **Usage**: Common in GAMIT/GLOBK time series analysis
- **Precision**: Sub-second accuracy possible

### Leap Seconds in GPS

GPS time and UTC diverge due to leap seconds:
- **1980**: GPS time = UTC (at GPS epoch)
- **2024**: GPS time = UTC + 18 seconds

The gtimes library automatically handles leap second calculations based on the date, using an internal leap second table that includes historical leap second events.

## Coordinate Reference Frames

### Primary Reference Frames Used

#### 1. ITRF2008 (EPSG:5332)
- **Description**: International Terrestrial Reference Frame 2008
- **Usage**: Primary reference frame for precise geodetic applications
- **Characteristics**: Earth-centered, Earth-fixed (ECEF) coordinate system

#### 2. WGS84 (EPSG:4326)
- **Description**: World Geodetic System 1984
- **Usage**: Standard GPS coordinates (latitude, longitude, height)
- **Compatibility**: Closely aligned with ITRF for most applications

#### 3. ISN93 (EPSG:3057)
- **Description**: Icelandic National Grid 1993
- **Usage**: Local mapping and surveying in Iceland
- **Projection**: Lambert Conformal Conic

#### 4. ISN2004 (EPSG:5322)
- **Description**: Icelandic National Grid 2004
- **Usage**: Updated local coordinate system for Iceland
- **Improvements**: Better accuracy for modern GPS applications

## RINEX Format Support

### RINEX (Receiver Independent Exchange Format)

RINEX is the standard format for GPS/GNSS observation and navigation data exchange.

#### Filename Conventions
- **Daily files**: `SSSSDDDF.YYt` (e.g., `REYK0010.20O`)
  - `SSSS`: 4-character station ID
  - `DDD`: Day of year (001-366)
  - `F`: File sequence (0 for daily)
  - `YY`: 2-digit year
  - `t`: File type (O=observation, N=navigation)

#### Special gtimes Extensions
The library supports GPS-specific formatting tokens:
- `#gpsw`: GPS week number
- `#b`: Lowercase month name
- `#Rin2`: RINEX 2.x day-of-year format
- `#8hRin2`: 8-hour session format

## Icelandic GPS Network

### Station Codes and Locations

Common Icelandic GPS stations supported by gtimes:
- **REYK**: Reykjavik (capital region)
- **HOFN**: Höfn (southeast Iceland)  
- **AKUR**: Akureyri (north Iceland)
- **VMEY**: Vestmannaeyjar (Westman Islands)
- **HVER**: Hveragerði (south Iceland)
- **OLKE**: Ólafsvík (west Iceland)
- **SKRO**: Skrokkalda (northeast Iceland)

### Processing Workflows

#### Daily Processing
1. **Data Collection**: Automatic download of RINEX files
2. **Quality Control**: Validation using gtimes functions
3. **Time Conversion**: GPS time to analysis epochs
4. **Processing**: GAMIT/GLOBK analysis with fractional year output

#### Real-Time Monitoring
- **GPS Week/SOW**: For real-time positioning
- **Leap Second Handling**: Automatic UTC/GPS conversion
- **Quality Metrics**: Data availability and precision monitoring

## Scientific Applications

### Plate Tectonics Studies
- **EURA Plate**: Eurasian plate motion parameters
- **NOAM Plate**: North American plate motion
- **Transform Zones**: Mid-Atlantic Ridge studies

### Seismic and Volcanic Monitoring
- **Co-seismic Displacement**: Earthquake-related position changes
- **Inter-seismic Motion**: Long-term tectonic motion
- **Volcanic Deformation**: Inflation/deflation monitoring

### Meteorological Applications
- **Precipitable Water Vapor**: GPS-derived atmospheric moisture
- **Tropospheric Delay**: Atmospheric correction parameters
- **Weather Model Validation**: GPS observations vs. numerical models

## Usage Examples

### Basic Time Conversions

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps

# Convert UTC to GPS time
gps_week, sow, gps_day, sod = gpsFromUTC(2020, 1, 1, 12, 0, 0)
print(f"GPS Week: {gps_week}, SOW: {sow}")

# Convert back to UTC
utc_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
print(f"UTC: {utc_dt}")
```

### Fractional Year Processing

```python
from gtimes.timefunc import dTimetoYearf, TimefromYearf
import datetime

# Convert datetime to fractional year (GAMIT format)
dt = datetime.datetime(2020, 6, 15, 12, 0, 0)
yearf = dTimetoYearf(dt)
print(f"Fractional year: {yearf:.6f}")

# Convert back to datetime
recovered_dt = TimefromYearf(yearf)
print(f"Recovered: {recovered_dt}")
```

### RINEX Filename Generation

```python
from gtimes.timefunc import datepathlist
import datetime

# Generate daily RINEX filenames for a station
start_date = datetime.datetime(2020, 1, 1)
filenames = datepathlist(
    stringformat="REYK%j0.%yO",
    lfrequency="1D", 
    starttime=start_date,
    periods=7
)

for filename in filenames:
    print(filename)
# Output: REYK0010.20O, REYK0020.20O, etc.
```

## References

- **GPS Time**: [Naval Observatory GPS Time](http://www.oc.nps.navy.mil/~jclynch/timsys.html)
- **RINEX Format**: [IGS RINEX Specification](https://files.igs.org/pub/data/format/rinex305.pdf)
- **GAMIT/GLOBK**: [MIT GPS Analysis Software](http://geoweb.mit.edu/gg/)
- **ITRF**: [International Terrestrial Reference Frame](https://itrf.ign.fr/)

## Support and Maintenance

This documentation is maintained as part of the gtimes library at Veðurstofan Íslands. 

For questions or issues:
- Technical: Review CLAUDE.md in the repository
- Scientific: Consult GPS/GNSS processing literature
- Local context: Icelandic Met Office GPS team