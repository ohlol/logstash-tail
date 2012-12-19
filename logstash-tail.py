#!/usr/bin/env python

import argparse
import json
import re
import socket
import sys


def to_path(metrics, prefix=""):
    if isinstance(metrics, dict):
        for k, v in metrics.items():
            if prefix:
                real_prefix = ".".join((prefix, k))
            else:
                real_prefix = k

            for line in to_path(v, real_prefix):
                yield line
    elif isinstance(metrics, list):
        yield (prefix, ",".join(metrics))
    else:
        yield (prefix, str(metrics))

def matched(filter, data):
    fk, kv = filter.split('=', 1)
    for (path, val) in to_path(data):
        if fk == path:
            if re.match(kv, val): return True
    return False

def formatted(fmt, data):
    return fmt % {k: v for k, v in to_path(data)}

parser = argparse.ArgumentParser(description="Tail logstash tcp output")
parser.add_argument("-H", "--host", default="localhost", help="Logstash host [default: %(default)s]")
parser.add_argument("-p", "--port", type=int, help="Logstash TCP output port")
parser.add_argument("--filter", action="append", help="Define some filters (multiple accepted; OR-ed)")
parser.add_argument("--format", dest="fmt", default="%(@timestamp)s %(@source_host)s: %(@message)s", help="Output format (see README for default)")
args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((args.host, args.port))
except socket.error:
    print "ERROR: could not connect to logstash on %s:%d" % (args.host, args.port)
    sys.exit(2)

while True:
    try:
        line = ""
        while not line.endswith('\n'):
            line += s.recv(1)
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
    except KeyboardInterrupt:
        print "Disconnecting..."
        sys.exit(0)
