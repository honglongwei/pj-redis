#!/bin/bash
tar -zxf monitor.tar.gz

mkdir -p /usr/local/redis-monitor
\cp -rf monitor/* /usr/local/redis-monitor
\cp -rf redis7009.conf /etc/redis/
\cp -rf redis-monitor /etc/init.d/
chmod 777 /etc/init.d/redis-monitor

chkconfig --add redis-monitor
service redis-monitor start

