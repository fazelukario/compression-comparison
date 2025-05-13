#!/usr/bin/env python3
# Script for visualizing compression algorithm comparison results
# Author: fazelukario
# Date: 2025-05-12

import json
import time
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from matplotlib.gridspec import GridSpec
import argparse
from pathlib import Path

# Colors for different algorithms
COLORS = {
    'bz2': '#1f77b4',
    'gz': '#ff7f0e',
    'lz4': '#2ca02c',
    'zstd': '#d62728'
}

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

def sort_data_by_level(data):
    """Sorts data by compression levels."""
    for filename in data:
        for algorithm in data[filename]:
            # Get indices for sorting
            indices = np.argsort(data[filename][algorithm]['compression_levels'])
            
            # Sort all data arrays
            for key in ['compression_levels', 'compression_ratio', 'compressed_percentage', 
                       'compression_time', 'decompression_time', 'compressed_size', 'memory_usage']:
                data[filename][algorithm][key] = [data[filename][algorithm][key][i] for i in indices]
    
    return data

def plot_compression_ratio(results, output_dir):
    """Plots compression ratio for each file."""
    for filename, algorithms in results.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, data in algorithms.items():
            plt.plot(
                data['compression_levels'], 
                data['compression_ratio'], 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        plt.title(f'Compression ratio for {filename}')
        plt.xlabel('Compression level')
        plt.ylabel('Compression ratio (original / compressed)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Save the plot
        plt.savefig(os.path.join(output_dir, f'{filename}_compression_ratio.png'), dpi=150)
        plt.close()

def plot_time_comparison(results, output_dir):
    """Plots compression and decompression time for each file."""
    for filename, algorithms in results.items():
        plt.figure(figsize=(12, 8))
        
        # Use two subplots
        gs = GridSpec(2, 1, height_ratios=[2, 1])
        
        # Compression time plot
        ax1 = plt.subplot(gs[0])
        for algorithm, data in algorithms.items():
            ax1.plot(
                data['compression_levels'], 
                data['compression_time'], 
                'o-', 
                label=f'{algorithm} - compression', 
                color=COLORS[algorithm]
            )
        
        ax1.set_title(f'Compression time for {filename}')
        ax1.set_ylabel('Time (seconds)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Decompression time plot
        ax2 = plt.subplot(gs[1])
        for algorithm, data in algorithms.items():
            ax2.plot(
                data['compression_levels'], 
                data['decompression_time'], 
                'o--', 
                label=f'{algorithm} - decompression', 
                color=COLORS[algorithm], 
                alpha=0.7
            )
        
        ax2.set_title('Decompression time')
        ax2.set_xlabel('Compression level')
        ax2.set_ylabel('Time (seconds)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(os.path.join(output_dir, f'{filename}_time_comparison.png'), dpi=150)
        plt.close()

def plot_memory_usage(results, output_dir):
    """Plots memory usage."""
    for filename, algorithms in results.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, data in algorithms.items():
            plt.plot(
                data['compression_levels'], 
                data['memory_usage'], 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        plt.title(f'Memory usage during compression for {filename}')
        plt.xlabel('Compression level')
        plt.ylabel('Memory usage (KB)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Save the plot
        plt.savefig(os.path.join(output_dir, f'{filename}_memory_usage.png'), dpi=150)
        plt.close()

def plot_size_comparison(results, output_dir):
    """Plots the size of compressed files."""
    for filename, algorithms in results.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, data in algorithms.items():
            plt.plot(
                data['compression_levels'], 
                data['compressed_size'], 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        # Add horizontal line for original size
        original_size = list(algorithms.values())[0]['original_size']
        plt.axhline(y=original_size, linestyle='--', color='gray', alpha=0.7, label='Original size')
        
        plt.title(f'File size after compression for {filename}')
        plt.xlabel('Compression level')
        plt.ylabel('Size (bytes)')
        plt.yscale('log')  # Logarithmic scale for better visualization
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Save the plot
        plt.savefig(os.path.join(output_dir, f'{filename}_size_comparison.png'), dpi=150)
        plt.close()

def plot_combined_metrics(results, output_dir):
    """Plots combined graphs with different metrics for each algorithm."""
    for filename, algorithms in results.items():
        plt.figure(figsize=(15, 10))
        
        # Split into 4 subplots for different metrics
        gs = GridSpec(2, 2)
        
        # 1. Compression ratio
        ax1 = plt.subplot(gs[0, 0])
        for algorithm, data in algorithms.items():
            ax1.plot(
                data['compression_levels'], 
                data['compression_ratio'], 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        ax1.set_title('Compression ratio')
        ax1.set_xlabel('Compression level')
        ax1.set_ylabel('Ratio (original / compressed)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 2. Compression time
        ax2 = plt.subplot(gs[0, 1])
        for algorithm, data in algorithms.items():
            ax2.plot(
                data['compression_levels'], 
                data['compression_time'], 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        ax2.set_title('Compression time')
        ax2.set_xlabel('Compression level')
        ax2.set_ylabel('Time (seconds)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 3. Decompression time
        ax3 = plt.subplot(gs[1, 0])
        for algorithm, data in algorithms.items():
            ax3.plot(
                data['compression_levels'], 
                data['decompression_time'], 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        ax3.set_title('Decompression time')
        ax3.set_xlabel('Compression level')
        ax3.set_ylabel('Time (seconds)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
          # 4. Memory usage
        ax4 = plt.subplot(gs[1, 1])
        for algorithm, data in algorithms.items():
            ax4.plot(
                data['compression_levels'], 
                data['memory_usage'], 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        ax4.set_title('Memory usage')
        ax4.set_xlabel('Compression level')
        ax4.set_ylabel('Memory (KB)')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.suptitle(f'Compression metrics comparison for {filename}', fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        
        # Save the plot
        plt.savefig(os.path.join(output_dir, f'{filename}_combined_metrics.png'), dpi=150)
        plt.close()

def plot_compression_efficiency(results, output_dir):
    """Plots compression efficiency (ratio of compression ratio to time)."""
    for filename, algorithms in results.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, data in algorithms.items():
            # Calculate efficiency: compression ratio / compression time
            # Add a small number to avoid division by zero
            efficiency = [ratio / (time + 0.001) for ratio, time in 
                          zip(data['compression_ratio'], data['compression_time'])]
            
            plt.plot(
                data['compression_levels'], 
                efficiency, 
                'o-', 
                label=algorithm, 
                color=COLORS[algorithm]
            )
        
        plt.title(f'Compression efficiency for {filename}')
        plt.xlabel('Compression level')
        plt.ylabel('Efficiency (compression ratio / time)')
        plt.yscale('log')  # Logarithmic scale for better visualization
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Save the plot
        plt.savefig(os.path.join(output_dir, f'{filename}_compression_efficiency.png'), dpi=150)
        plt.close()

def create_overview_table(results, output_dir):
    """Creates an HTML table with the best results for each algorithm and file."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Compression Algorithm Comparison</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .best { font-weight: bold; color: green; }
        </style>
    </head>
    <body>
        <h1>Best Compression Metrics</h1>
    """
    
    for filename, algorithms in results.items():
        html_content += f"<h2>File: {filename}</h2>"
        html_content += """
        <table>
            <tr>
                <th>Algorithm</th>
                <th>Best level</th>
                <th>Compression ratio</th>
                <th>Compression rate (%)</th>
                <th>Compression time (s)</th>
                <th>Decompression time (s)</th>
                <th>Memory usage (KB)</th>
            </tr>
        """        
        # Find the best values
        best_ratio = 0
        best_time = float('inf')
        best_memory = float('inf')
        best_decompression = float('inf')
        
        for algorithm in algorithms:
            idx = np.argmax(algorithms[algorithm]['compression_ratio'])
            if algorithms[algorithm]['compression_ratio'][idx] > best_ratio:
                best_ratio = algorithms[algorithm]['compression_ratio'][idx]
            
            idx = np.argmin(algorithms[algorithm]['compression_time'])
            if algorithms[algorithm]['compression_time'][idx] < best_time:
                best_time = algorithms[algorithm]['compression_time'][idx]
            
            idx = np.argmin(algorithms[algorithm]['memory_usage'])
            if algorithms[algorithm]['memory_usage'][idx] < best_memory:
                best_memory = algorithms[algorithm]['memory_usage'][idx]
            
            idx = np.argmin(algorithms[algorithm]['decompression_time'])
            if algorithms[algorithm]['decompression_time'][idx] < best_decompression:
                best_decompression = algorithms[algorithm]['decompression_time'][idx]
        
        # Add rows for each algorithm
        for algorithm, data in algorithms.items():
            # Best level = the one that gives the maximum compression ratio
            idx = np.argmax(data['compression_ratio'])
            level = data['compression_levels'][idx]
            ratio = data['compression_ratio'][idx]
            perc = 100 - data['compressed_percentage'][idx]  # Compression percentage
            c_time = data['compression_time'][idx]
            d_time = data['decompression_time'][idx]
            memory = data['memory_usage'][idx]            
            # Add "best" class for the best values
            ratio_class = " class='best'" if ratio == best_ratio else ""
            c_time_class = " class='best'" if c_time == best_time else ""
            d_time_class = " class='best'" if d_time == best_decompression else ""
            memory_class = " class='best'" if memory == best_memory else ""
            
            html_content += f"""
            <tr>
                <td>{algorithm}</td>
                <td>{level}</td>
                <td{ratio_class}>{ratio:.2f}</td>
                <td>{perc:.1f}%</td>
                <td{c_time_class}>{c_time:.3f}</td>
                <td{d_time_class}>{d_time:.3f}</td>
                <td{memory_class}>{memory}</td>
            </tr>
            """
        
        html_content += "</table>"
    
    html_content += """
    </body>
    </html>
    """
    
    # Save HTML file
    with open(os.path.join(output_dir, 'comparison_summary.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description='Visualization of compression algorithm comparison results')
    parser.add_argument('json_file', help='JSON file with test results')
    parser.add_argument('-o', '--output', help='Directory to save plots', default=('results/visualize/' + time.strftime("%Y-%m-%d-%H-%M-%S")))

    args = parser.parse_args()
    
    # Check if JSON file exists
    if not os.path.exists(args.json_file):
        print(f"Error: file {args.json_file} not found", file=sys.stderr)
        sys.exit(1)
    
    # Create directory for results if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Load data from JSON
    with open(args.json_file, 'r') as f:
        json_data = json.load(f)
    
    # Extract and organize data
    results = extract_data(json_data)
    
    # Sort data by compression levels
    results = sort_data_by_level(results)
    
    # Create plots
    plot_compression_ratio(results, args.output)
    plot_time_comparison(results, args.output)
    plot_memory_usage(results, args.output)
    plot_size_comparison(results, args.output)
    plot_combined_metrics(results, args.output)
    plot_compression_efficiency(results, args.output)
    
    # Create summary table
    create_overview_table(results, args.output)
    
    # Output information about created plots
    total_files = len(os.listdir(args.output))
    print(f"Created {total_files} visualization files in directory '{args.output}'")
    
    # Inform about summary report
    html_path = os.path.join(args.output, 'comparison_summary.html')
    print(f"Summary table of results saved to '{html_path}'")

if __name__ == "__main__":
    main()