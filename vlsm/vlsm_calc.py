from functools import lru_cache
from copy import copy
import math

class VLSM:

    def __init__(self, net_id: str, subnets: list = [2]):
        self.__net_id = net_id
        self.__masks_list = self.__precalculate_masks()
        self.__hosts, self.__total_hosts, self.__prefixes = self.__set_hosts_and_prefix(subnets)    
        self.__masks = self.__set_masks()
        self.__network_ids = self.__set_network_ids()
        self.__first_ips = self.__set_first_ips()
        self.__broadcasts = self.__set_broadcasts()
        self.__last_ips = self.__set_last_ips()
        self.__wildcard = self.__set_wildcard()

    @staticmethod
    @lru_cache(maxsize=None)
    def __precalculate_masks() -> dict:
        masks = {}
        for p in range(1, 33):
            full_octets = p // 8
            remaining_bits = p % 8
            
            mask = [255] * full_octets
            if remaining_bits:
                mask.append(256 - (1 << (8 - remaining_bits)))
            mask.extend([0] * (4 - len(mask)))
            masks[p] = tuple(mask)
        return masks

    def __set_hosts_and_prefix(self, subnets: list) -> tuple:
        subnets.sort(reverse=True)
        hosts = []
        total_hosts = []
        prefixes = []
        
        for sub in subnets:
            bits_needed = math.ceil(math.log2(sub + 2))
            prefix = 32 - bits_needed
            total_hosts_subnet = (1 << bits_needed) - 2
            hosts.append(sub)
            total_hosts.append(total_hosts_subnet)
            prefixes.append(prefix)
        
        return tuple(hosts), tuple(total_hosts), tuple(prefixes)

    @lru_cache(maxsize=None)
    def __set_masks(self) -> tuple:
        return tuple(self.__masks_list[p] for p in self.__prefixes)

    @lru_cache(maxsize=None)
    def __set_network_ids(self) -> tuple:
        ids = [tuple(map(int, self.__net_id.split('.')))]
        
        for prefix in self.__prefixes:
            octet_index = (prefix - 1) // 8
            new_id = list(ids[-1])
            
            increment = 1 << (32 - prefix)
            add = new_id[octet_index] + (increment >> (8 * (3 - octet_index)))
                        
            while add > 255:
                new_id[octet_index] = add % 256
                carry = add // 256
                octet_index -= 1
                if octet_index < 0:  # If carry exceeds the first octet
                    raise ValueError("Overflow cannot propagate beyond the first octet")
                add = new_id[octet_index] + carry
            
            new_id[octet_index] = add
            ids.append(tuple(new_id))
        
        return tuple(ids)

    @lru_cache(maxsize=None)
    def __set_first_ips(self) -> tuple:
        return tuple(net_id[:3] + (net_id[3] + 1,) for net_id in self.__network_ids)

    @lru_cache(maxsize=None)
    def __set_broadcasts(self) -> tuple:
        def process_ip(ip: list) -> tuple:
            for i in range(len(ip) - 1, -1, -1):
                if ip[i] != 0:
                    ip[i] -= 1
                    ip[i + 1:] = [255] * (len(ip) - i - 1)
                    break
            return tuple(ip)
        return tuple(process_ip(list(net_id)) for net_id in self.__network_ids[1:])

    @lru_cache(maxsize=None)
    def __set_last_ips(self) -> tuple:
        return tuple(ip[:3] + (ip[3] - 1,) for ip in self.__broadcasts)

    @lru_cache(maxsize=None)
    def __set_wildcard(self) -> tuple:
        return tuple(tuple(255 - octet for octet in mask) for mask in self.__masks)

    def get_hosts(self) -> tuple:
        return self.__hosts

    def get_total_hosts(self) -> tuple:
        return self.__total_hosts

    def get_prefixes(self) -> tuple:
        return self.__prefixes

    def get_masks(self) -> tuple:
        return self.__masks 

    def get_net_ids(self) -> tuple:
        return self.__network_ids[:-1]

    def get_first_ips(self) -> tuple:
        return self.__first_ips[:-1]

    def get_broadcasts(self) -> tuple:
        return self.__broadcasts

    def get_last_ips(self) -> tuple:
        return self.__last_ips

    def get_wildcard(self) -> tuple:
        return self.__wildcard

    def get_vlsm_dict(self) -> dict:
        def format_ips(ips: tuple) -> tuple:
            return tuple(".".join(map(str, ip)) for ip in ips)

        vlsm_output = {
            "#" : list(range(1, len(self.get_hosts())+1)),
            "Hosts" : self.get_hosts(),
            "Total Hosts" : self.get_total_hosts(),
            "Subnet" : format_ips(self.get_net_ids()),
            "Prefix" : [f"/{h}" for h in self.get_prefixes()],
            "Mask" : format_ips(self.get_masks()),  
            "First Host" : format_ips(self.get_first_ips()),
            "Last Host" : format_ips(self.get_last_ips()),
            "Broadcast" : format_ips(self.get_broadcasts()),
            "Wildcard" : format_ips(self.get_wildcard())
        }

        return vlsm_output