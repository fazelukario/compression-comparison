#!/usr/bin/env python3
# Script to visualize compression data from provided JSON

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

def process_data(json_data):
    """Process and organize compression data for visualization."""
    results = {}
    
    for test_data in json_data:
        for test_name, algorithms in test_data.items():
            results[test_name] = {}
            
            for algorithm, levels in algorithms.items():
                results[test_name][algorithm] = {
                    'levels': [],
                    'ratios': [],
                    'compressed_sizes': [],
                    'compression_times': [],
                    'decompression_times': [],
                    'memory_usage': [],
                    'original_size': None
                }
                
                # Get original size from the first level
                first_level = next(iter(levels.values()))
                results[test_name][algorithm]['original_size'] = first_level['compression']['originalSize']
                
                # Process each compression level
                for level, data in levels.items():
                    results[test_name][algorithm]['levels'].append(int(level))
                    results[test_name][algorithm]['ratios'].append(data['compression']['compressionRatio'])
                    results[test_name][algorithm]['compressed_sizes'].append(data['compression']['compressedSize'])
                    results[test_name][algorithm]['compression_times'].append(parse_time(data['compression']['real']))
                    results[test_name][algorithm]['decompression_times'].append(parse_time(data['decompression']['real']))
                    results[test_name][algorithm]['memory_usage'].append(data['compression']['max'])
                
                # Sort by compression level
                indices = np.argsort(results[test_name][algorithm]['levels'])
                for key in ['levels', 'ratios', 'compressed_sizes', 'compression_times', 
                           'decompression_times', 'memory_usage']:
                    results[test_name][algorithm][key] = [results[test_name][algorithm][key][i] for i in indices]
    
    return results

def plot_compression_ratios(data, output_dir):
    """Plot compression ratios for all tests and algorithms."""
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(10, 6))
    
    for test_name, algorithms in data.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, metrics in algorithms.items():
            plt.plot(
                metrics['levels'],
                metrics['ratios'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray'),
                linewidth=2
            )
        
        plt.title(f'Compression Ratio Comparison - {test_name}', fontsize=16)
        plt.xlabel('Compression Level', fontsize=14)
        plt.ylabel('Compression Ratio (higher is better)', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=12)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{test_name}_compression_ratios.png'), dpi=150)
        plt.close()

def plot_compression_times(data, output_dir):
    """Plot compression times for all tests and algorithms."""
    os.makedirs(output_dir, exist_ok=True)
    
    for test_name, algorithms in data.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, metrics in algorithms.items():
            plt.plot(
                metrics['levels'],
                metrics['compression_times'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray'),
                linewidth=2
            )
        
        plt.title(f'Compression Time Comparison - {test_name}', fontsize=16)
        plt.xlabel('Compression Level', fontsize=14)
        plt.ylabel('Time (seconds - lower is better)', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=12)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{test_name}_compression_times.png'), dpi=150)
        plt.close()

def plot_algorithm_performance_matrix(data, output_dir):
    """Create a comprehensive performance matrix for all tests."""
    os.makedirs(output_dir, exist_ok=True)
    
    for test_name, algorithms in data.items():
        fig = plt.figure(figsize=(15, 12))
        gs = GridSpec(2, 2, figure=fig)
        
        # 1. Compression Ratio
        ax1 = fig.add_subplot(gs[0, 0])
        for algorithm, metrics in algorithms.items():
            ax1.plot(
                metrics['levels'],
                metrics['ratios'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray'),
                linewidth=2
            )
        
        ax1.set_title('Compression Ratio', fontsize=14)
        ax1.set_xlabel('Compression Level', fontsize=12)
        ax1.set_ylabel('Ratio (higher is better)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=10)
        
        # 2. Compression Time
        ax2 = fig.add_subplot(gs[0, 1])
        for algorithm, metrics in algorithms.items():
            ax2.plot(
                metrics['levels'],
                metrics['compression_times'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray'),
                linewidth=2
            )
        
        ax2.set_title('Compression Time', fontsize=14)
        ax2.set_xlabel('Compression Level', fontsize=12)
        ax2.set_ylabel('Time (seconds)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=10)
        
        # 3. Decompression Time
        ax3 = fig.add_subplot(gs[1, 0])
        for algorithm, metrics in algorithms.items():
            ax3.plot(
                metrics['levels'],
                metrics['decompression_times'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray'),
                linewidth=2
            )
        
        ax3.set_title('Decompression Time', fontsize=14)
        ax3.set_xlabel('Compression Level', fontsize=12)
        ax3.set_ylabel('Time (seconds)', fontsize=12)
        ax3.grid(True, alpha=0.3)
        ax3.legend(fontsize=10)
        
        # 4. Memory Usage
        ax4 = fig.add_subplot(gs[1, 1])
        for algorithm, metrics in algorithms.items():
            ax4.plot(
                metrics['levels'],
                metrics['memory_usage'],
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray'),
                linewidth=2
            )
        
        ax4.set_title('Memory Usage', fontsize=14)
        ax4.set_xlabel('Compression Level', fontsize=12)
        ax4.set_ylabel('Memory (KB)', fontsize=12)
        ax4.grid(True, alpha=0.3)
        ax4.legend(fontsize=10)
        
        plt.suptitle(f'Compression Performance Metrics - {test_name}', fontsize=18)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        plt.savefig(os.path.join(output_dir, f'{test_name}_performance_matrix.png'), dpi=150)
        plt.close()

def plot_efficiency_comparison(data, output_dir):
    """Plot compression efficiency (ratio/time) for each algorithm."""
    os.makedirs(output_dir, exist_ok=True)
    
    for test_name, algorithms in data.items():
        plt.figure(figsize=(12, 8))
        
        for algorithm, metrics in algorithms.items():
            # Calculate efficiency
            efficiency = [r / (t + 0.001) for r, t in zip(metrics['ratios'], metrics['compression_times'])]
            
            plt.plot(
                metrics['levels'],
                efficiency,
                'o-',
                label=algorithm,
                color=COLORS.get(algorithm, 'gray'),
                linewidth=2
            )
        
        plt.title(f'Compression Efficiency - {test_name}', fontsize=16)
        plt.xlabel('Compression Level', fontsize=14)
        plt.ylabel('Efficiency (Ratio/Time - higher is better)', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=12)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{test_name}_efficiency.png'), dpi=150)
        plt.close()

def create_html_summary(data, output_dir):
    """Create HTML summary with tables and embedded images."""
    os.makedirs(output_dir, exist_ok=True)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Compression Benchmark Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .best { font-weight: bold; color: #009900; }
            h1, h2, h3 { color: #333; }
            .chart-container { margin: 20px 0; text-align: center; }
            .chart-container img { max-width: 100%; height: auto; }
        </style>
    </head>
    <body>
        <h1>Compression Algorithm Benchmark Results</h1>
    """
    
    for test_name, algorithms in data.items():
        html_content += f"<h2>Test: {test_name}</h2>"
        
        # Add performance matrix image
        html_content += f"""
        <div class="chart-container">
            <img src="{test_name}_performance_matrix.png" alt="Performance metrics">
            <p>Overall performance metrics for all algorithms</p>
        </div>
        """
        
        # Create best results table
        html_content += "<h3>Best Results Summary</h3>"
        html_content += """
        <table>
            <tr>
                <th>Algorithm</th>
                <th>Best Compression Ratio</th>
                <th>Level</th>
                <th>Fastest Compression (s)</th>
                <th>Level</th>
                <th>Fastest Decompression (s)</th>
                <th>Level</th>
                <th>Lowest Memory (KB)</th>
                <th>Level</th>
            </tr>
        """
        
        # Find best values for highlighting
        best_ratio = 0
        best_comp_time = float('inf')
        best_decomp_time = float('inf')
        best_memory = float('inf')
        
        # First pass to find best values
        for algorithm, metrics in algorithms.items():
            best_ratio = max(best_ratio, max(metrics['ratios']))
            best_comp_time = min(best_comp_time, min(metrics['compression_times']) if metrics['compression_times'] else float('inf'))
            best_decomp_time = min(best_decomp_time, min(metrics['decompression_times']) if metrics['decompression_times'] else float('inf'))
            best_memory = min(best_memory, min(metrics['memory_usage']) if metrics['memory_usage'] else float('inf'))
        
        # Second pass to create table rows
        for algorithm, metrics in algorithms.items():
            # Find indices for best values
            max_ratio_idx = metrics['ratios'].index(max(metrics['ratios']))
            min_comp_time_idx = metrics['compression_times'].index(min(metrics['compression_times'])) if metrics['compression_times'] else 0
            min_decomp_time_idx = metrics['decompression_times'].index(min(metrics['decompression_times'])) if metrics['decompression_times'] else 0
            min_memory_idx = metrics['memory_usage'].index(min(metrics['memory_usage'])) if metrics['memory_usage'] else 0
            
            # Get values and check if they are the best overall
            ratio = metrics['ratios'][max_ratio_idx]
            ratio_class = " class='best'" if ratio == best_ratio else ""
            
            comp_time = metrics['compression_times'][min_comp_time_idx]
            comp_class = " class='best'" if comp_time == best_comp_time else ""
            
            decomp_time = metrics['decompression_times'][min_decomp_time_idx]
            decomp_class = " class='best'" if decomp_time == best_decomp_time else ""
            
            memory = metrics['memory_usage'][min_memory_idx]
            memory_class = " class='best'" if memory == best_memory else ""
            
            html_content += f"""
            <tr>
                <td>{algorithm}</td>
                <td{ratio_class}>{ratio:.2f}</td>
                <td>{metrics['levels'][max_ratio_idx]}</td>
                <td{comp_class}>{comp_time:.3f}</td>
                <td>{metrics['levels'][min_comp_time_idx]}</td>
                <td{decomp_class}>{decomp_time:.3f}</td>
                <td>{metrics['levels'][min_decomp_time_idx]}</td>
                <td{memory_class}>{memory}</td>
                <td>{metrics['levels'][min_memory_idx]}</td>
            </tr>
            """
        
        html_content += "</table>"
        
        # Add detailed results table
        html_content += "<h3>Detailed Results by Compression Level</h3>"
        html_content += """
        <table>
            <tr>
                <th>Algorithm</th>
                <th>Level</th>
                <th>Ratio</th>
                <th>Compressed Size (bytes)</th>
                <th>Compression Time (s)</th>
                <th>Decompression Time (s)</th>
                <th>Memory Usage (KB)</th>
            </tr>
        """
        
        for algorithm, metrics in algorithms.items():
            original_size = metrics['original_size']
            for i, level in enumerate(metrics['levels']):
                html_content += f"""
                <tr>
                    <td>{algorithm}</td>
                    <td>{level}</td>
                    <td>{metrics['ratios'][i]:.2f}</td>
                    <td>{metrics['compressed_sizes'][i]} ({(100 * metrics['compressed_sizes'][i] / original_size):.1f}%)</td>
                    <td>{metrics['compression_times'][i]:.3f}</td>
                    <td>{metrics['decompression_times'][i]:.3f}</td>
                    <td>{metrics['memory_usage'][i]}</td>
                </tr>
                """
        
        html_content += "</table>"
        
        # Add additional charts
        html_content += """
        <div class="chart-container">
            <img src="{0}_compression_ratios.png" alt="Compression ratios">
            <p>Compression ratios at different levels</p>
        </div>
        
        <div class="chart-container">
            <img src="{0}_compression_times.png" alt="Compression times">
            <p>Compression times at different levels</p>
        </div>
        
        <div class="chart-container">
            <img src="{0}_efficiency.png" alt="Compression efficiency">
            <p>Compression efficiency (ratio/time) at different levels</p>
        </div>
        """.format(test_name)
    
    html_content += """
    </body>
    </html>
    """
    
    with open(os.path.join(output_dir, 'compression_results.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML summary created at {os.path.join(output_dir, 'compression_results.html')}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Visualize compression data from provided JSON')
    parser.add_argument('json_file', help='JSON file with compression data')
    parser.add_argument('-o', '--output', help='Directory to save plots', default=('results/comparison/' + time.strftime("%Y-%m-%d-%H-%M-%S")))
    args = parser.parse_args()
    if not os.path.exists(args.json_file):
        print(f"Error: file {args.json_file} not found", file=sys.stderr)
        sys.exit(1)
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    # Load JSON data
    try:
        with open(args.json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Process the data
        processed_data = process_data(json_data)
        
        # Create visualizations
        plot_compression_ratios(processed_data, output_dir)
        plot_compression_times(processed_data, output_dir)
        plot_algorithm_performance_matrix(processed_data, output_dir)
        plot_efficiency_comparison(processed_data, output_dir)
        # Create HTML summary
        create_html_summary(processed_data, output_dir)
        print(f"Analysis complete! All results saved to '{output_dir}' directory")
    
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()
