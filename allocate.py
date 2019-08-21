import sys
import ipaddress
from ipaddress import *
import json

allocated=[]
with open('allocated.json') as json_file:
    data = json.load(json_file)
    allocated = data["allocated"]

Size = {'small': 30, 'medium': 29, 'large': 28, 'xlarge': 27}

# TODO: Save and get map from db 
Addresses = {'small': 4, 'medium': 8, 'large': 16, 'xlarge': 32} 

# TODO get network address from input
networks=[IPv4Network(u'192.0.2.0/24')]

requested=str(sys.argv[1])
print('requested size - ' + requested)


def dump_to_json_file(data_new):
    with open('allocated.json', 'w') as outfile:
                json.dump(data_new, outfile)


#sort network list
def sort_networks():
    n = len(networks)

    for i in range(n):
        for j in range(0, n-i-1):
            num_hosts_j = networks[j].num_addresses
            num_hosts_next = networks[j+1].num_addresses
            # Swap if the number of addresses found is greater than in next subnet
            if num_hosts_j < num_hosts_next :
                networks[j], networks[j+1] = networks[j+1], networks[j]

def get_same_or_next():
    for allocated_network in allocated:
        a=IPv4Network(allocated_network)
        for network in networks:
            n=IPv4Network(network)
            if (a==n):
                print("same")
                networks.remove(n)
                sort_networks()
                break
            elif (a.subnet_of(n)):
                print("subnet")
                networks.remove(n)
                after_exclude=list(n.address_exclude(a))
                for addr in after_exclude:
                    networks.append(addr)
                    sort_networks()
                break
                # update networks

if not allocated:
    print("none allocated, skip checking previous allocations")
else:
    get_same_or_next()
    print('available - ')
    print(networks)
    print('allocated - ')
    print(allocated)

l=len(networks)

def allocate_new():
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
            print(data_new)
            dump_to_json_file(data_new)
            print(n)
            after_exclude=list(networks[i].address_exclude(n))
            networks.remove(networks[i])
            for addr in after_exclude:
                    networks.append(addr)
            break

print('sorting networks after allocation')
sort_networks()
print(networks)


print("available network - ")
print(networks)
allocate_new()
print("available network - ")
print(networks)
print("allocated pool - ")
print(allocated)

