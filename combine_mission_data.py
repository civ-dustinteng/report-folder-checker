#!/usr/bin/env python3
"""
Mission Data Combiner
Combines multiple CSV mission files and removes duplicates based on ID field.
"""

import pandas as pd
import glob
import os
import sys
from pathlib import Path

def get_available_date_folders(base_path='.'):
    """Get list of available date folders."""
    folders = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and item.startswith('Sep '):
            folders.append(item)
    return sorted(folders)

def combine_mission_files(folder_path='.', output_to_results=True):
    """
    Combines all CSV files in the specified folder and removes duplicates by ID.

    Args:
        folder_path (str): Path to folder containing CSV files (default: current directory)
        output_to_results (bool): Whether to save output to results folder

    Returns:
        str: Path to the output file
    """

    # Find all CSV files with flexible pattern
    csv_patterns = [
        os.path.join(folder_path, "Points Data Sept*.csv"),
        os.path.join(folder_path, "Points Data Sep*.csv"),
        os.path.join(folder_path, "*.csv")
    ]

    csv_files = []
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        if files:
            csv_files = files
            break

    if not csv_files:
        print(f"No CSV files found matching pattern in {folder_path}")
        return None

    print(f"Found {len(csv_files)} CSV files:")
    for file in sorted(csv_files):
        print(f"  - {os.path.basename(file)}")

    # Read and combine all CSV files
    all_dataframes = []
    file_source_info = []  # Track which file each record came from
    total_records = 0

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            filename = os.path.basename(file)
            print(f"Loaded {len(df)} records from {filename}")

            # Add source file info to each record
            df['_source_file'] = filename
            all_dataframes.append(df)
            total_records += len(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue

    if not all_dataframes:
        print("No valid CSV files could be read")
        return None

    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"\nTotal records before deduplication: {len(combined_df)}")

    # Remove duplicates based on 'id' column
    if 'id' in combined_df.columns:
        # Keep the first occurrence of each ID (earliest timestamp)
        unique_df = combined_df.drop_duplicates(subset=['id'], keep='first')
        duplicates_removed = len(combined_df) - len(unique_df)

        print(f"Duplicates removed: {duplicates_removed}")
        print(f"Unique records: {len(unique_df)}")

        # Show detailed duplicate information
        if duplicates_removed > 0:
            # Get all duplicated records (including originals)
            duplicated_records = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
            duplicate_ids = duplicated_records['id'].unique()

            print(f"\nDuplicate analysis:")
            print(f"  Total duplicate IDs: {len(duplicate_ids)}")

            # Show where each duplicate ID appeared
            for dup_id in sorted(duplicate_ids):
                dup_records = duplicated_records[duplicated_records['id'] == dup_id]
                files_with_dup = dup_records['_source_file'].tolist()
                print(f"  ID '{dup_id}' appears in: {', '.join(files_with_dup)}")

        # Remove the temporary source file column before saving
        if '_source_file' in unique_df.columns:
            unique_df = unique_df.drop(columns=['_source_file'])
    else:
        print("Warning: No 'id' column found, cannot remove duplicates")
        unique_df = combined_df

    # Sort by timestamp for chronological order
    if 'time' in unique_df.columns:
        unique_df = unique_df.sort_values('time').reset_index(drop=True)
        print("Data sorted by timestamp")

    # Generate output filename with dynamic date
    folder_name = os.path.basename(folder_path)
    if folder_name.startswith('Sep '):
        # Extract date from folder name (e.g., "Sep 25" -> "Sep25")
        date_part = folder_name.replace(' ', '')
        output_filename = f"Combined_Mission_Data_{date_part}_2025.csv"
    else:
        output_filename = "Combined_Mission_Data.csv"

    # Determine output path
    if output_to_results:
        # Get the parent directory and create results path
        parent_dir = os.path.dirname(os.path.abspath(folder_path))
        results_dir = os.path.join(parent_dir, "results")

        # Create results directory if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)
        output_file = os.path.join(results_dir, output_filename)
    else:
        output_file = os.path.join(folder_path, output_filename)

    # Calculate stats
    total_records = len(unique_df)
    duplicates_removed = len(combined_df) - len(unique_df)

    # Create header with summary stats
    header_lines = [
        f"# Mission Data Summary",
        f"# Total Survey Points: {total_records}",
        f"# Duplicates Removed: {duplicates_removed}",
        f"# Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"#"
    ]

    # Write header and data to file
    with open(output_file, 'w', newline='') as f:
        # Write header lines
        for line in header_lines:
            f.write(line + '\n')

        # Write CSV data
        unique_df.to_csv(f, index=False)

    print(f"\nCombined data saved to: {output_file}")

    # Print stats
    print(f"Total survey points: {total_records}")

    # Print summary statistics
    if 'time' in unique_df.columns:
        start_time = unique_df['time'].iloc[0]
        end_time = unique_df['time'].iloc[-1]
        print(f"\nMission Summary:")
        print(f"  Start time: {start_time}")
        print(f"  End time: {end_time}")

    if 'name' in unique_df.columns:
        name_range = f"{unique_df['name'].min()} - {unique_df['name'].max()}"
        print(f"  Point ID range: {name_range}")

    return output_file

def main():
    """Main function to run the script"""
    print("Mission Data Combiner")
    print("=" * 50)

    # Get current directory
    current_dir = os.getcwd()
    print(f"Script location: {current_dir}")

    # Find available date folders
    available_folders = get_available_date_folders(current_dir)

    if not available_folders:
        print("No date folders found (looking for folders starting with 'Sep ')")
        return

    selected_folder = None

    # Check for command line argument
    if len(sys.argv) > 1:
        folder_arg = sys.argv[1]
        if folder_arg in available_folders:
            selected_folder = folder_arg
            print(f"Using folder from command line: {selected_folder}")
        else:
            print(f"Folder '{folder_arg}' not found in available folders.")
            print("Available folders:", ", ".join(available_folders))
            return

    # Interactive selection if no command line argument
    if selected_folder is None:
        print(f"\nAvailable date folders:")
        for i, folder in enumerate(available_folders, 1):
            print(f"  {i}. {folder}")

        # Get user selection
        while True:
            try:
                choice = input(f"\nSelect a folder (1-{len(available_folders)}): ").strip()
                folder_index = int(choice) - 1
                if 0 <= folder_index < len(available_folders):
                    selected_folder = available_folders[folder_index]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(available_folders)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user")
                return

    folder_path = os.path.join(current_dir, selected_folder)
    print(f"\nProcessing files in: {folder_path}")

    # Combine files and save to results folder
    output_file = combine_mission_files(folder_path, output_to_results=True)

    if output_file:
        print(f"\n✅ Success! Combined file created: {os.path.basename(output_file)}")
        print(f"   Saved to: {output_file}")
    else:
        print("\n❌ Failed to create combined file")

if __name__ == "__main__":
    main()