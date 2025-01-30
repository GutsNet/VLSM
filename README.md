# VLSM Calculator

## Description

This program is a tool for calculating subnets using **VLSM** (Variable Length Subnet Masking). It allows you to input a base network and a list of host requirements per subnet, generating subnet masks, network addresses, valid IP ranges, and more. It is for students who want to learn or work with IP subnetting.

## Features

- Automatically calculates subnets based on host requirements.
- Generates detailed information for each subnet, including:
  - Network Address
  - Subnet Mask
  - Host Address Range
  - Broadcast Address
  - Wildcard
- Supports exporting results to multiple formats:
  - **TXT**
  - **CSV**
  - **JSON**
  - **HTML**
- Allows defining a custom network ID.
- Supports expressions like `NxM` to simplify repetitive subnet input.
- **Reverse Subnet Lookup**: Analyze a given network and retrieve details such as:
  - Network Address
  - Broadcast Address
  - Subnet Mask
  - Host Range
  - Total Hosts
- **IPv4 Validation**: Validates provided IPv4 addresses, identifying invalid inputs or special-case addresses such as:
  - Loopback (127.0.0.0/8)
  - Link-local (169.254.0.0/16)
  - Unspecified (0.0.0.0)

## Installation

1. Clone the repository or download the code:
   ```bash
   git clone https://github.com/GutsNet/VLSM.git
   cd VLSM
   ```
2. Ensure you have Python 3.6 or higher installed.
3. Install the package using `setup.py`:
   ```bash
   # Windows
   pip install .

   # Linux
   sudo pip install .
   ```

This will install the `vlsm` command-line tool and all its dependencies.

## Usage

The program is executed from the command line. Below are the available arguments:

### Available Arguments

| Argument             | Description                                                                                 | Required   | Default Value             |
|-----------------------|---------------------------------------------------------------------------------------------|------------|---------------------------|
| `-H` or `--Hosts`    | List of hosts separated by commas. Example: `120,2,23,8,2x10`.                              | **Yes**    | N/A                       |
| `-ID` or `--net-ID`  | Base network ID using CIDR notation. Example: `192.168.1.0/24`.                                                   | No         | `172.16.0.0/24`              |
| `-f` or `--format`   | Output format: `txt`, `csv`, `json`, `html`.                                               | No         | None                      |
| `-o` or `--output`   | Output file name (without extension).                                                      | No         | `vlsm_output`             |
| `-n` or `--no-table` | Hides the table in the standard output.                                                    | No         | N/A                       |
| `-r` or `--reverse-lookup` | Perform reverse lookup for a given network in CIDR format (e.g., `192.168.10.0/24`). | No         | N/A                       |

### Examples of Use

1. **Basic calculation with screen output**:
   ```bash
   vlsm -H 120,15,8
   ```

2. **Specify a custom network ID**:
   ```bash
   vlsm -H 50,30 -ID 192.168.1.0/24
   ```

3. **Export results to a TXT file**:
   ```bash
   vlsm -H 100,50,25 -f txt -o subnets
   ```

4. **Export to JSON without displaying the table in the console**:
   ```bash
   vlsm -H 200,50,10 -f json -n
   ```

5. **Use `NxM` syntax for repeated host requirements**:
   ```bash
   vlsm -H 20x5,50
   ```
   This command will generate 5 subnets with 20 hosts each and an additional subnet for 50 hosts. The NxM syntax is particularly useful when defining multiple subnets with the same number of required hosts. For example, 10x3 creates 3 subnets each capable of accommodating 10 hosts, saving time and simplifying input.

6. **Perform a reverse lookup for a CIDR network**:
   ```bash
   vlsm -r 192.168.1.0/24
   ```
   This will output details such as the network address, broadcast address, host range, and subnet mask for the given network.

### Output

When the program is executed, it generates a table in the console with the following information for each subnet:

- Subnet Number
- Number of Required Hosts
- Total Available Hosts
- Subnet Address
- CIDR Prefix
- Subnet Mask in Decimal Format
- First Host Address
- Last Host Address
- Broadcast Address
- Wildcard

#### Example Console Output:

```
╒════════╤════════╤══════════════╤═══════════════╤══════════╤═══════════════╤═══════════════╤═══════════════╤═══════════════╤══════════╕
│   #    │ Hosts  │ Total Hosts  │ Subnet        │ Prefix   │ Mask          │ First Host    │ Last Host     │ Broadcast     │ Wildcard │
╞════════╪════════╪══════════════╪═══════════════╪══════════╪═══════════════╪═══════════════╪═══════════════╪═══════════════╪══════════╡
│   1    │  120   │ 126          │ 192.168.1.0   │ /25      │ 255.255.255.128│ 192.168.1.1   │ 192.168.1.126 │ 192.168.1.127 │ 0.0.0.127│
│   2    │  15    │ 30           │ 192.168.1.128 │ /27      │ 255.255.255.224│ 192.168.1.129 │ 192.168.1.158 │ 192.168.1.159 │ 0.0.0.31 │
│   3    │   8    │ 14           │ 192.168.1.160 │ /28      │ 255.255.255.240│ 192.168.1.161 │ 192.168.1.174 │ 192.168.1.175 │ 0.0.0.15 │
╘════════╧════════╧══════════════╧═══════════════╧══════════╧═══════════════╧═══════════════╧═══════════════╧═══════════════╧══════════╛
```

### Output Files

Depending on the specified format, the results are exported to `txt`, `csv`, `json`, or `html` files. Example of a JSON file:

```json
{
  "1": {
    "Hosts": 120,
    "Total Hosts": 126,
    "Subnet": "192.168.1.0",
    "Prefix": "/25",
    "Mask": "255.255.255.128",
    "First Host": "192.168.1.1",
    "Last Host": "192.168.1.126",
    "Broadcast": "192.168.1.127",
    "Wildcard": "0.0.0.127"
  },
  "2": { ... },
  ...
}
```

## Additional Notes

- The program validates IP addresses and displays errors if the format is incorrect.
- Supports up to 24-bit prefixes for large subnets.
- The console table uses colors to enhance readability.

## Contributions

If you want to improve the program, please fork the repository and submit your changes via a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
