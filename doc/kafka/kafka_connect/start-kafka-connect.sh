#!/bin/bash

exec "connect-standalone.sh" \
        "/home/config/connect-standalone.properties" \
        "/home/config/source.properties" \
        "/home/config/sink.properties"