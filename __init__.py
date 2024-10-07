# Python program to demonstrate
# command line arguments
 
 
import argparse
import regex
import re
 
 
# Initialize parser
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-H", "--Hosts", help = "Add hosts list (separed by a coma e.g. 120,2,23,8,23)")
parser.add_argument("-ID", "--net-ID" , help="Set network ID: A.B.C.")
 
# Read arguments from command line
args = parser.parse_args()

if args.Hosts:
    hosts_list = args.Hosts.split(",")
    not_number_index = [" "] * len(args.Hosts)
    index = 0

    for h in hosts_list:
        if not h.isdigit():
            not_number_index[index] = "^"
        index += len(h) + 1

    print(f"""Next elements aren't valid hosts numbers:\nhosts_list: {args.Hosts}
            {"".join(not_number_index)}""")

if args.net_ID:
    print(args.net_ID)

