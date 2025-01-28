import argparse
import ipaddress
from .vlsm_table import VLSM
import csv
import json
from tabulate import tabulate
from termcolor import colored

def print_message(message, message_type="info"):
    """Prints a message with a colored signifier."""
    if message_type == "info":
        sign = colored("[!]", "blue")
    elif message_type == "error":
        sign = colored("[x]", "red")
    elif message_type == "success":
        sign = colored("[✓]", "green")
    else:
        sign = colored("[?]", "yellow") 
    print(f"{sign}: {message}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="VLSM Calculator: Calculate subnet masks and IP ranges for a given list of hosts."
    )
    
    parser.add_argument(
        "-H", "--Hosts", 
        help="List of hosts separated by commas (e.g., 120,2,23,8,2x10)", 
        required=True
    )
    parser.add_argument(
        "-ID", "--net-ID", 
        help="Network ID. Default ID: 172.16.0.0", 
        default="172.16.0.0"
    )
    parser.add_argument(
        "-f", "--format", 
        help="Export format: txt, csv, json", 
        choices=["txt", "csv", "json"]
    )
    parser.add_argument(
        "-o", "--output", 
        help="Specify the output file name without extension (e.g., 'custom_name').",
    )
    parser.add_argument(
        "-n", "--no-table", 
        action="store_true", 
        help="Hide the table in the standard output"
    )
    
    return parser.parse_args()

def expand_hosts(hosts: str) -> list:
    """Expand any 'NxM' expressions in the host list."""
    expanded_hosts = []
    for h in hosts.split(","):
        if "x" in h:
            try:
                number, repetitions = map(int, h.split("x"))
                expanded_hosts.extend([number] * repetitions)
            except ValueError:
                print_message(f"Invalid format in host range '{h}'. Use 'NxM' with integers.", "error")
                raise 
        else:
            try:
                expanded_hosts.append(int(h))
            except ValueError:
                print_message(f"Host '{h}' is not a valid number.", "error")
                raise 

    return expanded_hosts

def export_to_txt(data: dict, filename: str):
    """Export data to plain text format using tabulate."""
    table = tabulate(data, headers="keys", tablefmt="plain")
    with open(f"{filename}.txt", "w") as f:
        f.write(table)
    print_message(f"Data exported to {filename}.txt", "success")

def export_to_csv(data: dict, filename: str):
    """Export data to CSV format."""
    with open(f"{filename}.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        headers = list(data.keys())
        writer.writerow(headers)
        
        rows = zip(*data.values())
        writer.writerows(rows)
        
    print_message(f"Data exported to {filename}.csv", "success")

def export_to_json(data: dict, filename: str):
    """Export data to JSON format, creating a dictionary for each row."""
    headers = list(data.keys())
    rows = zip(*data.values())
    
    json_dict = {}
    for row in rows:
        row_dict = {headers[1:][i]: row[1:][i] for i in range(len(headers[1:]))}
        json_dict[row[0]] = row_dict

    with open(f"{filename}.json", "w") as jsonfile:
        json.dump([json_dict], jsonfile, indent=4)
    
    print_message(f"Data exported to {filename}.json", "success")

def validate_ip(ip: str) -> bool:
    """Validate if the given string is a valid IPv4 address and explain reasons if invalid."""
    try:
        ip_addr = ipaddress.IPv4Address(ip)

        # Check if the IP is loopback
        if ip_addr.is_loopback:
            print_message(f"{ip} is a loopback address (127.0.0.0/8). Loopback addresses are reserved for local communication within a host.", "error")
            return False

        # Check if the IP is link-local
        if ip_addr.is_link_local:
            print_message(f"{ip} is a link-local address (169.254.0.0/16). Link-local addresses are used for auto-configuration and are not routable.", "error")
            return False

        # Check if the IP is unspecified
        if ip_addr.is_unspecified:
            print_message(f"{ip} is the unspecified address (0.0.0.0). This address cannot be assigned to any device.", "error")
            return False

        return True
    except ipaddress.AddressValueError:
        print_message(f"{ip} is not a valid IPv4 address. Please check the format (e.g., 192.168.1.1).", "error")
        return False


def main():
    """Main function to execute VLSM logic."""
    args = parse_arguments()

    if args.no_table and not (args.format or args.output):
        print_message("'--no-table' or '-n' can only be used when specifying an export format or output file.", "error")
        return

    # Validate the network ID
    if not validate_ip(args.net_ID):
        return

    # Define the filename and the output format
    output_filename = args.output if args.output else "vlsm_output"
    output_format = args.format if args.format else "txt" if args.output else None

    try:
        # Expand the host list, supporting 'NxM' syntax
        subnets = expand_hosts(args.Hosts)

        # Create VLSM instance and generate the table
        vl = VLSM(net_id=args.net_ID, subnets=subnets)
        vlsm_data = vl.get_vlsm_dict()

        # Show the table if no format is specified or if --No-Table is not set
        if not args.no_table:
            vl.print_vlsm_table()

        # Export if a format is specified 
        if output_format:
            if output_format == "txt":
                export_to_txt(vlsm_data, output_filename)
            elif output_format == "csv":
                export_to_csv(vlsm_data, output_filename)
            elif output_format == "json":
                export_to_json(vlsm_data, output_filename)

    except ValueError as ve:
        print_message(f"Error in provided values: {ve}", "error")
    except Exception as e:
        print_message(f"Unexpected error: {e}", "error")

if __name__ == "__main__":
    main()