
import ipaddress
from ipaddress import *
import json
import boto3


Size = {'small': 30, 'medium': 29, 'large': 28}

# TODO: Save and get map from db
Addresses = {'small': 4, 'medium': 8, 'large': 16}

dynamodb = boto3.resource('dynamodb')

def get_previous_allocation_list():
    allocated = []
    table = dynamodb.Table('account_allocations')
    response = table.scan()
    items = response['Items']
    for item in items:
        allocated.append(item['allocated_address'])
    return allocated

def update_allocated(username, allocated_address, allocated_size):
    table = dynamodb.Table('account_allocations')
    table.put_item(
        Item={
            'username': username,
            'allocated_size': allocated_size,
            'allocated_address': allocated_address
        })

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
            update_allocated('some_user', str(networks[i]), requested)
            networks.remove(networks[i])
            break
        elif(Addresses[requested] < networks[i].num_addresses):
            print("allocating from subnet")
            n=list(networks[i].subnets(new_prefix=Size[requested]))[0]
            allocated.append(str(n))
            update_allocated('some_user', str(n), requested)
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



def lambda_handler(event, context):

    networks = [IPv4Network('192.0.0.0/24')]

    requested='small'
    if requested not in Addresses:
        print('Invalid size')
        sys.exit()
    print('requested size - ' + requested)

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
