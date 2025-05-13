#!/usr/bin/env python3
"""
Script to convert a compression benchmark JSON file into Markdown tables.
"""
import json
import time
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='Convert JSON compression results to Markdown')
    parser.add_argument('json_file', help='Path to the JSON file with benchmark results')
    parser.add_argument('-o', '--output', help='Output Markdown file (defaults to stdout)', default=('results/markdown/' + time.strftime("%Y-%m-%d-%H-%M-%S") + '.md'))
    args = parser.parse_args()

    if not os.path.exists(args.json_file):
        print(f"Error: file '{args.json_file}' not found", file=sys.stderr)
        sys.exit(1)

    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lines = []
    lines.append('# Compression Benchmark Results')
    lines.append('')

    # Each entry in JSON is one test
    for entry in data:
        for test_name, algos in entry.items():
            algos_list = list(algos.values())
            lines.append(f'## Test: {test_name} (Original size: {list(list(algos.values())[0].values())[0].get("compression").get("originalSize")} bytes)')
            lines.append('')
            # Table header
            header = ['Algorithm', 'Level', 'Compression Ratio', 'Compressed Size (bytes)',
                      'Compression Time', 'Decompression Time', 'Memory Usage (compression)', 'Memory Usage (decompression)']
            lines.append('| ' + ' | '.join(header) + ' |')
            lines.append('| ' + ' | '.join(['---'] * len(header)) + ' |')
            # Table rows
            for algo, levels in algos.items():
                for lvl, metrics in sorted(levels.items(), key=lambda x: int(x[0])):
                    comp = metrics.get('compression', {})
                    decomp = metrics.get('decompression', {})
                    ratio = comp.get('compressionRatio', '')
                    size = comp.get('compressedSize', '')
                    ctime = comp.get('real', '')
                    dtime = decomp.get('real', '')
                    cmem = comp.get('max', '')
                    dmem = decomp.get('max', '')
                    row = [algo, lvl, str(ratio), str(size), str(ctime), str(dtime), str(cmem), str(dmem)]
                    lines.append('| ' + ' | '.join(row) + ' |')
            lines.append('')

    output_text = '\n'.join(lines)

    if args.output:
        # Ensure the output directory exists
        if '/' in args.output:
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
        with open(args.output, 'w', encoding='utf-8') as out:
            out.write(output_text)
        print(f'Markdown written to {args.output}')
    else:
        print(output_text)

if __name__ == '__main__':
    main()
