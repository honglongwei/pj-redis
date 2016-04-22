#!/bin/bash
rm -rf monitor.tar.gz
tar -zcf monitor.tar.gz monitor/
rm -rf monitor/
./redis-monitor.sh
