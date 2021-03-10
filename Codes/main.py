# -*- coding = utf-8 -*-
# @Time : 2021-01-03 18:30
# @Author : Danny
# @File : u_main.py
# @Software: PyCharm
import argparse
import json
import time
from socket import *

local_dict = {}
org_local_dict = {}
node_name = ''
neighbour_addr = []
output_dict = {}


def _argparse():
    print('parsing args...')
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", "-node_name", default='', help="node name")
    arg = parser.parse_args()
    return arg


def listen_to_news_from_neighbours():
    global node_name
    global local_dict
    global org_local_dict
    global neighbour_addr
    global output_dict
    start_time = time.time()
    print('start listening distance vector from peer nodes...')
    while True:
        try:
            peer_info_b, peer_addr = localInfo_socket.recvfrom(10240)
            peer_node = peer_info_b[:1].decode()
            peer_dv = peer_info_b[1:].decode()
            print(node_name + ' recieve information from neighbour: ' + peer_node + ', peer_addr: ' + str(peer_addr))
            print('peer distance vector is: ' + peer_dv)
            peer_dict = eval(peer_dv)

            # If there are keys in the neighbour that local dict does not have
            # add them, and update the distance to infinity
            for neighbour_key in peer_dict:
                if not neighbour_key in local_dict.keys() and neighbour_key != node_name:
                    local_dict[neighbour_key] = float('inf')

            # Recompute distance vector, if the distance from peer to location is smaller, refresh the distance vector
            for key in dict(local_dict).keys():
                next_hop = key
                distance = local_dict[key]
                distance1 = local_dict[key]

                # If currently checked key is the same as peer_node name, then update the distance to 0
                if key == peer_node:
                    peer_dict[key] = 0
                # If the currently checked key is not in the dictionary of peer's, update the value to infinite
                if not key in peer_dict.keys():
                    peer_dict[key] = float('inf')

                # If there find nearer distance through the peer_node, update the next_hop to peer_node
                if local_dict[key] > peer_dict[node_name] + peer_dict[key] and peer_node in org_local_dict.keys():
                    local_dict[key] = peer_dict[node_name] + peer_dict[key]
                    next_hop = peer_node
                    distance1 = peer_dict[node_name] + peer_dict[key]
                    update_news_to_neighbours(neighbour_addr, node_name, local_dict)

                # If the distance and next_hop both changed, update the output distance vector
                if distance != distance1:
                    output_dict.update({key: {"distance": local_dict[key], "next_hop": next_hop}})
                end_time = time.time()
                print(node_name + ": " + str(output_dict))

                # If there are no more updates in the local dict and the result converges, write the final jason file
                if end_time - start_time > 20:
                    with open(node_name + '_output.json', 'w+') as output:
                        output.write(json.dumps(output_dict))
        except:
            time.sleep(1)
            print('no peers are online')
            end_time = time.time()
            #
            if end_time - start_time > 20:
                with open(node_name + '_output.json', 'w+') as output:
                    output.write(json.dumps(output_dict))
                print("Time out, program exits.")
                break


def update_news_to_neighbours(addresses, this_node, dv):
    print('Start sending local information to neighbors...')
    for addr in addresses:
        localInfo_socket.sendto(this_node.encode() + str(dv).encode(), addr)


def main():
    global local_dict
    global org_local_dict
    global node_name
    global neighbour_addr
    global output_dict
    node_name = _argparse().node

    # get local distance vector information
    with open(node_name + '_distance.json', 'r') as f:
        local_dict = json.load(f)
    print('local_dict is: ' + str(local_dict))

    with open(node_name + '_distance.json', 'r') as f:
        org_local_dict = json.load(f)

    # get ip address information
    with open(node_name + '_ip.json', 'r') as f:
        ip_dict = json.load(f)
    print('ips of neighbour nodes are: ' + str(ip_dict))

    localInfo_socket.bind(tuple(ip_dict[node_name]))  # bind socket to local port

    # get neighbour addresses
    for neighbour in ip_dict.keys():
        address = tuple(ip_dict[neighbour])
        if address != tuple(ip_dict[node_name]):
            neighbour_addr.append(address)
    print('neighbour addresses are: ' + str(neighbour_addr))

    # Initialize the output dict
    for key in local_dict:
        output_dict.update({key: {"distance": local_dict[key], "next_hop": key}})
    update_news_to_neighbours(neighbour_addr, node_name, local_dict)
    listen_to_news_from_neighbours()


if __name__ == '__main__':
    localInfo_socket = socket(AF_INET, SOCK_DGRAM)
    localInfo_socket.settimeout(1)
    main()
