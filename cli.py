import tkinter as tk
from scheduler import EnergyEfficientScheduler
from task import Task

def show_gui_results(scheduler):
    """Creates a pop-up window displaying scheduling results."""
    result_window = tk.Tk()
    result_window.title("Scheduling Results")

    tk.Label(result_window, text="🕒 Scheduling Order:", font=("Arial", 12, "bold")).pack()

    for task in scheduler.tasks:
        tk.Label(result_window, text=str(task)).pack()

    tk.Label(result_window, text=f"\n⚡ Total Energy Consumed: {scheduler.total_energy_consumed} units", font=("Arial", 12, "bold")).pack()
    
    tk.Button(result_window, text="Close", command=result_window.destroy).pack()
    
    result_window.mainloop()

def run_cli():
    tasks = []

    try:
        n = int(input("Enter the number of tasks: "))
        for i in range(n):
            arrival = int(input(f"Task {i+1} Arrival Time: "))
            burst = int(input(f"Task {i+1} Burst Time: "))
            power = int(input(f"Task {i+1} Power Consumption: "))

            task = Task(arrival, burst, power)
            tasks.append(task)
        
        scheduler = EnergyEfficientScheduler(tasks)
        scheduler.schedule()
        
        # Show results in a pop-up GUI window
        show_gui_results(scheduler)

    except ValueError:
        print("❌ Invalid input! Please enter integer values only.")
