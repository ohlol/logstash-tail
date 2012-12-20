#!/usr/bin/env python

import argparse
import json
import re
import socket
import sys

def formatted(fmt, data):
    return fmt % {k: v for k, v in to_path(data)}

def matched(flt, data):
    fk, kv = flt.split('=', 1)
    for (path, val) in to_path(data):
        if fk == path:
            if re.match(kv, val): return True
    return False

def to_path(data, prefix=""):
    if isinstance(data, dict):
        for k, v in data.items():
            if prefix:
                real_prefix = ".".join((prefix, k))
            else:
                real_prefix = k

            for line in to_path(v, real_prefix):
                yield line
    elif isinstance(data, list) and data:
        yield (prefix, ",".join(data))
    else:
        yield (prefix, str(data))


class LogstashClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.socket = self.connect()

    def connect(self):
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))
            return sock
        except socket.error:
            return None


parser = argparse.ArgumentParser(description="Tail logstash tcp output")
parser.add_argument("-H", "--host", dest="hosts", default=[], action="append", help="Logstash host(s) (multiple accepted)")
parser.add_argument("-p", "--port", required=True, type=int, help="Logstash TCP output port")
parser.add_argument("--filter", action="append", help="Define some filters (multiple accepted; OR-ed)")
parser.add_argument("--format", dest="fmt", default="%(@timestamp)s %(@source_host)s: %(@message)s", help="Output format (see README for default)")
args = parser.parse_args()

if not args.hosts: args.hosts.append('localhost')
cxns = [LogstashClient(host, args.port) for host in args.hosts]

try:
    while True:
        for cxn in cxns:
            if cxn.socket:
                line = ""
                while not line.endswith('\n'):
                    try:
                        line += cxn.socket.recv(1)
                    except socket.error:
                        cxns.remove(cxn)
                        cxns.append(LogstashClient(cxn.host, cxn.port))
                        break

                if line:
                    try:
                        parsed = json.loads(line)
                    except ValueError:
                        continue

                    if args.filter:
                        for filter in args.filter:
                            if matched(filter, parsed):
                                print formatted(args.fmt, parsed)
                    else:
                        print formatted(args.fmt, parsed)
            else:
                cxns.remove(cxn)
except KeyboardInterrupt:
    print "\nDisconnecting..."
    sys.exit(2)
