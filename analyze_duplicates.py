#!/usr/bin/env python3

import pandas as pd
import glob
import os
from datetime import datetime

def analyze_duplicates():
    # Find all CSV files
    sep25_files = glob.glob('./Sep 25/*.csv')
    sep26_files = glob.glob('./Sep 26/*.csv')
    sep25_files = [f for f in sep25_files if 'unique_missions.csv' not in f]
    all_files = sep25_files + sep26_files

    # Combine all data
    all_data = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            df['source_file'] = file  # Track which file each row came from
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"Total points loaded: {len(combined_df)}")

    # Let's try different duplicate detection strategies

    # 1. Check for exact duplicates (all columns)
    exact_dups = combined_df.duplicated()
    print(f"\n1. Exact duplicates (all columns): {exact_dups.sum()}")

    # 2. Check duplicates excluding time
    columns_no_time = [col for col in combined_df.columns if col not in ['time', 'source_file']]
    dups_no_time = combined_df.duplicated(subset=columns_no_time)
    print(f"2. Duplicates excluding time: {dups_no_time.sum()}")

    # 3. Check duplicates based on coordinates only
    coord_columns = ['originalLongitude', 'originalLatitude', 'originalAltitude']
    coord_dups = combined_df.duplicated(subset=coord_columns)
    print(f"3. Duplicates based on coordinates: {coord_dups.sum()}")

    # 4. Check duplicates based on rover position
    rover_columns = ['roverPositionLongitude', 'roverPositionLatitude', 'roverPositionAltitude']
    rover_dups = combined_df.duplicated(subset=rover_columns)
    print(f"4. Duplicates based on rover position: {rover_dups.sum()}")

    # 5. Check duplicates based on id
    id_dups = combined_df.duplicated(subset=['id'])
    print(f"5. Duplicates based on id: {id_dups.sum()}")

    # 6. Check duplicates based on name (point number)
    name_dups = combined_df.duplicated(subset=['name'])
    print(f"6. Duplicates based on name/point number: {name_dups.sum()}")

    # Let's look at some potential duplicates more closely
    if coord_dups.sum() > 0:
        print(f"\nSample coordinate duplicates:")
        dup_coords = combined_df[coord_dups]
        for idx, row in dup_coords.head(3).iterrows():
            original_idx = combined_df[
                (combined_df['originalLongitude'] == row['originalLongitude']) &
                (combined_df['originalLatitude'] == row['originalLatitude']) &
                (combined_df['originalAltitude'] == row['originalAltitude'])
            ].index.tolist()
            print(f"  Coordinate {row['originalLongitude']}, {row['originalLatitude']} appears in rows: {original_idx}")
            print(f"  From files: {combined_df.loc[original_idx, 'source_file'].unique()}")

    if name_dups.sum() > 0:
        print(f"\nSample name/point number duplicates:")
        dup_names = combined_df[name_dups]
        for idx, row in dup_names.head(3).iterrows():
            same_name_rows = combined_df[combined_df['name'] == row['name']]
            print(f"  Point {row['name']} appears {len(same_name_rows)} times")
            print(f"  From files: {same_name_rows['source_file'].unique()}")

    # Let's also check if there are near-duplicate coordinates (within small tolerance)
    print(f"\nChecking for near-duplicate coordinates (tolerance: 0.000001 degrees)...")
    tolerance = 0.000001
    near_dups = 0

    # This is a simplified check - in practice you'd want something more efficient
    for i, row1 in combined_df.iterrows():
        for j, row2 in combined_df.iterrows():
            if i < j:  # Only check each pair once
                if (abs(row1['originalLongitude'] - row2['originalLongitude']) < tolerance and
                    abs(row1['originalLatitude'] - row2['originalLatitude']) < tolerance and
                    abs(row1['originalAltitude'] - row2['originalAltitude']) < tolerance):
                    near_dups += 1
                    if near_dups <= 5:  # Show first few
                        print(f"  Near duplicate: Row {i} and {j}")
                        print(f"    Files: {row1['source_file']} vs {row2['source_file']}")
                        print(f"    Coords: ({row1['originalLongitude']}, {row1['originalLatitude']}) vs ({row2['originalLongitude']}, {row2['originalLatitude']})")

    print(f"Total near-duplicates found: {near_dups}")

    return combined_df

if __name__ == "__main__":
    analyze_duplicates()