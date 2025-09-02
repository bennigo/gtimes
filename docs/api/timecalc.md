# Command Line Interface API

The `gtimes.timecalc` module provides a powerful command-line interface for GPS time calculations and conversions. The main entry point is the `timecalc` command.

## Overview

The `timecalc` command-line tool provides quick access to GPS time conversions, date arithmetic, and file path generation directly from the shell. This is particularly useful for shell scripts, data processing pipelines, and quick calculations.

## Main Function

::: gtimes.timecalc.main
    options:
      show_source: true
      heading_level: 3

## Command-Line Options

### Basic Usage

```bash
timecalc [OPTIONS]
```

### Date Input Options

| Option | Description | Example |
|--------|-------------|---------|
| `-d DATE` | Input date (default: today) | `-d "2024-01-15"` |
| `-f FORMAT` | Input date format | `-f "%Y/%m/%d"` |
| `-D DAYS` | Add/subtract days | `-D 7` (add 7 days) |
| `--shift SHIFT` | Complex time shifts | `--shift "d5:H12:M30"` |

### Output Options

| Option | Description | Output Format |
|--------|-------------|---------------|
| `-wd, --weekday` | GPS week and day | `2297 001` |
| `-w, --week` | GPS week only | `2297` |
| `-u, --dayofw` | GPS day of week | `1` (Monday) |
| `-j` | Day of year | `015` |
| `-yf` | Fractional year | `2024.038356` |
| `-y YEAR` | Year conversion | 4-digit ↔ 2-digit |
| `-o FORMAT` | Custom format | User-defined |

### Time Information

| Option | Description | Output |
|--------|-------------|--------|
| `-t` | Complete time tuple | Year, month, day, DOY, yearf, GPS week, DOW |
| `-i, --datet` | ISO datetime | `2024-01-15T12:30:45` |
| `--GPST [TYPE]` | GPS time components | Various GPS time formats |
| `-H` | Hour of day | `14` |

### File Generation

| Option | Description | Usage |
|--------|-------------|-------|
| `-l, --list PATTERN FREQ [CLOSED]` | Generate file lists | `-l "REYK%j0.%yO" "1D"` |
| `-r, --rinex [H\|d]` | RINEX time format | `-r d` for daily |

### Utility Options

| Option | Description |
|--------|-------------|
| `-v, --version` | Show version |
| `-p DATE2` | Days between dates |
| `-ny` | Number of days in year |

## Usage Examples

### Basic GPS Time Queries

```bash
# Get current GPS week and day
timecalc -wd
# Output: 2297 001

# GPS time for specific date
timecalc -wd -d "2024-01-15"
# Output: 2297 001

# Get fractional year
timecalc -yf -d "2024-07-01"
# Output: 2024.497260

# Get day of year
timecalc -j -d "2024-01-15"
# Output: 015
```

### Date Arithmetic

```bash
# Add 30 days to a date
timecalc -D 30 -d "2024-01-15"
# Output: Mon, 14. Feb 2024

# Subtract 7 days
timecalc -D -7 -d "2024-01-15"
# Output: Mon, 08. Jan 2024

# Complex time shifts
timecalc --shift "d5:H12:M-30" -d "2024-01-15 10:00:00"
# Output: Sat, 20. Jan 2024 21:30:00

# Calculate days between dates
timecalc -p "2024-01-20" -d "2024-01-15"
# Output: 5
```

### File List Generation

```bash
# Generate daily RINEX observation files
timecalc -l "REYK%j0.%yO" "1D" -d "2024-01-15"
# Output:
# REYK0150.24O
# REYK0160.24O
# REYK0170.24O

# Generate hourly files for one day
timecalc -l "HOFN%j%H.%yO" "1H" -d "2024-01-15"
# Output:
# HOFN015a.24O
# HOFN015b.24O
# HOFN015c.24O
# ... (24 files total)

# Generate weekly processing directories
timecalc -l "/gps_proc/%Y/week_%U/" "7D" -d "2024-01-01"
# Output:
# /gps_proc/2024/week_01/
# /gps_proc/2024/week_02/
# /gps_proc/2024/week_03/
```

### Custom Formatting

```bash
# Custom date format output
timecalc -o "%Y%m%d_%H%M%S" -d "2024-01-15 14:30:45"
# Output: 20240115_143045

# ISO format
timecalc -i -d "2024-01-15 14:30:45"
# Output: 2024-01-15T14:30:45

# Complete time tuple
timecalc -t -d "2024-01-15"
# Output: 2024 01 15 015 2024.03836 2297 1 0 0 Mon, 15. Jan 2024
```

### GPS Time Components

```bash
# All GPS time components
timecalc --GPST all -d "2024-01-15 12:30:45"
# Output: 2297 216645 001 45045

# Just GPS week
timecalc --GPST w -d "2024-01-15"
# Output: 2297

# Week and day of week
timecalc --GPST wdow -d "2024-01-15"
# Output: 2297 001

# Seconds of week
timecalc --GPST sow -d "2024-01-15 12:30:45"
# Output: 216645
```

### RINEX Time Formats

```bash
# Daily RINEX format
timecalc -r d -d "2024-01-15"
# Output: 0150.24

# Hourly RINEX format
timecalc -r H -d "2024-01-15 14:00:00"
# Output: 015n.24
```

## Advanced Usage

### Shell Script Integration

```bash
#!/bin/bash
# GPS processing script

STATION="REYK"
START_DATE="2024-01-15"
NUM_DAYS=7

# Get GPS week for processing organization
GPS_WEEK=$(timecalc -w -d "$START_DATE")
echo "Processing GPS week: $GPS_WEEK"

# Generate list of RINEX files to process
echo "RINEX files to process:"
timecalc -l "${STATION}%j0.%yO" "${NUM_DAYS}D" -d "$START_DATE"

# Create processing directory
PROC_DIR="/gps_proc/$(timecalc -o "%Y/%j" -d "$START_DATE")"
echo "Processing directory: $PROC_DIR"

# Get fractional year for GAMIT
YEARF=$(timecalc -yf -d "$START_DATE")
echo "GAMIT fractional year: $YEARF"
```

### Date Range Processing

```bash
#!/bin/bash
# Process GPS data for a date range

START="2024-01-01"
END="2024-01-07"

# Calculate number of days
DAYS=$(timecalc -p "$END" -d "$START")
echo "Processing $DAYS days of data"

# Generate daily processing commands
for ((i=0; i<=$DAYS; i++)); do
    DATE=$(timecalc -D $i -d "$START" -o "%Y-%m-%d")
    DOY=$(timecalc -D $i -d "$START" -j)
    GPS_WD=$(timecalc -D $i -d "$START" -wd)
    
    echo "Day $i: $DATE (DOY $DOY, GPS $GPS_WD)"
done
```

### Batch File Generation

```bash
#!/bin/bash
# Generate RINEX files for multiple stations

STATIONS=("REYK" "HOFN" "AKUR" "VMEY")
DATE="2024-01-15"
DURATION="7D"

for STATION in "${STATIONS[@]}"; do
    echo "Files for $STATION:"
    
    # Observation files
    echo "  Observation files:"
    timecalc -l "    ${STATION}%j0.%yO" "$DURATION" -d "$DATE"
    
    # Navigation files
    echo "  Navigation files:"
    timecalc -l "    ${STATION}%j0.%yN" "$DURATION" -d "$DATE"
    
    echo
done
```

### Data Quality Checks

```bash
#!/bin/bash
# Validate GPS observation times

check_gps_time() {
    local datetime="$1"
    
    # Check if date converts to valid GPS time
    if GPS_TIME=$(timecalc -wd -d "$datetime" 2>/dev/null); then
        GPS_WEEK=$(echo $GPS_TIME | cut -d' ' -f1)
        GPS_DAY=$(echo $GPS_TIME | cut -d' ' -f2)
        
        if [[ $GPS_WEEK -gt 0 && $GPS_DAY -ge 0 && $GPS_DAY -le 6 ]]; then
            echo "VALID: $datetime -> GPS Week $GPS_WEEK, Day $GPS_DAY"
            return 0
        fi
    fi
    
    echo "INVALID: $datetime"
    return 1
}

# Test various timestamps
TEST_TIMES=(
    "2024-01-15 12:30:45"
    "1970-01-01 00:00:00"  # Before GPS epoch
    "2024-02-29 12:00:00"  # Valid leap day
    "2023-02-29 12:00:00"  # Invalid leap day
)

echo "GPS Time Validation Results:"
for time in "${TEST_TIMES[@]}"; do
    check_gps_time "$time"
done
```

## Error Handling

The `timecalc` command provides informative error messages for invalid inputs:

```bash
# Invalid date
timecalc -wd -d "2024-13-01"
# Output: Error: Invalid date format

# Invalid format string
timecalc -d "15/01/2024" -f "%Y-%m-%d"
# Output: Error: Date does not match format

# Invalid options combination
timecalc -wd -yf
# Output: Error: Mutually exclusive options
```

## Input Formats

### Date Format Specifiers

The `-f` option accepts standard `strftime` format codes plus GPS-specific extensions:

| Format | Description | Example |
|--------|-------------|---------|
| `%Y` | 4-digit year | 2024 |
| `%y` | 2-digit year | 24 |
| `%m` | Month (01-12) | 01 |
| `%d` | Day (01-31) | 15 |
| `%j` | Day of year (001-366) | 015 |
| `%H` | Hour (00-23) | 14 |
| `%M` | Minute (00-59) | 30 |
| `%S` | Second (00-59) | 45 |
| `yearf` | Fractional year | 2024.038356 |
| `w-dow` | GPS Week-Day of Week | 2297-1 |
| `w-sow` | GPS Week-Seconds of Week | 2297-216645 |

### Special Format Codes

For file generation (`-l` option), additional format codes are available:

| Code | Description | Output |
|------|-------------|--------|
| `#gpsw` | GPS week (4 digits) | 2297 |
| `#Rin2` | RINEX 2 format | 0150.24 |
| `#8hRin2` | 8-hour RINEX sessions | 015a.24, 015b.24, 015c.24 |
| `#b` | Lowercase month abbreviation | jan, feb, mar |
| `#datelist` | Date list format | One date per line |

## Integration with Python

The command-line tool can be used from Python scripts:

```python
import subprocess
import json

def run_timecalc(args):
    """Run timecalc command and return output."""
    cmd = ['timecalc'] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"timecalc failed: {result.stderr}")
    
    return result.stdout.strip()

# Examples
gps_week_day = run_timecalc(['-wd', '-d', '2024-01-15'])
print(f"GPS Week/Day: {gps_week_day}")

fractional_year = run_timecalc(['-yf', '-d', '2024-07-01'])
print(f"Fractional year: {fractional_year}")

# Generate file list
file_list = run_timecalc(['-l', 'REYK%j0.%yO', '3D', '-d', '2024-01-15'])
files = file_list.split('\n')
print(f"Generated files: {files}")
```

The `timecalc` command-line interface provides powerful GPS time processing capabilities directly from the shell, making it ideal for automation, scripting, and quick calculations.