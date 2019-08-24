import sys
import ipaddress
from ipaddress import *
import json


Size = {'small': 30, 'medium': 29, 'large': 28}

# TODO: Save and get map from db 
Addresses = {'small': 4, 'medium': 8, 'large': 16} 

def get_previous_allocation_list():
    allocated = []
    with open('allocated.json') as json_file:
        data = json.load(json_file)
        allocated = data["allocated"]
    return allocated

def dump_to_json_file(data_new):
    with open('allocated.json', 'w') as outfile:
                json.dump(data_new, outfile)


# calculate updated from previous allocations
def get_same_or_next(networks, allocated):
    for allocated_network in allocated:
        a=IPv4Network(allocated_network)
        for network in networks:
            n=IPv4Network(network)
            if (a==n):
                print("same")
                networks.remove(n)
                networks = sorted(networks)
                break
            elif (a.subnet_of(n)):
                print("subnet")
                networks.remove(n)
                after_exclude=list(n.address_exclude(a))
                for addr in after_exclude:
                    networks.append(addr)
                networks = sorted(networks)
                break
                
    prev_allocation = dict() 
    prev_allocation['networks'] = networks
    prev_allocation['allocated'] = allocated
    return prev_allocation

def allocate_new(networks, allocated, requested):
    len_networks = len(networks)
    len_allocated = len(allocated)
    for i in range(len_networks):
        print('checking availability in ' + str(i))
        print(networks[i])
        print('available addresses')
        print(networks[i].num_addresses)
        if (Addresses[requested]==networks[i].num_addresses): # get hosts, if requested number of hosts is same as available allocate else find next larger subnet
            print("allocating from original")
            allocated.append(str(networks[i]))
            data_new={"allocated": allocated}
            dump_to_json_file(data_new)
            networks.remove(networks[i])
            break
        elif(Addresses[requested] < networks[i].num_addresses):
            print("allocating from subnet")
            n=list(networks[i].subnets(new_prefix=Size[requested]))[0]
            allocated.append(str(n))
            data_new={"allocated": allocated}
            dump_to_json_file(data_new)
            after_exclude=list(networks[i].address_exclude(n))
            networks.remove(networks[i])
            for addr in after_exclude:
                networks.append(addr)
            break
    if(len(allocated) == len_allocated):
                print('not allocated, try another size. Available - ' + str(networks[i].num_addresses))
                sys.exit()
    
    new_allocation = dict() 
    new_allocation['networks'] = networks
    new_allocation['allocated'] = allocated
    return new_allocation


def main():

    if len(sys.argv) < 2:
        print("Incorrect usage")
        sys.exit()

    requested=str(sys.argv[1])
    if requested not in Addresses:
        print('Invalid size')
        sys.exit()
    print('requested size - ' + requested)

    # TODO get network address from input
    networks=[IPv4Network(u'192.0.0.0/24')]

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

    if not networks_updated:
        print('none available')
    else:
        new_allocation = allocate_new(networks_updated, allocated_updated, requested)
        network_new = new_allocation['networks']
        allocated_new = new_allocation['allocated']
        print("available network - ")
        print(network_new)
        print("allocated pool - ")
        print(allocated_new)


if __name__ == "__main__":
    main()


