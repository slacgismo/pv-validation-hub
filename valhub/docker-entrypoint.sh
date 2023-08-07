#!/bin/sh

# Simple entrypoint script to run in aws ecs

/usr/bin/supervisord -c "/root/valhub/supervisord.conf"
