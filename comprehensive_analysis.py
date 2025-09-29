#!/usr/bin/env python3

import pandas as pd
import glob
import os
from datetime import datetime
from collections import Counter

def comprehensive_analysis():
    # Find all CSV files
    sep25_files = glob.glob('./Sep 25/*.csv')
    sep26_files = glob.glob('./Sep 26/*.csv')
    sep25_files = [f for f in sep25_files if 'unique_missions.csv' not in f]
    all_files = sep25_files + sep26_files

    print("=" * 80)
    print("COMPREHENSIVE MISSION DATA ANALYSIS REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Load all data with source tracking
    all_data = []
    file_stats = {}

    print("FILE PROCESSING SUMMARY:")
    print("-" * 50)

    for file in sorted(all_files):
        try:
            df = pd.read_csv(file)
            df['source_file'] = file
            all_data.append(df)

            # Extract date from filename
            if 'Sep 25' in file:
                date = 'Sep 25, 2025'
            elif 'Sep 26' in file:
                date = 'Sep 26, 2025'
            else:
                date = 'Unknown'

            file_stats[file] = {
                'points': len(df),
                'date': date,
                'first_time': df['time'].min() if 'time' in df.columns else 'N/A',
                'last_time': df['time'].max() if 'time' in df.columns else 'N/A'
            }

            print(f"{file:<50} | {len(df):>4} points | {date}")

        except Exception as e:
            print(f"ERROR - {file}: {e}")

    combined_df = pd.concat(all_data, ignore_index=True)

    print()
    print("OVERALL STATISTICS:")
    print("-" * 50)
    print(f"Total files processed: {len(all_files)}")
    print(f"Sep 25 files: {len([f for f in all_files if 'Sep 25' in f])}")
    print(f"Sep 26 files: {len([f for f in all_files if 'Sep 26' in f])}")
    print(f"Total raw data points: {len(combined_df)}")

    # Time range analysis
    if 'time' in combined_df.columns:
        combined_df['datetime'] = pd.to_datetime(combined_df['time'])
        print(f"Data collection period: {combined_df['datetime'].min()} to {combined_df['datetime'].max()}")

        # Daily breakdown
        combined_df['date'] = combined_df['datetime'].dt.date
        daily_counts = combined_df['date'].value_counts().sort_index()
        print(f"Points by date:")
        for date, count in daily_counts.items():
            print(f"  {date}: {count} points")

    print()
    print("DUPLICATE ANALYSIS:")
    print("-" * 50)

    # Different types of duplicate analysis
    coord_columns = ['originalLongitude', 'originalLatitude', 'originalAltitude']

    # Find coordinate duplicates
    coord_dups = combined_df.duplicated(subset=coord_columns, keep=False)
    coord_dup_groups = combined_df[coord_dups].groupby(coord_columns)

    print(f"Total duplicate survey points: {combined_df.duplicated(subset=coord_columns).sum()}")
    print(f"Unique locations with duplicates: {len(coord_dup_groups)}")

    # ID duplicates
    id_dups = combined_df.duplicated(subset=['id'], keep=False)
    id_dup_groups = combined_df[id_dups].groupby('id')
    print(f"Duplicate IDs: {combined_df.duplicated(subset=['id']).sum()}")

    # Name duplicates
    name_dups = combined_df.duplicated(subset=['name'], keep=False)
    name_dup_groups = combined_df[name_dups].groupby('name')
    print(f"Duplicate point names: {combined_df.duplicated(subset=['name']).sum()}")

    print()
    print("DETAILED DUPLICATE BREAKDOWN:")
    print("-" * 50)

    dup_details = []

    for coords, group in coord_dup_groups:
        if len(group) > 1:
            lon, lat, alt = coords
            source_files = group['source_file'].unique()
            times = group['time'].tolist() if 'time' in group.columns else ['N/A'] * len(group)
            names = group['name'].unique()
            ids = group['id'].unique()

            dup_details.append({
                'longitude': lon,
                'latitude': lat,
                'altitude': alt,
                'occurrences': len(group),
                'source_files': list(source_files),
                'point_names': list(names),
                'point_ids': list(ids),
                'times': times
            })

    # Sort by number of occurrences (most duplicated first)
    dup_details.sort(key=lambda x: x['occurrences'], reverse=True)

    print(f"Found {len(dup_details)} coordinate locations with duplicates:")
    print()

    for i, dup in enumerate(dup_details, 1):
        print(f"DUPLICATE #{i}:")
        print(f"  Coordinates: ({dup['longitude']:.6f}, {dup['latitude']:.6f}, {dup['altitude']:.2f})")
        print(f"  Occurrences: {dup['occurrences']} times")
        print(f"  Point Names: {', '.join(map(str, dup['point_names']))}")
        print(f"  Point IDs: {', '.join(dup['point_ids'])}")
        print(f"  Source Files: {', '.join([os.path.basename(f) for f in dup['source_files']])}")
        if dup['times'][0] != 'N/A':
            print(f"  Timestamps: {', '.join(dup['times'])}")
        print()

    # File-specific duplicate analysis
    print("DUPLICATES BY SOURCE FILE:")
    print("-" * 50)

    file_dup_counts = {}
    for file in all_files:
        file_data = combined_df[combined_df['source_file'] == file]
        file_coord_dups = file_data.duplicated(subset=coord_columns).sum()
        file_dup_counts[file] = file_coord_dups
        if file_coord_dups > 0:
            print(f"{os.path.basename(file)}: {file_coord_dups} internal duplicates")

    if not any(file_dup_counts.values()):
        print("No internal duplicates found within individual files.")
        print("All duplicates are cross-file duplicates.")

    # Final deduplication
    print()
    print("FINAL RESULTS AFTER DEDUPLICATION:")
    print("-" * 50)

    before_dedup = len(combined_df)
    combined_df_clean = combined_df.drop_duplicates(subset=coord_columns, keep='first')
    after_dedup = len(combined_df_clean)
    duplicates_removed = before_dedup - after_dedup

    print(f"Original total points: {before_dedup}")
    print(f"Final unique points: {after_dedup}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Data reduction: {(duplicates_removed/before_dedup)*100:.1f}%")

    # Geographic coverage
    print()
    print("GEOGRAPHIC COVERAGE:")
    print("-" * 50)

    lon_range = combined_df_clean['originalLongitude'].max() - combined_df_clean['originalLongitude'].min()
    lat_range = combined_df_clean['originalLatitude'].max() - combined_df_clean['originalLatitude'].min()
    alt_range = combined_df_clean['originalAltitude'].max() - combined_df_clean['originalAltitude'].min()

    print(f"Longitude range: {combined_df_clean['originalLongitude'].min():.6f} to {combined_df_clean['originalLongitude'].max():.6f} ({lon_range:.6f}°)")
    print(f"Latitude range: {combined_df_clean['originalLatitude'].min():.6f} to {combined_df_clean['originalLatitude'].max():.6f} ({lat_range:.6f}°)")
    print(f"Altitude range: {combined_df_clean['originalAltitude'].min():.2f} to {combined_df_clean['originalAltitude'].max():.2f} ft ({alt_range:.2f} ft)")

    # Point naming analysis
    print()
    print("POINT NAMING ANALYSIS:")
    print("-" * 50)

    point_numbers = combined_df_clean['name'].astype(str)
    print(f"Point number range: {point_numbers.min()} to {point_numbers.max()}")
    print(f"Unique point names: {combined_df_clean['name'].nunique()}")

    # Status analysis
    if 'status' in combined_df_clean.columns:
        status_counts = combined_df_clean['status'].value_counts()
        print(f"Point status distribution:")
        for status, count in status_counts.items():
            print(f"  Status {status}: {count} points")

    print()
    print("=" * 80)
    print("END OF COMPREHENSIVE ANALYSIS")
    print("=" * 80)

    return combined_df_clean, dup_details

if __name__ == "__main__":
    comprehensive_analysis()