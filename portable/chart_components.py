#!/usr/bin/env python3
"""
Chart Components Module
Contains classes for different chart types used in the dashboard
"""

import tkinter as tk
import time
import numpy as np
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.ticker import MaxNLocator
import matplotlib

# Use TkAgg backend for matplotlib
matplotlib.use("TkAgg")

class LineChart:
    """Line chart for visualizing network traffic over time"""
    def __init__(self, parent, colors, bg_color='#252526', width=600, height=300):
        self.parent = parent
        self.colors = colors
        self.bg_color = bg_color
        self.width = width
        self.height = height
        
        # Create figure and axes
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Configure axes
        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)
        
        # Add grid
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.config(width=width, height=height)
        
        # Initialize empty plot
        self.lines = []
        self.device_data = []
        
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
    
    def _setup_plot(self):
        """Set up the initial plot"""
        # X-axis format as time
        self.ax.xaxis.set_major_locator(MaxNLocator(10))
        
        # Y-axis range
        self.ax.set_ylim(0, 20)
        
        # Labels
        self.ax.set_xlabel('Time', color='white')
        self.ax.set_ylabel('Traffic', color='white')
        
        # Remove top and right spines
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        # Set tick color
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        # Set spine color
        self.ax.spines['bottom'].set_color('#555555')
        self.ax.spines['left'].set_color('#555555')
        
        # Adjust layout
        self.fig.tight_layout()
    
    def update_data(self, device_data):
        """Update the chart with new data"""
        self.device_data = device_data
        
        # Clear previous plot
        self.ax.clear()
        self.lines = []
        
        # Setup plot again
        self._setup_plot()
        
        # Current time for x-axis reference
        current_time = time.time()
        
        # Plot each device's data
        for i, data in enumerate(device_data):
            color = data['color']
            times = data['times']
            values = data['values']
            auth = data['auth']
            
            # Convert to relative time (seconds ago)
            rel_times = [(current_time - t) for t in times]
            
            # Sort by time
            sorted_data = sorted(zip(rel_times, values, auth))
            rel_times = [t for t, _, _ in sorted_data]
            values = [v for _, v, _ in sorted_data]
            auth = [a for _, _, a in sorted_data]
            
            # Convert to positive x-values (time ago in seconds)
            x_values = [-t for t in rel_times]
            
            # Create the line
            line, = self.ax.plot(x_values, values, color=color, lw=2, label=data['name'])
            
            # Add red markers for unauthorized points
            unauth_x = [x for x, a in zip(x_values, auth) if not a]
            unauth_y = [v for v, a in zip(values, auth) if not a]
            self.ax.scatter(unauth_x, unauth_y, color='red', s=40, zorder=3, marker='x')
            
            # Store the line
            self.lines.append(line)
        
        # Set x-axis limits to show the last 60 seconds
        self.ax.set_xlim([-60, 0])
        
        # Format x-axis ticks
        self.ax.set_xticks([-50, -40, -30, -20, -10, 0])
        self.ax.set_xticklabels(['50s', '40s', '30s', '20s', '10s', 'now'])
        
        # Add legend
        self.ax.legend(loc='upper right', framealpha=0.7)
        
        # Draw the plot
        self.canvas.draw()
    
    def on_hover(self, event):
        """Handle mouse hover event"""
        if event.inaxes == self.ax:
            # Find the closest point for each line
            closest_line = None
            closest_distance = float('inf')
            closest_idx = -1
            closest_line_idx = -1
            
            for i, line in enumerate(self.lines):
                for j, (x, y) in enumerate(zip(line.get_xdata(), line.get_ydata())):
                    distance = np.sqrt((event.xdata - x) ** 2 + (event.ydata - y) ** 2)
                    if distance < closest_distance and distance < 3:  # Threshold for detection
                        closest_distance = distance
                        closest_line = line
                        closest_idx = j
                        closest_line_idx = i
            
            if closest_line is not None:
                # Get device data
                device = self.device_data[closest_line_idx]
                
                # Get the time for the closest point
                times = device['times']
                values = device['values']
                auth = device['auth']
                
                # Get point info
                if 0 <= closest_idx < len(times):
                    point_time = times[closest_idx]
                    point_value = values[closest_idx]
                    is_auth = auth[closest_idx]
                    
                    # Format time
                    time_str = time.strftime('%H:%M:%S', time.localtime(point_time))
                    
                    # Format tooltip text
                    status = "Authorized" if is_auth else "UNAUTHORIZED"
                    tooltip_text = f"Device: {device['name']}\nIP: {device['ip']}\n"
                    if hasattr(self.device_data[closest_line_idx], 'last_dst_ip'):
                        dst_ip = self.device_data[closest_line_idx].last_dst_ip
                        protocol = self.device_data[closest_line_idx].last_protocol
                        tooltip_text += f"Dest IP: {dst_ip}\nProtocol: {protocol}\n"
                    tooltip_text += f"Traffic: {point_value:.2f}\nStatus: {status}\nTime: {time_str}"
                    
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
    
    def pack(self, **kwargs):
        """Pack the chart widget"""
        self.canvas_widget.pack(**kwargs)


class GaugeChart:
    """Gauge chart for displaying percentage metrics"""
    def __init__(self, parent, title="", max_value=100, bg_color='#252526', color='#4caf50', width=300, height=300):
        self.parent = parent
        self.title = title
        self.max_value = max_value
        self.bg_color = bg_color
        self.color = color
        self.width = width
        self.height = height
        self.value = 0
        
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
        start_angle = 130  # Degrees
        end_angle = 410    # Degrees (50 + 360 = 410, full circle + 50 degrees)
        value_angle = start_angle + (end_angle - start_angle) * (percentage / 100)
        
        # Draw background arc
        self.ax.add_patch(Wedge((0, 0), 0.8, start_angle, end_angle, width=0.2, 
                                 facecolor='#333333', edgecolor=None, alpha=0.5))
        
        # Draw value arc
        if percentage > 0:
            # Choose color based on value
            if percentage < 50:
                arc_color = self.color
            elif percentage < 80:
                arc_color = '#ff9800'  # Orange for medium
            else:
                arc_color = '#f44336'  # Red for high
                
            self.ax.add_patch(Wedge((0, 0), 0.8, start_angle, value_angle, width=0.2, 
                                    facecolor=arc_color, edgecolor=None))
        
        # Add value text
        self.ax.text(0, 0, f"{percentage:.1f}%", ha='center', va='center', 
                    fontsize=14, fontweight='bold', color='white')
        
        # Add title
        if self.title:
            self.ax.text(0, -0.5, self.title, ha='center', va='center', 
                        fontsize=10, color='#bbbbbb')
        
        # Set limits
        self.ax.set_ylim(0, 1)
        
        # Draw the plot
        self.canvas.draw()
    
    def pack(self, **kwargs):
        """Pack the chart widget"""
        self.canvas_widget.pack(**kwargs)


class PieChart:
    """Pie chart for displaying authorized/unauthorized access percentages"""
    def __init__(self, parent, title="", bg_color='#252526', color='#4caf50', width=300, height=300):
        self.parent = parent
        self.title = title
        self.bg_color = bg_color
        self.color = color  # Main color for the pie slice
        self.width = width
        self.height = height
        self.percentage = 0
        
        # Create figure and axes
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Configure figure
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        
        # Hide axis
        self.ax.axis('off')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.config(width=width, height=height)
        
        # Initial plot
        self.update_data(0)
        
        # Pack the canvas
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    def update_data(self, percentage):
        """Update the chart with a new percentage value"""
        self.percentage = min(percentage, 100)
        
        # Clear the axes
        self.ax.clear()
        self.ax.axis('off')
        
        # Create data for pie chart
        values = [self.percentage, 100 - self.percentage]
        labels = [f"{self.percentage:.1f}%", f"{100 - self.percentage:.1f}%"]
        colors = [self.color, '#333333']  # Main color and background color
        
        # Draw pie chart
        wedges, texts = self.ax.pie(
            values, 
            labels=None,  # No labels on the chart itself
            colors=colors,
            startangle=90,
            wedgeprops={'edgecolor': self.bg_color, 'linewidth': 1}
        )
        
        # Add percentage text in the center
        self.ax.text(0, 0, f"{self.percentage:.1f}%", ha='center', va='center', 
                     fontsize=14, fontweight='bold', color='white')
        
        # Add title
        if self.title:
            self.ax.set_title(self.title, color='white', fontsize=10, pad=10)
        
        # Draw the plot
        self.canvas.draw()
    
    def pack(self, **kwargs):
        """Pack the chart widget"""
        self.canvas_widget.pack(**kwargs)


class BarChart:
    """Bar chart for displaying memory usage by hour"""
    def __init__(self, parent, colors, bg_color='#252526', width=900, height=200):
        self.parent = parent
        self.colors = colors
        self.bg_color = bg_color
        self.width = width
        self.height = height
        
        # Create figure and axes
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Configure axes
        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.config(width=width, height=height)
        
        # Initialize empty bar plot
        self.bars = None
        self.data = [0] * 24
        self.labels = [f"{h:02d}" for h in range(24)]
        
        # Initial plot setup
        self._setup_plot()
        
        # Pack the canvas
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    def _setup_plot(self):
        """Set up the initial plot"""
        # Labels
        self.ax.set_xlabel('Hour', color='white', fontsize=9)
        self.ax.set_ylabel('Usage %', color='white', fontsize=9)
        
        # Remove top and right spines
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        # Set tick color
        self.ax.tick_params(axis='x', colors='white', labelsize=8)
        self.ax.tick_params(axis='y', colors='white', labelsize=8)
        
        # Set spine color
        self.ax.spines['bottom'].set_color('#555555')
        self.ax.spines['left'].set_color('#555555')
        
        # Y-axis range
        self.ax.set_ylim(0, 100)
        
        # Adjust layout
        self.fig.tight_layout()
    
    def update_data(self, data, labels=None):
        """Update the chart with new data"""
        self.data = data
        if labels:
            self.labels = labels
        
        # Clear previous plot
        self.ax.clear()
        
        # Setup plot again
        self._setup_plot()
        
        # Set x-axis labels
        self.ax.set_xticks(range(len(self.labels)))
        self.ax.set_xticklabels(self.labels, rotation=45, ha='right')
        
        # Create bar colors based on value
        colors = []
        for value in self.data:
            if value < 50:
                colors.append('#4caf50')  # Green for low
            elif value < 80:
                colors.append('#ff9800')  # Orange for medium
            else:
                colors.append('#f44336')  # Red for high
        
        # Create the bars
        self.bars = self.ax.bar(range(len(self.data)), self.data, color=colors, alpha=0.7, width=0.8)
        
        # Add value labels on top of bars
        for i, v in enumerate(self.data):
            if v > 0:  # Only show labels for non-zero values
                self.ax.text(i, v + 2, f"{v:.0f}", ha='center', va='bottom', fontsize=8, color='white')
        
        # Draw the plot
        self.canvas.draw()
    
    def pack(self, **kwargs):
        """Pack the chart widget"""
        self.canvas_widget.pack(**kwargs)


class MultiLineChart:
    """Multi-line chart for displaying network load over time"""
    def __init__(self, parent, colors, bg_color='#252526', width=900, height=200):
        self.parent = parent
        self.colors = colors
        self.bg_color = bg_color
        self.width = width
        self.height = height
        
        # Create figure and axes
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Configure axes
        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)
        
        # Add grid
        self.ax.grid(True, linestyle='--', alpha=0.3)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.config(width=width, height=height)
        
        # Initialize empty plot
        self.lines = []
        self.device_data = []
        
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
    
    def _setup_plot(self):
        """Set up the initial plot"""
        # X-axis format
        self.ax.xaxis.set_major_locator(MaxNLocator(10))
        
        # Y-axis range
        self.ax.set_ylim(0, 20)
        
        # Labels
        self.ax.set_xlabel('Time', color='white', fontsize=9)
        self.ax.set_ylabel('Network Load', color='white', fontsize=9)
        
        # Remove top and right spines
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        # Set tick color
        self.ax.tick_params(axis='x', colors='white', labelsize=8)
        self.ax.tick_params(axis='y', colors='white', labelsize=8)
        
        # Set spine color
        self.ax.spines['bottom'].set_color('#555555')
        self.ax.spines['left'].set_color('#555555')
        
        # Adjust layout
        self.fig.tight_layout()
    
    def update_data(self, device_data):
        """Update the chart with new data"""
        self.device_data = device_data
        
        # Clear previous plot
        self.ax.clear()
        self.lines = []
        
        # Setup plot again
        self._setup_plot()
        
        # Current time for x-axis reference
        current_time = time.time()
        
        # Plot each device's data
        for i, data in enumerate(device_data):
            color = data['color']
            times = data['times']
            values = data['values']
            
            # Compute moving average
            avg_values = self._compute_moving_average(values, 5)
            
            # Convert to relative time (seconds ago)
            rel_times = [(current_time - t) for t in times]
            
            # Sort by time
            sorted_data = sorted(zip(rel_times, avg_values))
            rel_times = [t for t, _ in sorted_data]
            avg_values = [v for _, v in sorted_data]
            
            # Convert to positive x-values (time ago in seconds)
            x_values = [-t for t in rel_times]
            
            # Create the line with smaller line width
            line, = self.ax.plot(x_values, avg_values, color=color, lw=1.5, label=data['name'])
            
            # Store the line
            self.lines.append(line)
        
        # Set x-axis limits to show the last 60 seconds
        self.ax.set_xlim([-60, 0])
        
        # Format x-axis ticks
        self.ax.set_xticks([-50, -40, -30, -20, -10, 0])
        self.ax.set_xticklabels(['50s', '40s', '30s', '20s', '10s', 'now'])
        
        # Add legend
        self.ax.legend(loc='upper right', framealpha=0.7, fontsize=8)
        
        # Draw the plot
        self.canvas.draw()
    
    def _compute_moving_average(self, values, window_size):
        """Compute moving average of values"""
        if not values:
            return []
        if window_size <= 1:
            return values
        
        result = []
        for i in range(len(values)):
            start = max(0, i - window_size // 2)
            end = min(len(values), i + window_size // 2 + 1)
            window = values[start:end]
            result.append(sum(window) / len(window))
        
        return result
    
    def on_hover(self, event):
        """Handle mouse hover event"""
        if event.inaxes == self.ax:
            # Find the closest point for each line
            closest_line = None
            closest_distance = float('inf')
            closest_idx = -1
            closest_line_idx = -1
            
            for i, line in enumerate(self.lines):
                for j, (x, y) in enumerate(zip(line.get_xdata(), line.get_ydata())):
                    distance = np.sqrt((event.xdata - x) ** 2 + (event.ydata - y) ** 2)
                    if distance < closest_distance and distance < 5:  # Larger threshold for easier detection
                        closest_distance = distance
                        closest_line = line
                        closest_idx = j
                        closest_line_idx = i
            
            if closest_line is not None:
                # Get device data
                device = self.device_data[closest_line_idx]
                
                # Format tooltip text
                tooltip_text = f"Device: {device['name']}\nIP: {device['ip']}\nLoad: {closest_line.get_ydata()[closest_idx]:.2f}"
                
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
    
    def pack(self, **kwargs):
        """Pack the chart widget"""
        self.canvas_widget.pack(**kwargs)
