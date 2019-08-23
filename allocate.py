import sys
import ipaddress
from ipaddress import *
import json


Size = {'small': 24, 'medium': 23, 'large': 22}

# TODO: Save and get map from db 
Addresses = {'small': 256, 'medium': 512, 'large': 1024} 

def get_previous_allocation_list():
    allocated = []
    with open('allocated.json') as json_file:
        data = json.load(json_file)
        allocated = data["allocated"]
    return allocated

def dump_to_json_file(data_new):
    with open('allocated.json', 'w') as outfile:
                json.dump(data_new, outfile)

#sort network list
def sort_networks(networks):
    n = len(networks)
    for i in range(n):
        for j in range(0, n-i-1):
            num_hosts_j = networks[j].num_addresses
            num_hosts_next = networks[j+1].num_addresses
            # Swap if the number of addresses found is greater than in next subnet
            if num_hosts_j < num_hosts_next :
                networks[j], networks[j+1] = networks[j+1], networks[j]

# calculate updated from previous allocations
def get_same_or_next(networks, allocated):
    for allocated_network in allocated:
        a=IPv4Network(allocated_network)
        for network in networks:
            n=IPv4Network(network)
            if (a==n):
                print("same")
                networks.remove(n)
                sort_networks(networks)
                break
            elif (a.subnet_of(n)):
                print("subnet")
                networks.remove(n)
                after_exclude=list(n.address_exclude(a))
                for addr in after_exclude:
                    networks.append(addr)
                    sort_networks(networks)
                break
                # update networks
    prev_allocation = dict() 
    prev_allocation['networks'] = networks
    prev_allocation['allocated'] = allocated
    return prev_allocation

def allocate_new(networks, allocated, requested):
    l=len(networks)
    for i in reversed(range(l)):
        print(networks[i])
        print(networks[i].num_addresses)
        if (Addresses[requested]==networks[i].num_addresses): # get hosts, if requested number of hosts is same as available allocate else find next larger subnet
            print("allocating from original")
            allocated.append(str(networks[i]))
            data_new={"allocated": allocated}
            dump_to_json_file(data_new)
            networks.remove(networks[i])
            break
        elif(Addresses[requested] < networks[i].num_addresses):
            print("getting subnets")
            print(list(networks[i].subnets(new_prefix=Size[requested])))
            print("allocating from subnet")
            n=list(networks[i].subnets(new_prefix=Size[requested]))[0]
            allocated.append(str(n))
            data_new={"allocated": allocated}
            print('new json')
            dump_to_json_file(data_new)
            after_exclude=list(networks[i].address_exclude(n))
            networks.remove(networks[i])
            for addr in after_exclude:
                    networks.append(addr)
            break
    
    new_allocation = dict() 
    new_allocation['networks'] = networks
    new_allocation['allocated'] = allocated
    return new_allocation


def main():

    print('executing main')

    if len(sys.argv) < 2:
        print("Incorrect usage")
        sys.exit()

    requested=str(sys.argv[1])
    if requested not in Addresses:
        print('Invalid size')
        sys.exit()
    print('requested size - ' + requested)

    # TODO get network address from input
    networks=[IPv4Network(u'192.0.0.0/16')]

    networks_updated = []
    allocated_updated = []
    prev_allocation = dict()

    allocated = get_previous_allocation_list()

    if not allocated:
        print("none allocated, skip checking previous allocations")
        prev_allocation['networks'] = networks
        prev_allocation['allocated'] = allocated
    else:
        print('getting previous allocations')
        prev_allocation = get_same_or_next(networks, allocated)

    networks_updated = prev_allocation['networks']
    allocated_updated = prev_allocation['allocated']
    print('available - ')
    print(networks_updated)
    print('allocated - ')
    print(allocated_updated)
    
    new_allocation = allocate_new(networks_updated, allocated_updated, requested)
    network_new = new_allocation['networks']
    allocated_new = new_allocation['allocated']

    print("available network - ")
    print(network_new)
    print("allocated pool - ")
    print(allocated_new)


if __name__ == "__main__":
    main()


