#!/usr/bin/env python3
"""
Network Monitoring Dashboard
Main application entry point that integrates the network analyzer with the UI components
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import threading
import time
import dashboard_ui
import network_analyzer

def check_privileges():
    """Check if the application has the necessary privileges to capture packets"""
    if os.name != 'nt':  # Unix/Linux/Mac
        if os.geteuid() != 0:
            return False
    else:  # Windows
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            return False
    return True

class NetworkDashboard:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.capture_thread = None
        self.analyzer = network_analyzer.NetworkAnalyzer()
        self.ui = dashboard_ui.DashboardUI(root, self.analyzer)
        
        # Configure main window
        root.title("Network Monitoring Dashboard")
        root.geometry("1200x800")
        root.minsize(1000, 700)
        root.configure(bg="#1e1e1e")
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize the UI
        self.ui.setup_ui()
        
        # Start the update loop for UI
        self.update_ui()
        
    def start_network_capture(self):
        """Start the network packet capture in a separate thread"""
        if not self.running:
            self.running = True
            # Use the simulate_traffic method instead of real packet capture
            self.capture_thread = threading.Thread(target=self.analyzer.simulate_traffic)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            self.ui.update_status("Network monitoring started")
    
    def stop_network_capture(self):
        """Stop the network packet capture"""
        if self.running:
            self.running = False
            self.analyzer.stop_capture()
            if self.capture_thread:
                self.capture_thread.join(timeout=1.0)
            self.ui.update_status("Capture stopped")
    
    def update_ui(self):
        """Update the UI with the latest network data"""
        if self.running:
            # Update the UI components with the latest data
            self.ui.update_all_charts()
        
        # Schedule the next update
        self.root.after(1000, self.update_ui)
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.stop_network_capture()
            self.root.destroy()
            sys.exit(0)

def main():
    # Commenting privilege check since we're using simulated data
    # if not check_privileges():
    #     print("Warning: This application requires administrator/root privileges to capture packets.")
    #     print("Please restart the application with appropriate privileges.")
    #     messagebox.showerror("Insufficient Privileges", 
    #                          "This application requires administrator/root privileges to capture packets.\n"
    #                          "Please restart the application with appropriate privileges.")
    #     sys.exit(1)
    
    # Create the main application window
    root = tk.Tk()
    app = NetworkDashboard(root)
    
    # Start monitoring simulated network traffic
    app.start_network_capture()
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
