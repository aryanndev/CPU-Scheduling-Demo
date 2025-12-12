import matplotlib.pyplot as plt

class EnergyEfficientScheduler:
    def __init__(self, tasks):
        self.tasks = sorted(tasks, key=lambda t: t.arrival)  # Sort tasks by arrival time
        self.total_energy_consumed = sum(task.energy() for task in self.tasks)

    def schedule(self):
        """Simulates task execution and prints scheduling order."""
        print("\n🕒 Scheduling Order:")
        for task in self.tasks:
            print(task)
        print(f"\n⚡ Total Energy Consumed: {self.total_energy_consumed} units")

    import matplotlib.pyplot as plt

    def plot_energy_consumption(tasks):
        plt.ion()  # Enable interactive mode (keeps plots inside the same session)
        energies = [task.energy() for task in tasks]
        labels = [f'Task {i+1}' for i in range(len(tasks))]
        
        plt.figure(figsize=(6,4))
        plt.bar(labels, energies, color='blue')
        plt.xlabel("Tasks")
        plt.ylabel("Energy Consumed")
        plt.title("Energy Consumption per Task")
        
        plt.draw()  # Draws plot without blocking execution
        plt.pause(0.001)  # Allows GUI to update
