#!/bin/bash
# Automate daily sensor aggregation and OpenNote logging
python utils/aggregate_daily_sensor_data.py
python utils/opennote_daily_log.py
