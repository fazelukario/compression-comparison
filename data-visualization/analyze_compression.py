#!/usr/bin/env python3
# Script to visualize and analyze provided compression data

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
    """Extracts relevant data from JSON structure."""
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
                
                # Use the first level to get the original size
                if results[filename][algorithm]['original_size'] is None:
                    first_level = list(levels.keys())[0]
                    results[filename][algorithm]['original_size'] = levels[first_level]['compression']['originalSize']
                
                # Process data for each compression level
                for level, metrics in levels.items():
                    comp_data = metrics['compression']
                    decomp_data = metrics['decompression']
                    
                    # Some data conversions
                    try:
                        level_int = int(level)
                    except ValueError:
                        # Handle non-integer levels
                        level_int = float(level)
                    
                    results[filename][algorithm]['compression_levels'].append(level_int)
                    results[filename][algorithm]['compression_ratio'].append(comp_data['compressionRatio'])
                    results[filename][algorithm]['compressed_percentage'].append(float(comp_data['compressedPercentage']))
                    results[filename][algorithm]['compression_time'].append(parse_time(comp_data['real']))
                    results[filename][algorithm]['decompression_time'].append(parse_time(decomp_data['real']))
                    results[filename][algorithm]['compressed_size'].append(comp_data['compressedSize'])
                    results[filename][algorithm]['memory_usage'].append(comp_data['max'])
    
    # Sort data by compression levels
    for filename in results:
        for algorithm in results[filename]:
            # Get indices for sorting
            indices = np.argsort(results[filename][algorithm]['compression_levels'])
            
            # Sort all data arrays
            for key in results[filename][algorithm]:
                if key != 'original_size' and isinstance(results[filename][algorithm][key], list):
                    results[filename][algorithm][key] = [results[filename][algorithm][key][i] for i in indices]
    
    return results

def plot_compression_ratio(data, output_dir):
    """Creates compression ratio plots for each test file."""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, algorithms in data.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, metrics in algorithms.items():
            plt.plot(
                metrics['compression_levels'],
                metrics['compression_ratio'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray')
            )
        
        plt.title(f'Compression Ratio for {filename}')
        plt.xlabel('Compression Level')
        plt.ylabel('Compression Ratio (higher is better)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.savefig(os.path.join(output_dir, f'{filename}_compression_ratio.png'), dpi=150)
        plt.close()

def plot_time_vs_compression(data, output_dir):
    """Creates plots showing the relationship between compression time and ratio."""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, algorithms in data.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, metrics in algorithms.items():
            plt.scatter(
                metrics['compression_time'],
                metrics['compression_ratio'],
                s=80,
                label=algorithm,
                color=COLORS.get(algorithm, 'gray'),
                alpha=0.8
            )
            
            # Add compression level annotations
            for i, level in enumerate(metrics['compression_levels']):
                plt.annotate(
                    str(level),
                    (metrics['compression_time'][i], metrics['compression_ratio'][i]),
                    textcoords="offset points",
                    xytext=(0, 5),
                    ha='center'
                )
        
        plt.title(f'Compression Time vs. Ratio for {filename}')
        plt.xlabel('Compression Time (seconds)')
        plt.ylabel('Compression Ratio (higher is better)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.savefig(os.path.join(output_dir, f'{filename}_time_vs_ratio.png'), dpi=150)
        plt.close()

def plot_compression_efficiency(data, output_dir):
    """Creates plots showing compression efficiency (ratio/time)."""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, algorithms in data.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, metrics in algorithms.items():
            # Calculate efficiency: ratio / time (with small offset to avoid division by zero)
            efficiency = [ratio / (time + 0.001) for ratio, time in 
                         zip(metrics['compression_ratio'], metrics['compression_time'])]
            
            plt.plot(
                metrics['compression_levels'],
                efficiency,
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray')
            )
        
        plt.title(f'Compression Efficiency for {filename}')
        plt.xlabel('Compression Level')
        plt.ylabel('Efficiency (Ratio/Time - higher is better)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.savefig(os.path.join(output_dir, f'{filename}_efficiency.png'), dpi=150)
        plt.close()

def plot_algorithm_comparison(data, output_dir):
    """Creates a comprehensive comparison of all algorithms for each file."""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, algorithms in data.items():
        fig = plt.figure(figsize=(15, 12))
        gs = GridSpec(2, 2, figure=fig)
        
        # 1. Compression Ratio
        ax1 = fig.add_subplot(gs[0, 0])
        for algorithm, metrics in algorithms.items():
            ax1.plot(
                metrics['compression_levels'],
                metrics['compression_ratio'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray')
            )
        
        ax1.set_title('Compression Ratio')
        ax1.set_xlabel('Compression Level')
        ax1.set_ylabel('Ratio (higher is better)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 2. Compression Time
        ax2 = fig.add_subplot(gs[0, 1])
        for algorithm, metrics in algorithms.items():
            ax2.plot(
                metrics['compression_levels'],
                metrics['compression_time'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray')
            )
        
        ax2.set_title('Compression Time')
        ax2.set_xlabel('Compression Level')
        ax2.set_ylabel('Time (seconds - lower is better)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 3. Decompression Time
        ax3 = fig.add_subplot(gs[1, 0])
        for algorithm, metrics in algorithms.items():
            ax3.plot(
                metrics['compression_levels'],
                metrics['decompression_time'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray')
            )
        
        ax3.set_title('Decompression Time')
        ax3.set_xlabel('Compression Level')
        ax3.set_ylabel('Time (seconds - lower is better)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # 4. Memory Usage
        ax4 = fig.add_subplot(gs[1, 1])
        for algorithm, metrics in algorithms.items():
            ax4.plot(
                metrics['compression_levels'],
                metrics['memory_usage'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray')
            )
        
        ax4.set_title('Memory Usage')
        ax4.set_xlabel('Compression Level')
        ax4.set_ylabel('Memory (KB - lower is better)')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.suptitle(f'Algorithm Comparison for {filename}', fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        
        plt.savefig(os.path.join(output_dir, f'{filename}_algorithm_comparison.png'), dpi=150)
        plt.close()

def generate_summary_table(data, output_dir):
    """Generates an HTML table with a summary of best results."""
    os.makedirs(output_dir, exist_ok=True)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Compression Algorithm Comparison</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .best { font-weight: bold; color: green; }
            h1, h2 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Compression Algorithm Comparison Summary</h1>
    """
    
    for filename, algorithms in data.items():
        html_content += f"<h2>File: {filename}</h2>"
        
        # Find best values for highlighting
        best_ratio = max(max(alg['compression_ratio']) for alg in algorithms.values())
        best_comp_time = min(min(alg['compression_time']) for alg in algorithms.values() if min(alg['compression_time']) > 0)
        best_decomp_time = min(min(alg['decompression_time']) for alg in algorithms.values() if min(alg['decompression_time']) > 0)
        best_memory = min(min(alg['memory_usage']) for alg in algorithms.values())
        
        # Table for overall best results
        html_content += """
        <table>
            <tr>
                <th>Algorithm</th>
                <th>Best Compression Ratio</th>
                <th>Best Level for Ratio</th>
                <th>Fastest Compression</th>
                <th>Level for Fast Comp.</th>
                <th>Fastest Decompression</th>
                <th>Level for Fast Decomp.</th>
                <th>Lowest Memory</th>
                <th>Level for Low Memory</th>
            </tr>
        """
        
        for algorithm, metrics in algorithms.items():
            # Find indices for best values
            best_ratio_idx = np.argmax(metrics['compression_ratio'])
            best_comp_time_idx = np.argmin(metrics['compression_time'])
            best_decomp_time_idx = np.argmin(metrics['decompression_time'])
            best_memory_idx = np.argmin(metrics['memory_usage'])
            
            # Format values with highlights
            ratio_value = metrics['compression_ratio'][best_ratio_idx]
            ratio_class = " class='best'" if ratio_value == best_ratio else ""
            
            comp_time_value = metrics['compression_time'][best_comp_time_idx]
            comp_time_class = " class='best'" if comp_time_value == best_comp_time else ""
            
            decomp_time_value = metrics['decompression_time'][best_decomp_time_idx]
            decomp_time_class = " class='best'" if decomp_time_value == best_decomp_time else ""
            
            memory_value = metrics['memory_usage'][best_memory_idx]
            memory_class = " class='best'" if memory_value == best_memory else ""
            
            html_content += f"""
            <tr>
                <td>{algorithm}</td>
                <td{ratio_class}>{ratio_value:.2f}</td>
                <td>{metrics['compression_levels'][best_ratio_idx]}</td>
                <td{comp_time_class}>{comp_time_value:.3f}s</td>
                <td>{metrics['compression_levels'][best_comp_time_idx]}</td>
                <td{decomp_time_class}>{decomp_time_value:.3f}s</td>
                <td>{metrics['compression_levels'][best_decomp_time_idx]}</td>
                <td{memory_class}>{memory_value} KB</td>
                <td>{metrics['compression_levels'][best_memory_idx]}</td>
            </tr>
            """
        
        html_content += "</table>"
        
        # Add detailed table for each level
        html_content += "<h3>Detailed Results by Compression Level</h3>"
        html_content += """
        <table>
            <tr>
                <th>Algorithm</th>
                <th>Level</th>
                <th>Compression Ratio</th>
                <th>Compressed Size (bytes)</th>
                <th>Compression (%)</th>
                <th>Compression Time (s)</th>
                <th>Decompression Time (s)</th>
                <th>Memory Usage (KB)</th>
            </tr>
        """
        
        for algorithm, metrics in algorithms.items():
            for i, level in enumerate(metrics['compression_levels']):
                html_content += f"""
                <tr>
                    <td>{algorithm}</td>
                    <td>{level}</td>
                    <td>{metrics['compression_ratio'][i]:.2f}</td>
                    <td>{metrics['compressed_size'][i]}</td>
                    <td>{100 - float(metrics['compressed_percentage'][i]):.1f}%</td>
                    <td>{metrics['compression_time'][i]:.3f}</td>
                    <td>{metrics['decompression_time'][i]:.3f}</td>
                    <td>{metrics['memory_usage'][i]}</td>
                </tr>
                """
        
        html_content += "</table>"
    
    html_content += """
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(os.path.join(output_dir, 'compression_summary.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Summary table saved to {os.path.join(output_dir, 'compression_summary.html')}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Visualize and analyze compression data from JSON')
    parser.add_argument('json_file', help='JSON file with compression data')
    parser.add_argument('-o', '--output', help='Directory to save plots', default=('results/analysis/' + time.strftime("%Y-%m-%d-%H-%M-%S")))
    args = parser.parse_args()
    if not os.path.exists(args.json_file):
        print(f"Error: file {args.json_file} not found", file=sys.stderr)
        sys.exit(1)
    # Load JSON data
    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract and organize data
    processed_data = extract_data(data)
    
    # Create output directory
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    # Generate various visualizations
    plot_compression_ratio(processed_data, output_dir)
    plot_time_vs_compression(processed_data, output_dir)
    plot_compression_efficiency(processed_data, output_dir)
    plot_algorithm_comparison(processed_data, output_dir)
    # Generate summary table
    generate_summary_table(processed_data, output_dir)
    print(f"Analysis complete! All results saved to '{output_dir}' directory.")

if __name__ == "__main__":
    main()
