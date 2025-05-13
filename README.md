# Compression Comparison

A comprehensive benchmark suite to compare **bz2**, **gzip (gz)**, **lz4**, and **zstd** compression algorithms across multiple compression levels. This repository provides:

- A Bash script (`compression-comparison.sh`) to automate compression/decompression and collect performance metrics (ratio, time, memory).
- JSON-formatted results stored under `/results`.
- Python-based data visualization tools under `data-visualization/` to generate plots and summary HTML reports.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [Compression Benchmark](#compression-benchmark)
  - [Data Visualization](#data-visualization)
- [Directory Structure](#directory-structure)
- [Test Results](#test-results)
  - [Test 1 (0,5 MB)](#test-test1-05-original-size-555334-bytes)
  - [Test 2 (0,9 MB)](#test-test2-09-original-size-942634-bytes)
  - [Test 3 (6,8 MB)](#test-test3-68-original-size-7037012-bytes)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Tests **bz2**, **gzip**, **lz4**, and **zstd** across configurable compression levels.
- Captures:
  - Compression ratio and percentage.
  - Compression/decompression real time, user/system time.
  - Memory usage.
- Outputs detailed JSON results for each input file.
- Automated plotting and HTML report generation via Python scripts.

---

## Prerequisites

### System Tools

Ensure the following CLI tools are installed and available in your `PATH`:

- `bzip2`
- `gzip`
- `lz4`
- `zstd`
- `/usr/bin/time` (GNU time)
- `jq` (for JSON manipulation)

On Debian/Ubuntu:

```powershell
sudo apt-get update
sudo apt-get install -y bzip2 gzip lz4 zstd time jq
```

### Python (for Visualization)

- Python 3.7+
- [matplotlib](https://matplotlib.org/)
- [numpy](https://numpy.org/)
- [pandas](https://pandas.pydata.org/) (optional for custom analysis)

Install Python dependencies:

```powershell
pip install matplotlib numpy pandas
```

---

## Usage

### Compression Benchmark

1. Make the main script executable (if on Unix-like OS):
   ```powershell
   chmod +x compression-comparison.sh
   ```
2. Run the benchmark for one or more files:
   ```powershell
   ./compression-comparison.sh path/to/file1 path/to/file2
   ```
3. Results will be written as timestamped JSON under `results/`.

### Data Visualization

Use the Python scripts in `data-visualization/` to generate plots and HTML summaries from JSON output.

1. **Analyze compression data** (produces in-depth HTML summary):
   ```powershell
   cd data-visualization
   python analyze_compression.py ../results/YYYY-MM-DD-HH-MM-SS.json
   ```
2. **Visualize JSON data** (generates individual charts and an HTML report):
   ```powershell
   python visualize.py ../results/YYYY-MM-DD-HH-MM-SS.json
   ```
3. **Alternative scripts**:
   - `visualize_json.py`: Customizable JSON-based plotting.
   - `visualize_sample.py` / `visualize_md.py`: Example notebooks and Markdown outputs.

All outputs are saved into corresponding timestamped directories under `results/`.

---

## Directory Structure

```
/ (root)
├── compression-comparison.sh   # Main benchmarking script
├── data-visualization/        # Python scripts for plotting and HTML report
│   ├── analyze_compression.py
│   ├── visualize.py
│   └── ...
├── results/                   # JSON results and generated visualizations
│   ├── YYYY-MM-DD-HH-MM-SS.json
│   ├── analysis/              # Outputs from analyze_compression.py
│   ├── comparison/            # Outputs from visualize_json.py
│   └── ...
├── LICENSE.md
└── README.md                  # ← You are here
```

---

## Test Results

Testing was done on `Raspberry Pi 5 (8GB)`.

### Test: test1-0,5 (Original size: 555334 bytes)

| Algorithm | Level | Compression Ratio | Compressed Size (bytes) | Compression Time | Decompression Time | Memory Usage (compression) | Memory Usage (decompression) |
| --------- | ----- | ----------------- | ----------------------- | ---------------- | ------------------ | -------------------------- | ---------------------------- |
| lz4       | 1     | 7.69              | 72160                   | 0:00.00          | 0:00.00            | 1920                       | 2048                         |
| lz4       | 2     | 7.69              | 72160                   | 0:00.00          | 0:00.00            | 1920                       | 2048                         |
| lz4       | 3     | 10.24             | 54199                   | 0:00.00          | 0:00.00            | 2176                       | 1920                         |
| lz4       | 4     | 10.35             | 53622                   | 0:00.00          | 0:00.00            | 2176                       | 1920                         |
| lz4       | 5     | 10.41             | 53334                   | 0:00.01          | 0:00.00            | 2176                       | 1920                         |
| lz4       | 6     | 10.44             | 53155                   | 0:00.01          | 0:00.00            | 2176                       | 1920                         |
| lz4       | 7     | 10.45             | 53095                   | 0:00.01          | 0:00.00            | 2176                       | 1920                         |
| lz4       | 8     | 10.46             | 53057                   | 0:00.02          | 0:00.00            | 2176                       | 1920                         |
| lz4       | 9     | 10.47             | 53016                   | 0:00.02          | 0:00.00            | 2176                       | 1920                         |
| zstd      | 1     | 12.61             | 44005                   | 0:00.00          | 0:00.00            | 3456                       | 2816                         |
| zstd      | 2     | 12.66             | 43836                   | 0:00.00          | 0:00.00            | 3712                       | 2816                         |
| zstd      | 3     | 12.83             | 43276                   | 0:00.00          | 0:00.00            | 4224                       | 2816                         |
| zstd      | 4     | 12.82             | 43304                   | 0:00.00          | 0:00.00            | 5504                       | 2816                         |
| zstd      | 5     | 14.3              | 38819                   | 0:00.01          | 0:00.00            | 6016                       | 2816                         |
| zstd      | 6     | 14.84             | 37420                   | 0:00.01          | 0:00.00            | 6016                       | 2816                         |
| zstd      | 7     | 14.97             | 37083                   | 0:00.01          | 0:00.00            | 8576                       | 2816                         |
| zstd      | 8     | 15.11             | 36741                   | 0:00.01          | 0:00.00            | 8576                       | 2816                         |
| zstd      | 9     | 15.12             | 36716                   | 0:00.02          | 0:00.00            | 13696                      | 2816                         |
| zstd      | 10    | 15.25             | 36403                   | 0:00.02          | 0:00.00            | 13696                      | 2816                         |
| zstd      | 11    | 15.32             | 36238                   | 0:00.03          | 0:00.00            | 13696                      | 2816                         |
| zstd      | 12    | 15.32             | 36238                   | 0:00.02          | 0:00.00            | 13696                      | 2816                         |
| zstd      | 13    | 15.3              | 36285                   | 0:00.03          | 0:00.00            | 19968                      | 2816                         |
| zstd      | 14    | 15.4              | 36039                   | 0:00.04          | 0:00.00            | 19968                      | 2816                         |
| zstd      | 15    | 15.47             | 35877                   | 0:00.04          | 0:00.00            | 19968                      | 2816                         |
| zstd      | 16    | 15.6              | 35584                   | 0:00.08          | 0:00.00            | 19840                      | 2816                         |
| zstd      | 17    | 15.77             | 35199                   | 0:00.09          | 0:00.00            | 19840                      | 2816                         |
| zstd      | 18    | 15.96             | 34782                   | 0:00.12          | 0:00.00            | 20352                      | 2816                         |
| zstd      | 19    | 17.55             | 31632                   | 0:00.42          | 0:00.00            | 20352                      | 2816                         |
| bz2       | 1     | 14.52             | 38220                   | 0:00.07          | 0:00.01            | 2176                       | 1664                         |
| bz2       | 2     | 16.15             | 34374                   | 0:00.07          | 0:00.01            | 2816                       | 2048                         |
| bz2       | 3     | 17.44             | 31834                   | 0:00.07          | 0:00.01            | 3584                       | 2432                         |
| bz2       | 4     | 17.37             | 31965                   | 0:00.08          | 0:00.01            | 4224                       | 2816                         |
| bz2       | 5     | 17.53             | 31671                   | 0:00.08          | 0:00.01            | 4992                       | 3200                         |
| bz2       | 6     | 18.59             | 29871                   | 0:00.09          | 0:00.01            | 5248                       | 3456                         |
| bz2       | 7     | 18.59             | 29871                   | 0:00.09          | 0:00.01            | 5248                       | 3456                         |
| bz2       | 8     | 18.59             | 29871                   | 0:00.08          | 0:00.01            | 5248                       | 3456                         |
| bz2       | 9     | 18.59             | 29871                   | 0:00.08          | 0:00.01            | 5248                       | 3456                         |
| gz        | 1     | 9.64              | 57602                   | 0:00.00          | 0:00.00            | 1536                       | 1280                         |
| gz        | 2     | 10.02             | 55418                   | 0:00.00          | 0:00.00            | 1536                       | 1280                         |
| gz        | 3     | 10.32             | 53784                   | 0:00.00          | 0:00.00            | 1536                       | 1280                         |
| gz        | 4     | 11.23             | 49439                   | 0:00.00          | 0:00.00            | 1536                       | 1280                         |
| gz        | 5     | 12.18             | 45570                   | 0:00.01          | 0:00.00            | 1536                       | 1280                         |
| gz        | 6     | 12.57             | 44150                   | 0:00.01          | 0:00.00            | 1536                       | 1280                         |
| gz        | 7     | 12.82             | 43286                   | 0:00.01          | 0:00.00            | 1408                       | 1280                         |
| gz        | 8     | 12.99             | 42733                   | 0:00.02          | 0:00.00            | 1408                       | 1280                         |
| gz        | 9     | 13.01             | 42683                   | 0:00.01          | 0:00.00            | 1408                       | 1280                         |

### Test: test2-0,9 (Original size: 942634 bytes)

| Algorithm | Level | Compression Ratio | Compressed Size (bytes) | Compression Time | Decompression Time | Memory Usage (compression) | Memory Usage (decompression) |
| --------- | ----- | ----------------- | ----------------------- | ---------------- | ------------------ | -------------------------- | ---------------------------- |
| lz4       | 1     | 8.37              | 112607                  | 0:00.00          | 0:00.00            | 2304                       | 2432                         |
| lz4       | 2     | 8.37              | 112607                  | 0:00.00          | 0:00.00            | 2304                       | 2432                         |
| lz4       | 3     | 11.02             | 85530                   | 0:00.01          | 0:00.00            | 2560                       | 2432                         |
| lz4       | 4     | 11.12             | 84731                   | 0:00.01          | 0:00.00            | 2560                       | 2432                         |
| lz4       | 5     | 11.17             | 84374                   | 0:00.01          | 0:00.00            | 2560                       | 2432                         |
| lz4       | 6     | 11.19             | 84179                   | 0:00.01          | 0:00.00            | 2560                       | 2432                         |
| lz4       | 7     | 11.2              | 84099                   | 0:00.02          | 0:00.00            | 2560                       | 2432                         |
| lz4       | 8     | 11.21             | 84066                   | 0:00.02          | 0:00.00            | 2560                       | 2432                         |
| lz4       | 9     | 11.21             | 84029                   | 0:00.03          | 0:00.00            | 2560                       | 2432                         |
| zstd      | 1     | 14.52             | 64905                   | 0:00.00          | 0:00.00            | 3968                       | 3072                         |
| zstd      | 2     | 14.55             | 64772                   | 0:00.00          | 0:00.00            | 4224                       | 3200                         |
| zstd      | 3     | 14.92             | 63156                   | 0:00.00          | 0:00.00            | 4736                       | 3200                         |
| zstd      | 4     | 14.92             | 63153                   | 0:00.01          | 0:00.00            | 6016                       | 3200                         |
| zstd      | 5     | 16.61             | 56731                   | 0:00.01          | 0:00.00            | 6528                       | 3200                         |
| zstd      | 6     | 17.11             | 55074                   | 0:00.01          | 0:00.00            | 6400                       | 3200                         |
| zstd      | 7     | 17.29             | 54505                   | 0:00.02          | 0:00.00            | 9088                       | 3200                         |
| zstd      | 8     | 17.46             | 53981                   | 0:00.02          | 0:00.00            | 9088                       | 3200                         |
| zstd      | 9     | 17.46             | 53963                   | 0:00.03          | 0:00.00            | 14208                      | 3200                         |
| zstd      | 10    | 17.62             | 53487                   | 0:00.03          | 0:00.00            | 14208                      | 3200                         |
| zstd      | 11    | 17.69             | 53286                   | 0:00.03          | 0:00.00            | 14208                      | 3200                         |
| zstd      | 12    | 17.69             | 53286                   | 0:00.03          | 0:00.00            | 14208                      | 3200                         |
| zstd      | 13    | 17.7              | 53248                   | 0:00.04          | 0:00.00            | 20352                      | 3200                         |
| zstd      | 14    | 17.9              | 52648                   | 0:00.05          | 0:00.00            | 20352                      | 3200                         |
| zstd      | 15    | 17.93             | 52553                   | 0:00.05          | 0:00.00            | 20480                      | 3200                         |
| zstd      | 16    | 18.42             | 51149                   | 0:00.15          | 0:00.00            | 20352                      | 3200                         |
| zstd      | 17    | 18.65             | 50536                   | 0:00.16          | 0:00.00            | 20352                      | 3200                         |
| zstd      | 18    | 18.73             | 50314                   | 0:00.22          | 0:00.00            | 20864                      | 3200                         |
| zstd      | 19    | 20.37             | 46255                   | 0:00.83          | 0:00.00            | 20992                      | 3200                         |
| bz2       | 1     | 15.16             | 62179                   | 0:00.12          | 0:00.02            | 2176                       | 1664                         |
| bz2       | 2     | 17.69             | 53258                   | 0:00.12          | 0:00.01            | 2816                       | 2048                         |
| bz2       | 3     | 18.79             | 50150                   | 0:00.13          | 0:00.02            | 3584                       | 2432                         |
| bz2       | 4     | 20.05             | 46997                   | 0:00.14          | 0:00.02            | 4224                       | 2816                         |
| bz2       | 5     | 21.78             | 43261                   | 0:00.16          | 0:00.02            | 4992                       | 3200                         |
| bz2       | 6     | 20.61             | 45716                   | 0:00.15          | 0:00.02            | 5632                       | 3584                         |
| bz2       | 7     | 20.55             | 45866                   | 0:00.16          | 0:00.02            | 6272                       | 3968                         |
| bz2       | 8     | 20.55             | 45864                   | 0:00.17          | 0:00.03            | 7040                       | 4352                         |
| bz2       | 9     | 21.38             | 44076                   | 0:00.17          | 0:00.03            | 7680                       | 4736                         |
| gz        | 1     | 10.72             | 87878                   | 0:00.01          | 0:00.00            | 1536                       | 1280                         |
| gz        | 2     | 11.1              | 84907                   | 0:00.00          | 0:00.00            | 1536                       | 1280                         |
| gz        | 3     | 11.34             | 83114                   | 0:00.00          | 0:00.00            | 1536                       | 1280                         |
| gz        | 4     | 12.41             | 75927                   | 0:00.01          | 0:00.00            | 1536                       | 1280                         |
| gz        | 5     | 13.06             | 72134                   | 0:00.01          | 0:00.00            | 1536                       | 1280                         |
| gz        | 6     | 13.25             | 71116                   | 0:00.01          | 0:00.00            | 1536                       | 1280                         |
| gz        | 7     | 13.5              | 69785                   | 0:00.01          | 0:00.00            | 1536                       | 1280                         |
| gz        | 8     | 14.19             | 66420                   | 0:00.03          | 0:00.00            | 1408                       | 1280                         |
| gz        | 9     | 14.21             | 66335                   | 0:00.02          | 0:00.00            | 1408                       | 1280                         |

### Test: test3-6,8 (Original size: 7037012 bytes)

| Algorithm | Level | Compression Ratio | Compressed Size (bytes) | Compression Time | Decompression Time | Memory Usage (compression) | Memory Usage (decompression) |
| --------- | ----- | ----------------- | ----------------------- | ---------------- | ------------------ | -------------------------- | ---------------------------- |
| lz4       | 1     | 7.21              | 975005                  | 0:00.02          | 0:00.02            | 6016                       | 6144                         |
| lz4       | 2     | 7.21              | 975005                  | 0:00.02          | 0:00.02            | 6016                       | 6144                         |
| lz4       | 3     | 9.02              | 779713                  | 0:00.06          | 0:00.02            | 6144                       | 6016                         |
| lz4       | 4     | 9.07              | 775295                  | 0:00.07          | 0:00.02            | 6144                       | 6016                         |
| lz4       | 5     | 9.09              | 773471                  | 0:00.08          | 0:00.02            | 6144                       | 6016                         |
| lz4       | 6     | 9.1               | 772636                  | 0:00.09          | 0:00.02            | 6144                       | 6016                         |
| lz4       | 7     | 9.11              | 772445                  | 0:00.11          | 0:00.02            | 6144                       | 6016                         |
| lz4       | 8     | 9.1               | 772803                  | 0:00.15          | 0:00.02            | 6144                       | 6016                         |
| lz4       | 9     | 9.1               | 772887                  | 0:00.19          | 0:00.02            | 6144                       | 6016                         |
| zstd      | 1     | 12.29             | 572223                  | 0:00.02          | 0:00.01            | 10112                      | 3968                         |
| zstd      | 2     | 12.04             | 584267                  | 0:00.03          | 0:00.01            | 10496                      | 4352                         |
| zstd      | 3     | 12.16             | 578262                  | 0:00.04          | 0:00.02            | 11392                      | 5376                         |
| zstd      | 4     | 12.15             | 579112                  | 0:00.05          | 0:00.01            | 12672                      | 5376                         |
| zstd      | 5     | 13.12             | 535992                  | 0:00.09          | 0:00.02            | 13056                      | 5376                         |
| zstd      | 6     | 13.62             | 516502                  | 0:00.11          | 0:00.01            | 13056                      | 5376                         |
| zstd      | 7     | 13.89             | 506569                  | 0:00.13          | 0:00.02            | 15616                      | 5248                         |
| zstd      | 8     | 15.45             | 455221                  | 0:00.16          | 0:00.02            | 15616                      | 5248                         |
| zstd      | 9     | 15.48             | 454514                  | 0:00.16          | 0:00.02            | 20736                      | 7296                         |
| zstd      | 10    | 15.59             | 451125                  | 0:00.24          | 0:00.02            | 30848                      | 7296                         |
| zstd      | 11    | 15.66             | 449249                  | 0:00.34          | 0:00.02            | 30976                      | 7296                         |
| zstd      | 12    | 15.65             | 449364                  | 0:00.35          | 0:00.01            | 51456                      | 7296                         |
| zstd      | 13    | 15.78             | 445850                  | 0:00.36          | 0:00.02            | 43392                      | 7296                         |
| zstd      | 14    | 15.97             | 440595                  | 0:00.47          | 0:00.02            | 59776                      | 7296                         |
| zstd      | 15    | 15.96             | 440727                  | 0:00.58          | 0:00.02            | 76160                      | 7296                         |
| zstd      | 16    | 15.92             | 442006                  | 0:01.37          | 0:00.02            | 43264                      | 7296                         |
| zstd      | 17    | 15.96             | 440723                  | 0:01.57          | 0:00.02            | 59520                      | 9728                         |
| zstd      | 18    | 14.69             | 478770                  | 0:02.13          | 0:00.02            | 60160                      | 9728                         |
| zstd      | 19    | 18.83             | 373565                  | 0:04.67          | 0:00.03            | 92928                      | 9472                         |
| bz2       | 1     | 13.22             | 532143                  | 0:00.79          | 0:00.13            | 2176                       | 1664                         |
| bz2       | 2     | 14.71             | 478166                  | 0:00.86          | 0:00.14            | 2816                       | 2048                         |
| bz2       | 3     | 15.43             | 455838                  | 0:00.92          | 0:00.14            | 3584                       | 2432                         |
| bz2       | 4     | 16.05             | 438372                  | 0:00.98          | 0:00.15            | 4224                       | 2816                         |
| bz2       | 5     | 16.38             | 429452                  | 0:01.02          | 0:00.16            | 4992                       | 3200                         |
| bz2       | 6     | 16.72             | 420694                  | 0:01.08          | 0:00.19            | 5632                       | 3584                         |
| bz2       | 7     | 16.81             | 418556                  | 0:01.12          | 0:00.21            | 6272                       | 3968                         |
| bz2       | 8     | 16.88             | 416869                  | 0:01.18          | 0:00.21            | 7040                       | 4352                         |
| bz2       | 9     | 16.95             | 415030                  | 0:01.24          | 0:00.23            | 7680                       | 4736                         |
| gz        | 1     | 9.6               | 732430                  | 0:00.07          | 0:00.04            | 1664                       | 1536                         |
| gz        | 2     | 9.69              | 725787                  | 0:00.06          | 0:00.05            | 1664                       | 1536                         |
| gz        | 3     | 9.75              | 721360                  | 0:00.06          | 0:00.04            | 1664                       | 1536                         |
| gz        | 4     | 10.6              | 663557                  | 0:00.07          | 0:00.04            | 1664                       | 1536                         |
| gz        | 5     | 10.99             | 639824                  | 0:00.07          | 0:00.04            | 1664                       | 1536                         |
| gz        | 6     | 11.63             | 605074                  | 0:00.10          | 0:00.04            | 1664                       | 1536                         |
| gz        | 7     | 12.19             | 577046                  | 0:00.15          | 0:00.04            | 1664                       | 1536                         |
| gz        | 8     | 12.43             | 565983                  | 0:00.33          | 0:00.04            | 1664                       | 1536                         |
| gz        | 9     | 12.43             | 565947                  | 0:00.35          | 0:00.04            | 1664                       | 1536                         |

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork this repository.
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m "Add YourFeature"
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a Pull Request.

Please follow the existing code style and provide tests/examples where applicable.

---

## License

This project is licensed under the [MIT License](LICENSE.md).
