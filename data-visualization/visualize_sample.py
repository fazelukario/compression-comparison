#!/usr/bin/env python3
# Example script to visualize compression data using the sample JSON

import json
import time
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
import argparse
import sys

# Colors for different algorithms
COLORS = {
    'bz2': '#1f77b4',
    'gz': '#ff7f0e',
    'lz4': '#2ca02c',
    'zstd': '#d62728'
}

def extract_data(json_data):
    """Extracts data from JSON structure and organizes it in a convenient format."""
    results = {}
    
    for file_data in json_data:
        for filename, algorithms in file_data.items():
            if filename not in results:
                results[filename] = {}
            
            for algorithm, levels in algorithms.items():
                if algorithm not in results[filename]:
                    results[filename][algorithm] = {
                        'compression_levels': [],
                        'compression_ratio': [],
                        'compressed_percentage': [],
                        'compression_time': [],
                        'decompression_time': [],
                        'original_size': None,
                        'compressed_size': [],
                        'memory_usage': []
                    }
                
                # Save the original file size (same for all levels)
                if results[filename][algorithm]['original_size'] is None:
                    # Use the first level to get the original size
                    first_level = list(levels.keys())[0]
                    results[filename][algorithm]['original_size'] = levels[first_level]['compression']['originalSize']
                
                # Process data for each compression level
                for level, metrics in levels.items():
                    results[filename][algorithm]['compression_levels'].append(int(level))
                    
                    comp_data = metrics['compression']
                    decomp_data = metrics['decompression']
                    
                    results[filename][algorithm]['compression_ratio'].append(comp_data['compressionRatio'])
                    results[filename][algorithm]['compressed_percentage'].append(float(comp_data['compressedPercentage']))
                    results[filename][algorithm]['compression_time'].append(parse_time(comp_data['real']))
                    results[filename][algorithm]['decompression_time'].append(parse_time(decomp_data['real']))
                    results[filename][algorithm]['compressed_size'].append(comp_data['compressedSize'])
                    results[filename][algorithm]['memory_usage'].append(comp_data['max'])
    
    return results

def parse_time(time_str):
    """Converts time string to seconds in format [hours:]minutes:seconds."""
    if not time_str:
        return 0.0
    
    parts = time_str.split(':')
    
    if len(parts) == 2:
        # Format: minutes:seconds
        minutes, seconds = float(parts[0]), float(parts[1])
        return minutes * 60 + seconds
    elif len(parts) == 3:
        # Format: hours:minutes:seconds
        hours, minutes, seconds = float(parts[0]), float(parts[1]), float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    else:
        # Unexpected format, return 0
        return 0.0

def plot_compression_ratio_comparison(results, output_dir='plots'):
    """Plots compression ratio comparison for all files and algorithms."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(14, 10))
    
    # Get all file names
    filenames = list(results.keys())
    
    # Set up the grid layout
    num_files = len(filenames)
    cols = 1
    rows = num_files
    
    for i, filename in enumerate(filenames):
        ax = plt.subplot(rows, cols, i + 1)
        
        for algorithm, data in results[filename].items():
            # Sort data by compression level
            sorted_indices = np.argsort(data['compression_levels'])
            levels = [data['compression_levels'][i] for i in sorted_indices]
            ratios = [data['compression_ratio'][i] for i in sorted_indices]
            
            ax.plot(
                levels, 
                ratios, 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        ax.set_title(f'Compression ratio for {filename}')
        ax.set_xlabel('Compression level')
        ax.set_ylabel('Ratio (original / compressed)')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'compression_ratio_comparison.png'), dpi=150)
    plt.close()
    
    print(f"Compression ratio comparison saved to {os.path.join(output_dir, 'compression_ratio_comparison.png')}")

def plot_compression_time_comparison(results, output_dir='plots'):
    """Plots compression time comparison for all files and algorithms."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(14, 10))
    
    # Get all file names
    filenames = list(results.keys())
    
    # Set up the grid layout
    num_files = len(filenames)
    cols = 1
    rows = num_files
    
    for i, filename in enumerate(filenames):
        ax = plt.subplot(rows, cols, i + 1)
        
        for algorithm, data in results[filename].items():
            # Sort data by compression level
            sorted_indices = np.argsort(data['compression_levels'])
            levels = [data['compression_levels'][i] for i in sorted_indices]
            times = [data['compression_time'][i] for i in sorted_indices]
            
            ax.plot(
                levels, 
                times, 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        ax.set_title(f'Compression time for {filename}')
        ax.set_xlabel('Compression level')
        ax.set_ylabel('Time (seconds)')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'compression_time_comparison.png'), dpi=150)
    plt.close()
    
    print(f"Compression time comparison saved to {os.path.join(output_dir, 'compression_time_comparison.png')}")

def plot_efficiency_matrix(results, output_dir='plots'):
    """Creates a matrix of plots showing efficiency metrics for all algorithms."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot size vs. compression ratio
    plt.figure(figsize=(14, 10))
    
    # Get all file names
    filenames = list(results.keys())
    
    for filename in filenames:
        plt.figure(figsize=(12, 10))
        
        # Create a scatter plot of size vs. ratio for all algorithms
        for algorithm, data in results[filename].items():
            plt.scatter(
                data['compressed_size'], 
                data['compression_ratio'],
                s=100,  # point size
                alpha=0.7,
                label=algorithm,
                color=COLORS[algorithm]
            )
            
            # Add annotations for compression levels
            for i, level in enumerate(data['compression_levels']):
                plt.annotate(
                    str(level),
                    (data['compressed_size'][i], data['compression_ratio'][i]),
                    textcoords="offset points",
                    xytext=(0, 5),
                    ha='center'
                )
        
        plt.title(f'Compression ratio vs. Size for {filename}')
        plt.xlabel('Compressed size (bytes)')
        plt.ylabel('Compression ratio')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Add original file size as text
        original_size = results[filename][list(results[filename].keys())[0]]['original_size']
        plt.figtext(0.5, 0.01, f'Original file size: {original_size} bytes', ha='center')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{filename}_ratio_vs_size.png'), dpi=150)
        plt.close()
        
        print(f"Size vs. ratio plot saved for {filename}")

def main():
    parser = argparse.ArgumentParser(description='Visualize compression data from JSON')
    parser.add_argument('json_file', help='JSON file with compression data')
    parser.add_argument('-o', '--output', help='Directory to save plots', default=('results/plots/' + time.strftime("%Y-%m-%d-%H-%M-%S")))
    args = parser.parse_args()

    # Check if JSON file exists
    if not os.path.exists(args.json_file):
        print(f"Error: file {args.json_file} not found", file=sys.stderr)
        sys.exit(1)

    # Load JSON data
    with open(args.json_file, 'r') as f:
        try:
            sample_data = json.load(f)
        except json.JSONDecodeError:
            print("Error parsing JSON data. Please check the file format.", file=sys.stderr)
            sys.exit(1)

    # Extract and organize the data
    results = extract_data(sample_data)

    # Set output directory
    output_dir = args.output

    # Create various visualization plots
    plot_compression_ratio_comparison(results, output_dir)
    plot_compression_time_comparison(results, output_dir)
    plot_efficiency_matrix(results, output_dir)
    print(f"Visualization complete! Check the '{output_dir}' folder for the output.")

if __name__ == "__main__":
    main()
