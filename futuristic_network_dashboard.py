#!/usr/bin/env python3
"""
Futuristic Network Monitoring Dashboard
A single-file application that monitors network traffic with a modern, futuristic UI
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
import random
import math
from collections import defaultdict, deque
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, FancyArrowPatch
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LinearSegmentedColormap, to_rgba
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors

# Use TkAgg backend for matplotlib
matplotlib.use("TkAgg")

# Create custom colormaps for a futuristic look
cmap_green = LinearSegmentedColormap.from_list("CustomGreen", ["#052e1c", "#0abf53", "#7fffb7"])
cmap_orange = LinearSegmentedColormap.from_list("CustomOrange", ["#4a1c00", "#ff9800", "#ffd180"])
cmap_blue = LinearSegmentedColormap.from_list("CustomBlue", ["#001a33", "#0078d7", "#66ccff"])

# Mock classes for simulation
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
    """Class to analyze network traffic"""
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
    
    def simulate_traffic(self):
        """Simulate network traffic for demonstration purposes"""
        while self.running:
            # Update system stats
            hour_idx = int((time.time() % 86400) / 3600)
            
            # Simulate random traffic for each device
            with self.lock:
                for ip, device in self.devices.items():
                    # Simulate a packet
                    if np.random.random() < 0.7:  # 70% chance of traffic
                        # Determine if this will be authorized or unauthorized (90/10 split)
                        is_auth = np.random.random() < 0.9
                        
                        # Random destination from our device list
                        dst_candidates = [d for d in self.devices.keys() if d != ip]
                        dst_ip = np.random.choice(dst_candidates)
                        
                        # Random protocol
                        protocol = np.random.choice(["TCP", "UDP"])
                        
                        # Traffic value (higher for unauthorized)
                        value = np.random.random() * 5
                        if not is_auth:
                            value *= 3  # Make unauthorized traffic more visible
                        
                        device.add_traffic_point(value, is_auth, dst_ip, protocol)
                        
                        # Update global stats
                        if is_auth:
                            self.total_authorized += 1
                        else:
                            self.total_unauthorized += 1
            
            # Sleep for a short time
            time.sleep(0.2)
    
    def start_capture(self):
        """Start capturing network packets"""
        self.running = True
        
        try:
            # For demo purposes, we'll simulate traffic
            threading.Thread(target=self.simulate_traffic, daemon=True).start()
            
            # We're not using real packet capture in this demo
            # Instead, we'll keep the main thread alive
            while self.running:
                time.sleep(0.5)
        except Exception as e:
            print(f"Error in network monitoring: {e}")
            self.running = False
    
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
    
    def get_system_load(self):
        """Get current system load"""
        with self.lock:
            return self.system_load


class FuturisticLineChart:
    """Enhanced line chart with futuristic look for visualizing network traffic over time"""
    def __init__(self, parent, title, labels, colors, bg_color='#080f1c', grid_color='#143062', 
                 width=600, height=300, line_width=3.0, font_color='#e0f2ff'):
        self.parent = parent
        self.title = title
        self.labels = labels
        self.colors = colors
        self.bg_color = bg_color
        self.grid_color = grid_color
        self.width = width
        self.height = height
        self.line_width = line_width
        self.font_color = font_color
        
        # Neon color dictionary - these will create the glowing effect
        self.neon_colors = {
            '#00d084': '#7fffd4', # Green to lighter teal
            '#00c2ff': '#80e5ff', # Cyan to lighter cyan
            '#ff9800': '#ffcc80', # Orange to light orange
            '#d400ab': '#ff80dd', # Magenta to pink
            '#00cca4': '#80ffe5', # Teal to lighter teal
            '#ff4569': '#ff99ac', # Red to pink
            '#c0ff21': '#e5ffb3'  # Yellow-green to lighter version
        }
        
        # Create figure and axes
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Configure axes
        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)
        
        # Add grid
        self.ax.grid(True, linestyle='-', alpha=0.15, color=grid_color)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.config(width=width, height=height)
        
        # Initialize empty plot
        self.lines = []
        self.hover_annotation = None
        self.data_history = []
        
        # Create tooltip
        self.tooltip = tk.Label(
            self.parent, 
            text="", 
            bg="#152238", 
            fg="#e0f2ff",
            font=("Segoe UI", 9),
            bd=0,
            relief=tk.SOLID,
            padx=8,
            pady=5
        )
        
        # Connect events
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.canvas.mpl_connect('figure_leave_event', self.on_leave)
        
        # Initial plot setup
        self._setup_plot()
        
        # Pack the canvas
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    def _setup_plot(self):
        """Set up the initial plot"""
        # X-axis format as time
        self.ax.xaxis.set_major_locator(MaxNLocator(5))
        
        # Y-axis range
        self.ax.set_ylim(0, 20)
        
        # Labels
        self.ax.set_xlabel('Time', color=self.font_color, fontsize=9, alpha=0.9)
        self.ax.set_ylabel(self.title, color=self.font_color, fontsize=9, alpha=0.9)
        
        # Remove top and right spines
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        # Set tick color
        self.ax.tick_params(axis='x', colors=self.font_color, labelsize=8)
        self.ax.tick_params(axis='y', colors=self.font_color, labelsize=8)
        
        # Set spine color
        self.ax.spines['bottom'].set_color(self.grid_color)
        self.ax.spines['left'].set_color(self.grid_color)
        
        # Add subtle background gradient effect like in the reference image
        gradient = np.linspace(0, 1, 100).reshape(1, -1)
        gradient = np.vstack((gradient, gradient))
        extent = [0, 1, 0, 0.15]
        
        # Create a very subtle background hill effect
        x = np.linspace(0, 1, 100)
        y_base = 0
        
        for i in range(3):
            # Create wavy background hills
            phase = i * np.pi / 3
            y = 0.03 * np.sin(8 * x + phase) + 0.05 * np.sin(5 * x + phase) + y_base
            self.ax.fill_between(x, y_base, y, color=self.grid_color, alpha=0.07, zorder=-10)
            y_base = y
        
        # Adjust layout
        self.fig.tight_layout()
    
    def _get_smooth_data(self, data, window=5):
        """Create smoothed version of data for more natural curves"""
        if len(data) < window:
            return data
        
        # Simple moving average for smoothing
        smoothed = np.convolve(data, np.ones(window)/window, mode='valid')
        # Pad beginning to match original length
        padding = np.full(window-1, data[0])
        return np.concatenate([padding, smoothed])
    
    def update_data(self, new_values, timestamp=None):
        """Update the chart with new data points"""
        # Keep a history of the data for smoother transitions
        self.data_history.append(new_values)
        if len(self.data_history) > 30:  # Keep only the last 30 data points
            self.data_history = self.data_history[-30:]
        
        # Clear previous plot
        self.ax.clear()
        self.lines = []
        
        # Setup plot again
        self._setup_plot()
        
        # Create smooth data by interpolating between points
        smooth_data = []
        
        # For each data series (device or metric)
        for i in range(len(new_values)):
            if i < len(self.colors) and i < len(self.labels):
                # Extract history for this series
                series_history = [d[i] if i < len(d) else 0 for d in self.data_history]
                # Create smoother curve by interpolating between points
                smooth_data.append(self._get_smooth_data(series_history))
        
        # Get the x values for plotting
        x = np.arange(len(smooth_data[0])) if smooth_data else []
        
        # Plot each data series with a neon glowing effect
        for i, values in enumerate(smooth_data):
            if i < len(self.colors) and i < len(self.labels):
                base_color = self.colors[i]
                glow_color = self.neon_colors.get(base_color, '#ffffff')
                
                # Add multiple layers to create glow effect (from largest/dimmest to smallest/brightest)
                # Layer 1: Wide dim glow
                self.ax.plot(x, values, color=glow_color, alpha=0.2, linewidth=self.line_width + 6, 
                           solid_capstyle='round', solid_joinstyle='round')
                
                # Layer 2: Medium glow
                self.ax.plot(x, values, color=glow_color, alpha=0.4, linewidth=self.line_width + 3, 
                           solid_capstyle='round', solid_joinstyle='round')
                
                # Layer 3: Core glow
                self.ax.plot(x, values, color=glow_color, alpha=0.6, linewidth=self.line_width + 1, 
                           solid_capstyle='round', solid_joinstyle='round')
                
                # Layer 4: Bright core
                line = self.ax.plot(x, values, color=base_color, alpha=1.0, linewidth=self.line_width,
                                  solid_capstyle='round', solid_joinstyle='round')
                
                # Add a dot at the end with glow effect
                if len(values) > 0:
                    # Outer glow
                    self.ax.scatter([x[-1]], [values[-1]], s=80, color=glow_color, alpha=0.3)
                    self.ax.scatter([x[-1]], [values[-1]], s=50, color=glow_color, alpha=0.5)
                    # Inner dot
                    self.ax.scatter([x[-1]], [values[-1]], s=25, color=base_color, 
                                  edgecolor='white', linewidth=0.5, zorder=10)
                
                self.lines.append(line[0])
        
        # Add current timestamp if provided
        if timestamp:
            self.ax.text(0.98, 0.02, timestamp, 
                       transform=self.ax.transAxes, 
                       ha='right', va='bottom', 
                       color=self.font_color, alpha=0.7, fontsize=7)
        
        # Update legend with custom styling
        if len(self.labels) > 0:
            handles = [plt.Line2D([0], [0], color=self.colors[i], lw=2) 
                       for i in range(min(len(self.labels), len(self.colors)))]
            self.ax.legend(handles, self.labels, loc='upper right', framealpha=0.3, 
                         fontsize=8, labelcolor=self.font_color, facecolor=self.bg_color)
        
        # Draw the plot
        self.canvas.draw()
    
    def on_hover(self, event):
        """Handle mouse hover event"""
        if event.inaxes == self.ax:
            self.tooltip.place_forget()
            
            # Get position for tooltip
            bbox = self.ax.get_window_extent()
            x, y = event.x, event.y
            
            # Create tooltip text
            text = f"Value: {event.ydata:.2f} at x={event.xdata:.1f}"
            
            # Show tooltip
            self.tooltip.config(text=text)
            self.tooltip.place(x=x+10, y=y+10)
    
    def on_leave(self, event):
        """Handle mouse leave event"""
        self.tooltip.place_forget()
    
    def pack(self, **kwargs):
        """Pack the chart widget"""
        self.canvas_widget.pack(**kwargs)


class FuturisticGaugeChart:
    """Futuristic gauge chart for displaying percentage metrics"""
    def __init__(self, parent, title="", max_value=100, bg_color='#080f1c', color='#00c2ff', 
                 width=300, height=300, font_color='#e0f2ff'):
        self.parent = parent
        self.title = title
        self.max_value = max_value
        self.bg_color = bg_color
        self.color = color
        self.width = width
        self.height = height
        self.value = 0
        self.font_color = font_color
        
        # Create figure and axes
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.fig.add_subplot(111, polar=True)
        
        # Configure figure
        self.fig.patch.set_facecolor(bg_color)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.config(width=width, height=height)
        
        # Initial plot
        self.update_data(0)
        
        # Pack the canvas
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    def update_data(self, value):
        """Update the chart with a new value"""
        self.value = min(value, self.max_value)
        percentage = (self.value / self.max_value) * 100
        
        # Clear the axes
        self.ax.clear()
        
        # Set chart parameters
        self.ax.set_theta_zero_location('N')
        self.ax.set_theta_direction(-1)
        
        # Hide the grid and axis
        self.ax.grid(False)
        self.ax.axis('off')
        
        # Calculate angles
        start_angle = 140  # Degrees
        end_angle = 400    # Degrees 
        value_angle = start_angle + (end_angle - start_angle) * (percentage / 100)
        
        # Draw stylized outer ring
        theta = np.linspace(0, 2*np.pi, 200)
        r = np.ones_like(theta) * 0.9
        self.ax.plot(theta, r, color='#143062', linewidth=1.5, alpha=0.5)
        
        # Draw background arc
        theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 100)
        arc_r = np.ones_like(theta) * 0.82
        self.ax.plot(theta, arc_r, color='#143062', linewidth=5, alpha=0.3, solid_capstyle='round')
        
        # Draw multiple value arcs for glow effect
        if percentage > 0:
            # Choose color based on value
            if percentage < 50:
                arc_color = self.color
                inner_color = '#00c2ff'
            elif percentage < 80:
                arc_color = '#ff9800'
                inner_color = '#ffba52'
            else:
                arc_color = '#f44336'
                inner_color = '#ff7b73'
            
            # Create gradient effect with multiple arcs
            theta = np.linspace(np.radians(start_angle), np.radians(value_angle), 100)
            arc_r = np.ones_like(theta) * 0.82
            
            # Glow effect with multiple arcs of decreasing opacity
            for i, alpha in enumerate([0.1, 0.2, 0.3, 0.5, 0.7, 1.0]):
                width = 5 - i*0.5
                if i == 5:  # The main arc
                    width = 4.5
                self.ax.plot(theta, arc_r, color=arc_color, linewidth=width, alpha=alpha, 
                           solid_capstyle='round')
            
            # Add dot at the end of the arc
            end_x = 0.82 * np.cos(np.radians(value_angle))
            end_y = 0.82 * np.sin(np.radians(value_angle))
            
            # Add glow effect to the dot
            for s in [12, 8, 5]:
                self.ax.scatter(np.radians(value_angle), 0.82, s=s, color=arc_color, 
                              alpha=0.3, zorder=10)
            
            # Main dot
            self.ax.scatter(np.radians(value_angle), 0.82, s=30, color=inner_color, 
                         edgecolor='white', linewidth=0.5, zorder=10)
        
        # Add percentage value text with futuristic styling
        percent_text = f"{percentage:.1f}%"
        self.ax.text(0, 0, percent_text, ha='center', va='center', 
                    fontsize=18, fontweight='bold', color=self.font_color,
                    path_effects=[path_effects.withStroke(linewidth=3, foreground=self.bg_color)])
        
        # Add subtitle text
        if self.title:
            self.ax.text(0, -0.3, self.title, ha='center', va='center', 
                       fontsize=10, color=self.font_color, alpha=0.8)
        
        # Add tick marks for a futuristic look
        for angle in range(start_angle, end_angle+1, 20):
            # Skip marks too close to the start/end to avoid clutter
            if abs(angle - start_angle) < 10 or abs(angle - end_angle) < 10:
                continue
                
            # Calculate tick position
            tick_r_inner = 0.75
            tick_r_outer = 0.82
            
            # Draw the tick
            theta = np.radians(angle)
            x_inner = tick_r_inner * np.cos(theta)
            y_inner = tick_r_inner * np.sin(theta)
            x_outer = tick_r_outer * np.cos(theta)
            y_outer = tick_r_outer * np.sin(theta)
            
            # Make ticks that represent 25%, 50%, 75% more prominent
            tick_percent = (angle - start_angle) / (end_angle - start_angle) * 100
            if abs(tick_percent - 25) < 5 or abs(tick_percent - 50) < 5 or abs(tick_percent - 75) < 5:
                self.ax.plot([theta, theta], [tick_r_inner-0.05, tick_r_outer], 
                           color='#a0d8ff', linewidth=1.5, alpha=0.7)
                # Add percent label
                r_label = tick_r_inner - 0.12
                x_label = r_label * np.cos(theta)
                y_label = r_label * np.sin(theta)
                self.ax.text(x_label, y_label, f"{int(tick_percent)}%", 
                           ha='center', va='center', fontsize=7, color=self.font_color, alpha=0.8)
            else:
                self.ax.plot([theta, theta], [tick_r_inner, tick_r_outer], 
                           color='#143062', linewidth=0.8, alpha=0.5)
        
        # Set limits
        self.ax.set_ylim(0, 1)
        
        # Draw the plot
        self.canvas.draw()
    
    def pack(self, **kwargs):
        """Pack the chart widget"""
        self.canvas_widget.pack(**kwargs)


class NetworkData:
    """Class for simulating network device data"""
    def __init__(self):
        # Data storage
        self.network_traffic = []
        self.system_load = []
        self.auth_status = []  # List to track authorized/unauthorized access counts
        self.timestamps = []
        
        # Current metrics
        self.current_network = 25.0
        self.current_auth_percent = 85.0     # Percentage of authorized traffic
        self.current_unauth_percent = 15.0   # Percentage of unauthorized traffic
        
        # Device data for 7 devices
        self.devices = [
            {"name": "Device 1", "ip": "192.168.1.100", "traffic": []},
            {"name": "Device 2", "ip": "192.168.1.101", "traffic": []},
            {"name": "Device 3", "ip": "192.168.1.102", "traffic": []},
            {"name": "Device 4", "ip": "192.168.1.103", "traffic": []},
            {"name": "Device 5", "ip": "192.168.1.104", "traffic": []},
            {"name": "Device 6", "ip": "192.168.1.105", "traffic": []},
            {"name": "Device 7", "ip": "192.168.1.106", "traffic": []}
        ]
        
        # System load for 3 lines
        self.load_values = [
            {'value': 150, 'direction': 1},  # 1m
            {'value': 180, 'direction': 1},  # 5m
            {'value': 120, 'direction': 1}   # 15m
        ]
        
        # Initialize with some data
        self._generate_initial_data()
    
    def _generate_initial_data(self):
        """Initialize with 60 data points of historical data"""
        for _ in range(60):
            self._generate_next_data_point()
    
    def _generate_next_data_point(self):
        """Generate the next data point with randomized fluctuations"""
        timestamp = time.strftime('%H:%M')
        self.timestamps.append(timestamp)
        
        # Keep only last 60 points
        if len(self.timestamps) > 60:
            self.timestamps = self.timestamps[-60:]
            self.network_traffic = self.network_traffic[-60:]
            self.system_load = self.system_load[-60:]
            self.auth_status = self.auth_status[-60:]
        
        # Generate network traffic for each device with authorization status
        network_values = []
        auth_count = 0
        unauth_count = 0
        
        for device in self.devices:
            # Random traffic with occasional spikes
            base_traffic = random.uniform(5, 20)
            is_authorized = True
            
            if random.random() < 0.15:  # 15% chance of unauthorized access
                # Create a traffic spike (unauthorized access)
                base_traffic *= 3
                is_authorized = False
                unauth_count += 1
            else:
                auth_count += 1
            
            # Store device traffic
            if len(device['traffic']) > 60:
                device['traffic'] = device['traffic'][-60:]
            device['traffic'].append(base_traffic)
            network_values.append(base_traffic)
        
        # Store overall network traffic
        self.network_traffic.append(network_values)
        
        # Calculate and store auth percentages
        total = auth_count + unauth_count
        if total > 0:
            self.current_auth_percent = (auth_count / total) * 100
            self.current_unauth_percent = (unauth_count / total) * 100
        
        # Store auth status for historical data
        self.auth_status.append([auth_count, unauth_count])
        
        # Update system load (3 lines, wandering with trends)
        current_loads = []
        for i, load in enumerate(self.load_values):
            # Change direction occasionally
            if random.random() < 0.1:
                load['direction'] *= -1
            
            # Update value with trend
            change = (random.random() * 15) * load['direction']
            load['value'] += change
            
            # Keep within reasonable bounds (100-300%)
            load['value'] = max(100, min(300, load['value']))
            current_loads.append(load['value'])
        
        self.system_load.append(current_loads)
    
    def update(self):
        """Generate a new data point and return current metrics"""
        self._generate_next_data_point()
        
        # Extract latest network traffic for each device
        network_values = []
        for device in self.devices:
            network_values.append(device['traffic'][-1])
            
        # Extract latest auth status data
        auth_data = self.auth_status[-1] if self.auth_status else [0, 0]
            
        return {
            'network_traffic': network_values,
            'auth_percent': self.current_auth_percent,
            'unauth_percent': self.current_unauth_percent,
            'auth_counts': auth_data,
            'network_history': self.network_traffic,
            'system_load': self.system_load[-1],
            'timestamp': self.timestamps[-1]
        }


class FuturisticNetworkDashboard:
    def __init__(self, root):
        self.root = root
        self.running = True
        
        # Configure main window
        root.title("Futuristic Network Monitoring Dashboard")
        root.geometry("1200x800")
        root.minsize(1000, 700)
        root.configure(bg="#080f1c")  # Dark blue-black for futuristic feel
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create data simulator
        self.node_data = NetworkData()
        
        # Colors for the UI - updated for futuristic look
        self.colors = {
            'bg': '#080f1c',          # Dark blue-black base
            'header_bg': '#0a172e',   # Slightly lighter dark blue
            'text': '#e0f2ff',        # Light blue-white text
            'highlight': '#00c2ff',   # Bright cyan highlight
            'chart_bg': '#080f1c',    # Dark blue for charts
            'green': '#00d084',       # Bright green (authorized)
            'orange': '#ff9800',      # Orange (warnings/unauthorized)
            'blue': '#00c2ff',        # Cyan blue
            'purple': '#9c27b0',      # Purple
            'teal': '#00bcd4',        # Teal
            'grid': '#143062',        # Blue grid lines
            'red': '#f44336'          # Red for alerts
        }
        
        # Chart colors - adjusted for higher contrast and futuristic look
        self.load_colors = ['#00d084', '#00c2ff', '#ff9800']  # Green, Blue, Orange
        
        # Device colors (one for each of the 7 devices)
        self.device_colors = [
            '#00d084',  # Green
            '#00c2ff',  # Cyan
            '#ff9800',  # Orange
            '#d400ab',  # Magenta
            '#00cca4',  # Teal
            '#ff4569',  # Red
            '#c0ff21'   # Neon green-yellow
        ]
        
        # UI components
        self.main_frame = None
        self.header_frame = None
        self.charts_frame = None
        
        # Chart components
        self.network_chart = None
        self.system_load_chart = None
        self.auth_chart = None
        self.auth_gauge = None
        self.unauth_chart = None
        self.unauth_gauge = None
        
        # Styles for the UI
        self.style = ttk.Style()
        self._setup_styles()
        
        # Setup UI
        self.setup_ui()
        
        # Start the update loop
        self.update_ui()
    
    def _setup_styles(self):
        """Set up custom styles for UI components"""
        self.style.configure('TFrame', background=self.colors['bg'])
        self.style.configure('Header.TFrame', background=self.colors['header_bg'])
        self.style.configure('TLabel', 
                          background=self.colors['bg'], 
                          foreground=self.colors['text'],
                          font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', 
                          background=self.colors['header_bg'], 
                          foreground=self.colors['text'],
                          font=('Segoe UI', 11))
        self.style.configure('Title.TLabel', 
                          background=self.colors['bg'], 
                          foreground=self.colors['text'],
                          font=('Segoe UI', 12, 'bold'))
        self.style.configure('Subtitle.TLabel', 
                          background=self.colors['bg'], 
                          foreground=self.colors['highlight'],
                          font=('Segoe UI', 9))
    
    def setup_ui(self):
        """Set up the main UI components"""
        # Create main frame
        self.main_frame = ttk.Frame(self.root, style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create header frame
        self._create_header()
        
        # Create charts frame
        self._create_charts_area()
    
    def _create_header(self):
        """Create the header section of the UI"""
        self.header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        self.header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Add a subtle separator line under the header
        separator = tk.Frame(self.main_frame, height=1, bg=self.colors['highlight'])
        separator.pack(fill=tk.X, padx=0, pady=0)
        
        # Title with futuristic styling
        header_label = ttk.Label(self.header_frame, 
                              text="NETWORK SECURITY DASHBOARD", 
                              style='Header.TLabel',
                              font=('Segoe UI', 14, 'bold'))
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Subtitle
        subtitle_label = ttk.Label(self.header_frame, 
                                text="FPGA-IDS Traffic Analyzer", 
                                style='Subtitle.TLabel')
        subtitle_label.pack(side=tk.LEFT, padx=5, pady=12)
        
        # Device selector
        device_frame = ttk.Frame(self.header_frame, style='Header.TFrame')
        device_frame.pack(side=tk.LEFT, padx=30, pady=10)
        
        device_label = ttk.Label(device_frame, text="7 devices monitored", style='Header.TLabel')
        device_label.pack(side=tk.LEFT, padx=5)
        
        # Last hour dropdown frame
        time_frame = ttk.Frame(self.header_frame, style='Header.TFrame')
        time_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Digital clock display
        self.time_display = ttk.Label(time_frame, 
                                   text=time.strftime("%H:%M:%S"), 
                                   style='Header.TLabel',
                                   font=('Segoe UI', 11, 'bold'),
                                   foreground=self.colors['highlight'])
        self.time_display.pack(side=tk.RIGHT, padx=10)
        
        # Update the clock every second
        self._update_clock()
    
    def _update_clock(self):
        """Update the digital clock"""
        current_time = time.strftime("%H:%M:%S")
        self.time_display.config(text=current_time)
        self.root.after(1000, self._update_clock)
    
    def _create_charts_area(self):
        """Create the area for charts and visualizations"""
        self.charts_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create 3x2 grid for charts
        for i in range(6):
            self.charts_frame.columnconfigure(i % 3, weight=1)
        self.charts_frame.rowconfigure(0, weight=1)
        self.charts_frame.rowconfigure(1, weight=1)
        self.charts_frame.rowconfigure(2, weight=1)
        
        # Network Traffic chart (top left)
        self._create_network_chart()
        
        # System Load chart (top right)
        self._create_system_load_chart()
        
        # Network Access Monitor chart (middle left & center)
        self._create_auth_chart()
        
        # Authorized Access gauge (middle right)
        self._create_auth_gauge()
        
        # Security Alerts chart (bottom left & center)
        self._create_unauth_chart()
        
        # Unauthorized Access gauge (bottom right)
        self._create_unauth_gauge()
    
    def _create_network_chart(self):
        """Create the Network Traffic chart"""
        network_frame = ttk.Frame(self.charts_frame, style='TFrame')
        network_frame.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=8, pady=8)
        
        # Title with icon
        title_label = ttk.Label(network_frame, text="≡ NETWORK TRAFFIC", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.network_chart = FuturisticLineChart(
            network_frame,
            "Traffic Rate",
            ["Device 1", "Device 2", "Device 3", "Device 4", "Device 5", "Device 6", "Device 7"],
            self.device_colors,
            bg_color=self.colors['chart_bg'],
            grid_color=self.colors['grid'],
            width=500,
            height=200,
            font_color=self.colors['text']
        )
        self.network_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_system_load_chart(self):
        """Create the System Load chart"""
        load_frame = ttk.Frame(self.charts_frame, style='TFrame')
        load_frame.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=8, pady=8)
        
        # Title with icon
        title_label = ttk.Label(load_frame, text="◉ SYSTEM LOAD", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.system_load_chart = FuturisticLineChart(
            load_frame,
            "System Load",
            ["Short-term", "Medium-term", "Long-term"],
            self.load_colors,
            bg_color=self.colors['chart_bg'],
            grid_color=self.colors['grid'],
            width=600,
            height=200,
            font_color=self.colors['text']
        )
        self.system_load_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_auth_chart(self):
        """Create the Network Access Monitor chart"""
        auth_frame = ttk.Frame(self.charts_frame, style='TFrame')
        auth_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        
        # Title with icon
        title_label = ttk.Label(auth_frame, text="✓ NETWORK ACCESS MONITOR", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart for network access monitoring
        self.auth_chart = FuturisticLineChart(
            auth_frame,
            "Access Requests",
            ["Authorized", "Unauthorized"],
            [self.colors['green'], self.colors['orange']],  # Green for authorized, Orange for unauthorized
            bg_color=self.colors['chart_bg'],
            grid_color=self.colors['grid'],
            width=750,
            height=200,
            font_color=self.colors['text']
        )
        self.auth_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_auth_gauge(self):
        """Create Authorized Access gauge"""
        auth_gauge_frame = ttk.Frame(self.charts_frame, style='TFrame')
        auth_gauge_frame.grid(row=1, column=2, sticky="nsew", padx=8, pady=8)
        
        # Title with icon
        title_label = ttk.Label(auth_gauge_frame, text="✓ AUTHORIZED ACCESS", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create gauge
        self.auth_gauge = FuturisticGaugeChart(
            auth_gauge_frame,
            "Authorization Rate",
            bg_color=self.colors['chart_bg'],
            color=self.colors['green'],
            width=300,
            height=250,
            font_color=self.colors['text']
        )
        self.auth_gauge.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_unauth_chart(self):
        """Create the Security Alerts chart"""
        unauth_frame = ttk.Frame(self.charts_frame, style='TFrame')
        unauth_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        
        # Title with alert icon
        title_label = ttk.Label(unauth_frame, text="⚠ SECURITY ALERTS", style='Title.TLabel',
                            foreground=self.colors['orange'])
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart for unauthorized access monitoring
        self.unauth_chart = FuturisticLineChart(
            unauth_frame,
            "Alert Count",
            ["Security Alerts"],
            [self.colors['orange']],  # Orange for alerts
            bg_color=self.colors['chart_bg'],
            grid_color=self.colors['grid'],
            width=750,
            height=200,
            font_color=self.colors['text']
        )
        self.unauth_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_unauth_gauge(self):
        """Create Unauthorized Access gauge"""
        unauth_gauge_frame = ttk.Frame(self.charts_frame, style='TFrame')
        unauth_gauge_frame.grid(row=2, column=2, sticky="nsew", padx=8, pady=8)
        
        # Title with alert icon
        title_label = ttk.Label(unauth_gauge_frame, text="⚠ UNAUTHORIZED ACCESS", 
                            style='Title.TLabel', foreground=self.colors['orange'])
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create gauge
        self.unauth_gauge = FuturisticGaugeChart(
            unauth_gauge_frame,
            "Alert Level",
            bg_color=self.colors['chart_bg'],
            color=self.colors['orange'],  # Orange for unauthorized
            width=300,
            height=250,
            font_color=self.colors['text']
        )
        self.unauth_gauge.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_ui(self):
        """Update the UI with the latest data"""
        if self.running:
            # Get the latest data
            data = self.node_data.update()
            
            # Update Network Traffic chart (all 7 devices)
            self.network_chart.update_data(data['network_traffic'], data['timestamp'])
            
            # Update System Load chart with 3 values
            self.system_load_chart.update_data(data['system_load'], data['timestamp'])
            
            # Update Auth/Unauth charts
            self.auth_chart.update_data(data['auth_counts'], data['timestamp'])
            self.auth_gauge.update_data(data['auth_percent'])
            
            # Update Unauthorized charts
            # For the unauth_chart, we're just passing the unauthorized count
            self.unauth_chart.update_data([data['auth_counts'][1]], data['timestamp'])
            self.unauth_gauge.update_data(data['unauth_percent'])
        
        # Schedule the next update
        self.root.after(1000, self.update_ui)
    
    def on_closing(self):
        """Handle application closing"""
        self.running = False
        self.root.destroy()


def main():
    # Create the main application window
    root = tk.Tk()
    app = FuturisticNetworkDashboard(root)
    
    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()