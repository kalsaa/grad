#!/usr/bin/env python3
"""
Network Monitoring Dashboard
A single-file application that monitors network traffic for multiple devices
"""

import os
import sys
import time
import random
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.figure as Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle, Wedge
from matplotlib.ticker import MaxNLocator

class GaugeChart:
    """Gauge chart for displaying percentage metrics like memory and disk usage"""
    def __init__(self, parent, title="", max_value=100, bg_color='#252526', color='#4caf50', 
                width=300, height=300, font_color='white'):
        self.parent = parent
        self.title = title
        self.max_value = max_value
        self.bg_color = bg_color
        self.color = color
        self.width = width
        self.height = height
        self.font_color = font_color
        self.value = 0
        
        # Create figure and axes
        self.fig = Figure.Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        
        # Initial setup
        self._draw_gauge()
    
    def update_data(self, value):
        """Update the chart with a new value"""
        self.value = min(value, self.max_value)
        self._draw_gauge()
        self.canvas.draw()
    
    def _draw_gauge(self):
        """Draw the gauge chart"""
        self.ax.clear()
        
        # Configure axes
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.axis('off')
        
        # Calculate angles for the gauge
        percentage = self.value / self.max_value
        angle = 180 * percentage
        
        # Draw gauge background (grey arc)
        background = Wedge((0, 0), 0.8, 180, 0, width=0.2, 
                         facecolor='#3e3e42', edgecolor=None)
        self.ax.add_patch(background)
        
        # Draw gauge value (colored arc)
        if angle > 0:
            foreground = Wedge((0, 0), 0.8, 180, 180-angle, width=0.2,
                            facecolor=self.color, edgecolor=None)
            self.ax.add_patch(foreground)
        
        # Add text in center
        self.ax.text(0, -0.2, f"{int(self.value)}%", 
                  ha='center', va='center', 
                  fontsize=24, color=self.font_color,
                  fontweight='bold')
        
        # Add title if provided
        if self.title:
            self.ax.text(0, 0.7, self.title, 
                      ha='center', va='center', 
                      fontsize=12, color=self.font_color)
    
    def pack(self, **kwargs):
        """Pack the chart widget"""
        self.canvas_widget.pack(**kwargs)

class LineChart:
    """Line chart for visualizing network metrics over time"""
    def __init__(self, parent, title, labels, colors, bg_color='#151515', grid_color='#333', 
                 width=600, height=300, line_width=1.5, font_color='white'):
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
        
        # Data
        self.timestamps = []
        self.data_series = [[] for _ in range(len(labels))]
        self.hover_annotation = None
        
        # Create figure and axes
        self.fig = Figure.Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        
        # Create canvas with hover support
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.canvas.mpl_connect('axes_leave_event', self.on_leave)
        
        # Initial setup
        self._setup_plot()
    
    def on_hover(self, event):
        """Handle mouse hover event"""
        if event.inaxes == self.ax and len(self.timestamps) > 0:
            # Get the x-value
            x_val = event.xdata
            
            # Find the closest timestamp index
            closest_idx = min(int(x_val), len(self.timestamps) - 1)
            closest_idx = max(0, closest_idx)  # Ensure it's not negative
            
            # Create or update annotation
            if self.hover_annotation:
                self.hover_annotation.remove()
            
            # Prepare annotation text
            text = f"Time: {self.timestamps[closest_idx]}\n"
            for i, label in enumerate(self.labels):
                if i < len(self.data_series) and closest_idx < len(self.data_series[i]):
                    val = self.data_series[i][closest_idx]
                    text += f"{label}: {val:.1f}\n"
            
            # Display the annotation
            self.hover_annotation = self.ax.annotate(
                text, xy=(event.xdata, event.ydata),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round', fc='#2a2a2a', alpha=0.9),
                color=self.font_color,
                fontsize=9
            )
            self.canvas.draw_idle()
    
    def on_leave(self, event):
        """Handle mouse leave event"""
        if self.hover_annotation:
            self.hover_annotation.remove()
            self.hover_annotation = None
            self.canvas.draw_idle()
    
    def _setup_plot(self):
        """Set up the initial plot"""
        # Configure axis
        self.ax.tick_params(axis='both', colors=self.font_color, direction='out')
        self.ax.spines['bottom'].set_color(self.grid_color)
        self.ax.spines['left'].set_color(self.grid_color)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.set_facecolor(self.bg_color)
        
        # Add grid
        self.ax.grid(color=self.grid_color, linestyle='-', linewidth=0.5, alpha=0.3)
        
        # Set labels
        self.ax.set_title(self.title, color=self.font_color, fontsize=12)
        
        # Add legend if multiple labels
        if len(self.labels) > 1:
            self.ax.legend(self.labels, loc='upper right', facecolor=self.bg_color, 
                         edgecolor='none', labelcolor=self.font_color)
        
        # Set dynamic x-axis (will adjust as data comes in)
        self.ax.set_xlim(0, 60)  # Show up to 60 points
        self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Tight layout
        self.fig.tight_layout()
    
    def update_data(self, new_values, timestamp=None):
        """Update the chart with new data points"""
        if timestamp is None:
            timestamp = time.strftime('%H:%M:%S')
        
        # Add new timestamp
        self.timestamps.append(timestamp)
        
        # Keep only last 60 points
        if len(self.timestamps) > 60:
            self.timestamps = self.timestamps[-60:]
        
        # Handle single value or list
        if not isinstance(new_values, list):
            new_values = [new_values]
        
        # Update each data series
        for i, value in enumerate(new_values):
            if i < len(self.data_series):
                self.data_series[i].append(value)
                # Keep only last 60 points
                if len(self.data_series[i]) > 60:
                    self.data_series[i] = self.data_series[i][-60:]
        
        # Clear and redraw plot
        self.ax.clear()
        self._setup_plot()
        
        # Plot each data series
        x_values = list(range(len(self.timestamps)))
        for i, data in enumerate(self.data_series):
            if i < len(self.colors) and len(data) > 0:
                self.ax.plot(
                    x_values[-len(data):], 
                    data, 
                    color=self.colors[i],
                    linewidth=self.line_width
                )
        
        # Set x-axis ticks
        if len(self.timestamps) > 0:
            # Only show a subset of timestamps to avoid crowding
            step = max(1, len(self.timestamps) // 6)
            tick_indices = list(range(0, len(self.timestamps), step))
            self.ax.set_xticks(tick_indices)
            self.ax.set_xticklabels([self.timestamps[i] for i in tick_indices], rotation=30)
        
        # Update plot
        self.canvas.draw()
    
    def pack(self, **kwargs):
        """Pack the chart widget"""
        self.canvas_widget.pack(**kwargs)

class MultiLineChart(LineChart):
    """Multi-line chart for memory usage display"""
    def __init__(self, parent, title, labels, colors, bg_color='#151515', grid_color='#333', 
                width=600, height=200, y_min=0, y_max=5, y_label='GB', font_color='white'):
        self.y_min = y_min
        self.y_max = y_max
        self.y_label = y_label
        super().__init__(parent, title, labels, colors, bg_color, grid_color, 
                       width, height, line_width=1.5, font_color=font_color)
    
    def _setup_plot(self):
        """Override the setup_plot method to customize for memory display"""
        super()._setup_plot()
        
        # Fixed y-axis range
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.set_ylabel(self.y_label, color=self.font_color, fontsize=10)
    
    def update_data(self, data_dict, timestamp=None):
        """Update with dictionary of named data series"""
        # Convert dictionary to lists matching our labels order
        values = []
        for label in self.labels:
            if label in data_dict:
                values.append(data_dict[label])
            else:
                values.append(0)  # Default if not found
        
        # Call parent update method
        super().update_data(values, timestamp)

class DiskIOChart(LineChart):
    """Special line chart for disk I/O with positive and negative values"""
    def __init__(self, parent, title, labels, colors, bg_color='#151515', grid_color='#333', 
                width=600, height=200, font_color='white'):
        super().__init__(parent, title, labels, colors, bg_color, grid_color, 
                       width, height, line_width=1.5, font_color=font_color)
    
    def _setup_plot(self):
        """Override the setup_plot method to customize for disk I/O display"""
        super()._setup_plot()
        
        # Set y-axis to show both positive and negative values
        self.ax.set_ylim(-1, 1)
        self.ax.set_ylabel("I/O", color=self.font_color, fontsize=10)
        # Allow for negative values
        self.ax.axhline(y=0, color=self.grid_color, linestyle='-', alpha=0.3)

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

class NetworkDashboard:
    def __init__(self, root):
        self.root = root
        self.running = True
        
        # Configure main window
        root.title("Network Monitoring Dashboard")
        root.geometry("1200x800")
        root.minsize(1000, 700)
        root.configure(bg="#151515")
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create data simulator
        self.node_data = NetworkData()
        
        # Colors for the UI - matched to the reference image
        self.colors = {
            'bg': '#151515',
            'header_bg': '#1d1d1d',
            'text': '#e0e0e0',
            'highlight': '#0078d7',
            'chart_bg': '#151515',
            'green': '#4caf50',  # Green
            'orange': '#ff9800',  # Orange
            'blue': '#2196f3',  # Blue
            'purple': '#9c27b0',  # Purple
            'teal': '#00bcd4',  # Teal
            'grid': '#333333'
        }
        
        # Chart colors
        self.cpu_colors = ['#e6b030', '#e6b334', '#e6bd64']  # Yellow shades
        self.load_colors = ['#4caf50', '#2196f3', '#ff9800']  # Green, Blue, Orange
        self.memory_colors = ['#606060', '#4682b4', '#00aad4', '#30c270']  # Grey, Steel Blue, Light Blue, Green
        self.disk_colors = ['#4caf50']  # Green
        
        # Device colors (one for each of the 7 devices)
        self.device_colors = [
            '#4caf50',  # Green
            '#2196f3',  # Blue
            '#ff9800',  # Orange
            '#9c27b0',  # Purple
            '#00bcd4',  # Teal
            '#f44336',  # Red
            '#ffeb3b'   # Yellow
        ]
        
        # UI components
        self.main_frame = None
        self.header_frame = None
        self.charts_frame = None
        
        # Chart components
        self.cpu_chart = None
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
        
        # Title
        header_label = ttk.Label(self.header_frame, 
                              text="Network Monitoring Dashboard", 
                              style='Header.TLabel')
        header_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Device selector
        device_frame = ttk.Frame(self.header_frame, style='Header.TFrame')
        device_frame.pack(side=tk.LEFT, padx=20, pady=7)
        
        device_label = ttk.Label(device_frame, text="7 devices", style='Header.TLabel')
        device_label.pack(side=tk.LEFT, padx=5)
        
        # Last hour dropdown frame
        time_frame = ttk.Frame(self.header_frame, style='Header.TFrame')
        time_frame.pack(side=tk.RIGHT, padx=20, pady=7)
        
        last_hour_label = ttk.Label(time_frame, text="Last 1 hour", style='Header.TLabel')
        last_hour_label.pack(side=tk.LEFT, padx=5)
    
    def _create_charts_area(self):
        """Create the area for charts and visualizations"""
        self.charts_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create 3x2 grid for charts
        for i in range(6):
            self.charts_frame.columnconfigure(i % 3, weight=1)
        self.charts_frame.rowconfigure(0, weight=1)
        self.charts_frame.rowconfigure(1, weight=1)
        self.charts_frame.rowconfigure(2, weight=1)
        
        # Network Traffic chart (top left)
        self._create_cpu_chart()
        
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
    
    def _create_cpu_chart(self):
        """Create the Network Traffic chart"""
        cpu_frame = ttk.Frame(self.charts_frame, style='TFrame')
        cpu_frame.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(cpu_frame, text="Network Traffic", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.cpu_chart = LineChart(
            cpu_frame,
            "Network Traffic",
            ["Device 1", "Device 2", "Device 3", "Device 4", "Device 5", "Device 6", "Device 7"],
            self.device_colors,
            bg_color=self.colors['chart_bg'],
            grid_color=self.colors['grid'],
            width=500,
            height=200,
            font_color=self.colors['text']
        )
        self.cpu_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_system_load_chart(self):
        """Create the System Load chart"""
        load_frame = ttk.Frame(self.charts_frame, style='TFrame')
        load_frame.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(load_frame, text="System Load", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.system_load_chart = LineChart(
            load_frame,
            "System Load",
            ["load 1m", "load 5m", "load 15m"],
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
        auth_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(auth_frame, text="Network Access Monitor", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart for network access monitoring
        self.auth_chart = LineChart(
            auth_frame,
            "Network Access Monitor",
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
        auth_gauge_frame.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(auth_gauge_frame, text="Authorized Access", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create gauge
        self.auth_gauge = GaugeChart(
            auth_gauge_frame,
            bg_color=self.colors['chart_bg'],
            color=self.colors['green'],
            width=300,
            height=250,
            font_color=self.colors['text']
        )
        self.auth_gauge.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_unauth_chart(self):
        """Create the Unauthorized Access Monitor chart"""
        unauth_frame = ttk.Frame(self.charts_frame, style='TFrame')
        unauth_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(unauth_frame, text="Security Alerts", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart for unauthorized access monitoring
        self.unauth_chart = LineChart(
            unauth_frame,
            "Security Alerts",
            ["Alerts"],
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
        unauth_gauge_frame.grid(row=2, column=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(unauth_gauge_frame, text="Unauthorized Access", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create gauge
        self.unauth_gauge = GaugeChart(
            unauth_gauge_frame,
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
            self.cpu_chart.update_data(data['network_traffic'], data['timestamp'])
            
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
    app = NetworkDashboard(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
