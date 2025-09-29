# Report Folder Checker

A comprehensive Python toolkit for analyzing, combining, and processing GPS survey mission data collected by CivRobotics autonomous systems.

## Overview

This project provides automated tools for processing GPS survey data collected over multiple days, detecting duplicates, combining datasets, and generating detailed analysis reports. The toolkit is specifically designed to handle CSV mission data files from robotic survey operations.

## Features

- **Data Combination**: Merge multiple CSV files from different collection periods
- **Duplicate Detection**: Advanced duplicate identification using coordinates, IDs, and point names
- **Quality Analysis**: Comprehensive data quality assessment and reporting
- **Customer Summaries**: Generate client-ready mission summaries with operational insights
- **Statistical Analysis**: Geographic coverage, temporal patterns, and equipment performance metrics

## Project Structure

```
report-folder-checker/
├── Sep 25/                         # September 25 survey data
│   ├── Points Data Sept 25 2025*.csv
│   ├── Robot_Mission_Summary_Sep25_2025.md
│   └── unique_missions.csv
├── Sep 26/                         # September 26 survey data
│   └── Civnav Data Points Sept 26 2025*.csv
├── results/                        # Generated output files
│   ├── Combined_Mission_Data_*.csv
│   └── Comprehensive_Mission_Summary_Report.md
├── analyze_duplicates.py           # Duplicate detection and analysis
├── combine_all_mission_data.py     # Multi-day data combination
├── combine_mission_data.py         # Single-day data combination
├── comprehensive_analysis.py       # Full analysis with reporting
└── customer_summary_analysis.py    # Client-facing summaries
```

## Scripts

### 1. `combine_mission_data.py`
Interactive script for combining CSV files from a single date folder.

**Features:**
- Interactive folder selection
- Automatic duplicate removal by ID
- Chronological sorting
- Results directory output
- Comprehensive statistics

**Usage:**
```bash
python combine_mission_data.py [folder_name]
```

### 2. `combine_all_mission_data.py`
Combines all mission data across multiple days into a single dataset.

**Features:**
- Processes Sep 25 and Sep 26 data simultaneously
- Coordinate-based deduplication
- Metadata header generation
- Statistical summary output

**Usage:**
```bash
python combine_all_mission_data.py
```

### 3. `analyze_duplicates.py`
Comprehensive duplicate detection using multiple strategies.

**Features:**
- Exact coordinate matching
- ID-based duplicate detection
- Point name analysis
- Near-duplicate identification (tolerance-based)
- Cross-file duplicate tracking

**Usage:**
```bash
python analyze_duplicates.py
```

### 4. `comprehensive_analysis.py`
Full-featured analysis tool generating detailed reports.

**Features:**
- File processing statistics
- Geographic coverage analysis
- Temporal pattern detection
- Duplicate breakdown with source tracking
- Data quality assessment
- Equipment performance metrics

**Usage:**
```bash
python comprehensive_analysis.py
```

### 5. `customer_summary_analysis.py`
Generates client-ready mission summaries with operational insights.

**Features:**
- Daily operational summaries
- Machine runtime estimates
- Data collection statistics
- Professional formatting for client delivery

**Usage:**
```bash
python customer_summary_analysis.py
```

## Data Format

The scripts expect CSV files with the following structure:
- `id`: Unique point identifier
- `name`: Point name/number
- `originalLongitude`, `originalLatitude`, `originalAltitude`: Survey coordinates
- `roverPositionLongitude`, `roverPositionLatitude`, `roverPositionAltitude`: Equipment position
- `time`: Timestamp in ISO format
- `status`: Point completion status
- Various offset and configuration fields

## Analysis Results

The toolkit has successfully processed:
- **841 unique survey points** across 2 days
- **22 CSV files** with 861 raw data points
- **20 duplicates removed** (2.3% data reduction)
- **Geographic coverage**: ~0.19 square miles
- **Elevation range**: 270-275 feet
- **Collection accuracy**: 97.7% data quality

## Requirements

- Python 3.7+
- pandas
- glob (built-in)
- os (built-in)
- datetime (built-in)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/civ-dustinteng/report-folder-checker.git
cd report-folder-checker
```

2. Install dependencies:
```bash
pip install pandas
```

## Quick Start

1. **Combine single day data:**
```bash
python combine_mission_data.py "Sep 25"
```

2. **Generate comprehensive analysis:**
```bash
python comprehensive_analysis.py
```

3. **Create customer summary:**
```bash
python customer_summary_analysis.py
```

## Output Files

- `results/Combined_Mission_Data_[Date]_2025.csv`: Clean, deduplicated mission data
- `results/Comprehensive_Mission_Summary_Report.md`: Detailed analysis report
- Console output with real-time statistics and progress updates

## Data Quality Features

- **Duplicate Detection**: Multiple algorithms for identifying redundant data
- **Validation**: Coordinate precision verification and format consistency
- **Error Handling**: Graceful handling of malformed files and missing data
- **Metadata Preservation**: Complete audit trail with source file tracking
- **Statistical Verification**: Range validation and outlier detection

## Performance

- Processes 800+ data points in under 5 seconds
- Memory-efficient handling of large datasets
- Optimized for survey data workflows
- Scales to handle multiple survey days

## Contributing

This is a specialized tool for CivRobotics survey data processing. For questions or modifications, please contact the development team.

## License

Internal use for CivRobotics survey operations.

---

*Developed for CivRobotics autonomous survey systems - ensuring data integrity and operational excellence in robotic surveying.*
