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

class EnergyEfficientSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Energy-Efficient CPU Scheduler")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
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
        
        # Initialize UI
        self.create_main_frame()
        self.create_control_panel()
        self.create_visualization_frame()
        self.create_status_bar()
        
        # Start system monitoring thread
        self.start_monitoring()
        
        # Configure styles
        self.configure_styles()
        
        # Set close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', font=('Segoe UI', 10))
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
    
    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_control_panel(self):
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Task input section
        input_frame = ttk.LabelFrame(control_frame, text="Task Input", padding=10)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Number of Tasks:").grid(row=0, column=0, sticky=tk.W)
        self.num_tasks_entry = ttk.Entry(input_frame)
        self.num_tasks_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(input_frame, text="Enter Task Details", 
                  command=self.open_task_window).grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(input_frame, text="Generate Random Tasks",
                 command=self.generate_random_tasks).grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(input_frame, text="Load Tasks from File",
                 command=self.load_tasks_from_file).grid(row=3, column=0, columnspan=2, pady=5)
        
        ttk.Button(input_frame, text="Save Tasks to File",
                 command=self.save_tasks_to_file).grid(row=4, column=0, columnspan=2, pady=5)
        
        # Scheduling policy section
        policy_frame = ttk.LabelFrame(control_frame, text="Scheduling Policy", padding=10)
        policy_frame.pack(fill=tk.X, pady=5)
        
        self.policy_var = tk.StringVar(value="FCFS")
        policies = ["FCFS", "Round Robin", "Shortest Job First", "Energy-Aware", "Priority-Based"]
        
        for i, policy in enumerate(policies):
            ttk.Radiobutton(policy_frame, text=policy, variable=self.policy_var,
                           value=policy).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Power management section
        power_frame = ttk.LabelFrame(control_frame, text="Power Management", padding=10)
        power_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(power_frame, text="Power Profile:").grid(row=0, column=0, sticky=tk.W)
        self.power_profile = ttk.Combobox(power_frame, 
                                         values=["Performance", "Balanced", "Power Saver"])
        self.power_profile.current(1)
        self.power_profile.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(power_frame, text="Max Temperature (°C):").grid(row=1, column=0, sticky=tk.W)
        self.temp_slider = ttk.Scale(power_frame, from_=50, to=100, value=85)
        self.temp_slider.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(power_frame, text="Active Cores:").grid(row=2, column=0, sticky=tk.W)
        self.core_slider = ttk.Scale(power_frame, from_=1, to=8, value=4)
        self.core_slider.grid(row=2, column=1, padx=5, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Schedule Tasks", 
                  command=self.schedule_tasks).pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Reset System", 
                  command=self.reset_system).pack(fill=tk.X, pady=5)
    
    def create_visualization_frame(self):
        viz_frame = ttk.Frame(self.main_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.notebook = ttk.Notebook(viz_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Gantt Chart Tab
        gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(gantt_frame, text="Gantt Chart")
        
        self.gantt_fig, self.gantt_ax = plt.subplots(figsize=(10, 5))
        self.gantt_fig.set_facecolor('#f0f0f0')
        self.gantt_ax.set_facecolor('#f0f0f0')
        self.gantt_canvas = FigureCanvasTkAgg(self.gantt_fig, gantt_frame)
        self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Energy Consumption Tab
        energy_frame = ttk.Frame(self.notebook)
        self.notebook.add(energy_frame, text="Energy Consumption")
        
        self.energy_fig, self.energy_ax = plt.subplots(figsize=(10, 5))
        self.energy_fig.set_facecolor('#f0f0f0')
        self.energy_ax.set_facecolor('#f0f0f0')
        self.energy_canvas = FigureCanvasTkAgg(self.energy_fig, energy_frame)
        self.energy_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # System Monitor Tab
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="System Monitor")
        
        # CPU Utilization
        self.cpu_fig, self.cpu_ax = plt.subplots(figsize=(10, 2))
        self.cpu_fig.set_facecolor('#f0f0f0')
        self.cpu_ax.set_facecolor('#f0f0f0')
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, monitor_frame)
        self.cpu_canvas.get_tk_widget().pack(fill=tk.X, pady=5)
        
        # Temperature Gauge
        self.temp_fig, self.temp_ax = plt.subplots(figsize=(10, 2))
        self.temp_fig.set_facecolor('#f0f0f0')
        self.temp_ax.set_facecolor('#f0f0f0')
        self.temp_canvas = FigureCanvasTkAgg(self.temp_fig, monitor_frame)
        self.temp_canvas.get_tk_widget().pack(fill=tk.X, pady=5)
        
        # Task History Tab
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="Task History")
        
        columns = ("Task ID", "Arrival", "Burst", "Power", "Start", "End", "Energy")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=80, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.root, height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.energy_label = ttk.Label(self.status_bar, text="Total Energy: 0 units")
        self.energy_label.pack(side=tk.LEFT, padx=10)
        
        self.power_label = ttk.Label(self.status_bar, text="Avg Power: 0 W")
        self.power_label.pack(side=tk.LEFT, padx=10)
        
        self.util_label = ttk.Label(self.status_bar, text="CPU Util: 0%")
        self.util_label.pack(side=tk.LEFT, padx=10)
        
        self.temp_label = ttk.Label(self.status_bar, text="Temp: 40°C")
        self.temp_label.pack(side=tk.LEFT, padx=10)
        
        self.cores_label = ttk.Label(self.status_bar, text="Active Cores: 4/8")
        self.cores_label.pack(side=tk.LEFT, padx=10)
    
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
        self.energy_label.config(text=f"Total Energy: {self.system_stats['total_energy']} units")
        self.power_label.config(text=f"Avg Power: {self.system_stats['avg_power']:.1f} W")
        self.util_label.config(text=f"CPU Util: {self.system_stats['cpu_utilization']}%")
        self.temp_label.config(text=f"Temp: {self.system_stats['temperature']}°C")
        self.cores_label.config(text=f"Active Cores: {self.system_stats['active_cores']}/8")
    
    def update_monitor_tabs(self):
        """Update the monitoring tabs"""
        # Update CPU utilization gauge
        self.cpu_ax.clear()
        self.cpu_ax.barh(['CPU Usage'], [self.system_stats['cpu_utilization']], color='#2ecc71')
        self.cpu_ax.set_xlim(0, 100)
        self.cpu_ax.set_title('CPU Utilization')
        self.cpu_canvas.draw()
        
        # Update temperature gauge
        self.temp_ax.clear()
        temp = self.system_stats['temperature']
        max_temp = int(self.temp_slider.get())
        color = '#e74c3c' if temp > max_temp - 10 else '#3498db'
        
        self.temp_ax.barh(['Temperature'], [temp], color=color)
        self.temp_ax.axvline(max_temp, color='red', linestyle='--')
        self.temp_ax.set_xlim(0, 100)
        self.temp_ax.set_title('CPU Temperature')
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
        task_window.title("Enter Task Details")
        task_window.geometry("600x400")
        task_window.transient(self.root)
        task_window.grab_set()
        
        # Create a frame with scrollbar
        container = ttk.Frame(task_window)
        canvas = tk.Canvas(container)
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
        
        container.pack(fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create headers
        headers = ["Task ID", "Arrival Time", "Burst Time", "Power Consumption", "Priority"]
        for col, header in enumerate(headers):
            ttk.Label(scrollable_frame, text=header, font=('Segoe UI', 9, 'bold')).grid(row=0, column=col, padx=5, pady=5)
        
        # Create entry rows
        self.task_entries = []
        for i in range(num_tasks):
            task_id = ttk.Label(scrollable_frame, text=f"Task {i+1}")
            task_id.grid(row=i+1, column=0, padx=5, pady=2)
            
            arrival_entry = ttk.Entry(scrollable_frame)
            arrival_entry.grid(row=i+1, column=1, padx=5, pady=2)
            
            burst_entry = ttk.Entry(scrollable_frame)
            burst_entry.grid(row=i+1, column=2, padx=5, pady=2)
            
            power_entry = ttk.Entry(scrollable_frame)
            power_entry.grid(row=i+1, column=3, padx=5, pady=2)
            
            priority_entry = ttk.Entry(scrollable_frame)
            priority_entry.insert(0, "1")  # Default priority
            priority_entry.grid(row=i+1, column=4, padx=5, pady=2)
            
            self.task_entries.append({
                'arrival': arrival_entry,
                'burst': burst_entry,
                'power': power_entry,
                'priority': priority_entry
            })
        
        # Add buttons at the bottom
        button_frame = ttk.Frame(task_window)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Schedule Tasks", 
                  command=lambda: self.safe_schedule_tasks(task_window)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=task_window.destroy).pack(side=tk.RIGHT, padx=5)
    
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
        
        if not self.scheduled_tasks:
            return
        
        colors = plt.cm.tab20.colors
        for i, task in enumerate(self.scheduled_tasks):
            self.gantt_ax.barh(
                y=f"Task {task['id']}",
                width=task['end'] - task['start'],
                left=task['start'],
                height=0.6,
                color=colors[i % len(colors)],
                label=f"Task {task['id']}"
            )
        
        self.gantt_ax.set_xlabel("Time")
        self.gantt_ax.set_ylabel("Tasks")
        self.gantt_ax.set_title(f"Gantt Chart - {self.policy_var.get()} Scheduling")
        self.gantt_ax.grid(True, axis='x')
        
        # Add legend if not too many tasks
        if len(self.scheduled_tasks) <= 20:
            self.gantt_ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.gantt_canvas.draw()
    
    def update_energy_chart(self):
        """Update the energy consumption chart"""
        self.energy_ax.clear()
        
        if not self.scheduled_tasks:
            return
        
        task_ids = [f"Task {t['id']}" for t in self.scheduled_tasks]
        energy_values = [t['energy'] for t in self.scheduled_tasks]
        
        bars = self.energy_ax.barh(task_ids, energy_values, color='#e74c3c')
        self.energy_ax.bar_label(bars, fmt='%.1f')
        
        self.energy_ax.set_xlabel("Energy Consumption (units)")
        self.energy_ax.set_ylabel("Tasks")
        self.energy_ax.set_title("Energy Consumption per Task")
        self.energy_ax.grid(True, axis='x')
        
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