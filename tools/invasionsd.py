#!/usr/bin/env python2
import argparse
import base64
import json
import os
import random
import time

from Crypto.Cipher import AES
from jsonrpclib import Server


parser = argparse.ArgumentParser()
parser.add_argument('--rpc-endpoint', default='http://localhost:8080/',
                    help='The endpoint belonging to the game RPC server.')
parser.add_argument('--rpc-secret', default='7368686868686868',
                    help='The secret key used to interact with the game RPC server.')
parser.add_argument('--update-interval', type=int, default=60,
                    help='The amount of time to wait (in seconds) before each attempt to spawn an'
                         ' invasion.')
parser.add_argument('--invasion-probability', type=float, default=0.05,
                    help='The probability that an invasion will spawn in any given district'
                         ' (unless the invasion maximum is currently met).')
parser.add_argument('--invasion-max', type=int, default=3,
                    help='The maximum amount of shards that may have an invasion spawned at any'
                         ' given time. If this is 0, there will be no maximum.')
parser.add_argument('--shard', action='append',
                    help='Adds this shard to the list of shards that are eligible for automatic'
                         ' invasion spawning.')
args = parser.parse_args()

client = Server(args.rpc_endpoint)


def generate_token(access_level):
    data = json.dumps({'timestamp': int(time.mktime(time.gmtime())),
                       'accesslevel': access_level})
    data += '\x00' * (16 - (len(data) % AES.block_size))  # Padding
    iv = os.urandom(AES.block_size)
    cipher = AES.new(args.rpc_secret, mode=AES.MODE_CBC, IV=iv)
    return base64.b64encode(iv + cipher.encrypt(data))


while True:
    time.sleep(args.update_interval)

    try:
        shards = client.listShards(generate_token(700))

        if args.invasion_max > 0:
            invasion_count = len(filter(lambda v: v['invasion'], shards.values()))
            if invasion_count >= args.invasion_max:
                continue

        for key, value in shards.items():
            if (str(key) not in args.shard) or value['invasion']:
                continue
            if random.random() < args.invasion_probability:
                suit_dept_index = int(random.random() * 4)
                suit_type_index = int(random.random() * 8)
                client.startInvasion(generate_token(700), int(key), suit_dept_index,
                                     suit_type_index, 0, 0)
                print 'Spawning an invasion in shard %s: %d, %d' % (
                    key, suit_dept_index, suit_type_index)
    except Exception, e:
        print e
