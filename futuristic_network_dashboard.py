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
                 width=600, height=300, line_width=3.0, font_color='#e0f2ff', show_hover_values=False):
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
        self.show_hover_values = show_hover_values  # Flag to control value boxes on hover
        
        # Store connection details for hover functionality
        self.connection_details = None
        self.device_names = None
        self.device_ips = None
        
        # Tooltip for displaying detailed information when hovering
        self.detail_tooltip = None
        
        # Pause traffic when hovering
        self.hovering = False
        self.hover_device_index = None
        
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
        self.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Initial plot setup
        self._setup_plot()
        
        # Store selected device index
        self.selected_device_idx = None
        
        # Pack the canvas
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    def _setup_plot(self):
        """Set up the initial plot"""
        # X-axis format as time
        self.ax.xaxis.set_major_locator(MaxNLocator(5))
        
        # Y-axis range with more headroom
        self.ax.set_ylim(0, 60)  # Increased to 60 to avoid cutting off traffic spikes
        
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
    
    def update_data(self, new_values, timestamp=None, connection_details=None, device_names=None, device_ips=None):
        """Update the chart with new data points and connection details for hover information"""
        # Store connection details for hover functionality if provided
        if connection_details is not None:
            self.connection_details = connection_details
        if device_names is not None:
            self.device_names = device_names
        if device_ips is not None:
            self.device_ips = device_ips
            
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
        
        # Plot each data series with smooth curves like in the reference image
        for i, values in enumerate(smooth_data):
            if i < len(self.colors) and i < len(self.labels):
                base_color = self.colors[i]
                
                # Draw the main line with high-quality smoothing and rounded joins
                line = self.ax.plot(x, values, color=base_color, 
                                  linewidth=self.line_width,
                                  solid_capstyle='round', 
                                  solid_joinstyle='round',
                                  path_effects=[path_effects.SimpleLineShadow(offset=(1, -1), alpha=0.3),
                                                path_effects.Normal()])
                
                # Add a dot at the end of each line
                if len(values) > 0:
                    # Add an endpoint dot - subtle shadow first then the main dot
                    self.ax.scatter([x[-1]], [values[-1]], s=30, color='black', alpha=0.2, zorder=9)
                    self.ax.scatter([x[-1]], [values[-1]], s=20, color=base_color, 
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
        """Handle mouse hover event with detailed connection information"""
        if event.inaxes == self.ax and self.show_hover_values:  # Only show hover values if flag is set
            self.tooltip.place_forget()
            
            # Get position for tooltip
            bbox = self.ax.get_window_extent()
            x, y = event.x, event.y
            
            # See if we're hovering over a line point
            closest_line_idx = None
            closest_dist = float('inf')
            
            # Find closest data point
            for i, line in enumerate(self.lines):
                # Check if there's line data available
                if not line.get_xdata().size or not line.get_ydata().size:
                    continue
                
                # Get the line data
                line_xdata = line.get_xdata()
                line_ydata = line.get_ydata()
                
                # Find the closest point on the line
                for j in range(len(line_xdata)):
                    # Convert data coordinates to display coordinates
                    display_coords = self.ax.transData.transform((line_xdata[j], line_ydata[j]))
                    dist = np.sqrt((display_coords[0] - event.x)**2 + (display_coords[1] - event.y)**2)
                    
                    if dist < closest_dist and dist < 50:  # Within 50 pixels
                        closest_dist = dist
                        closest_line_idx = i
            
            # Set paused state if we're hovering over a line
            if closest_line_idx is not None:
                # Get reference to the main application's data source (NetworkData instance)
                # This reference is stored in the parent window's hierarchy
                app = self.find_app_reference()
                if app and hasattr(app, 'node_data'):
                    # Set the hovering state to pause data updates
                    app.node_data.paused = True
                    app.node_data.selected_device = closest_line_idx
                    self.hovering = True
                    self.hover_device_index = closest_line_idx
                        
            # Basic hover information
            text = f"Value: {event.ydata:.2f} at x={event.xdata:.1f}"
            
            # If we have connection details and we're hovering near a line
            if self.connection_details and closest_line_idx is not None and closest_line_idx < len(self.connection_details):
                device_connections = self.connection_details[closest_line_idx]
                if device_connections and len(device_connections) > 0:
                    device_name = self.device_names[closest_line_idx] if self.device_names else f"Device {closest_line_idx+1}"
                    device_ip = self.device_ips[closest_line_idx] if self.device_ips else "Unknown IP"
                    
                    # Create detailed tooltip with connection information
                    text = f"{device_name} ({device_ip}) - PAUSED\n"
                    text += f"Traffic: {event.ydata:.2f} Mbps\n\n"
                    text += "Active Connections:\n"
                    
                    # List up to 3 connections to keep tooltip manageable
                    for i, conn in enumerate(device_connections[:3]):
                        # Format bytes in a readable way
                        bytes_sent = self._format_bytes(conn["bytes_sent"]) if "bytes_sent" in conn else "N/A"
                        bytes_received = self._format_bytes(conn["bytes_received"]) if "bytes_received" in conn else "N/A"
                        
                        text += f"{i+1}. {conn['protocol']} → {conn['destination']}:{conn['port']}\n"
                        text += f"   Status: {conn['status']} | Sent: {bytes_sent} | Recv: {bytes_received}\n"
                        if "authorized" in conn:
                            auth_status = "✓ Authorized" if conn["authorized"] else "⚠ Unauthorized" 
                            text += f"   {auth_status}\n"
                    
                    if len(device_connections) > 3:
                        text += f"\n+ {len(device_connections) - 3} more connections"
            
            # Create a more advanced tooltip if not already created
            if not hasattr(self, 'detail_tooltip') or not self.detail_tooltip:
                self.detail_tooltip = tk.Label(
                    self.parent, 
                    text=text,
                    bg="#152238", 
                    fg="#e0f2ff",
                    font=("Segoe UI", 9),
                    bd=1,
                    relief=tk.SOLID,
                    padx=10,
                    pady=6,
                    justify=tk.LEFT,
                    wraplength=350
                )
            else:
                self.detail_tooltip.config(text=text)
            
            # Position and display tooltip
            # Check if tooltip would go off screen and adjust if needed
            max_x = self.canvas_widget.winfo_width()
            max_y = self.canvas_widget.winfo_height()
            
            tooltip_x = x + 15
            tooltip_y = y + 15
            
            # Estimate tooltip size (approx 8 pixels per character, 18 pixels per line)
            line_count = text.count('\n') + 1
            tooltip_width = min(350, max(len(max(text.split('\n'), key=len)) * 8, 100))
            tooltip_height = line_count * 18
            
            # Adjust if would go off right edge
            if tooltip_x + tooltip_width > max_x:
                tooltip_x = max(10, x - tooltip_width - 10)
                
            # Adjust if would go off bottom edge
            if tooltip_y + tooltip_height > max_y:
                tooltip_y = max(10, y - tooltip_height - 10)
            
            self.detail_tooltip.place(x=tooltip_x, y=tooltip_y)
    
    def find_app_reference(self):
        """Find reference to the main application by walking up the widget hierarchy"""
        parent = self.parent
        while parent:
            if hasattr(parent, 'node_data'):
                return parent
            if parent.master is None or parent.master == parent:
                break
            parent = parent.master
        
        # If we reached here, try searching through all children of root
        if hasattr(self.parent, 'winfo_toplevel'):
            root = self.parent.winfo_toplevel()
            
            # Search through all children recursively
            def search_children(widget):
                if hasattr(widget, 'node_data'):
                    return widget
                
                for child in widget.winfo_children():
                    result = search_children(child)
                    if result:
                        return result
                return None
                
            return search_children(root)
            
        return None
    
    def _format_bytes(self, bytes_value):
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
    
    def on_leave(self, event):
        """Handle mouse leave event"""
        self.tooltip.place_forget()
        if hasattr(self, 'detail_tooltip') and self.detail_tooltip:
            self.detail_tooltip.place_forget()
            
        # Resume data updates if we were paused
        if self.hovering:
            # Find and update the main application's data source
            app = self.find_app_reference()
            if app and hasattr(app, 'node_data'):
                app.node_data.paused = False
                app.node_data.selected_device = None
            
            self.hovering = False
            self.hover_device_index = None
    
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
        
        # Pause state - when True, the data generation is paused
        self.paused = False
        self.selected_device = None  # Store currently selected device index
        
        # Common protocols, ports and destinations
        self.protocols = ["TCP", "UDP", "HTTP", "HTTPS", "DNS", "FTP", "SSH"]
        self.common_ports = [80, 443, 22, 21, 53, 8080, 3306, 5432, 25, 110]
        self.destinations = [
            "10.0.0.1", "172.16.0.5", "192.168.10.25", "10.10.10.1", 
            "8.8.8.8", "1.1.1.1", "204.152.189.116", "13.107.21.200"
        ]
        
        # Device data for 7 devices
        self.devices = [
            {"name": "Device 1", "ip": "192.168.1.100", "traffic": [], "connections": []},
            {"name": "Device 2", "ip": "192.168.1.101", "traffic": [], "connections": []},
            {"name": "Device 3", "ip": "192.168.1.102", "traffic": [], "connections": []},
            {"name": "Device 4", "ip": "192.168.1.103", "traffic": [], "connections": []},
            {"name": "Device 5", "ip": "192.168.1.104", "traffic": [], "connections": []},
            {"name": "Device 6", "ip": "192.168.1.105", "traffic": [], "connections": []},
            {"name": "Device 7", "ip": "192.168.1.106", "traffic": [], "connections": []}
        ]
        
        # System load for 3 lines
        self.load_values = [
            {'value': 150, 'direction': 1},  # 1m
            {'value': 180, 'direction': 1},  # 5m
            {'value': 120, 'direction': 1}   # 15m
        ]
        
        # Initialize with some data
        self._generate_initial_data()
        
        # Generate initial connection data for each device
        self._generate_connection_details()
    
    def _generate_initial_data(self):
        """Initialize with 60 data points of historical data"""
        for _ in range(60):
            self._generate_next_data_point()
    
    def _generate_connection_details(self):
        """Generate detailed connection information for each device"""
        for device in self.devices:
            source_ip = device["ip"]
            
            # Each device has 2-4 active connections
            num_connections = random.randint(2, 4)
            connections = []
            
            for _ in range(num_connections):
                dest_ip = random.choice(self.destinations)
                protocol = random.choice(self.protocols)
                port = random.choice(self.common_ports)
                
                # Add status and timestamp
                status = "ESTABLISHED" if random.random() < 0.8 else random.choice(["LISTENING", "TIME_WAIT", "CLOSE_WAIT"])
                timestamp = time.time() - random.uniform(0, 300)  # Connection started between 0-300 seconds ago
                
                # Create a detailed connection object
                connection = {
                    "source": source_ip,
                    "destination": dest_ip,
                    "protocol": protocol,
                    "port": port,
                    "status": status,
                    "bytes_sent": int(random.uniform(1024, 1024*1024)),
                    "bytes_received": int(random.uniform(1024, 1024*1024)),
                    "packets": int(random.uniform(10, 1000)),
                    "created": timestamp,
                    "duration": time.time() - timestamp,
                    "authorized": random.random() < 0.85  # 85% authorized connections
                }
                
                connections.append(connection)
            
            device["connections"] = connections
    
    def _update_connection_details(self):
        """Update connection details for each device"""
        for device in self.devices:
            # 20% chance to update connection details for this device
            if random.random() < 0.2:
                # Update existing connections (bytes, packets, duration)
                for conn in device["connections"]:
                    conn["bytes_sent"] += int(random.uniform(1024, 8192))
                    conn["bytes_received"] += int(random.uniform(1024, 8192))
                    conn["packets"] += int(random.uniform(5, 20))
                    conn["duration"] = time.time() - conn["created"]
                    
                    # 5% chance to change status
                    if random.random() < 0.05:
                        conn["status"] = random.choice(["ESTABLISHED", "LISTENING", "TIME_WAIT", "CLOSE_WAIT"])
                
                # 10% chance to replace a connection with a new one
                if random.random() < 0.1 and device["connections"]:
                    # Remove a random connection
                    conn_index = random.randint(0, len(device["connections"])-1)
                    device["connections"].pop(conn_index)
                    
                    # Add a new connection
                    source_ip = device["ip"]
                    dest_ip = random.choice(self.destinations)
                    protocol = random.choice(self.protocols)
                    port = random.choice(self.common_ports)
                    status = "ESTABLISHED"
                    timestamp = time.time()
                    
                    new_conn = {
                        "source": source_ip,
                        "destination": dest_ip,
                        "protocol": protocol,
                        "port": port,
                        "status": status,
                        "bytes_sent": int(random.uniform(1024, 4096)),
                        "bytes_received": int(random.uniform(1024, 4096)),
                        "packets": int(random.uniform(5, 20)),
                        "created": timestamp,
                        "duration": 0,
                        "authorized": random.random() < 0.85  # 85% authorized connections
                    }
                    
                    device["connections"].append(new_conn)
    
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
                # Create a traffic spike (unauthorized access) - increased from 3x to 5x for better visibility
                base_traffic *= 5
                is_authorized = False
                unauth_count += 1
            else:
                # Occasionally create authorized traffic spikes too
                if random.random() < 0.05:  # 5% chance of authorized spike
                    base_traffic *= 2.5
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
        
        # Update connection details for each device
        self._update_connection_details()
    
    def update(self):
        """Generate a new data point and return current metrics"""
        # Only generate new data if not paused
        if not self.paused:
            self._generate_next_data_point()
        
        # Extract latest network traffic for each device
        network_values = []
        for device in self.devices:
            network_values.append(device['traffic'][-1])
            
        # Extract latest auth status data
        auth_data = self.auth_status[-1] if self.auth_status else [0, 0]
        
        # Extract connection details for each device
        connection_details = []
        for device in self.devices:
            connection_details.append(device["connections"])
            
        # Calculate totals for hover displays
        total_auth_requests = sum([data[0] for data in self.auth_status])
        total_unauth_requests = sum([data[1] for data in self.auth_status])
        total_security_alerts = total_unauth_requests
        
        # Create response dictionary
        response = {
            'network_traffic': network_values,
            'auth_percent': self.current_auth_percent,
            'unauth_percent': self.current_unauth_percent,
            'auth_counts': auth_data,
            'network_history': self.network_traffic,
            'system_load': self.system_load[-1],
            'timestamp': self.timestamps[-1],
            'connections': connection_details,
            'device_names': [d["name"] for d in self.devices],
            'device_ips': [d["ip"] for d in self.devices],
            'paused': self.paused,
            'selected_device': self.selected_device,
            
            # Add totals for hover displays
            'total_auth_requests': total_auth_requests,
            'total_unauth_requests': total_unauth_requests,
            'total_security_alerts': total_security_alerts
        }
        
        # Store last data for hover information
        self.last_data = response
        
        return response


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
        
        # Chart colors - vibrant modern palette for FPGA load
        self.load_colors = ['#4287f5', '#00b3ff', '#36d6a1']  # Royal Blue, Azure, Aqua Green
        
        # Device colors (one for each of the 7 devices) - Enhanced color palette
        self.device_colors = [
            '#00bfff',  # Deep Sky Blue
            '#ff3e6c',  # Crimson
            '#ffe100',  # Vivid Yellow
            '#7b42ff',  # Vibrant Purple
            '#00e676',  # Bright Green
            '#ff9100',  # Amber Orange
            '#ff16e9'   # Hot Pink
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
        
        device_label = ttk.Label(device_frame, text="Device:", style='Header.TLabel')
        device_label.pack(side=tk.LEFT, padx=5)
        
        # Create device dropdown with the list of devices
        self.device_var = tk.StringVar()
        self.device_var.set("All Devices")  # Default selection
        
        # Create custom style for dropdown
        self.style.configure('Dropdown.TCombobox', 
                          fieldbackground=self.colors['header_bg'],
                          background=self.colors['header_bg'],
                          foreground=self.colors['text'],
                          arrowcolor=self.colors['highlight'],
                          selectbackground=self.colors['highlight'])
        
        # Create the dropdown with all devices
        device_options = ["All Devices"] + [f"Device {i+1}" for i in range(7)]
        self.device_dropdown = ttk.Combobox(device_frame, 
                                         textvariable=self.device_var,
                                         values=device_options,
                                         width=15,
                                         style='Dropdown.TCombobox')
        self.device_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Bind the dropdown selection event
        self.device_dropdown.bind("<<ComboboxSelected>>", self._on_device_selected)
        
        # Last hour dropdown frame
        time_frame = ttk.Frame(self.header_frame, style='Header.TFrame')
        time_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Digital clock display using SF Pro (Apple iPhone font)
        # If SF Pro is not available, fall back to a similar sans-serif font
        self.time_display = ttk.Label(time_frame, 
                                   text=time.strftime("%H:%M:%S"), 
                                   style='Header.TLabel',
                                   font=('-apple-system', 12, 'bold'),
                                   foreground=self.colors['highlight'])
        self.time_display.pack(side=tk.RIGHT, padx=10)
        
        # Update the clock every second
        self._update_clock()
    
    def _update_clock(self):
        """Update the digital clock with accurate time"""
        current_time = time.strftime("%H:%M:%S")
        self.time_display.config(text=current_time)
        # Schedule the update to occur precisely at the next second
        msecs_remaining = 1000 - (int(time.time() * 1000) % 1000)
        self.root.after(msecs_remaining, self._update_clock)
    
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
        
        # Create title frame with hover capability
        title_frame = ttk.Frame(network_frame, style='TFrame')
        title_frame.pack(fill=tk.X, anchor=tk.NW, padx=5, pady=5)
        
        # Title with icon
        title_label = ttk.Label(title_frame, text="≡ NETWORK TRAFFIC", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Info label for hover stats (initially empty)
        self.network_info_label = ttk.Label(title_frame, text="", style='Subtitle.TLabel',
                                         foreground=self.colors['highlight'])
        self.network_info_label.pack(side=tk.RIGHT, padx=10)
        
        # Bind hover events to the title frame
        title_frame.bind("<Enter>", self._on_network_hover)
        title_frame.bind("<Leave>", self._on_network_leave)
        
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
            font_color=self.colors['text'],
            show_hover_values=True  # Enable hover values for Network chart
        )
        self.network_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind hover events to the chart canvas to pause traffic
        self.network_chart.canvas.get_tk_widget().bind("<Enter>", self._on_network_hover)
        self.network_chart.canvas.get_tk_widget().bind("<Leave>", self._on_network_leave)
    
    def _create_system_load_chart(self):
        """Create the FPGA Load chart"""
        load_frame = ttk.Frame(self.charts_frame, style='TFrame')
        load_frame.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=8, pady=8)
        
        # Title with icon
        title_label = ttk.Label(load_frame, text="◉ FPGA LOAD", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.system_load_chart = FuturisticLineChart(
            load_frame,
            "FPGA Load",
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
        
        # Create title frame with hover capability
        title_frame = ttk.Frame(auth_frame, style='TFrame')
        title_frame.pack(fill=tk.X, anchor=tk.NW, padx=5, pady=5)
        
        # Title with icon - replace check mark with a shield icon
        title_label = ttk.Label(title_frame, text="🛡️ NETWORK ACCESS MONITOR", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Info label for hover stats (initially empty)
        self.auth_info_label = ttk.Label(title_frame, text="", style='Subtitle.TLabel',
                                       foreground=self.colors['highlight'])
        self.auth_info_label.pack(side=tk.RIGHT, padx=10)
        
        # Bind hover events to the title frame
        title_frame.bind("<Enter>", self._on_auth_hover)
        title_frame.bind("<Leave>", self._on_auth_leave)
        
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
            font_color=self.colors['text'],
            show_hover_values=False  # Disable hover values for Auth chart
        )
        self.auth_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind hover events to the chart canvas
        self.auth_chart.canvas.get_tk_widget().bind("<Enter>", self._on_auth_hover)
        self.auth_chart.canvas.get_tk_widget().bind("<Leave>", self._on_auth_leave)
    
    def _create_auth_gauge(self):
        """Create Authorized Access gauge"""
        auth_gauge_frame = ttk.Frame(self.charts_frame, style='TFrame')
        auth_gauge_frame.grid(row=1, column=2, sticky="nsew", padx=8, pady=8)
        
        # Create title frame with hover capability
        title_frame = ttk.Frame(auth_gauge_frame, style='TFrame')
        title_frame.pack(fill=tk.X, anchor=tk.NW, padx=5, pady=5)
        
        # Title with better icon (✓ replaced with 🔐)
        title_label = ttk.Label(title_frame, text="🔐 AUTHORIZED ACCESS", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Info label for hover stats (initially empty)
        self.auth_gauge_info_label = ttk.Label(title_frame, text="", style='Subtitle.TLabel',
                                           foreground=self.colors['highlight'])
        self.auth_gauge_info_label.pack(side=tk.RIGHT, padx=10)
        
        # Bind hover events to the title frame
        title_frame.bind("<Enter>", self._on_auth_gauge_hover)
        title_frame.bind("<Leave>", self._on_auth_gauge_leave)
        
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
        
        # Bind hover events to the gauge canvas
        self.auth_gauge.canvas.get_tk_widget().bind("<Enter>", self._on_auth_gauge_hover)
        self.auth_gauge.canvas.get_tk_widget().bind("<Leave>", self._on_auth_gauge_leave)
    
    def _create_unauth_chart(self):
        """Create the Security Alerts chart"""
        unauth_frame = ttk.Frame(self.charts_frame, style='TFrame')
        unauth_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        
        # Create title frame with hover capability
        title_frame = ttk.Frame(unauth_frame, style='TFrame')
        title_frame.pack(fill=tk.X, anchor=tk.NW, padx=5, pady=5)
        
        # Title with alert icon
        title_label = ttk.Label(title_frame, text="⚠ SECURITY ALERTS", style='Title.TLabel',
                            foreground=self.colors['orange'])
        title_label.pack(side=tk.LEFT)
        
        # Info label for hover stats (initially empty)
        self.unauth_info_label = ttk.Label(title_frame, text="", style='Subtitle.TLabel',
                                        foreground=self.colors['orange'])
        self.unauth_info_label.pack(side=tk.RIGHT, padx=10)
        
        # Bind hover events to the title frame
        title_frame.bind("<Enter>", self._on_unauth_hover)
        title_frame.bind("<Leave>", self._on_unauth_leave)
        
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
            font_color=self.colors['text'],
            show_hover_values=False  # Disable hover values for Security Alerts chart
        )
        self.unauth_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind hover events to the chart canvas
        self.unauth_chart.canvas.get_tk_widget().bind("<Enter>", self._on_unauth_hover)
        self.unauth_chart.canvas.get_tk_widget().bind("<Leave>", self._on_unauth_leave)
    
    def _create_unauth_gauge(self):
        """Create Unauthorized Access gauge"""
        unauth_gauge_frame = ttk.Frame(self.charts_frame, style='TFrame')
        unauth_gauge_frame.grid(row=2, column=2, sticky="nsew", padx=8, pady=8)
        
        # Create title frame with hover capability
        title_frame = ttk.Frame(unauth_gauge_frame, style='TFrame')
        title_frame.pack(fill=tk.X, anchor=tk.NW, padx=5, pady=5)
        
        # Title with alert icon
        title_label = ttk.Label(title_frame, text="⚠ UNAUTHORIZED ACCESS", 
                            style='Title.TLabel', foreground=self.colors['orange'])
        title_label.pack(side=tk.LEFT)
        
        # Info label for hover stats (initially empty)
        self.unauth_gauge_info_label = ttk.Label(title_frame, text="", style='Subtitle.TLabel',
                                             foreground=self.colors['orange'])
        self.unauth_gauge_info_label.pack(side=tk.RIGHT, padx=10)
        
        # Bind hover events to the title frame
        title_frame.bind("<Enter>", self._on_unauth_gauge_hover)
        title_frame.bind("<Leave>", self._on_unauth_gauge_leave)
        
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
        
        # Bind hover events to the gauge canvas
        self.unauth_gauge.canvas.get_tk_widget().bind("<Enter>", self._on_unauth_gauge_hover)
        self.unauth_gauge.canvas.get_tk_widget().bind("<Leave>", self._on_unauth_gauge_leave)
    
    def update_ui(self):
        """Update the UI with the latest data"""
        if self.running:
            # Get the latest data
            data = self.node_data.update()
            
            # Update Network Traffic chart (all 7 devices) with connection details for hover
            self.network_chart.update_data(
                data['network_traffic'], 
                data['timestamp'],
                connection_details=data['connections'] if 'connections' in data else None,
                device_names=data['device_names'] if 'device_names' in data else None,
                device_ips=data['device_ips'] if 'device_ips' in data else None
            )
            
            # Update FPGA Load chart with 3 values
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
    
    def _on_device_selected(self, event):
        """Handle device selection from dropdown"""
        selected = self.device_var.get()
        
        if selected == "All Devices":
            # Show all devices, unpause data
            self.node_data.paused = False
            self.node_data.selected_device = None
            
            # Close the detail window if it exists
            if hasattr(self, 'detail_window') and self.detail_window.winfo_exists():
                self.detail_window.destroy()
        else:
            # Extract device index (0-6) from the selected device string
            try:
                # Parse "Device X" to get the device index (0-based)
                device_idx = int(selected.split()[1]) - 1
                if 0 <= device_idx < 7:
                    # Pause data and set selected device
                    self.node_data.paused = True
                    self.node_data.selected_device = device_idx
                    
                    # Show device details in a popup
                    self._show_device_details(device_idx)
            except (ValueError, IndexError):
                # If the parsing fails, just ignore
                pass
    
    def _show_device_details(self, device_idx):
        """Show device details in a popup window"""
        if not hasattr(self, 'detail_window') or not self.detail_window.winfo_exists():
            # Create new detail window
            self.detail_window = tk.Toplevel(self.root)
            self.detail_window.title(f"Device {device_idx+1} Details")
            self.detail_window.geometry("500x400")
            self.detail_window.configure(bg=self.colors['bg'])
            self.detail_window.transient(self.root)  # Set as transient to main window
            
            # Get device data
            device = self.node_data.devices[device_idx]
            device_name = device["name"]
            device_ip = device["ip"]
            
            # Create header with device info
            header_frame = tk.Frame(self.detail_window, bg=self.colors['header_bg'])
            header_frame.pack(fill=tk.X, padx=0, pady=0)
            
            # Device name and IP
            tk.Label(header_frame, 
                  text=f"{device_name} ({device_ip})", 
                  font=('Segoe UI', 14, 'bold'),
                  bg=self.colors['header_bg'],
                  fg=self.colors['text']).pack(pady=10)
            
            # Connection details section
            details_frame = tk.Frame(self.detail_window, bg=self.colors['bg'])
            details_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # Create connections list
            conn_frame = tk.Frame(details_frame, bg=self.colors['bg'])
            conn_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=10)
            
            # Header
            tk.Label(conn_frame, 
                  text="ACTIVE CONNECTIONS", 
                  font=('Segoe UI', 11, 'bold'),
                  bg=self.colors['bg'],
                  fg=self.colors['highlight']).pack(anchor=tk.W, pady=(0, 10))
            
            # Create scrollable frame for connections
            canvas = tk.Canvas(conn_frame, bg=self.colors['bg'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(conn_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add connection details
            if device["connections"]:
                for i, conn in enumerate(device["connections"]):
                    # Create connection frame
                    connection_frame = tk.Frame(scrollable_frame, bg=self.colors['bg'], padx=5, pady=5)
                    connection_frame.pack(fill=tk.X, pady=5)
                    
                    # Connection header (Protocol and destination)
                    status_color = self.colors['green'] if conn.get("authorized", True) else self.colors['orange']
                    conn_header = tk.Frame(connection_frame, bg=self.colors['bg'])
                    conn_header.pack(fill=tk.X)
                    
                    # Icon based on protocol
                    icon = "⚡" if conn['protocol'] in ["HTTP", "HTTPS"] else "⟷"
                    if conn['protocol'] == "SSH":
                        icon = "🔒"
                    elif conn['protocol'] == "DNS":
                        icon = "🔍"
                        
                    tk.Label(conn_header, 
                          text=f"{icon} {conn['protocol']} → {conn['destination']}:{conn['port']}", 
                          font=('Segoe UI', 10, 'bold'),
                          bg=self.colors['bg'],
                          fg=status_color).pack(side=tk.LEFT)
                    
                    # Status indicator
                    auth_text = "✓ Authorized" if conn.get("authorized", True) else "⚠ Unauthorized"
                    tk.Label(conn_header, 
                          text=auth_text, 
                          font=('Segoe UI', 9),
                          bg=self.colors['bg'],
                          fg=status_color).pack(side=tk.RIGHT)
                    
                    # Connection details
                    details_text = f"Status: {conn['status']}  |  Duration: {int(conn['duration'])}s\n"
                    details_text += f"Bytes sent: {self._format_bytes(conn['bytes_sent'])}  |  "
                    details_text += f"Received: {self._format_bytes(conn['bytes_received'])}  |  "
                    details_text += f"Packets: {conn['packets']}"
                    
                    tk.Label(connection_frame, 
                          text=details_text, 
                          font=('Segoe UI', 9),
                          bg=self.colors['bg'],
                          fg=self.colors['text'],
                          justify=tk.LEFT).pack(anchor=tk.W, pady=(5, 0))
                    
                    # Add separator except for last item
                    if i < len(device["connections"]) - 1:
                        separator = tk.Frame(scrollable_frame, height=1, bg=self.colors['grid'])
                        separator.pack(fill=tk.X, padx=5, pady=5)
            else:
                # No connections
                tk.Label(scrollable_frame, 
                      text="No active connections", 
                      font=('Segoe UI', 10),
                      bg=self.colors['bg'],
                      fg=self.colors['text']).pack(pady=20)
                      
            # Close button
            close_button = tk.Button(self.detail_window, 
                                   text="Close", 
                                   font=('Segoe UI', 10),
                                   bg=self.colors['header_bg'],
                                   fg=self.colors['text'],
                                   bd=0,
                                   padx=15,
                                   pady=5,
                                   activebackground=self.colors['highlight'],
                                   activeforeground=self.colors['text'],
                                   command=lambda: self.detail_window.destroy())
            close_button.pack(pady=10)
        else:
            # Update existing window with new device
            self.detail_window.title(f"Device {device_idx+1} Details")
            # Update window content here...
    
    def _on_network_hover(self, event):
        """Handle hover over network traffic chart - pauses the chart updates"""
        # Pause data updates
        self.node_data.paused = True
        
        # Show tooltip with network traffic details if available
        if hasattr(self.node_data, 'last_data'):
            total_traffic = sum(self.node_data.last_data['network_traffic'])
            self.network_info_label.config(text=f"Total Traffic: {total_traffic:.1f} MB/s")
    
    def _on_network_leave(self, event):
        """Handle mouse leave event - resumes chart updates"""
        # Resume data updates if we're not looking at a specific device
        if not self.node_data.selected_device:
            self.node_data.paused = False
        
        # Clear tooltip
        self.network_info_label.config(text="")
        
        # Also hide any tooltips on the chart
        if self.network_chart and hasattr(self.network_chart, 'detail_tooltip') and self.network_chart.detail_tooltip:
            self.network_chart.detail_tooltip.place_forget()
    
    def _on_auth_hover(self, event):
        """Show details about network access monitoring on hover"""
        if hasattr(self.node_data, 'last_data'):
            data = self.node_data.last_data
            if 'total_auth_requests' in data and 'total_unauth_requests' in data:
                total_requests = data['total_auth_requests'] + data['total_unauth_requests']
                auth_text = f"Total Access Requests: {total_requests:,}"
                auth_text += f" | Authorized: {data['total_auth_requests']:,}"
                self.auth_info_label.config(text=auth_text)
    
    def _on_auth_leave(self, event):
        """Clear the auth info label on mouse leave"""
        self.auth_info_label.config(text="")
    
    def _on_auth_gauge_hover(self, event):
        """Show details about authorization rate on hover"""
        if hasattr(self.node_data, 'last_data'):
            data = self.node_data.last_data
            if 'auth_percent' in data:
                auth_text = f"Authorization Rate: {data['auth_percent']}%"
                self.auth_gauge_info_label.config(text=auth_text)
    
    def _on_auth_gauge_leave(self, event):
        """Clear the auth gauge info label on mouse leave"""
        self.auth_gauge_info_label.config(text="")
    
    def _on_unauth_hover(self, event):
        """Show details about security alerts on hover"""
        if hasattr(self.node_data, 'last_data'):
            data = self.node_data.last_data
            if 'total_security_alerts' in data:
                alert_text = f"Total Alerts: {data['total_security_alerts']:,}"
                self.unauth_info_label.config(text=alert_text)
    
    def _on_unauth_leave(self, event):
        """Clear the unauth info label on mouse leave"""
        self.unauth_info_label.config(text="")
    
    def _on_unauth_gauge_hover(self, event):
        """Show details about unauthorized access on hover"""
        if hasattr(self.node_data, 'last_data'):
            data = self.node_data.last_data
            if 'unauth_percent' in data:
                unauth_text = f"Alert Level: {data['unauth_percent']}%"
                self.unauth_gauge_info_label.config(text=unauth_text)
    
    def _on_unauth_gauge_leave(self, event):
        """Clear the unauth gauge info label on mouse leave"""
        self.unauth_gauge_info_label.config(text="")
    
    def _format_bytes(self, bytes_value):
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
    
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