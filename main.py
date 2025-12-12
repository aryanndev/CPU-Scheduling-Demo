import sys
import tkinter as tk  # Required for GUI mode

def main():
    print("\n🚀 Welcome to the Energy-Efficient CPU Scheduler! 🚀")
    
    while True:
        mode = input("Choose Mode: [1] CLI, [2] GUI, [3] Exit: ").strip()
        
        if mode == "1":
            try:
                from cli import run_cli
                run_cli()
            except ImportError:
                print("❌ CLI module not available")
            break
        elif mode == "2":
            try:
                from gui import EnergyEfficientSchedulerGUI
                root = tk.Tk()
                app = EnergyEfficientSchedulerGUI(root)
                root.mainloop()
            except ImportError as e:
                print(f"❌ GUI module not available: {e}")
            break
        elif mode == "3":
            print("👋 Exiting...")
            sys.exit(0)
        else:
            print("❌ Invalid choice! Please enter 1 for CLI, 2 for GUI, or 3 to Exit.")
if __name__ == "__main__":
    main()
