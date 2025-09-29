#!/usr/bin/env python3

import pandas as pd
import glob
import os
from datetime import datetime

def combine_all_mission_data():
    # Find all CSV files in Sep 25 and Sep 26 directories
    sep25_files = glob.glob('./Sep 25/*.csv')
    sep26_files = glob.glob('./Sep 26/*.csv')

    # Filter out the unique_missions.csv file from Sep 25
    sep25_files = [f for f in sep25_files if 'unique_missions.csv' not in f]

    all_files = sep25_files + sep26_files

    print(f"Found {len(all_files)} CSV files to process:")
    for file in sorted(all_files):
        print(f"  {file}")

    # Combine all data
    all_data = []
    total_original_points = 0

    for file in all_files:
        try:
            print(f"\nProcessing: {file}")
            df = pd.read_csv(file)
            print(f"  Loaded {len(df)} points")
            total_original_points += len(df)
            all_data.append(df)
        except Exception as e:
            print(f"  Error reading {file}: {e}")

    if not all_data:
        print("No data found to combine!")
        return

    # Concatenate all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal points before duplicate removal: {len(combined_df)}")

    # Remove duplicates using a more appropriate strategy
    # We'll use coordinates as the primary duplicate detection method since
    # the same survey point might be recorded multiple times with different timestamps

    before_dedup = len(combined_df)

    # Strategy 1: Remove exact coordinate duplicates
    coord_columns = ['originalLongitude', 'originalLatitude', 'originalAltitude']
    print(f"Duplicates based on coordinates: {combined_df.duplicated(subset=coord_columns).sum()}")

    # Strategy 2: Also check for ID duplicates
    id_duplicates = combined_df.duplicated(subset=['id']).sum()
    print(f"Duplicates based on ID: {id_duplicates}")

    # Strategy 3: Check for point name duplicates
    name_duplicates = combined_df.duplicated(subset=['name']).sum()
    print(f"Duplicates based on point name: {name_duplicates}")

    # Use coordinate-based deduplication as it's most reliable for survey points
    combined_df_dedup = combined_df.drop_duplicates(subset=coord_columns, keep='first')
    after_dedup = len(combined_df_dedup)
    duplicates_removed = before_dedup - after_dedup

    print(f"Points after duplicate removal: {after_dedup}")
    print(f"Duplicates removed: {duplicates_removed}")

    # Sort by time
    combined_df_dedup = combined_df_dedup.sort_values('time').reset_index(drop=True)

    # Create output directory if it doesn't exist
    os.makedirs('results', exist_ok=True)

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create output filename
    output_file = f'results/Combined_Mission_Data_All_Days_{datetime.now().strftime("%b%d_%Y")}.csv'

    # Write header with metadata
    with open(output_file, 'w') as f:
        f.write(f"# Mission Data Summary - All Days\n")
        f.write(f"# Total Survey Points: {after_dedup}\n")
        f.write(f"# Original Points Before Deduplication: {before_dedup}\n")
        f.write(f"# Duplicates Removed: {duplicates_removed}\n")
        f.write(f"# Files Processed: {len(all_files)}\n")
        f.write(f"# Generated: {timestamp}\n")
        f.write("#\n")

    # Append the CSV data
    combined_df_dedup.to_csv(output_file, mode='a', index=False)

    print(f"\nCombined data saved to: {output_file}")
    print(f"\nSummary:")
    print(f"  Files processed: {len(all_files)}")
    print(f"  Total original points: {before_dedup}")
    print(f"  Final points: {after_dedup}")
    print(f"  Duplicates removed: {duplicates_removed}")

    return output_file

if __name__ == "__main__":
    combine_all_mission_data()