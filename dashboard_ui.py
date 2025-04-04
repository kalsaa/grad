#!/usr/bin/env python3
"""
Dashboard UI Module
Handles the UI components and layout for the network monitoring dashboard
"""

import tkinter as tk
from tkinter import ttk
import time
import datetime
import chart_components

class DashboardUI:
    """Class to handle the UI components of the network dashboard"""
    def __init__(self, root, analyzer):
        self.root = root
        self.analyzer = analyzer
        
        # UI components
        self.main_frame = None
        self.header_frame = None
        self.charts_frame = None
        self.status_bar = None
        
        # Chart components
        self.traffic_chart = None
        self.memory_chart = None
        self.auth_pie_chart = None
        self.unauth_pie_chart = None
        self.bottom_chart = None
        
        # Colors for the UI
        self.colors = {
            'bg': '#1e1e1e',
            'header_bg': '#252526',
            'text': '#e0e0e0',
            'highlight': '#0078d7',
            'chart_bg': '#252526',
            'authorized': '#4caf50',  # Green
            'unauthorized': '#f44336',  # Red
            'device_colors': [
                '#4caf50',  # Green
                '#2196f3',  # Blue
                '#ff9800',  # Orange
                '#e91e63',  # Pink
                '#9c27b0',  # Purple
                '#00bcd4',  # Cyan
                '#ffeb3b',  # Yellow
            ]
        }
        
        # Styles for the UI
        self.style = ttk.Style()
        self._setup_styles()
    
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
                            font=('Segoe UI', 12, 'bold'))
        self.style.configure('Status.TLabel', 
                            background=self.colors['header_bg'], 
                            foreground=self.colors['text'],
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
        
        # Create status bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create the header section of the UI"""
        self.header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        self.header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Title
        header_label = ttk.Label(self.header_frame, 
                                text="Network Monitoring Dashboard", 
                                style='Header.TLabel')
        header_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Time label
        self.time_label = ttk.Label(self.header_frame, 
                                   text=self._get_current_time(), 
                                   style='Header.TLabel')
        self.time_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Update time every second
        self._update_time()
    
    def _create_charts_area(self):
        """Create the area for charts and visualizations"""
        self.charts_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid
        self.charts_frame.columnconfigure(0, weight=2)
        self.charts_frame.columnconfigure(1, weight=1)
        self.charts_frame.rowconfigure(0, weight=2)
        self.charts_frame.rowconfigure(1, weight=1)
        self.charts_frame.rowconfigure(2, weight=1)
        
        # Create traffic chart (top left)
        self._create_traffic_chart()
        
        # Create auth charts (top right)
        self._create_auth_charts()
        
        # Create memory usage chart (middle)
        self._create_memory_chart()
        
        # Create bottom chart
        self._create_bottom_chart()
    
    def _create_traffic_chart(self):
        """Create the main traffic visualization chart"""
        traffic_frame = ttk.Frame(self.charts_frame, style='TFrame')
        traffic_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(traffic_frame, text="Live Traffic", style='Header.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.traffic_chart = chart_components.LineChart(
            traffic_frame,
            self.colors,
            bg_color=self.colors['chart_bg'],
            width=600,
            height=300
        )
        self.traffic_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_auth_charts(self):
        """Create the authorization pie charts (top right)"""
        auth_frame = ttk.Frame(self.charts_frame, style='TFrame')
        auth_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Configure grid
        auth_frame.columnconfigure(0, weight=1)
        auth_frame.rowconfigure(0, weight=1)
        auth_frame.rowconfigure(1, weight=1)
        
        # Unauthorized access pie chart
        unauth_frame = ttk.Frame(auth_frame, style='TFrame')
        unauth_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        unauth_label = ttk.Label(unauth_frame, text="System Usage", style='Header.TLabel')
        unauth_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        self.unauth_pie_chart = chart_components.GaugeChart(
            unauth_frame,
            title="System Load",
            max_value=100,
            bg_color=self.colors['chart_bg'],
            color=self.colors['unauthorized'],
            width=250,
            height=150
        )
        self.unauth_pie_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Authorized access pie chart
        auth_frame = ttk.Frame(auth_frame, style='TFrame')
        auth_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        auth_label = ttk.Label(auth_frame, text="CPU Usage", style='Header.TLabel')
        auth_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        self.auth_pie_chart = chart_components.GaugeChart(
            auth_frame,
            title="CPU Usage",
            max_value=100,
            bg_color=self.colors['chart_bg'],
            color="#ff9800",  # Orange
            width=250,
            height=150
        )
        self.auth_pie_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_memory_chart(self):
        """Create the memory usage chart (middle)"""
        memory_frame = ttk.Frame(self.charts_frame, style='TFrame')
        memory_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(memory_frame, text="Memory Usage", style='Header.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.memory_chart = chart_components.BarChart(
            memory_frame,
            self.colors,
            bg_color=self.colors['chart_bg'],
            width=900,
            height=150
        )
        self.memory_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_bottom_chart(self):
        """Create the bottom chart"""
        bottom_frame = ttk.Frame(self.charts_frame, style='TFrame')
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(bottom_frame, text="Network Load", style='Header.TLabel')
        title_label.pack(anchor=tk.NW, padx=5, pady=5)
        
        # Create chart
        self.bottom_chart = chart_components.MultiLineChart(
            bottom_frame,
            self.colors,
            bg_color=self.colors['chart_bg'],
            width=900,
            height=150
        )
        self.bottom_chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_status_bar(self):
        """Create the status bar at the bottom of the UI"""
        status_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)
        
        self.status_bar = ttk.Label(status_frame, 
                                  text="Ready", 
                                  style='Status.TLabel')
        self.status_bar.pack(side=tk.LEFT, padx=10, pady=3)
        
        # Device status indicators
        self.device_indicators = {}
        for i, (ip, device) in enumerate(self.analyzer.get_all_devices().items()):
            color = self.colors['device_colors'][i % len(self.colors['device_colors'])]
            indicator = ttk.Label(status_frame, 
                                text=f"{device.name}: Online", 
                                foreground=color,
                                style='Status.TLabel')
            indicator.pack(side=tk.LEFT, padx=10, pady=3)
            self.device_indicators[ip] = indicator
    
    def update_status(self, message):
        """Update the status message in the status bar"""
        self.status_bar.config(text=message)
    
    def _update_time(self):
        """Update the time display in the header"""
        self.time_label.config(text=self._get_current_time())
        self.root.after(1000, self._update_time)
    
    def _get_current_time(self):
        """Get the current formatted time string"""
        return datetime.datetime.now().strftime("%H:%M:%S | %Y-%m-%d")
    
    def update_all_charts(self):
        """Update all charts with the latest data"""
        # Update traffic chart
        devices = self.analyzer.get_all_devices()
        device_data = []
        
        for i, (ip, device) in enumerate(devices.items()):
            times, values, auth = device.get_traffic_data()
            color = self.colors['device_colors'][i % len(self.colors['device_colors'])]
            
            device_data.append({
                'ip': ip,
                'name': device.name,
                'times': times,
                'values': values,
                'auth': auth,
                'color': color
            })
            
            # Update device status indicators
            if ip in self.device_indicators:
                auth_status = "Auth" if auth[-1] else "Unauth"
                self.device_indicators[ip].config(
                    text=f"{device.name}: {auth_status}",
                    foreground=color
                )
        
        self.traffic_chart.update_data(device_data)
        
        # Update pie charts
        self.unauth_pie_chart.update_data(self.analyzer.get_system_load())
        self.auth_pie_chart.update_data(self.analyzer.get_cpu_usage())
        
        # Update memory chart
        memory_data = self.analyzer.get_memory_usage()
        time_labels = [f"{h:02d}:00" for h in range(24)]
        self.memory_chart.update_data(memory_data, time_labels)
        
        # Update bottom chart
        self.bottom_chart.update_data(device_data)
