#!/usr/bin/env bash
# Script to compare compression algorithms: bz2, gz, lz4, zstd
# Author: fazelukario
# Date: 2025-05-12

set -e

# Check for required tools
check_requirements() {
    local missing_tools=()

    for tool in bzip2 gzip lz4 zstd time jq; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done

    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo "Error: the following tools are missing from the system:"
        for tool in "${missing_tools[@]}"; do
            echo "  - $tool"
        done
        echo "Please install the required tools and try again."
        exit 1
    fi
}

# Function to calculate compression ratio and percentage
calculate_compression_stats() {
    local original_size=$1
    local compressed_size=$2
    local compression_ratio
    local compression_percentage

    # Calculate compression ratio (original size to compressed size)
    compression_ratio=$(echo "scale=2; $original_size / $compressed_size" | bc)

    # Calculate compression percentage
    compression_percentage=$(echo "scale=2; (1 - ($compressed_size / $original_size)) * 100" | bc)
    compression_percentage="${compression_percentage}%"

    compressed_percentage=$(echo "scale=2; ($compressed_size / $original_size) * 100" | bc)

    echo "$compression_ratio $compression_percentage $compressed_percentage"
}

# Function to compress file and collect metrics
compress_file() {
    local file=$1
    local algorithm=$2
    local level=$3
    local temp_dir=$4
    local output_file
    local time_output
    local real_time
    local cpu_percentage
    local sys_time
    local user_time
    local avg_mem
    local max_mem
    local original_size
    local compressed_size
    local compression_ratio
    local compression_percentage
    local json_result

    trap '_trap_DEBUG' DEBUG

    output_file="${temp_dir}/$(basename "$file").${algorithm}"

    if [ "$algorithm" = "bz2" ]; then
        # Add -$level explicitly for compression level
        time_output=$(/usr/bin/time -f "%E %P %S %U %K %M" bzip2 -k -c -"$level" "$file" > "$output_file" 2>&1)
    elif [ "$algorithm" = "gz" ]; then
        time_output=$(/usr/bin/time -f "%E %P %S %U %K %M" gzip -k -c -"$level" "$file" > "$output_file" 2>&1)
    elif [ "$algorithm" = "lz4" ]; then
        time_output=$(/usr/bin/time -f "%E %P %S %U %K %M" lz4 -k -c -"$level" "$file" > "$output_file" 2>&1)
    elif [ "$algorithm" = "zstd" ]; then
        time_output=$(/usr/bin/time -f "%E %P %S %U %K %M" zstd -k -c -"$level" "$file" > "$output_file" 2>&1)
    else
        echo "Unknown algorithm: $algorithm"
        exit 1
    fi

    # Parse time output
    real_time=$(echo "$time_output" | awk '{print $1}')
    cpu_percentage=$(echo "$time_output" | awk '{print $2}')
    sys_time=$(echo "$time_output" | awk '{print $3}')
    user_time=$(echo "$time_output" | awk '{print $4}')
    avg_mem=$(echo "$time_output" | awk '{print $5}')
    max_mem=$(echo "$time_output" | awk '{print $6}')

    # Get file sizes
    original_size=$(stat -c %s "$file")
    compressed_size=$(stat -c %s "$output_file")

    # Calculate compression ratio and percentage
    read -r compression_ratio compression_percentage compressed_percentage < <(calculate_compression_stats "$original_size" "$compressed_size")

    # Result in JSON format - using jq to ensure proper JSON escaping
    json_result=$(jq -n \
        --arg orig_size "$original_size" \
        --arg comp_size "$compressed_size" \
        --arg comp_ratio "$compression_ratio" \
        --arg comp_perc "$compression_percentage" \
        --arg comp_size_perc "$compressed_percentage" \
        --arg real "$real_time" \
        --arg cpu "$cpu_percentage" \
        --arg max "$max_mem" \
        --arg avg "$avg_mem" \
        --arg sys "$sys_time" \
        --arg user "$user_time" \
        --arg output "$output_file" \
        '{
            originalSize: ($orig_size | tonumber),
            compressedSize: ($comp_size | tonumber),
            compressionRatio: ($comp_ratio | tonumber),
            compressionPercentage: $comp_perc,
            compressedPercentage: $comp_size_perc,
            real: $real,
            CPU: $cpu,
            max: ($max | tonumber),
            avg: ($avg | tonumber),
            sys: ($sys | tonumber),
            user: ($user | tonumber),
            outputFile: $output
        }')

    echo "$json_result"
}

# Function to decompress file and collect metrics
decompress_file() {
    local compressed_file=$1
    local algorithm=$2
    local temp_dir=$3
    local output_file
    local time_output
    local real_time
    local cpu_percentage
    local sys_time
    local user_time
    local avg_mem
    local max_mem
    local json_result

    trap '_trap_DEBUG' DEBUG

    output_file="${temp_dir}/decompressed_$(basename "$compressed_file")"

    if [ "$algorithm" = "bz2" ]; then
        time_output=$(/usr/bin/time -f "%E %P %S %U %K %M" bzip2 -d -c "$compressed_file" > "$output_file" 2>&1)
    elif [ "$algorithm" = "gz" ]; then
        time_output=$(/usr/bin/time -f "%E %P %S %U %K %M" gzip -d -c "$compressed_file" > "$output_file" 2>&1)
    elif [ "$algorithm" = "lz4" ]; then
        time_output=$(/usr/bin/time -f "%E %P %S %U %K %M" lz4 -d -c "$compressed_file" > "$output_file" 2>&1)
    elif [ "$algorithm" = "zstd" ]; then
        time_output=$(/usr/bin/time -f "%E %P %S %U %K %M" zstd -d -c "$compressed_file" > "$output_file" 2>&1)
    else
        echo "Unknown algorithm: $algorithm"
        exit 1
    fi

    # Parse time output
    real_time=$(echo "$time_output" | awk '{print $1}')
    cpu_percentage=$(echo "$time_output" | awk '{print $2}')
    sys_time=$(echo "$time_output" | awk '{print $3}')
    user_time=$(echo "$time_output" | awk '{print $4}')
    avg_mem=$(echo "$time_output" | awk '{print $5}')
    max_mem=$(echo "$time_output" | awk '{print $6}')

    # Result in JSON format
    json_result=$(jq -n \
        --arg real "$real_time" \
        --arg cpu "$cpu_percentage" \
        --arg max "$max_mem" \
        --arg avg "$avg_mem" \
        --arg sys "$sys_time" \
        --arg user "$user_time" \
        '{
            real: $real,
            CPU: $cpu,
            max: ($max | tonumber),
            avg: ($avg | tonumber),
            sys: ($sys | tonumber),
            user: ($user | tonumber)
        }')

    echo "$json_result"
}

# Function to test all combinations of algorithms and compression levels
test_compression_algorithms() {
    local file=$1
    local temp_dir
    local filename
    local results
    local algorithms
    local algorithm_results
    local compression_result
    local output_file
    local decompression_result
    local level_results

    trap '_trap_DEBUG' DEBUG

    temp_dir=$(mktemp -d)
    filename=$(basename "$file")
    results="{}"

    echo "Testing compression for file: $filename"

    # Algorithms and their compression level ranges
    declare -A algorithms=(
        ["bz2"]="1 2 3 4 5 6 7 8 9"
        ["gz"]="0 1 2 3 4 5 6 7 8 9"
        ["lz4"]="1 2 3 4 5 6 7 8 9"
        ["zstd"]="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19"
    ) # Process all algorithms
    for algorithm in "${!algorithms[@]}"; do
        echo "  Algorithm: $algorithm"
        algorithm_results="{}"

        # Process all compression levels for the algorithm
        for level in ${algorithms[$algorithm]}; do
            echo "    Compression level: $level"

            # Get compression results (ensure we get clean JSON outputs)
            compression_result=$(compress_file "$file" "$algorithm" "$level" "$temp_dir")
            output_file=$(echo "$compression_result" | jq -r '.outputFile')

            # Get decompression results (ensure we get clean JSON outputs)
            decompression_result=$(decompress_file "$output_file" "$algorithm" "$temp_dir")

            # Create JSON for this compression level using jq
            level_results=$(jq -n \
                --argjson compression "$(echo "$compression_result" | jq 'del(.outputFile)')" \
                --argjson decompression "$decompression_result" \
                '{
                    compression: $compression,
                    decompression: $decompression
                }')

            # Add this level's results to algorithm results - sanitize with jq
            algorithm_results=$(echo "$algorithm_results" | jq --argjson level_results "$level_results" --arg level "$level" '. + {($level): $level_results}')
        done

        # Add this algorithm's results to overall results - sanitize with jq
        results=$(echo "$results" | jq --argjson algorithm_results "$algorithm_results" --arg algorithm "$algorithm" '. + {($algorithm): $algorithm_results}')
    done

    # Remove temporary directory
    rm -rf "$temp_dir"

    echo "$results"
}

# Main function
main() {
    local output_json
    local file_results
    local output_file

    trap '_trap_DEBUG' ERR

    # Check for required tools
    check_requirements

    # Check for arguments
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <file1> [file2] [file3] ..."
        exit 1
    fi

    output_json="[]"

    # Process each file
    for file in "$@"; do
        if [ ! -f "$file" ]; then
            echo "Error: file '$file' does not exist or is not a regular file."
            continue
        fi

        # Test compression algorithms for the file
        file_results=$(test_compression_algorithms "$file")

        # Add file results to overall JSON - sanitize with jq
        output_json=$(echo "$output_json" | jq --argjson file_results "$file_results" --arg filename "$(basename "$file")" '. + [{($filename): $file_results}]')
    done

    # Create output JSON file
    output_file="$(date +%Y-%m-%d-%H-%M-%S).json"
    echo "$output_json" | jq '.' > "$output_file"

    echo "Results saved to file: $output_file"
}

# Run main function with all arguments
main "$@"
