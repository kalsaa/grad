# Network Monitoring Dashboard

A Python-based network monitoring dashboard that visualizes traffic from 7 devices, displays authorization status, and provides real-time network insights.

## Overview

This dashboard is designed for an FPGA-based IDS (Intrusion Detection System) hardware project that filters authorized and unauthorized network access based on IP source/destination and protocol validation.

## Features

- Real-time visualization of network traffic from 7 devices
- Traffic line charts showing authorized vs. unauthorized access
- System resource monitoring (CPU, Memory, System Load)
- Device status indicators
- Network load overview

## Components

- **Main Traffic Chart**: Shows network traffic for each device with color-coded lines. Unauthorized access appears as higher spikes.
- **System Load Gauge**: Shows current system load in real-time.
- **CPU Usage Gauge**: Displays current CPU utilization.
- **Memory Usage Chart**: Shows memory utilization by hour.
- **Network Load Chart**: Provides an alternative view of overall network traffic.
- **Status Bar**: Shows device statuses and overall authorization percentages.

## Running the Dashboard

```
python network_dashboard.py
```

## Requirements

- Python 3.8+
- Required Python packages:
  - numpy
  - matplotlib
  - tkinter (usually included with Python)

## Integration with FPGA Hardware

This dashboard is designed to integrate with an FPGA-based hardware IDS system. In production, the dashboard will receive real network traffic data from the FPGA, which will perform the actual packet filtering based on ACL rules.

For demonstration purposes, the dashboard currently simulates network traffic data.

## Future Improvements

- Integration with real FPGA hardware
- More detailed packet analysis
- Custom alert configuration
- Historical data analysis
