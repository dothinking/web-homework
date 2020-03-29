#!/bin/bash
connect_cfg="/home/config/connect-standalone.properties"
source_cfg="/home/config/source.properties"
sink_cfg="/home/config/sink.properties"

if [ ! -e "${connect_cfg}" ]; then
    echo "Missing config file for standalone connection: ${connect_cfg}"
    exit 1
fi

if [ ! -e "${source_cfg}" ]; then
    echo "Missing config file for source connector: ${source_cfg}"
    exit 1
fi

if [ ! -e "${sink_cfg}" ]; then
    echo "Missing config file for sink connector: ${sink_cfg}"
    exit 1
fi

exec "connect-standalone.sh" "${connect_cfg}" "${source_cfg}" "${sink_cfg}"