# logstash-tail

Tail logstash tcp outputs

```
usage: logstash-tail.py [-h] [-H HOSTS] -p PORT [--filter FILTERS] [--and]
                        [--format FMT]

Tail logstash tcp output

optional arguments:
  -h, --help            show this help message and exit
  -H HOSTS, --host HOSTS
                        Logstash host(s) (multiple accepted)
  -p PORT, --port PORT  Logstash TCP output port
  --filter FILTERS      Define some filters (multiple accepted; default is to
                        `OR' them
  --and                 AND multiple filters
  --format FMT          Output format (see README for default)
```

## An example

```
(scott@lalala:~)% logstash-tail.py -p 9090 --filter @fields.program=sensu-client
2012-12-19T20:43:16.661Z vagrant: {"timestamp":"2012-12-19T20:43:16.242832+0000","message":"config file applied changes","config_file":"/etc/sensu/conf.d/checks/check_root_df.json","changes":{"checks":{"check_root_df":[null,{"command":"/etc/sensu/plugins/check_graphite.py -U http://127.0.0.1 -t 'tl.org.housepub.int.vagrant.base.df.root.blocks.percent_used' --from=-5min -W 92.0 -C 95.0","interval":60,"standalone":true,"graph":"http://localhost/render?target=lineWidth(color(tl.org.housepub.int.vagrant.base.df.root.blocks.percent_used,'green'),2)&target=threshold(92,'warn','yellow')&target=threshold(95,'crit','red')&yMin=0&yMax=100&width=1000&height=500"}]}},"level":"warn"}
2012-12-19T20:43:16.676Z vagrant: {"timestamp":"2012-12-19T20:43:16.243040+0000","message":"config file applied changes","config_file":"/etc/sensu/conf.d/checks/check_ssh.json","changes":{"checks":{"check_ssh":[null,{"command":"/usr/lib/nagios/plugins/check_ssh vagrant.int.housepub.org","interval":60,"standalone":true}]}},"level":"warn"}
2012-12-19T20:43:16.677Z vagrant: {"timestamp":"2012-12-19T20:43:16.243196+0000","message":"config file applied changes","config_file":"/etc/sensu/conf.d/checks/check_memory.json","changes":{"checks":{"check_memory":[null,{"command":"/etc/sensu/plugins/check_graphite.py -U http://localhost -t 'asPercent(tl.org.housepub.int.vagrant.base.meminfo.memused,tl.org.housepub.int.vagrant.base.meminfo.memtotal)' --from=-5min -W 90.0 -C 95.0","interval":60,"standalone":true,"graph":"http://localhost/render?target=lineWidth(color(asPercent(tl.org.housepub.int.vagrant.base.meminfo.memused,tl.org.housepub.int.vagrant.base.meminfo.memtotal),'green'),2)&target=threshold(90,'warn','yellow')&target=threshold(95,'crit','red')&yMin=0&yMax=100&width=1000&height=500"}]}},"level":"warn"}
2012-12-19T20:43:16.681Z vagrant: {"timestamp":"2012-12-19T20:43:16.243330+0000","message":"config file applied changes","config_file":"/etc/sensu/conf.d/checks/check_chef_success.json","changes":{"checks":{"check_chef_success":[null,{"command":"/etc/sensu/plugins/check_graphite.py -U http://localhost -t 'diffSeries(chef._default.vagrant.success,chef._default.vagrant.fail)' --from=-24h -W 0 -C 0 --under --count 36","handlers":["nopage-noemail"],"interval":60,"standalone":true,"graph":"http://localhost/render?target=drawAsInfinite(diffSeries(chef._default.vagrant.success,chef._default.vagrant.fail))&width=1000&height=500"}]}},"level":"warn"}
2012-12-19T20:43:16.683Z vagrant: {"timestamp":"2012-12-19T20:43:16.243486+0000","message":"config file applied changes","config_file":"/etc/sensu/conf.d/checks/check_loadavg.json","changes":{"checks":{"check_loadavg":[null,{"command":"/etc/sensu/plugins/check_graphite.py -U http://localhost -t tl.org.housepub.int.vagrant.base.loadavg.midterm --from=-5min -W 1.5 -C 2.0","interval":60,"standalone":true,"graph":"http://localhost/render?target=lineWidth(color(tl.org.housepub.int.vagrant.base.loadavg.midterm,'green'),2)&target=threshold(1.5,'warn','yellow')&target=threshold(2,'crit','red')&width=1000&height=500","grouped":3}]}},"level":"warn"}
2012-12-19T20:43:16.688Z vagrant: {"timestamp":"2012-12-19T20:43:16.243645+0000","message":"config file applied changes","config_file":"/etc/sensu/conf.d/checks/check_ntpd_process.json","changes":{"checks":{"check_ntpd_process":[null,{"command":"/usr/lib/nagios/plugins/check_procs -w 1:2 -c 1:2 -C ntpd","interval":60,"standalone":true}]}},"level":"warn"}
2012-12-19T20:43:16.692Z vagrant: {"timestamp":"2012-12-19T20:43:16.243781+0000","message":"config file applied changes","config_file":"/etc/sensu/conf.d/client.json","changes":{"client":[null,{"name":"vagrant.int.housepub.org","address":"10.0.2.15","subscriptions":["default"],"roles":[]}]},"level":"warn"}
2012-12-19T20:43:16.694Z vagrant: {"timestamp":"2012-12-19T20:43:16.276462+0000","message":"cannot connect to rabbitmq","settings":{"host":"localhost","port":5672,"vhost":"/sensu","user":"sensu","password":"password"},"level":"fatal"}
2012-12-19T20:43:16.695Z vagrant: {"timestamp":"2012-12-19T20:43:16.276702+0000","message":"SENSU NOT RUNNING!","level":"fatal"}
```

If you want to tail several logstash instances, simply add more `-H/--host` arguments. They must all be listening on the same port, though.

You can also specify multiple filters. By default they will be OR'ed, but if you specify `--and`, a message will only be printed if all filters match.

## Setup

In your logstash server, add a tcp output

```
output {
  tcp {
    host => '0.0.0.0'
    port => '9090'
    mode => 'server'
  }
}
```

## Output formatting

You can specify the output format using --format. Internally, this just uses Python's string formatting. Nested fields and attributes of the Logstash JSON are converted to dot-delimited strings (as seen in the example above with @fields.program).

The default is `"%(@timestamp)s %(@source_host)s: %(@message)s"`
