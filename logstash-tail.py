#!/usr/bin/env python

import argparse
import json
import logging
import re
import socket
import sys

from colorama import Fore, Style

def matched(filters, data, andd, colored):
    highlighted = {k: v for k, v in to_path(data)}
    found = 0
    for flt in filters:
        fk, kv = flt.split('=', 1)
        for path, val in highlighted.iteritems():
            if fk == path and re.search(kv, val):
                found += 1
                if colored:
                    highlighted[path] = re.sub(r'(%s)' % kv, Style.BRIGHT + Fore.GREEN + r'\1' + Fore.RESET + Style.RESET_ALL, val)
    if andd:
        if len(filters) == found:
            return highlighted
    else:
        if found > 0:
            return highlighted
        else:
            return None

def stringify(obj):
    if isinstance(obj, str):
        return obj
    else:
        return repr(obj)

def to_path(data, prefix=""):
    if isinstance(data, dict):
        for k, v in data.items():
            if prefix:
                real_prefix = ".".join((prefix, k))
            else:
                real_prefix = k

            for line in to_path(v, real_prefix):
                yield line
    elif isinstance(data, list):
        yield (prefix, ",".join([stringify(x) for x in data]))
    else:
        yield (prefix, str(data))


class LogstashClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.socket = self.connect()

    def connect(self):
        logging.warning("Connecting to %s:%d" % (self.host, self.port))
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))
            return sock
        except socket.error:
            return None


logging.basicConfig(format="%(message)s")

parser = argparse.ArgumentParser(description="Tail logstash tcp output")
parser.add_argument("-H", "--host", metavar="HOST", dest="hosts", default=[], action="append", help="Logstash host(s) (multiple accepted)")
parser.add_argument("-p", "--port", required=True, type=int, help="Logstash TCP output port")
parser.add_argument("--and", dest="andd", action="store_true", default=False, help="AND multiple filters")
parser.add_argument("--color", action="store_true", default=False, help="Color highlight filtered output [default: %(default)s]")
parser.add_argument("--filter", metavar="FILTER", dest="filters", action="append", help="Define some filters (multiple accepted; default is to `OR' them")
parser.add_argument("--format", dest="fmt", default="%(@timestamp)s %(@source_host)s: %(@message)s", help="Output format (see README for default)")
args = parser.parse_args()

if not args.hosts: args.hosts.append("localhost")
cxns = [LogstashClient(host, args.port) for host in args.hosts]

try:
    while True:
        for cxn in cxns:
            if cxn.socket:
                line = ""
                while not line.endswith("\n"):
                    try:
                        line += cxn.socket.recv(1)
                    except socket.error:
                        logging.warning("Lost connection to %s:%d, trying again." % (cxn.host, cxn.port))
                        cxns.remove(cxn)
                        cxns.append(LogstashClient(cxn.host, cxn.port))
                        break

                if line:
                    try:
                        parsed = json.loads(line)
                    except ValueError:
                        continue

                    if args.filters:
                        highlighted = matched(args.filters, parsed, args.andd, args.color)
                        if highlighted:
                            print args.fmt % highlighted
                    else:
                        print args.fmt % {k: v for k, v in to_path(parsed)}
            else:
                logging.warning("No socket for %s:%d, ignoring." % (cxn.host, cxn.debug))
                cxns.remove(cxn)
except KeyboardInterrupt:
    logging.warning("Disconnecting...")
    sys.exit(2)
