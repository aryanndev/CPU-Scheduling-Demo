import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
import threading
import json
from collections import deque
import sys

# Modern color scheme
COLORS = {
    'bg_primary': '#1e1e2e',      # Dark background
    'bg_secondary': '#2a2a3e',    # Slightly lighter dark
    'bg_tertiary': '#3a3a4e',     # Even lighter
    'accent_primary': '#6c5ce7',  # Purple accent
    'accent_secondary': '#00d2d3', # Cyan accent
    'accent_success': '#00b894',   # Green
    'accent_warning': '#fdcb6e',   # Yellow
    'accent_danger': '#e17055',    # Orange/Red
    'text_primary': '#ffffff',     # White text
    'text_secondary': '#b8b8b8',   # Light gray text
    'border': '#4a4a5e',          # Border color
}

class EnergyEfficientSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Energy-Efficient CPU Scheduler ⚡")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['bg_primary'])

        # System state variables
        self.scheduled_tasks = []
        self.task_history = deque(maxlen=100)
        self.current_tasks = []
        self.task_entries = []
        self.cached_tasks = []

        # System statistics
        self.system_stats = {
            'total_energy': 0,
            'avg_power': 0,
            'cpu_utilization': 0,
            'temperature': 40,
            'active_cores': 4
        }

        # Thread control
        self.shutdown_event = threading.Event()
        self.monitor_thread = None

        # Configure matplotlib style
        plt.style.use('dark_background')

        # Configure styles first
        self.configure_styles()

        # Initialize UI
        self.create_header()
        self.create_main_frame()
        self.create_control_panel()
        self.create_visualization_frame()
        self.create_status_bar()

        # Start system monitoring thread
        self.start_monitoring()

        # Set close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Configure modern dark theme colors
        style.configure('TFrame', background=COLORS['bg_primary'], borderwidth=0)
        style.configure('Header.TFrame', background=COLORS['bg_secondary'])
        style.configure('Card.TFrame', background=COLORS['bg_secondary'], relief=tk.RAISED, borderwidth=1)

        style.configure('TLabel', background=COLORS['bg_primary'], foreground=COLORS['text_primary'],
                       font=('Segoe UI', 10))
        style.configure('Header.TLabel', background=COLORS['bg_secondary'], foreground=COLORS['text_primary'],
                       font=('Segoe UI', 16, 'bold'))
        style.configure('Title.TLabel', background=COLORS['bg_secondary'], foreground=COLORS['accent_primary'],
                       font=('Segoe UI', 18, 'bold'))
        style.configure('Card.TLabel', background=COLORS['bg_secondary'], foreground=COLORS['text_primary'],
                       font=('Segoe UI', 10, 'bold'))

        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=10)
        style.map('TButton',
                 background=[('active', COLORS['accent_primary']), ('!active', COLORS['bg_tertiary'])],
                 foreground=[('active', COLORS['text_primary']), ('!active', COLORS['text_primary'])],
                 borderwidth=[('active', 0), ('!active', 0)])

        style.configure('Primary.TButton', background=COLORS['accent_primary'], foreground=COLORS['text_primary'],
                       font=('Segoe UI', 10, 'bold'), padding=12)
        style.map('Primary.TButton',
                 background=[('active', '#5a4cd6'), ('!active', COLORS['accent_primary'])],
                 foreground=[('active', COLORS['text_primary']), ('!active', COLORS['text_primary'])])

        style.configure('Success.TButton', background=COLORS['accent_success'], foreground=COLORS['text_primary'],
                       font=('Segoe UI', 10, 'bold'), padding=12)
        style.map('Success.TButton',
                 background=[('active', '#00a085'), ('!active', COLORS['accent_success'])],
                 foreground=[('active', COLORS['text_primary']), ('!active', COLORS['text_primary'])])

        style.configure('TNotebook', background=COLORS['bg_primary'], borderwidth=0)
        style.configure('TNotebook.Tab', background=COLORS['bg_tertiary'], foreground=COLORS['text_secondary'],
                       padding=[20, 10], font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', COLORS['accent_primary']), ('!selected', COLORS['bg_tertiary'])],
                 foreground=[('selected', COLORS['text_primary']), ('!selected', COLORS['text_secondary'])],
                 expand=[('selected', [1, 1, 1, 0])])

        style.configure('Treeview', background=COLORS['bg_secondary'], foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['bg_secondary'], font=('Segoe UI', 10), rowheight=30)
        style.configure('Treeview.Heading', background=COLORS['bg_tertiary'], foreground=COLORS['text_primary'],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', COLORS['accent_primary'])])

        style.configure('TLabelFrame', background=COLORS['bg_secondary'], foreground=COLORS['accent_primary'],
                       font=('Segoe UI', 11, 'bold'), borderwidth=2, relief=tk.RAISED)
        style.configure('TLabelFrame.Label', background=COLORS['bg_secondary'], foreground=COLORS['accent_primary'],
                       font=('Segoe UI', 11, 'bold'))

        style.configure('TEntry', fieldbackground=COLORS['bg_tertiary'], foreground=COLORS['text_primary'],
                       borderwidth=1, font=('Segoe UI', 10))
        style.map('TEntry', fieldbackground=[('focus', COLORS['bg_tertiary'])],
                 bordercolor=[('focus', COLORS['accent_primary'])])

        style.configure('TCombobox', fieldbackground=COLORS['bg_tertiary'], foreground=COLORS['text_primary'],
                       borderwidth=1, font=('Segoe UI', 10))

        style.configure('TRadiobutton', background=COLORS['bg_secondary'], foreground=COLORS['text_primary'],
                       font=('Segoe UI', 10))
        style.map('TRadiobutton', background=[('selected', COLORS['bg_secondary'])],
                 foreground=[('selected', COLORS['accent_primary'])])

        style.configure('TScale', background=COLORS['bg_secondary'], troughcolor=COLORS['bg_tertiary'])

        style.configure('Status.TFrame', background=COLORS['bg_secondary'], relief=tk.RAISED, borderwidth=1)
        style.configure('Status.TLabel', background=COLORS['bg_secondary'], foreground=COLORS['text_primary'],
                       font=('Segoe UI', 9, 'bold'), padding=5)

    def create_header(self):
        """Create an attractive header bar"""
        header = ttk.Frame(self.root, style='Header.TFrame')
        header.pack(fill=tk.X, padx=0, pady=0)

        title = ttk.Label(header, text="⚡ Energy-Efficient CPU Scheduler", style='Title.TLabel')
        title.pack(side=tk.LEFT, padx=20, pady=15)

        subtitle = ttk.Label(header, text="Optimize Task Scheduling for Maximum Energy Efficiency",
                           style='Header.TLabel', font=('Segoe UI', 10))
        subtitle.pack(side=tk.LEFT, padx=10, pady=15)

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    def create_control_panel(self):
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Task input section
        input_frame = ttk.LabelFrame(control_frame, text="📋 Task Input", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Number of Tasks:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.num_tasks_entry = ttk.Entry(input_frame, width=15)
        self.num_tasks_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        input_frame.columnconfigure(1, weight=1)

        btn1 = ttk.Button(input_frame, text="✏️ Enter Task Details",
                  command=self.open_task_window, style='Primary.TButton')
        btn1.grid(row=1, column=0, columnspan=2, pady=8, sticky=tk.EW)

        btn2 = ttk.Button(input_frame, text="🎲 Generate Random Tasks",
                 command=self.generate_random_tasks, style='TButton')
        btn2.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)

        btn3 = ttk.Button(input_frame, text="📂 Load Tasks from File",
                 command=self.load_tasks_from_file, style='TButton')
        btn3.grid(row=3, column=0, columnspan=2, pady=5, sticky=tk.EW)

        btn4 = ttk.Button(input_frame, text="💾 Save Tasks to File",
                 command=self.save_tasks_to_file, style='TButton')
        btn4.grid(row=4, column=0, columnspan=2, pady=5, sticky=tk.EW)

        # Scheduling policy section
        policy_frame = ttk.LabelFrame(control_frame, text="⚙️ Scheduling Policy", padding=15)
        policy_frame.pack(fill=tk.X, pady=(0, 10))

        self.policy_var = tk.StringVar(value="FCFS")
        policies = ["FCFS", "Round Robin", "Shortest Job First", "Energy-Aware", "Priority-Based"]

        for i, policy in enumerate(policies):
            ttk.Radiobutton(policy_frame, text=policy, variable=self.policy_var,
                           value=policy).grid(row=i, column=0, sticky=tk.W, padx=5, pady=4)

        # Power management section
        power_frame = ttk.LabelFrame(control_frame, text="🔋 Power Management", padding=15)
        power_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(power_frame, text="Power Profile:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.power_profile = ttk.Combobox(power_frame,
                                         values=["Performance", "Balanced", "Power Saver"], width=12)
        self.power_profile.current(1)
        self.power_profile.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        power_frame.columnconfigure(1, weight=1)

        ttk.Label(power_frame, text="Max Temperature (°C):", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.temp_slider = ttk.Scale(power_frame, from_=50, to=100, value=85)
        self.temp_slider.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)

        ttk.Label(power_frame, text="Active Cores:", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.core_slider = ttk.Scale(power_frame, from_=1, to=8, value=4)
        self.core_slider.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)

        # Action buttons
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(fill=tk.X, pady=10)

        schedule_btn = ttk.Button(action_frame, text="🚀 Schedule Tasks",
                  command=self.schedule_tasks, style='Success.TButton')
        schedule_btn.pack(fill=tk.X, pady=5)

        reset_btn = ttk.Button(action_frame, text="🔄 Reset System",
                  command=self.reset_system, style='TButton')
        reset_btn.pack(fill=tk.X, pady=5)

    def create_visualization_frame(self):
        viz_frame = ttk.Frame(self.main_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(viz_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Gantt Chart Tab
        gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(gantt_frame, text="📊 Gantt Chart")

        self.gantt_fig, self.gantt_ax = plt.subplots(figsize=(10, 5), facecolor=COLORS['bg_secondary'])
        self.gantt_ax.set_facecolor(COLORS['bg_secondary'])
        self.gantt_ax.tick_params(colors=COLORS['text_primary'])
        self.gantt_ax.xaxis.label.set_color(COLORS['text_primary'])
        self.gantt_ax.yaxis.label.set_color(COLORS['text_primary'])
        self.gantt_ax.title.set_color(COLORS['text_primary'])
        self.gantt_canvas = FigureCanvasTkAgg(self.gantt_fig, gantt_frame)
        self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Energy Consumption Tab
        energy_frame = ttk.Frame(self.notebook)
        self.notebook.add(energy_frame, text="⚡ Energy Consumption")

        self.energy_fig, self.energy_ax = plt.subplots(figsize=(10, 5), facecolor=COLORS['bg_secondary'])
        self.energy_ax.set_facecolor(COLORS['bg_secondary'])
        self.energy_ax.tick_params(colors=COLORS['text_primary'])
        self.energy_ax.xaxis.label.set_color(COLORS['text_primary'])
        self.energy_ax.yaxis.label.set_color(COLORS['text_primary'])
        self.energy_ax.title.set_color(COLORS['text_primary'])
        self.energy_canvas = FigureCanvasTkAgg(self.energy_fig, energy_frame)
        self.energy_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # System Monitor Tab
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="🖥️ System Monitor")

        # CPU Utilization
        self.cpu_fig, self.cpu_ax = plt.subplots(figsize=(10, 2), facecolor=COLORS['bg_secondary'])
        self.cpu_ax.set_facecolor(COLORS['bg_secondary'])
        self.cpu_ax.tick_params(colors=COLORS['text_primary'])
        self.cpu_ax.xaxis.label.set_color(COLORS['text_primary'])
        self.cpu_ax.yaxis.label.set_color(COLORS['text_primary'])
        self.cpu_ax.title.set_color(COLORS['text_primary'])
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, monitor_frame)
        self.cpu_canvas.get_tk_widget().pack(fill=tk.X, pady=10, padx=10)

        # Temperature Gauge
        self.temp_fig, self.temp_ax = plt.subplots(figsize=(10, 2), facecolor=COLORS['bg_secondary'])
        self.temp_ax.set_facecolor(COLORS['bg_secondary'])
        self.temp_ax.tick_params(colors=COLORS['text_primary'])
        self.temp_ax.xaxis.label.set_color(COLORS['text_primary'])
        self.temp_ax.yaxis.label.set_color(COLORS['text_primary'])
        self.temp_ax.title.set_color(COLORS['text_primary'])
        self.temp_canvas = FigureCanvasTkAgg(self.temp_fig, monitor_frame)
        self.temp_canvas.get_tk_widget().pack(fill=tk.X, pady=10, padx=10)

        # Task History Tab
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="📜 Task History")

        columns = ("Task ID", "Arrival", "Burst", "Power", "Start", "End", "Energy")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.root, style='Status.TFrame', height=40)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)

        # Create separator labels with icons
        self.energy_label = ttk.Label(self.status_bar, text="⚡ Total Energy: 0 units", style='Status.TLabel')
        self.energy_label.pack(side=tk.LEFT, padx=15)

        separator1 = ttk.Label(self.status_bar, text="|", style='Status.TLabel', foreground=COLORS['text_secondary'])
        separator1.pack(side=tk.LEFT, padx=5)

        self.power_label = ttk.Label(self.status_bar, text="🔋 Avg Power: 0 W", style='Status.TLabel')
        self.power_label.pack(side=tk.LEFT, padx=15)

        separator2 = ttk.Label(self.status_bar, text="|", style='Status.TLabel', foreground=COLORS['text_secondary'])
        separator2.pack(side=tk.LEFT, padx=5)

        self.util_label = ttk.Label(self.status_bar, text="💻 CPU Util: 0%", style='Status.TLabel')
        self.util_label.pack(side=tk.LEFT, padx=15)

        separator3 = ttk.Label(self.status_bar, text="|", style='Status.TLabel', foreground=COLORS['text_secondary'])
        separator3.pack(side=tk.LEFT, padx=5)

        self.temp_label = ttk.Label(self.status_bar, text="🌡️ Temp: 40°C", style='Status.TLabel')
        self.temp_label.pack(side=tk.LEFT, padx=15)

        separator4 = ttk.Label(self.status_bar, text="|", style='Status.TLabel', foreground=COLORS['text_secondary'])
        separator4.pack(side=tk.LEFT, padx=5)

        self.cores_label = ttk.Label(self.status_bar, text="🔧 Active Cores: 4/8", style='Status.TLabel')
        self.cores_label.pack(side=tk.LEFT, padx=15)

    def start_monitoring(self):
        """Start the system monitoring thread"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return

        self.shutdown_event.clear()
        self.monitor_thread = threading.Thread(target=self.system_monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def system_monitor(self):
        """Background thread to update system monitoring"""
        while not self.shutdown_event.is_set():
            try:
                if not self.root.winfo_exists():
                    break

                # Update system stats
                self.update_system_stats()

                # Update UI
                self.update_status_bar()
                self.update_monitor_tabs()

                time.sleep(1)
            except tk.TclError:
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)

    def update_system_stats(self):
        """Update the system statistics"""
        # Simulate changing system stats
        temp_change = random.uniform(-1, 1)
        new_temp = self.system_stats['temperature'] + temp_change
        self.system_stats['temperature'] = min(
            max(40, new_temp),
            int(self.temp_slider.get())
        )

        self.system_stats['active_cores'] = int(self.core_slider.get())

        if self.scheduled_tasks:
            utilization = min(100, random.randint(70, 95))
        else:
            utilization = random.randint(5, 20)

        self.system_stats['cpu_utilization'] = utilization

    def update_status_bar(self):
        """Update the status bar with current system stats"""
        self.energy_label.config(text=f"⚡ Total Energy: {self.system_stats['total_energy']} units")
        self.power_label.config(text=f"🔋 Avg Power: {self.system_stats['avg_power']:.1f} W")
        self.util_label.config(text=f"💻 CPU Util: {self.system_stats['cpu_utilization']}%")
        self.temp_label.config(text=f"🌡️ Temp: {self.system_stats['temperature']:.1f}°C")
        self.cores_label.config(text=f"🔧 Active Cores: {self.system_stats['active_cores']}/8")

    def update_monitor_tabs(self):
        """Update the monitoring tabs"""
        # Update CPU utilization gauge
        self.cpu_ax.clear()
        self.cpu_ax.set_facecolor(COLORS['bg_secondary'])
        util = self.system_stats['cpu_utilization']
        color = COLORS['accent_success'] if util < 70 else (COLORS['accent_warning'] if util < 90 else COLORS['accent_danger'])
        self.cpu_ax.barh(['CPU Usage'], [util], color=color, height=0.5, edgecolor=COLORS['text_primary'], linewidth=2)
        self.cpu_ax.set_xlim(0, 100)
        self.cpu_ax.set_title('CPU Utilization', color=COLORS['text_primary'], fontsize=12, fontweight='bold')
        self.cpu_ax.tick_params(colors=COLORS['text_primary'])
        self.cpu_ax.text(util + 2, 0, f'{util}%', va='center', color=COLORS['text_primary'], fontsize=11, fontweight='bold')
        self.cpu_ax.grid(True, alpha=0.3, color=COLORS['text_secondary'])
        self.cpu_canvas.draw()

        # Update temperature gauge
        self.temp_ax.clear()
        self.temp_ax.set_facecolor(COLORS['bg_secondary'])
        temp = self.system_stats['temperature']
        max_temp = int(self.temp_slider.get())
        if temp > max_temp - 10:
            color = COLORS['accent_danger']
        elif temp > max_temp - 20:
            color = COLORS['accent_warning']
        else:
            color = COLORS['accent_secondary']

        self.temp_ax.barh(['Temperature'], [temp], color=color, height=0.5, edgecolor=COLORS['text_primary'], linewidth=2)
        self.temp_ax.axvline(max_temp, color=COLORS['accent_danger'], linestyle='--', linewidth=2, label='Max Temp')
        self.temp_ax.set_xlim(0, 100)
        self.temp_ax.set_title('CPU Temperature', color=COLORS['text_primary'], fontsize=12, fontweight='bold')
        self.temp_ax.tick_params(colors=COLORS['text_primary'])
        self.temp_ax.text(temp + 2, 0, f'{temp:.1f}°C', va='center', color=COLORS['text_primary'], fontsize=11, fontweight='bold')
        self.temp_ax.grid(True, alpha=0.3, color=COLORS['text_secondary'])
        self.temp_canvas.draw()

    def open_task_window(self):
        """Open window for task input"""
        try:
            num_tasks = int(self.num_tasks_entry.get())
            if num_tasks <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of tasks.")
            return

        task_window = tk.Toplevel(self.root)
        task_window.title("📋 Enter Task Details")
        task_window.geometry("700x500")
        task_window.configure(bg=COLORS['bg_primary'])
        task_window.transient(self.root)
        task_window.grab_set()

        # Header
        header_frame = ttk.Frame(task_window, style='Header.TFrame')
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_label = ttk.Label(header_frame, text="📋 Task Details Input", style='Title.TLabel')
        header_label.pack(padx=20, pady=15)

        # Create a frame with scrollbar
        container = ttk.Frame(task_window)
        canvas = tk.Canvas(container, bg=COLORS['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill="both", expand=True, padx=10, pady=10)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create headers with better styling
        headers = ["Task ID", "Arrival Time", "Burst Time", "Power Consumption", "Priority"]
        for col, header in enumerate(headers):
            label = ttk.Label(scrollable_frame, text=header, style='Card.TLabel',
                            font=('Segoe UI', 10, 'bold'))
            label.grid(row=0, column=col, padx=8, pady=10, sticky=tk.EW)

        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        scrollable_frame.columnconfigure(2, weight=1)
        scrollable_frame.columnconfigure(3, weight=1)
        scrollable_frame.columnconfigure(4, weight=1)

        # Create entry rows
        self.task_entries = []
        for i in range(num_tasks):
            task_id = ttk.Label(scrollable_frame, text=f"Task {i+1}", style='TLabel')
            task_id.grid(row=i+1, column=0, padx=8, pady=5, sticky=tk.W)

            arrival_entry = ttk.Entry(scrollable_frame, width=12)
            arrival_entry.grid(row=i+1, column=1, padx=8, pady=5, sticky=tk.EW)

            burst_entry = ttk.Entry(scrollable_frame, width=12)
            burst_entry.grid(row=i+1, column=2, padx=8, pady=5, sticky=tk.EW)

            power_entry = ttk.Entry(scrollable_frame, width=12)
            power_entry.grid(row=i+1, column=3, padx=8, pady=5, sticky=tk.EW)

            priority_entry = ttk.Entry(scrollable_frame, width=12)
            priority_entry.insert(0, "1")  # Default priority
            priority_entry.grid(row=i+1, column=4, padx=8, pady=5, sticky=tk.EW)

            self.task_entries.append({
                'arrival': arrival_entry,
                'burst': burst_entry,
                'power': power_entry,
                'priority': priority_entry
            })

        # Add buttons at the bottom
        button_frame = ttk.Frame(task_window)
        button_frame.pack(fill=tk.X, pady=10, padx=10)

        ttk.Button(button_frame, text="🚀 Schedule Tasks",
                  command=lambda: self.safe_schedule_tasks(task_window),
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="❌ Cancel",
                  command=task_window.destroy,
                  style='TButton').pack(side=tk.RIGHT, padx=5)

    def safe_schedule_tasks(self, window):
        """Wrapper for schedule_tasks that handles window destruction"""
        try:
            self.schedule_tasks(window)
        except tk.TclError:
            # Window was destroyed, use cached values if available
            if hasattr(self, 'cached_tasks') and self.cached_tasks:
                self.schedule_tasks(None)
            else:
                messagebox.showerror("Error", "No valid task data available")

    def generate_random_tasks(self):
        """Generate random tasks for simulation"""
        try:
            num_tasks = int(self.num_tasks_entry.get())
            if num_tasks <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of tasks.")
            return

        # Generate random tasks
        self.task_entries = []
        for _ in range(num_tasks):
            self.task_entries.append({
                'arrival': random.randint(0, 20),
                'burst': random.randint(1, 10),
                'power': random.randint(1, 5),
                'priority': random.randint(1, 5)
            })

        # Schedule with the generated tasks
        self.schedule_tasks(None)

    def load_tasks_from_file(self):
        """Load tasks from a JSON file"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                tasks = json.load(f)

            self.num_tasks_entry.delete(0, tk.END)
            self.num_tasks_entry.insert(0, str(len(tasks)))

            self.task_entries = []
            for task in tasks:
                self.task_entries.append({
                    'arrival': task.get('arrival', 0),
                    'burst': task.get('burst', 1),
                    'power': task.get('power', 1),
                    'priority': task.get('priority', 1)
                })

            # Schedule with the loaded tasks
            self.schedule_tasks(None)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")

    def save_tasks_to_file(self):
        """Save current tasks to a JSON file"""
        if not self.task_entries:
            messagebox.showerror("Error", "No tasks to save")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return

        try:
            tasks = []
            for entry in self.task_entries:
                if isinstance(entry['arrival'], tk.Entry):
                    # From manual input window
                    tasks.append({
                        'arrival': int(entry['arrival'].get()),
                        'burst': int(entry['burst'].get()),
                        'power': int(entry['power'].get()),
                        'priority': int(entry['priority'].get()) if entry['priority'].get() else 1
                    })
                else:
                    # From random generation or load
                    tasks.append({
                        'arrival': entry['arrival'],
                        'burst': entry['burst'],
                        'power': entry['power'],
                        'priority': entry.get('priority', 1)
                    })

            with open(file_path, 'w') as f:
                json.dump(tasks, f, indent=2)

            messagebox.showinfo("Success", "Tasks saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {str(e)}")

    def schedule_tasks(self, window=None):
        """Schedule tasks using the selected policy"""
        tasks = []

        if window:
            try:
                # Get values from window if it exists
                for i, entry in enumerate(self.task_entries):
                    arrival = int(entry['arrival'].get().strip())
                    burst = int(entry['burst'].get().strip())
                    power = int(entry['power'].get().strip())
                    priority = int(entry['priority'].get().strip()) if entry['priority'].get().strip() else 1

                    tasks.append({
                        'id': i + 1,
                        'arrival': arrival,
                        'burst': burst,
                        'power': power,
                        'priority': priority
                    })
            except tk.TclError:
                # Window was destroyed, use cached values if available
                if hasattr(self, 'cached_tasks') and self.cached_tasks:
                    tasks = self.cached_tasks
                else:
                    messagebox.showerror("Error", "No valid task data available")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for all fields.")
                return
        else:
            # Create tasks from cached or generated data
            for i, entry in enumerate(self.task_entries):
                tasks.append({
                    'id': i + 1,
                    'arrival': entry['arrival'],
                    'burst': entry['burst'],
                    'power': entry['power'],
                    'priority': entry.get('priority', 1)
                })

        if not tasks:
            messagebox.showerror("Error", "No tasks to schedule")
            return

        # Cache the tasks
        self.cached_tasks = tasks.copy()

        # Sort tasks based on selected policy
        policy = self.policy_var.get()
        if policy == "FCFS":
            tasks.sort(key=lambda x: x['arrival'])
        elif policy == "Shortest Job First":
            tasks.sort(key=lambda x: (x['arrival'], x['burst']))
        elif policy == "Priority-Based":
            tasks.sort(key=lambda x: (x['priority'], x['arrival']))
        elif policy == "Energy-Aware":
            tasks.sort(key=lambda x: (x['power'], x['arrival']))

        # Calculate scheduling
        completion_time = 0
        total_energy = 0
        self.scheduled_tasks = []

        for task in tasks:
            start_time = max(completion_time, task['arrival'])
            completion_time = start_time + task['burst']
            energy_used = task['burst'] * task['power']
            total_energy += energy_used

            scheduled_task = {
                'id': task['id'],
                'arrival': task['arrival'],
                'burst': task['burst'],
                'power': task['power'],
                'priority': task['priority'],
                'start': start_time,
                'end': completion_time,
                'energy': energy_used
            }

            self.scheduled_tasks.append(scheduled_task)
            self.task_history.append(scheduled_task)

        # Update system stats
        self.system_stats['total_energy'] = total_energy
        if completion_time > 0:
            self.system_stats['avg_power'] = total_energy / completion_time
        else:
            self.system_stats['avg_power'] = 0

        # Update visualizations
        self.update_gantt_chart()
        self.update_energy_chart()
        self.update_history_tree()

        # Show summary
        summary = f"Scheduled {len(tasks)} tasks using {policy} policy\n"
        summary += f"Total Energy Consumed: {total_energy} units\n"
        summary += f"Average Power: {self.system_stats['avg_power']:.1f} W\n"
        summary += f"Makespan: {completion_time} time units"

        messagebox.showinfo("Scheduling Complete", summary)

    def update_gantt_chart(self):
        """Update the Gantt chart visualization"""
        self.gantt_ax.clear()
        self.gantt_ax.set_facecolor(COLORS['bg_secondary'])

        if not self.scheduled_tasks:
            self.gantt_ax.text(0.5, 0.5, 'No tasks scheduled yet',
                             ha='center', va='center', transform=self.gantt_ax.transAxes,
                             color=COLORS['text_secondary'], fontsize=14)
            self.gantt_canvas.draw()
            return

        # Modern color palette
        colors = ['#6c5ce7', '#00d2d3', '#00b894', '#fdcb6e', '#e17055', '#a29bfe', '#fd79a8', '#fdcb6e',
                 '#55efc4', '#74b9ff', '#0984e3', '#6c5ce7', '#a29bfe', '#fd79a8', '#e84393']

        for i, task in enumerate(self.scheduled_tasks):
            color = colors[i % len(colors)]
            self.gantt_ax.barh(
                y=f"Task {task['id']}",
                width=task['end'] - task['start'],
                left=task['start'],
                height=0.6,
                color=color,
                edgecolor=COLORS['text_primary'],
                linewidth=1.5,
                label=f"Task {task['id']}",
                alpha=0.85
            )
            # Add task ID label on the bar
            mid_point = task['start'] + (task['end'] - task['start']) / 2
            self.gantt_ax.text(mid_point, i, f"T{task['id']}",
                             ha='center', va='center', color=COLORS['text_primary'],
                             fontweight='bold', fontsize=9)

        self.gantt_ax.set_xlabel("Time (units)", color=COLORS['text_primary'], fontsize=11, fontweight='bold')
        self.gantt_ax.set_ylabel("Tasks", color=COLORS['text_primary'], fontsize=11, fontweight='bold')
        self.gantt_ax.set_title(f"Gantt Chart - {self.policy_var.get()} Scheduling",
                               color=COLORS['text_primary'], fontsize=13, fontweight='bold', pad=15)
        self.gantt_ax.tick_params(colors=COLORS['text_primary'])
        self.gantt_ax.grid(True, axis='x', alpha=0.3, color=COLORS['text_secondary'], linestyle='--')
        self.gantt_ax.set_axisbelow(True)

        # Add legend if not too many tasks
        if len(self.scheduled_tasks) <= 20:
            legend = self.gantt_ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left',
                                        facecolor=COLORS['bg_tertiary'], edgecolor=COLORS['border'],
                                        labelcolor=COLORS['text_primary'], fontsize=9)

        self.gantt_canvas.draw()

    def update_energy_chart(self):
        """Update the energy consumption chart"""
        self.energy_ax.clear()
        self.energy_ax.set_facecolor(COLORS['bg_secondary'])

        if not self.scheduled_tasks:
            self.energy_ax.text(0.5, 0.5, 'No tasks scheduled yet',
                              ha='center', va='center', transform=self.energy_ax.transAxes,
                              color=COLORS['text_secondary'], fontsize=14)
            self.energy_canvas.draw()
            return

        task_ids = [f"Task {t['id']}" for t in self.scheduled_tasks]
        energy_values = [t['energy'] for t in self.scheduled_tasks]

        # Use gradient colors based on energy consumption
        max_energy = max(energy_values) if energy_values else 1
        colors_list = []
        for energy in energy_values:
            ratio = energy / max_energy
            if ratio > 0.7:
                colors_list.append(COLORS['accent_danger'])
            elif ratio > 0.4:
                colors_list.append(COLORS['accent_warning'])
            else:
                colors_list.append(COLORS['accent_success'])

        bars = self.energy_ax.barh(task_ids, energy_values, color=colors_list,
                                  edgecolor=COLORS['text_primary'], linewidth=1.5, alpha=0.85)
        self.energy_ax.bar_label(bars, fmt='%.1f', color=COLORS['text_primary'],
                                fontweight='bold', padding=5)

        self.energy_ax.set_xlabel("Energy Consumption (units)", color=COLORS['text_primary'],
                                 fontsize=11, fontweight='bold')
        self.energy_ax.set_ylabel("Tasks", color=COLORS['text_primary'],
                                 fontsize=11, fontweight='bold')
        self.energy_ax.set_title("Energy Consumption per Task", color=COLORS['text_primary'],
                               fontsize=13, fontweight='bold', pad=15)
        self.energy_ax.tick_params(colors=COLORS['text_primary'])
        self.energy_ax.grid(True, axis='x', alpha=0.3, color=COLORS['text_secondary'], linestyle='--')
        self.energy_ax.set_axisbelow(True)

        self.energy_canvas.draw()

    def update_history_tree(self):
        """Update the task history treeview"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Add new items
        for task in reversed(self.task_history):
            self.history_tree.insert("", 0, values=(
                task['id'],
                task['arrival'],
                task['burst'],
                task['power'],
                task['start'],
                task['end'],
                task['energy']
            ))

    def reset_system(self):
        """Reset the system state"""
        self.scheduled_tasks = []
        self.task_history.clear()
        self.task_entries = []
        self.cached_tasks = []

        self.system_stats = {
            'total_energy': 0,
            'avg_power': 0,
            'cpu_utilization': 0,
            'temperature': 40,
            'active_cores': 4
        }

        # Clear visualizations
        self.gantt_ax.clear()
        self.gantt_canvas.draw()

        self.energy_ax.clear()
        self.energy_canvas.draw()

        self.update_history_tree()
        self.update_status_bar()

        messagebox.showinfo("System Reset", "All tasks and statistics have been cleared.")

    def on_closing(self):
        """Handle window close event"""
        self.shutdown_event.set()

        # Wait for monitor thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)

        # Destroy the root window
        self.root.destroy()

def run_gui():
    """Run the GUI application"""
    root = tk.Tk()
    app = EnergyEfficientSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()