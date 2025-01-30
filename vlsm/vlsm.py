from tabulate import tabulate
from termcolor import colored
from .vlsm_calc import VLSM
import argparse
import ipaddress
import re
import csv
import json

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
        help="List of hosts separated by commas (e.g., 120,2,23,8,2x10)"
    )
    parser.add_argument(
        "-ID", "--net-ID", 
        help="Network ID. Default ID: 172.16.0.0/24", 
        default="172.16.0.0/24"
    )
    parser.add_argument(
        "-f", "--format", 
        help="Export format: txt, csv, json, html", 
        choices=["txt", "csv", "json", "html"]
    )
    parser.add_argument(
        "-o", "--output", 
        help="Specify the output file name without extension (e.g., 'custom_name')."
    )
    parser.add_argument(
        "-n", "--no-table", 
        action="store_true", 
        help="Hide the table in the standard output"
    )
    parser.add_argument(
        "-r", "--reverse-lookup", 
        help="Perform reverse VLSM lookup for a given network in CIDR format (e.g., 192.168.10.0/24)."
    )
    
    return parser.parse_args()

def expand_hosts(hosts: str) -> list:
    """Expand any 'NxM' expressions in the host list."""
    expanded_hosts = []
    for h in hosts.split(","):
        if "x" in h:
            try:
                number, repetitions = map(int, h.split("x"))
                if number <= 0 or repetitions <= 0:
                    print_message(f"Host values must be greater than zero in '{h}'.", "error")
                    raise ValueError
                expanded_hosts.extend([number] * repetitions)
            except ValueError:
                print_message(f"Invalid format in host range '{h}'. Use 'NxM' with positive integers.", "error")
                raise 
        else:
            try:
                host_value = int(h)
                if host_value <= 0:
                    print_message(f"Host value '{h}' must be greater than zero.", "error")
                    raise ValueError
                expanded_hosts.append(host_value)
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

def export_to_html(data: dict, filename: str):
    """Export data to HTML format."""
    headers = list(data.keys())
    rows = zip(*data.values())

    # Build the HTML content
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VLSM Table</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        table, th, td { border: 1px solid #ddd; }
        th, td { padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>VLSM Calculation Results</h1>
    <table>
        <thead>
            <tr>""" + "".join(f"<th>{header}</th>" for header in headers) + """</tr>
        </thead>
        <tbody>"""

    # Add table rows
    for row in rows:
        html_content += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"

    html_content += """
        </tbody>
    </table>
</body>
</html>"""

    # Write the HTML to a file
    with open(f"{filename}.html", "w") as f:
        f.write(html_content)
    print_message(f"Data exported to {filename}.html", "success")
    
def reverse_subnet_lookup(ip_with_prefix: str):
    """Perform reverse subnet lookup for a given IP and prefix."""
    try:
        network = ipaddress.ip_network(ip_with_prefix, strict=False)
        
        print_message(f"Reverse Lookup Results for {ip_with_prefix}", "info")

        # Crear los datos para la tabla
        headers = ["Property", "Value"]
        table_data = [
            ["Network Address", network.network_address],
            ["Broadcast Address", network.broadcast_address],
            ["Subnet Mask", network.netmask],
            ["Host Range", f"{network.network_address + 1} - {network.broadcast_address - 1}"],
            ["Total Hosts", network.num_addresses - 2]
        ]

        # Imprimir la tabla
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    except ValueError:
        print_message(f"Invalid input '{ip_with_prefix}'. Please provide in CIDR format (e.g., 192.168.1.10/24).", "error")

def validate_ip(net_id: str) -> bool:
    """Validate if the given string is a valid IPv4 network and check additional restrictions."""
    try:
        # Try to create an IPv4 network object
        network = ipaddress.IPv4Network(net_id, strict=False)
        ip_addr = ipaddress.IPv4Address(net_id.split('/')[0])  # Extraer solo la dirección IP

        # Validating the CIDR notation
        cidr_pattern = r"^\d{1,3}(\.\d{1,3}){3}/\d{1,2}$"
                
        if not re.match(cidr_pattern, net_id):
            print_message(f"Invalid format: {net_id}. Please use CIDR notation (e.g., 192.168.1.0/24).", "error")
            return False
        
        # Check if the network is a broadcast address
        if ip_addr == network.broadcast_address:
            print_message(f"{net_id} is the broadcast address of the network.", "error")
            return False
        
        # Check if the network is a valid network address (not the broadcast address or invalid IP)
        if ip_addr != network.network_address:
            print_message(f"{net_id} is not a valid network address. Please provide a network address.", "error")
            return False
        
        # Check if the network is a loopback address
        if ip_addr.is_loopback:
            print_message(f"{net_id} is a loopback address (127.0.0.0/8). Reserved for internal host communication.", "error")
            return False

        # Check if the network is a link-local address  
        if ip_addr.is_link_local:
            print_message(f"{net_id} is a link-local address (169.254.0.0/16). Used for auto-configuration and not routable.", "error")
            return False

        # Check if the network is a unspecified address
        if ip_addr.is_unspecified:
            print_message(f"{net_id} is the unspecified address (0.0.0.0). This address cannot be assigned to any device.", "error")
            return False

        return True

    except ValueError:
        print_message(f"{net_id} is not a valid IPv4 address or CIDR notation (e.g., 192.168.1.0/24).", "error")
        return False


def print_vlsm_table(vl_obj, table_format: str="fancy_grid") -> None:
        def format_ips(ips: list) -> tuple:
            return tuple([".".join(str(o) for o in p) for p in ips])

        def rows(row: list) -> tuple:
            out_row = []
            for i in range(len(row)):
                if i % 2 == 0:
                    out_row.append(colored(row[i], "white"))
                else:
                    out_row.append(colored(row[i], "blue"))

            return tuple(out_row)

        header = lambda text: colored(text, "green")

        vlsm_output = {
            header("#") : rows(list(range(1, len(vl_obj.get_hosts())+1))),
            header("Hosts") : rows(vl_obj.get_hosts()),
            header("Total Hosts") : rows(vl_obj.get_total_hosts()),
            header("Subnet") : rows(format_ips(vl_obj.get_net_ids())),
            header("Prefix") : rows([f"/{h}" for h in vl_obj.get_prefixes()]),
            header("Mask") : rows(format_ips(vl_obj.get_masks())),
            header("First Host") : rows(format_ips(vl_obj.get_first_ips())),
            header("Last Host") : rows(format_ips(vl_obj.get_last_ips())),
            header("Broadcast") : rows(format_ips(vl_obj.get_broadcasts())),
            header("Wildcard") : rows(format_ips(vl_obj.get_wildcard()) ) 
        }
    
        print(tabulate(vlsm_output, headers="keys", tablefmt=table_format))

def main():
    """Main function to execute VLSM logic."""
    args = parse_arguments()

    # Check for reverse lookup option
    if args.reverse_lookup:
        reverse_subnet_lookup(args.reverse_lookup)
        return

    if not args.Hosts:
        print_message("Argument '-H/--Hosts' is required unless '-r/--reverse-lookup' is used.", "error")
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
        vl = VLSM(net_id=args.net_ID.split('/')[0], subnets=subnets)
        
        # Show the table if no format is specified or if --No-Table is not set
        if not args.no_table:
            print_vlsm_table(vl_obj=vl)

        # Export if a format is specified 
        if output_format:
            if output_format == "txt":
                
                export_to_txt(vl.get_vlsm_dict(), output_filename)
            elif output_format == "csv":
                export_to_csv(vl.get_vlsm_dict(), output_filename)
            elif output_format == "json":
                export_to_json(vl.get_vlsm_dict(), output_filename)
            elif output_format == "html":
                export_to_html(vl.get_vlsm_dict(), output_filename)

    except ValueError as ve:
        return
    except Exception as e:
        print_message(f"Unexpected error: {e}", "error")

if __name__ == "__main__":
    main()