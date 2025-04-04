#!/usr/bin/env python3
"""
Network Monitoring Dashboard 
A single-file application that monitors network traffic for multiple devices
"""

import tkinter as tk
from tkinter import ttk
import time
import datetime
import threading
import numpy as np
import random
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Wedge
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
        self.value = 0
        self.font_color = font_color
        
        # Create figure and axes
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
        start_angle = 150  # Degrees
        end_angle = 390    # Degrees (30 + 360 = 390, full circle + 30 degrees)
        value_angle = start_angle + (end_angle - start_angle) * (percentage / 100)
        
        # Draw background arc
        self.ax.add_patch(Wedge((0, 0), 0.8, start_angle, end_angle, width=0.2, 
                             facecolor='#333333', edgecolor=None, alpha=0.5))
        
        # Draw value arc
        if percentage > 0:
            # Choose color based on value
            if percentage < 70:
                arc_color = '#4caf50'  # Green for low
            elif percentage < 85:
                arc_color = '#ff9800'  # Orange for medium
            else:
                arc_color = '#f44336'  # Red for high
                
            self.ax.add_patch(Wedge((0, 0), 0.8, start_angle, value_angle, width=0.2, 
                                facecolor=arc_color, edgecolor=None))
        
        # Add value text
        self.ax.text(0, 0, f"{percentage:.2f}%", ha='center', va='center', 
                fontsize=18, fontweight='bold', color=self.font_color)
        
        # Draw the plot
        self.canvas.draw()

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
        
        # Create figure and axes
        self.fig = Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Configure axes
        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)
        
        # Add grid
        self.ax.grid(True, linestyle='-', alpha=0.3, color=grid_color)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.config(width=width, height=height)
        
        # Initialize empty plot
        self.lines = []
        self.data = [[] for _ in range(len(labels))]
        self.timestamps = []
        
        # Create tooltip
        self.tooltip = tk.Label(
            self.parent, 
            text="", 
            bg="#333333", 
            fg="white",
            font=("Segoe UI", 9),
            bd=1,
            relief=tk.SOLID,
            padx=5,
            pady=3
        )
        
        # Connect events
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.fig.canvas.mpl_connect('figure_leave_event', self.on_leave)
        
        # Initial plot setup
        self._setup_plot()
        
        # Pack the canvas
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
    def on_hover(self, event):
        """Handle mouse hover event"""
        if event.inaxes == self.ax:
            # Find the closest point for each line
            closest_line = None
            closest_distance = float('inf')
            closest_idx = -1
            closest_line_idx = -1
            
            for i, line in enumerate(self.lines):
                if not line or len(line.get_xdata()) == 0:
                    continue
                    
                for j, (x, y) in enumerate(zip(line.get_xdata(), line.get_ydata())):
                    distance = np.sqrt((event.xdata - x) ** 2 + (event.ydata - y) ** 2)
                    if distance < closest_distance and distance < 3:  # Threshold for detection
                        closest_distance = distance
                        closest_line = line
                        closest_idx = j
                        closest_line_idx = i
            
            if closest_line is not None and closest_idx >= 0 and closest_line_idx >= 0:
                # Get device info 
                device_name = self.labels[closest_line_idx] if closest_line_idx < len(self.labels) else "Device"
                value = closest_line.get_ydata()[closest_idx]
                
                # Format tooltip text
                tooltip_text = f"Device: {device_name}\nTraffic: {value:.2f}"
                
                # Show tooltip
                self.tooltip.config(text=tooltip_text)
                self.tooltip.place(x=event.x + 15, y=event.y + 10)
                self.tooltip.lift()
                return
            
            # Hide tooltip if not over a point
            self.tooltip.place_forget()
    
    def on_leave(self, event):
        """Handle mouse leave event"""
        self.tooltip.place_forget()
    
    def _setup_plot(self):
        """Set up the initial plot"""
        # Add title
        self.ax.set_title(self.title, color=self.font_color, fontsize=12, pad=10)
        
        # X-axis format
        self.ax.xaxis.set_major_locator(MaxNLocator(10))
        
        # Labels
        self.ax.set_xlabel('Time', color=self.font_color, fontsize=10)
        self.ax.set_ylabel('Value', color=self.font_color, fontsize=10)
        
        # Remove top and right spines
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        # Set tick color
        self.ax.tick_params(axis='x', colors=self.font_color, labelsize=8)
        self.ax.tick_params(axis='y', colors=self.font_color, labelsize=8)
        
        # Set spine color
        self.ax.spines['bottom'].set_color(self.grid_color)
        self.ax.spines['left'].set_color(self.grid_color)
        
        # Adjust layout
        self.fig.tight_layout()
    
    def update_data(self, new_values, timestamp=None):
        """Update the chart with new data points"""
        if timestamp is None:
            timestamp = time.strftime('%H:%M')
        
        # Add new data
        self.timestamps.append(timestamp)
        for i, value in enumerate(new_values):
            if i < len(self.data):
                self.data[i].append(value)
        
        # Keep only the most recent 60 points
        max_points = 60
        if len(self.timestamps) > max_points:
            self.timestamps = self.timestamps[-max_points:]
            for i in range(len(self.data)):
                self.data[i] = self.data[i][-max_points:]
        
        # Clear previous plot
        self.ax.clear()
        self.lines = []
        
        # Setup plot again
        self._setup_plot()
        
        # Plot each line
        for i, values in enumerate(self.data):
            if i < len(self.colors) and values:
                line, = self.ax.plot(range(len(values)), values, 
                                    color=self.colors[i], 
                                    lw=self.line_width, 
                                    label=self.labels[i])
                self.lines.append(line)
        
        # Set x-axis ticks
        step = max(1, len(self.timestamps) // 10)
        ticks = range(0, len(self.timestamps), step)
        self.ax.set_xticks(ticks)
        self.ax.set_xticklabels([self.timestamps[i] for i in ticks], rotation=45)
        
        # Set y-axis limits
        all_values = [v for sublist in self.data for v in sublist if v is not None]
        if all_values:
            y_min = min(0, min(all_values) * 0.9)
            y_max = max(all_values) * 1.1
            self.ax.set_ylim(y_min, y_max)
        
        # Add legend
        if self.lines:
            self.ax.legend(loc='upper left', fontsize=8)
        
        # Draw the plot
        self.canvas.draw()

class MultiLineChart(LineChart):
    """Multi-line chart for memory usage display"""
    def __init__(self, parent, title, labels, colors, bg_color='#151515', grid_color='#333', 
                width=600, height=200, y_min=0, y_max=5, y_label='GB', font_color='white'):
        super().__init__(parent, title, labels, colors, bg_color, grid_color, width, height, 1.5, font_color)
        self.y_min = y_min
        self.y_max = y_max
        self.y_label = y_label
        
    def _setup_plot(self):
        """Override the setup_plot method to customize for memory display"""
        super()._setup_plot()
        self.ax.set_ylabel(self.y_label, color=self.font_color, fontsize=10)
        self.ax.set_ylim(self.y_min, self.y_max)
    
    def update_data(self, data_dict, timestamp=None):
        """Update with dictionary of named data series"""
        if timestamp is None:
            timestamp = time.strftime('%H:%M')
        
        # Extract values in the order of labels
        values = [data_dict.get(label, 0) for label in self.labels]
        super().update_data(values, timestamp)
        
        # Fixed y-axis
        self.ax.set_ylim(self.y_min, self.y_max)

class DiskIOChart(LineChart):
    """Special line chart for disk I/O with positive and negative values"""
    def __init__(self, parent, title, labels, colors, bg_color='#151515', grid_color='#333', 
                width=600, height=200, font_color='white'):
        super().__init__(parent, title, labels, colors, bg_color, grid_color, width, height, 1.5, font_color)
        
    def _setup_plot(self):
        """Override the setup_plot method to customize for disk I/O display"""
        super()._setup_plot()
        self.ax.set_ylabel("I/O", color=self.font_color, fontsize=10)
        # Allow for negative values
        self.ax.axhline(y=0, color=self.grid_color, linestyle='-', alpha=0.3)

class NetworkData:
    """Class for simulating network device data"""
    def __init__(self):
        # Data storage
        self.network_traffic = []
        self.system_load = []
        self.memory_usage = {
            'memory used': [],
            'memory buffers': [],
            'memory cached': [],
            'memory free': []
        }
        self.disk_io = []
        self.timestamps = []
        
        # Current metrics
        self.current_network = 25.0
        self.current_memory_percent = 68.0
        self.current_disk_percent = 13.33
        self.current_memory_gb = {
            'memory used': 3.1,
            'memory buffers': 0.8,
            'memory cached': 0.6,
            'memory free': 0.5
        }
        
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
            self.disk_io = self.disk_io[-60:]
            for key in self.memory_usage:
                self.memory_usage[key] = self.memory_usage[key][-60:]
        
        # Generate network traffic for each device
        network_values = []
        for device in self.devices:
            # Random traffic with occasional spikes
            base_traffic = random.uniform(5, 20)
            if random.random() < 0.1:  # 10% chance of spike
                # Create a traffic spike (unauthorized access)
                base_traffic *= 3
            
            # Store device traffic
            if len(device['traffic']) > 60:
                device['traffic'] = device['traffic'][-60:]
            device['traffic'].append(base_traffic)
            network_values.append(base_traffic)
        
        # Store overall network traffic
        self.network_traffic.append(network_values)
        
        # Update memory percent (wandering between 65-75%)
        self.current_memory_percent += (random.random() - 0.5) * 2
        self.current_memory_percent = max(65, min(75, self.current_memory_percent))
        
        # Update disk percent (wandering between 10-15%)
        self.current_disk_percent += (random.random() - 0.5)
        self.current_disk_percent = max(10, min(15, self.current_disk_percent))
        
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
        
        # Update memory usage (4 stacked lines)
        for key in self.memory_usage:
            # Small random fluctuations in each memory category
            self.current_memory_gb[key] += (random.random() - 0.5) * 0.05
            self.current_memory_gb[key] = max(0.1, min(4.0, self.current_memory_gb[key]))
            self.memory_usage[key].append(self.current_memory_gb[key])
        
        # Update disk I/O (fluctuating positive and negative)
        disk_io_value = (random.random() - 0.5) * 1.0  # Between -0.5 and 0.5
        self.disk_io.append(disk_io_value)
    
    def update(self):
        """Generate a new data point and return current metrics"""
        self._generate_next_data_point()
        
        # Extract latest network traffic for each device
        network_values = []
        for device in self.devices:
            network_values.append(device['traffic'][-1])
            
        return {
            'network_traffic': network_values,
            'memory_percent': self.current_memory_percent,
            'disk_percent': self.current_disk_percent,
            'network_history': self.network_traffic,
            'system_load': self.system_load[-1],
            'memory_usage': {k: v[-1] for k, v in self.memory_usage.items()},
            'disk_io': self.disk_io[-1],
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
        self.memory_chart = None
        self.memory_gauge = None
        self.disk_io_chart = None
        self.disk_gauge = None
        
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
        
        # CPU Usage chart (top left)
        self._create_cpu_chart()
        
        # System Load chart (top right)
        self._create_system_load_chart()
        
        # Memory Usage chart (middle left)
        self._create_memory_chart()
        
        # Memory Usage gauge (middle right)
        self._create_memory_gauge()
        
        # Disk I/O chart (bottom left)
        self._create_disk_io_chart()
        
        # Disk Space gauge (bottom right)
        self._create_disk_gauge()
    
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
    
    def _create_memory_chart(self):
        """Create the Memory Usage chart"""
        memory_frame = ttk.Frame(self.charts_frame, style='TFrame')
        memory_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(memory_frame, text="Memory Usage", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.memory_chart = MultiLineChart(
            memory_frame,
            "Memory Usage",
            ["memory used", "memory buffers", "memory cached", "memory free"],
            self.memory_colors,
            bg_color=self.colors['chart_bg'],
            grid_color=self.colors['grid'],
            width=750,
            height=200,
            y_min=0,
            y_max=5,
            y_label="GB",
            font_color=self.colors['text']
        )
        self.memory_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_memory_gauge(self):
        """Create Memory Usage gauge"""
        memory_gauge_frame = ttk.Frame(self.charts_frame, style='TFrame')
        memory_gauge_frame.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(memory_gauge_frame, text="Memory Usage", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create gauge
        self.memory_gauge = GaugeChart(
            memory_gauge_frame,
            bg_color=self.colors['chart_bg'],
            color=self.colors['green'],
            width=300,
            height=250,
            font_color=self.colors['text']
        )
        self.memory_gauge.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_disk_io_chart(self):
        """Create the Disk I/O chart"""
        disk_frame = ttk.Frame(self.charts_frame, style='TFrame')
        disk_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(disk_frame, text="Disk I/O", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.disk_io_chart = DiskIOChart(
            disk_frame,
            "Disk I/O",
            ["io time"],
            self.disk_colors,
            bg_color=self.colors['chart_bg'],
            grid_color=self.colors['grid'],
            width=750,
            height=200,
            font_color=self.colors['text']
        )
        self.disk_io_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_disk_gauge(self):
        """Create Disk Space Usage gauge"""
        disk_gauge_frame = ttk.Frame(self.charts_frame, style='TFrame')
        disk_gauge_frame.grid(row=2, column=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(disk_gauge_frame, text="Disk Space Usage", style='Title.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create gauge
        self.disk_gauge = GaugeChart(
            disk_gauge_frame,
            bg_color=self.colors['chart_bg'],
            color=self.colors['green'],
            width=300,
            height=250,
            font_color=self.colors['text']
        )
        self.disk_gauge.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_ui(self):
        """Update the UI with the latest data"""
        if self.running:
            # Get the latest data
            data = self.node_data.update()
            
            # Update Network Traffic chart (all 7 devices)
            self.cpu_chart.update_data(data['network_traffic'], data['timestamp'])
            
            # Update System Load chart with 3 values
            self.system_load_chart.update_data(data['system_load'], data['timestamp'])
            
            # Update Memory charts
            self.memory_chart.update_data(data['memory_usage'], data['timestamp'])
            self.memory_gauge.update_data(data['memory_percent'])
            
            # Update Disk charts
            self.disk_io_chart.update_data([data['disk_io']], data['timestamp'])
            self.disk_gauge.update_data(data['disk_percent'])
        
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