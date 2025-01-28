from copy import deepcopy

class VLSM:

    def __init__(self, net_id: str, subnets: list = [2]):
        self.__net_id = net_id
        self.__subnets = subnets
        self.__masks = self.__precalculate_masks()
        self.__hosts, self.__total_hosts, self.__prefixes = self.__set_hosts_and_prefix(self.__subnets)    
        self.__decimal_masks = self.__set_masks(self.__prefixes)
        self.__network_ids = self.__set_network_ids(self.__net_id, self.__prefixes, self.__decimal_masks)
        self.__first_ips = self.__set_first_ips(self.__network_ids)
        self.__broadcasts = self.__set_broadcasts(self.__network_ids)
        self.__last_ips = self.__set_last_ips(self.__broadcasts)
        self.__wildcard = self.__set_wildcard(self.__decimal_masks)

    @staticmethod
    def __precalculate_masks() -> dict:
        OCTET_VALUES = [0, 128, 192, 224, 240, 248, 252, 254, 255]
        masks = {}
        for p in range(1, 33):
            mask = [255] * 4
            octet_index = (p - 1) // 8 + 1
            mask[octet_index - 1] = OCTET_VALUES[8 - ((octet_index * 8) - p)]
            mask[octet_index:] = [0] * (4 - octet_index)
            masks[p] = mask
        return masks

    def __set_hosts_and_prefix(self, subnets: list) -> tuple:
        subnets.sort(reverse=True)
        powers_of_two = [2**p for p in range(24)]
        hosts = []
        total_hosts = []
        prefixes = []
        for sub in subnets:
            for p, power in enumerate(powers_of_two):
                if power > sub and (sub - (power-2)) not in (1, 2):
                    hosts.append(sub)
                    total_hosts.append(power-2)
                    prefixes.append(32-p)
                    break
        return hosts, total_hosts, prefixes

    def __set_masks(self, prefixes: list) -> list:
        return [self.__masks.get(p) for p in prefixes]

    def __set_network_ids(self, net_id: str, prefixes: list, masks: list) -> list:
        ids = [list(map(int, net_id.split('.')))]
        
        for i, prefix in enumerate(prefixes):
            octet_index = (prefix - 1) // 8
            new_id = ids[-1][:]  
            add = new_id[octet_index] + 256 - int(masks[i][octet_index])
            
            while add > 255:
                new_id[octet_index] = add % 256
                carry = add // 256
                octet_index -= 1
                if octet_index < 0:  # If carry exceeds the first octet
                    raise ValueError("Overflow cannot propagate beyond the first octet")
                add = new_id[octet_index] + carry
            
            new_id[octet_index] = add
            ids.append(new_id)
        
        return ids


    def __set_first_ips(self, net_ids: list) -> list:
        return [i[:3] + [i[3] + 1] for i in net_ids]

    def __set_broadcasts(self, net_ids: list) -> list:
        def process_ip(ip: list) -> list:
            for i in range(len(ip) - 1, -1, -1):
                if ip[i] != 0:
                    ip[i] -= 1
                    ip[i + 1:] = [255] * (len(ip) - i - 1)
                    break
            return ip
        return [process_ip(deepcopy(i)) for i in net_ids[1:]]

    def __set_last_ips(self, broadcasts: list) -> list:
        return [b[:3] + [b[3] - 1] for b in broadcasts]

    def __set_wildcard(self, masks: list) -> list:
        return [[255 - o for o in w] for w in masks]

    def get_hosts(self) -> tuple:
        return tuple(self.__hosts)

    def get_total_hosts(self) -> tuple:
        return tuple(self.__total_hosts)

    def get_prefixes(self) -> tuple:
        return tuple(self.__prefixes)

    def get_masks(self) -> tuple:
        return tuple(self.__decimal_masks) 

    def get_net_ids(self) -> tuple:
        return tuple(self.__network_ids[:-1])

    def get_first_ips(self) -> tuple:
        return tuple(self.__first_ips[:-1])

    def get_broadcasts(self) -> tuple:
        return tuple(self.__broadcasts)

    def get_last_ips(self) -> tuple:
        return tuple(self.__last_ips)

    def get_wildcard(self) -> tuple:
        return tuple(self.__wildcard)

    def get_vlsm_dict(self) -> dict:
        def format_ips(ips: list) -> tuple:
            return tuple([".".join(str(o) for o in p) for p in ips])

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