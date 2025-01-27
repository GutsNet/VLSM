# VLSM Calculator

## Description

The VLSM Calculator is a Python program that calculates subnet masks and IP ranges for a given list of hosts using Variable Length Subnet Masking (VLSM). It supports exporting the results in various formats including plain text, CSV, and JSON.

## Features

- Calculate subnet masks and IP ranges for a list of hosts.
- Support for 'NxM' syntax to specify multiple subnets.
- Export results to plain text, CSV, or JSON formats.
- Option to hide the table in the standard output.

## Requirements

- Python 3.x

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/GutsNet/VLSM.git
   ```
2. Navigate to the project directory:
   ```sh
   cd VLSM
   ```
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

Run the program with the required arguments:

```sh
python vlsm.py -H <hosts> [-ID <network_id>] [-f <format>] [-o <output_filename>] [-n]
```

### Arguments

- `-H`, `--Hosts`: List of hosts separated by commas (e.g., `120,2,23,8,2x10`). (Required)
- `-ID`, `--net-ID`: Network ID. Default is `172.16.0.0`.
- `-f`, `--format`: Export format: `txt`, `csv`, `json`.
- `-o`, `--output`: Specify the output file name without extension (e.g., `custom_name`).
- `-n`, `--no-table`: Hide the table in the standard output.

### Examples

Calculate VLSM for a list of hosts and display the table:

```sh
python vlsm.py -H 120,23,8,2x10
```

Calculate VLSM for a list of hosts with a custom network ID:

```sh
python vlsm.py -H 50,20,10,5 -ID 192.168.1.0
```

Calculate VLSM and export the results to a CSV file:

```sh
python vlsm.py -H 120,223,8,2x10 -f csv -o vlsm_results
```

Calculate VLSM and export the results to a JSON file, hiding the table in the standard output:

```sh
python vlsm.py -H 100,50,25,10 -f json -o vlsm_output -n
```

## License

