import argparse
from vlsm_table import VLSM
import csv
import json
from tabulate import tabulate

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="VLSM Calculator: Calculate subnet masks and IP ranges for a given list of hosts."
    )
    
    parser.add_argument(
        "-H", "--Hosts", 
        help="List of hosts separated by commas (e.g., 120,2,23,8,23)", 
        required=True
    )
    parser.add_argument(
        "-ID", "--net-ID", 
        help="Network ID. Default ID: 172.16.0.0", 
        default="172.16.0.0"
    )
    parser.add_argument(
        "-F", "--Format", 
        help="Export format: txt, csv, json", 
        choices=["txt", "csv", "json"]
    )
    parser.add_argument(
        "-N", "--No-Table", 
        action="store_true", 
        help="Hide the table in the standard output"
    )
    
    return parser.parse_args()

def export_to_txt(data, filename="vlsm_output.txt"):
    """Export data to plain text format using tabulate."""
    table = tabulate(data, headers="keys", tablefmt="plain")
    with open(filename, "w") as f:
        f.write(table)
    print(f"Data exported to {filename}")

def export_to_csv(data, filename="vlsm_output.csv"):
    """Export data to CSV format."""
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        headers = list(data.keys())
        writer.writerow(headers)
        
        rows = zip(*data.values())
        writer.writerows(rows)
        
    print(f"Data exported to {filename}")

def export_to_json(data, filename="vlsm_output.json"):
    """Export data to JSON format, creating a dictionary for each row."""
    headers = list(data.keys())
    rows = zip(*data.values())
    
    json_dict = {}
    for row in rows:
        # Create a dictionary for each row
        row_dict = {headers[1:][i]: row[1:][i] for i in range(len(headers[1:]))}
        json_dict[row[0]] = row_dict

    # Export JSON file
    with open(filename, "w") as jsonfile:
        json.dump([json_dict], jsonfile, indent=4)
    
    print(f"Datos exportados a {filename}")


def main():
    """Main function to execute VLSM logic."""
    args = parse_arguments()

    if args.No_Table and not args.Format:
        print("[x] Error: --No-Table or -N can only be used when specifying an export format.")
        return

    try:
        # Convert the list of hosts to integers
        subnets = [int(h) for h in args.Hosts.split(",")]

        # Create VLSM instance and generate the table
        vl = VLSM(net_id=args.net_ID, subnets=subnets)
        vlsm_data = vl.get_vlsm_dict()

        # Show the table if no format is specified or if --No-Table is not set
        if not args.Format or not args.No_Table:
            vl.print_vlsm_table()

        # Export if a format is specified
        if args.Format:
            if args.Format == "txt":
                export_to_txt(vlsm_data)
            elif args.Format == "csv":
                export_to_csv(vlsm_data)
            elif args.Format == "json":
                export_to_json(vlsm_data)

    except ValueError as ve:
        print(f"[x] Error in provided values: {ve}")
    except Exception as e:
        print(f"[x] Unexpected error: {e}")

if __name__ == "__main__":
    main()
