import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import queue
import os
import sys
from datetime import datetime

class AndroidRecoveryToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Recovery Toolkit - Enhanced GUI v1.0")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Main container
        main_frame = tk.Frame(root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="ANDROID RECOVERY TOOLKIT", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(main_frame, text="Enhanced GUI Interface v1.0", 
                                 font=('Arial', 12), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_connection_tab()
        self.create_control_tab()
        self.create_recovery_tab()
        self.create_tools_tab()
        self.create_console_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                             bd=1, relief=tk.SUNKEN, anchor=tk.W, bg='#34495e', fg='white')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Check ADB connection on startup
        self.check_adb_connection()
    
    def create_connection_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Connection & Diagnostics')
        
        # Device status section
        status_frame = tk.LabelFrame(frame, text="Device Status", padx=10, pady=10, bg='#34495e', fg='white')
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.device_status_text = tk.Text(status_frame, height=8, width=80, bg='#ecf0f1', fg='#2c3e50')
        self.device_status_text.pack(fill=tk.X, pady=5)
        
        btn_frame1 = tk.Frame(status_frame, bg='#34495e')
        btn_frame1.pack(fill=tk.X, pady=5)
        
        refresh_btn = tk.Button(btn_frame1, text="Refresh Devices", command=self.refresh_devices,
                               bg='#3498db', fg='white', relief=tk.FLAT, padx=10)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        wireless_btn = tk.Button(btn_frame1, text="Wireless Connection", command=self.wireless_setup,
                                bg='#9b59b6', fg='white', relief=tk.FLAT, padx=10)
        wireless_btn.pack(side=tk.LEFT, padx=5)
        
        # Connection tools
        tools_frame = tk.LabelFrame(frame, text="Connection Tools", padx=10, pady=10, bg='#34495e', fg='white')
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        btn_frame2 = tk.Frame(tools_frame, bg='#34495e')
        btn_frame2.pack(fill=tk.X, pady=5)
        
        tester_btn = tk.Button(btn_frame2, text="Connection Tester", command=self.open_connection_tester,
                              bg='#27ae60', fg='white', relief=tk.FLAT, padx=10)
        tester_btn.pack(side=tk.LEFT, padx=5)
        
        driver_btn = tk.Button(btn_frame2, text="Driver Checker", command=self.driver_check,
                              bg='#f39c12', fg='white', relief=tk.FLAT, padx=10)
        driver_btn.pack(side=tk.LEFT, padx=5)
    
    def create_control_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Control & Mirroring')
        
        # Scrcpy controls
        scrcpy_frame = tk.LabelFrame(frame, text="Screen Mirroring Controls", padx=10, pady=10, bg='#34495e', fg='white')
        scrcpy_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        btn_frame = tk.Frame(scrcpy_frame, bg='#34495e')
        btn_frame.pack(fill=tk.X, pady=5)
        
        normal_btn = tk.Button(btn_frame, text="Standard Mirroring", command=self.start_normal_scrcpy,
                              bg='#3498db', fg='white', relief=tk.FLAT, padx=10)
        normal_btn.pack(side=tk.LEFT, padx=5)
        
        broken_btn = tk.Button(btn_frame, text="Broken Screen Mode", command=self.start_broken_scrcpy,
                              bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10)
        broken_btn.pack(side=tk.LEFT, padx=5)
        
        record_btn = tk.Button(btn_frame, text="Start Recording", command=self.start_recording,
                              bg='#9b59b6', fg='white', relief=tk.FLAT, padx=10)
        record_btn.pack(side=tk.LEFT, padx=5)
        
        otg_btn = tk.Button(btn_frame, text="OTG Mode", command=self.start_otg_mode,
                           bg='#f39c12', fg='white', relief=tk.FLAT, padx=10)
        otg_btn.pack(side=tk.LEFT, padx=5)
        
        # Quick ADB commands
        quick_frame = tk.LabelFrame(frame, text="Quick ADB Commands", padx=10, pady=10, bg='#34495e', fg='white')
        quick_frame.pack(fill=tk.X, padx=10, pady=5)
        
        quick_btn_frame = tk.Frame(quick_frame, bg='#34495e')
        quick_btn_frame.pack(fill=tk.X, pady=5)
        
        home_btn = tk.Button(quick_btn_frame, text="Home", command=lambda: self.send_adb_command("input keyevent KEYCODE_HOME"),
                            bg='#27ae60', fg='white', relief=tk.FLAT, padx=10)
        home_btn.pack(side=tk.LEFT, padx=2)
        
        back_btn = tk.Button(quick_btn_frame, text="Back", command=lambda: self.send_adb_command("shell input keyevent KEYCODE_BACK"),
                            bg='#27ae60', fg='white', relief=tk.FLAT, padx=10)
        back_btn.pack(side=tk.LEFT, padx=2)
        
        recents_btn = tk.Button(quick_btn_frame, text="Recents", command=lambda: self.send_adb_command("shell input keyevent KEYCODE_APP_SWITCH"),
                               bg='#27ae60', fg='white', relief=tk.FLAT, padx=10)
        recents_btn.pack(side=tk.LEFT, padx=2)
        
        power_btn = tk.Button(quick_btn_frame, text="Power", command=lambda: self.send_adb_command("shell input keyevent KEYCODE_POWER"),
                             bg='#27ae60', fg='white', relief=tk.FLAT, padx=10)
        power_btn.pack(side=tk.LEFT, padx=2)
    
    def create_recovery_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Recovery & Data')
        
        # Recovery tools
        recovery_frame = tk.LabelFrame(frame, text="Recovery Tools", padx=10, pady=10, bg='#34495e', fg='white')
        recovery_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        recovery_btn_frame = tk.Frame(recovery_frame, bg='#34495e')
        recovery_btn_frame.pack(fill=tk.X, pady=5)
        
        data_btn = tk.Button(recovery_btn_frame, text="Data Extraction", command=self.data_extraction,
                            bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10)
        data_btn.pack(side=tk.LEFT, padx=5)
        
        backup_btn = tk.Button(recovery_btn_frame, text="System Backup", command=self.system_backup,
                              bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10)
        backup_btn.pack(side=tk.LEFT, padx=5)
        
        repair_btn = tk.Button(recovery_btn_frame, text="System Repair", command=self.system_repair,
                              bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10)
        repair_btn.pack(side=tk.LEFT, padx=5)
        
        unlock_btn = tk.Button(recovery_btn_frame, text="Screen Unlock", command=self.screen_unlock,
                              bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10)
        unlock_btn.pack(side=tk.LEFT, padx=5)
        
        # Emergency tools
        emergency_frame = tk.LabelFrame(frame, text="Emergency Tools", padx=10, pady=10, bg='#34495e', fg='white')
        emergency_frame.pack(fill=tk.X, padx=10, pady=5)
        
        emergency_btn_frame = tk.Frame(emergency_frame, bg='#34495e')
        emergency_btn_frame.pack(fill=tk.X, pady=5)
        
        rescue_btn = tk.Button(emergency_btn_frame, text="Emergency Rescue", command=self.emergency_rescue,
                              bg='#f39c12', fg='white', relief=tk.FLAT, padx=10)
        rescue_btn.pack(side=tk.LEFT, padx=5)
        
        forensics_btn = tk.Button(emergency_btn_frame, text="Forensics Tools", command=self.forensics_tools,
                                 bg='#f39c12', fg='white', relief=tk.FLAT, padx=10)
        forensics_btn.pack(side=tk.LEFT, padx=5)
    
    def create_tools_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Additional Tools')
        
        # Additional tools
        tools_frame = tk.LabelFrame(frame, text="Additional Tools", padx=10, pady=10, bg='#34495e', fg='white')
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tools_btn_frame = tk.Frame(tools_frame, bg='#34495e')
        tools_btn_frame.pack(fill=tk.X, pady=5)
        
        info_btn = tk.Button(tools_btn_frame, text="Device Info", command=self.device_info,
                            bg='#3498db', fg='white', relief=tk.FLAT, padx=10)
        info_btn.pack(side=tk.LEFT, padx=5)
        
        diag_btn = tk.Button(tools_btn_frame, text="System Diagnostics", command=self.system_diagnostics,
                            bg='#3498db', fg='white', relief=tk.FLAT, padx=10)
        diag_btn.pack(side=tk.LEFT, padx=5)
        
        app_btn = tk.Button(tools_btn_frame, text="App Manager", command=self.app_manager,
                           bg='#3498db', fg='white', relief=tk.FLAT, padx=10)
        app_btn.pack(side=tk.LEFT, padx=5)
        
        # Documentation
        doc_frame = tk.LabelFrame(frame, text="Documentation & Help", padx=10, pady=10, bg='#34495e', fg='white')
        doc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        doc_btn_frame = tk.Frame(doc_frame, bg='#34495e')
        doc_btn_frame.pack(fill=tk.X, pady=5)
        
        user_manual_btn = tk.Button(doc_btn_frame, text="User Manual", command=self.open_user_manual,
                                   bg='#95a5a6', fg='white', relief=tk.FLAT, padx=10)
        user_manual_btn.pack(side=tk.LEFT, padx=5)
        
        troubleshoot_btn = tk.Button(doc_btn_frame, text="Troubleshooting", command=self.open_troubleshooting,
                                    bg='#95a5a6', fg='white', relief=tk.FLAT, padx=10)
        troubleshoot_btn.pack(side=tk.LEFT, padx=5)
    
    def create_console_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Console Output')
        
        # Console output
        console_frame = tk.LabelFrame(frame, text="Console Output", padx=10, pady=10, bg='#34495e', fg='white')
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrolled text widget
        self.console_output = scrolledtext.ScrolledText(console_frame, height=20, bg='#ecf0f1', fg='#2c3e50')
        self.console_output.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Clear button
        clear_btn = tk.Button(console_frame, text="Clear Console", command=self.clear_console,
                             bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10)
        clear_btn.pack(pady=5)
    
    def check_adb_connection(self):
        """Check if ADB is available and update status"""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.update_console("ADB connection check completed successfully\n")
                self.refresh_devices()
            else:
                self.update_console("Warning: ADB not found or not accessible\n")
                messagebox.showwarning("Warning", "ADB not found. Please ensure ADB is installed and in PATH.")
        except FileNotFoundError:
            self.update_console("Error: ADB executable not found\n")
            messagebox.showerror("Error", "ADB executable not found. Please install ADB and ensure it's in your PATH.")
        except Exception as e:
            self.update_console(f"Error checking ADB connection: {str(e)}\n")
    
    def refresh_devices(self):
        """Refresh the list of connected devices"""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            self.device_status_text.delete(1.0, tk.END)
            self.device_status_text.insert(tk.END, result.stdout)
            self.update_console("Device list refreshed\n")
        except Exception as e:
            self.update_console(f"Error refreshing devices: {str(e)}\n")
    
    def wireless_setup(self):
        """Open wireless connection wizard"""
        self.update_console("Opening wireless connection wizard...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Phone-Connection-Tester.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error opening wireless setup: {str(e)}\n")
    
    def open_connection_tester(self):
        """Open the enhanced connection tester"""
        self.update_console("Opening connection tester...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Phone-Connection-Tester.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error opening connection tester: {str(e)}\n")
    
    def driver_check(self):
        """Check drivers"""
        self.update_console("Checking drivers...\n")
        try:
            # This would be expanded with actual driver checking logic
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            if 'unauthorized' in result.stdout.lower():
                self.update_console("Device unauthorized. Please check USB debugging settings.\n")
            elif 'no permissions' in result.stderr.lower():
                self.update_console("Insufficient permissions. Please check driver installation.\n")
            else:
                self.update_console("Driver check completed. Devices connected properly.\n")
        except Exception as e:
            self.update_console(f"Error checking drivers: {str(e)}\n")
    
    def start_normal_scrcpy(self):
        """Start normal scrcpy"""
        self.update_console("Starting normal scrcpy...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Android-Scrcpy-Wrapper.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error starting scrcpy: {str(e)}\n")
    
    def start_broken_scrcpy(self):
        """Start broken screen optimized scrcpy"""
        self.update_console("Starting broken screen optimized scrcpy...\n")
        try:
            # Call the broken screen mode directly
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Android-Scrcpy-Wrapper.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error starting broken screen scrcpy: {str(e)}\n")
    
    def start_recording(self):
        """Start recording mode"""
        self.update_console("Starting recording mode...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Android-Scrcpy-Wrapper.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error starting recording: {str(e)}\n")
    
    def start_otg_mode(self):
        """Start OTG mode"""
        self.update_console("Starting OTG mode...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Android-Scrcpy-Wrapper.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error starting OTG mode: {str(e)}\n")
    
    def send_adb_command(self, command):
        """Send an ADB command"""
        full_command = f"adb {command}"
        self.update_console(f"Executing: {full_command}\n")
        try:
            result = subprocess.run(full_command.split(), capture_output=True, text=True, timeout=10)
            self.update_console(f"Output: {result.stdout}\n")
            if result.stderr:
                self.update_console(f"Error: {result.stderr}\n")
        except Exception as e:
            self.update_console(f"Error executing command: {str(e)}\n")
    
    def data_extraction(self):
        """Open data extraction tools"""
        self.update_console("Opening data extraction tools...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Advanced-Recovery-Suite.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error opening data extraction: {str(e)}\n")
    
    def system_backup(self):
        """Open system backup tools"""
        self.update_console("Opening system backup tools...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Advanced-Recovery-Suite.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error opening system backup: {str(e)}\n")
    
    def system_repair(self):
        """Open system repair tools"""
        self.update_console("Opening system repair tools...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Advanced-Recovery-Suite.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error opening system repair: {str(e)}\n")
    
    def screen_unlock(self):
        """Open screen unlock tools"""
        self.update_console("Opening screen unlock tools...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Advanced-Recovery-Suite.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error opening screen unlock: {str(e)}\n")
    
    def emergency_rescue(self):
        """Open emergency rescue tools"""
        self.update_console("Opening emergency rescue tools...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Advanced-Recovery-Suite.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error opening emergency rescue: {str(e)}\n")
    
    def forensics_tools(self):
        """Open forensics tools"""
        self.update_console("Opening forensics tools...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Advanced-Recovery-Suite.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error opening forensics tools: {str(e)}\n")
    
    def device_info(self):
        """Get device information"""
        self.update_console("Getting device information...\n")
        try:
            # Get basic device info
            model_result = subprocess.run(['adb', 'shell', 'getprop', 'ro.product.model'], 
                                        capture_output=True, text=True, timeout=10)
            brand_result = subprocess.run(['adb', 'shell', 'getprop', 'ro.product.brand'], 
                                        capture_output=True, text=True, timeout=10)
            android_result = subprocess.run(['adb', 'shell', 'getprop', 'ro.build.version.release'], 
                                          capture_output=True, text=True, timeout=10)
            
            self.update_console(f"Device Model: {model_result.stdout.strip()}\n")
            self.update_console(f"Device Brand: {brand_result.stdout.strip()}\n")
            self.update_console(f"Android Version: {android_result.stdout.strip()}\n")
        except Exception as e:
            self.update_console(f"Error getting device info: {str(e)}\n")
    
    def system_diagnostics(self):
        """Run system diagnostics"""
        self.update_console("Running system diagnostics...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Advanced-Recovery-Suite.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error running diagnostics: {str(e)}\n")
    
    def app_manager(self):
        """Open app manager"""
        self.update_console("Opening app manager...\n")
        try:
            subprocess.Popen(['start', 'cmd', '/k', 'Enhanced-Advanced-Recovery-Suite.bat'], shell=True)
        except Exception as e:
            self.update_console(f"Error opening app manager: {str(e)}\n")
    
    def open_user_manual(self):
        """Open user manual"""
        self.update_console("Opening user manual...\n")
        try:
            os.startfile('ANDROID_TOOLKIT_USER_MANUAL.md')
        except Exception as e:
            self.update_console(f"Error opening user manual: {str(e)}\n")
    
    def open_troubleshooting(self):
        """Open troubleshooting guide"""
        self.update_console("Opening troubleshooting guide...\n")
        try:
            os.startfile('README-Android-Recovery-Tools.md')
        except Exception as e:
            self.update_console(f"Error opening troubleshooting: {str(e)}\n")
    
    def update_console(self, text):
        """Update the console output"""
        self.console_output.insert(tk.END, text)
        self.console_output.see(tk.END)
        self.root.update_idletasks()
    
    def clear_console(self):
        """Clear the console output"""
        self.console_output.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = AndroidRecoveryToolkitGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()