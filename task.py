class Task:
    def __init__(self, arrival, burst, power):
        self.arrival = arrival
        self.burst = burst
        self.power = power

    def energy(self):
        """Calculate energy consumption for this task."""
        return self.burst * self.power

    def __str__(self):
        return f"Task(Arrival: {self.arrival}, Burst: {self.burst}, Power: {self.power}, Energy: {self.energy()})"
