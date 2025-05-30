#!/usr/bin/env python3
"""
Network Analyzer Module
Responsible for capturing and analyzing network packets using Scapy
"""

import time
import threading
import ipaddress
from collections import defaultdict, deque
import numpy as np
import random

# Mock classes for simulation when scapy is not available
class MockPacket:
    def __init__(self, src_ip, dst_ip, protocol="TCP", dport=80):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.protocol = protocol
        self.dport = dport
        self.layers = []
        
        # Add IP layer
        self.layers.append("IP")
        if protocol == "TCP":
            self.layers.append("TCP")
        elif protocol == "UDP":
            self.layers.append("UDP")
    
    def __getitem__(self, layer):
        if layer == IP:
            return MockIP(self.src_ip, self.dst_ip)
        elif layer == TCP:
            return MockTCP(self.dport)
        elif layer == UDP:
            return MockUDP(self.dport)
        return None
    
    def __contains__(self, layer):
        return layer.__name__ in self.layers
    
    def __len__(self):
        return random.randint(64, 1500)  # Random packet size

class MockIP:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

class MockTCP:
    def __init__(self, dport):
        self.dport = dport

class MockUDP:
    def __init__(self, dport):
        self.dport = dport

# Mock layer classes for simulation
class IP:
    __name__ = "IP"

class TCP:
    __name__ = "TCP"

class UDP:
    __name__ = "UDP"

class DeviceData:
    """Class to store data for a specific network device"""
    def __init__(self, ip, name=None):
        self.ip = ip
        self.name = name if name else f"Device ({ip})"
        # Store traffic history (timestamp, traffic_value, is_authorized)
        self.traffic_history = deque(maxlen=100)
        self.auth_history = deque(maxlen=100)
        # Stats
        self.total_packets = 0
        self.authorized_packets = 0
        self.unauthorized_packets = 0
        # Connection info
        self.connections = []
        # Last destination
        self.last_dst_ip = None
        self.last_protocol = None
        # Initialize with zero traffic
        current_time = time.time()
        for i in range(100):
            self.traffic_history.append((current_time - (100-i)*0.5, 0, True))
            self.auth_history.append(True)
    
    def add_traffic_point(self, value, is_authorized, dst_ip=None, protocol=None):
        """Add a new traffic data point"""
        self.traffic_history.append((time.time(), value, is_authorized))
        self.auth_history.append(is_authorized)
        self.total_packets += 1
        
        if is_authorized:
            self.authorized_packets += 1
        else:
            self.unauthorized_packets += 1
            
        if dst_ip:
            self.last_dst_ip = dst_ip
        
        if protocol:
            self.last_protocol = protocol
    
    def get_traffic_data(self):
        """Get traffic data for plotting"""
        times = [t for t, _, _ in self.traffic_history]
        values = [v for _, v, _ in self.traffic_history]
        auth = [a for _, _, a in self.traffic_history]
        return times, values, auth
    
    def get_auth_percentage(self):
        """Get the percentage of authorized traffic"""
        if self.total_packets == 0:
            return 100.0
        return (self.authorized_packets / self.total_packets) * 100
    
    def get_unauth_percentage(self):
        """Get the percentage of unauthorized traffic"""
        if self.total_packets == 0:
            return 0.0
        return (self.unauthorized_packets / self.total_packets) * 100


class NetworkAnalyzer:
    """Class to analyze network traffic using Scapy"""
    def __init__(self):
        # Flag to control packet capture
        self.running = False
        self.lock = threading.Lock()
        
        # Dictionary to store device data by IP
        self.devices = {}
        
        # Initialize with 7 example devices
        self._initialize_devices()
        
        # ACL rules (simplified for demonstration)
        self.acl_rules = self._initialize_acl_rules()
        
        # System stats
        self.memory_usage = [0] * 24  # 24 hour tracking
        self.system_load = 0
        self.cpu_usage = 33.7  # Starting value shown in image
        
        # Overall authorization stats
        self.total_authorized = 0
        self.total_unauthorized = 0
        
        # Start time
        self.start_time = time.time()
    
    def _initialize_devices(self):
        """Initialize the device list with 7 devices"""
        device_ips = [
            "192.168.1.100",
            "192.168.1.101",
            "192.168.1.102",
            "192.168.1.103",
            "192.168.1.104",
            "192.168.1.105",
            "192.168.1.106"
        ]
        
        device_names = [
            "Server",
            "Workstation 1",
            "Workstation 2",
            "Dev Machine",
            "Admin Laptop",
            "IoT Gateway",
            "Testing VM"
        ]
        
        for i, ip in enumerate(device_ips):
            self.devices[ip] = DeviceData(ip, device_names[i])
    
    def _initialize_acl_rules(self):
        """Initialize Access Control List rules for network traffic validation"""
        acl_rules = []
        
        # Format: (src_ip, dst_ip, protocol, port range)
        # Allow HTTP/HTTPS traffic from all devices to the server
        acl_rules.append(("192.168.1.101", "192.168.1.100", "TCP", (80, 443)))
        acl_rules.append(("192.168.1.102", "192.168.1.100", "TCP", (80, 443)))
        acl_rules.append(("192.168.1.103", "192.168.1.100", "TCP", (80, 443)))
        acl_rules.append(("192.168.1.104", "192.168.1.100", "TCP", (80, 443)))
        acl_rules.append(("192.168.1.105", "192.168.1.100", "TCP", (80, 443)))
        acl_rules.append(("192.168.1.106", "192.168.1.100", "TCP", (80, 443)))
        
        # Allow SSH only from Admin to all devices
        acl_rules.append(("192.168.1.104", "192.168.1.100", "TCP", (22, 22)))
        acl_rules.append(("192.168.1.104", "192.168.1.101", "TCP", (22, 22)))
        acl_rules.append(("192.168.1.104", "192.168.1.102", "TCP", (22, 22)))
        acl_rules.append(("192.168.1.104", "192.168.1.103", "TCP", (22, 22)))
        acl_rules.append(("192.168.1.104", "192.168.1.105", "TCP", (22, 22)))
        acl_rules.append(("192.168.1.104", "192.168.1.106", "TCP", (22, 22)))
        
        # Allow FTP from Dev Machine to Server
        acl_rules.append(("192.168.1.103", "192.168.1.100", "TCP", (20, 21)))
        
        # Allow DNS queries to the server
        acl_rules.append(("192.168.1.101", "192.168.1.100", "UDP", (53, 53)))
        acl_rules.append(("192.168.1.102", "192.168.1.100", "UDP", (53, 53)))
        acl_rules.append(("192.168.1.103", "192.168.1.100", "UDP", (53, 53)))
        acl_rules.append(("192.168.1.104", "192.168.1.100", "UDP", (53, 53)))
        acl_rules.append(("192.168.1.105", "192.168.1.100", "UDP", (53, 53)))
        acl_rules.append(("192.168.1.106", "192.168.1.100", "UDP", (53, 53)))
        
        return acl_rules
    
    def is_authorized(self, src_ip, dst_ip, protocol, port):
        """Check if the traffic is authorized based on ACL rules"""
        for rule_src, rule_dst, rule_proto, port_range in self.acl_rules:
            # Check if this rule applies
            if (src_ip == rule_src and 
                dst_ip == rule_dst and 
                protocol == rule_proto and
                port_range[0] <= port <= port_range[1]):
                return True
        return False
    
    def process_packet(self, packet):
        """Process a captured packet and update device statistics"""
        if IP not in packet:
            return
        
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        # Check if the source IP is in our monitored devices
        if src_ip not in self.devices:
            return
        
        # Determine protocol and port
        protocol = None
        dport = 0
        
        if TCP in packet:
            protocol = "TCP"
            dport = packet[TCP].dport
        elif UDP in packet:
            protocol = "UDP"
            dport = packet[UDP].dport
        else:
            protocol = "OTHER"
        
        # Check if traffic is authorized
        is_authorized = self.is_authorized(src_ip, dst_ip, protocol, dport)
        
        # Update device traffic
        with self.lock:
            # Packet size as traffic value (normalized)
            packet_size = len(packet) / 100.0
            
            # Add traffic with higher value if unauthorized
            traffic_value = packet_size
            if not is_authorized:
                traffic_value *= 3  # Make unauthorized traffic more visible
            
            self.devices[src_ip].add_traffic_point(
                traffic_value, 
                is_authorized,
                dst_ip,
                protocol
            )
            
            # Update global stats
            if is_authorized:
                self.total_authorized += 1
            else:
                self.total_unauthorized += 1
            
            # Simulate system load changes
            self.system_load = min(100, max(0, self.system_load + (np.random.random() - 0.5) * 5))
    
    def packet_callback(self, packet):
        """Callback function for packet processing"""
        if self.running:
            self.process_packet(packet)
    
    def start_capture(self, serial_port='/dev/ttyUSB0', baud_rate=9600):
        """Start capturing serial data"""
        self.running = True
        
        try:
            import serial
            ser = serial.Serial(serial_port, baud_rate)
            
            while self.running:
                if ser.in_waiting:
                    data = ser.readline().decode('utf-8')
                    self.process_serial_data(data)
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Error in serial capture: {e}")
            self.running = False
        except Exception as e:
            print(f"Error in network monitoring: {e}")
            self.running = False
    
    def process_serial_data(self, serial_data):
        """Process incoming serial data and update network stats"""
        try:
            # Update system stats
            hour_idx = int((time.time() % 86400) / 3600)
            
            # Parse the serial data and update device stats
            with self.lock:
                # Example format: "device_ip,dest_ip,protocol,port,bytes"
                data = serial_data.strip().split(',')
                if len(data) >= 5:
                    src_ip, dst_ip, protocol, port, bytes = data[:5]
                    port = int(port)
                    bytes = float(bytes)
                    
                    if src_ip in self.devices:
                        # Check if traffic is authorized
                        is_auth = self.is_authorized(src_ip, dst_ip, protocol, port)
                        
                        # Add traffic point with real data
                        self.devices[src_ip].add_traffic_point(bytes, is_auth, dst_ip, protocol)
                        
                        # Update global stats
                        if is_auth:
                            self.total_authorized += 1
                        else:
                            self.total_unauthorized += 1
                            
        except Exception as e:
            print(f"Error processing serial data: {e}")
    
    def stop_capture(self):
        """Stop the packet capture"""
        self.running = False
    
    def get_auth_percentage(self):
        """Get the overall percentage of authorized traffic"""
        total = self.total_authorized + self.total_unauthorized
        if total == 0:
            return 100.0
        return (self.total_authorized / total) * 100
    
    def get_unauth_percentage(self):
        """Get the overall percentage of unauthorized traffic"""
        total = self.total_authorized + self.total_unauthorized
        if total == 0:
            return 0.0
        return (self.total_unauthorized / total) * 100
    
    def get_all_devices(self):
        """Get all monitored devices"""
        with self.lock:
            return dict(self.devices)
    
    def get_memory_usage(self):
        """Get memory usage data"""
        with self.lock:
            return list(self.memory_usage)
    
    def get_system_load(self):
        """Get current system load"""
        with self.lock:
            return self.system_load
    
    def get_cpu_usage(self):
        """Get simulated CPU usage"""
        with self.lock:
            # Slightly adjust the CPU usage for animation effect
            self.cpu_usage = min(100, max(0, self.cpu_usage + (np.random.random() - 0.5) * 2))
            return self.cpu_usage
