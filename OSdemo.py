import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from PIL import Image, ImageTk  # Ensure to install the Pillow library

# Scheduling algorithms
def fcfs_scheduling(processes):
    processes.sort(key=lambda x: x[1])  # Sort by arrival time
    time = 0
    schedule = []
    for process in processes:
        if time < process[1]:  # If CPU is idle
            time = process[1]
        schedule.append((process[0], time, time + process[2]))  # (PID, Start, End)
        time += process[2]
    return schedule

def sjn_scheduling(processes):
    processes.sort(key=lambda x: (x[1], x[2]))  # Sort by arrival time, then burst time
    time = 0
    schedule = []
    remaining_processes = processes[:]
    
    while remaining_processes:
        ready_queue = [p for p in remaining_processes if p[1] <= time]
        if not ready_queue:
            time = min(remaining_processes, key=lambda x: x[1])[1]
            continue
        
        shortest_process = min(ready_queue, key=lambda x: x[2])
        remaining_processes.remove(shortest_process)
        schedule.append((shortest_process[0], time, time + shortest_process[2]))
        time += shortest_process[2]
    
    return schedule

def priority_scheduling(processes):
    processes.sort(key=lambda x: (x[1], x[3]))  # Sort by arrival time, then priority
    time = 0
    schedule = []
    remaining_processes = processes[:]
    
    while remaining_processes:
        ready_queue = [p for p in remaining_processes if p[1] <= time]
        if not ready_queue:
            time = min(remaining_processes, key=lambda x: x[1])[1]
            continue
        
        highest_priority = min(ready_queue, key=lambda x: x[3])
        remaining_processes.remove(highest_priority)
        schedule.append((highest_priority[0], time, time + highest_priority[2]))
        time += highest_priority[2]
    
    return schedule

def round_robin_scheduling(processes, time_quantum):
    queue = processes[:]
    time = 0
    schedule = []
    while queue:
        process = queue.pop(0)
        if time < process[1]:
            time = process[1]
        start_time = time
        exec_time = min(time_quantum, process[2])
        time += exec_time
        schedule.append((process[0], start_time, time))
        remaining_time = process[2] - exec_time
        if remaining_time > 0:
            queue.append((process[0], time, remaining_time, process[3]))
    return schedule

# SRTF (Shortest Remaining Time First)
def srtf_scheduling(processes):
    time = 0
    schedule = []
    remaining_processes = processes[:]
    while remaining_processes:
        ready_queue = [p for p in remaining_processes if p[1] <= time]
        if not ready_queue:
            time = min(remaining_processes, key=lambda x: x[1])[1]
            continue
        shortest_remaining = min(ready_queue, key=lambda x: x[2])
        remaining_processes.remove(shortest_remaining)
        exec_time = shortest_remaining[2]
        time += exec_time
        schedule.append((shortest_remaining[0], time - exec_time, time))
    return schedule

# Plot Gantt chart
def plot_gantt_chart(schedule):
    fig, gnt = plt.subplots()
    gnt.set_ylim(0, 10)
    gnt.set_xlim(0, max([x[2] for x in schedule]) + 10)
    
    gnt.set_xlabel('Time')
    gnt.set_yticks([5])
    gnt.set_yticklabels(['Process Execution'])
    
    # Add the bars to the Gantt chart
    for task in schedule:
        gnt.broken_barh([(task[1], task[2] - task[1])], (4, 2), facecolors=('tab:blue'))
        gnt.text(task[1] + (task[2] - task[1]) / 2, 5, f'P{task[0]}', color='white', ha='center', va='center')
    
    plt.show()

# Run scheduling and plotting
def run_scheduling(algorithm):
    try:
        processes = []
        for i in range(int(num_processes.get())):
            pid = i + 1
            arrival_time = int(arrival_entries[i].get())
            burst_time = int(burst_entries[i].get())
            priority = int(priority_entries[i].get())
            processes.append((pid, arrival_time, burst_time, priority))
        
        time_quantum = int(time_quantum_entry.get()) if algorithm == "Round Robin" else None
        
        if algorithm == "FCFS":
            schedule = fcfs_scheduling(processes)
        elif algorithm == "SJN":
            schedule = sjn_scheduling(processes)
        elif algorithm == "Priority":
            schedule = priority_scheduling(processes)
        elif algorithm == "Round Robin":
            schedule = round_robin_scheduling(processes, time_quantum)
        elif algorithm == "SRTF":
            schedule = srtf_scheduling(processes)
        
        plot_gantt_chart(schedule)
    
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI Setup
root = tk.Tk()
root.title("Process Scheduling Simulator")

# Set the window to full screen
root.attributes('-fullscreen', True)
root.bind("<F11>", lambda event: root.attributes('-fullscreen', True))  # Bind F11 key to toggle full screen
root.bind("<Escape>", lambda event: root.attributes('-fullscreen', False))  # Bind Escape key to exit full screen

# Load the background image
try:
    background_image = Image.open(r"operating_system.jpg")  # Adjust the path as necessary
    # Resize to fit the window or 2K resolution (2560x1440) or 4K (3840x2160)
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    
    # Use 2K resolution for larger screens
    target_resolution = (screen_width, screen_height)  # Will match the current screen resolution
    background_image = background_image.resize(target_resolution, Image.LANCZOS)  # Resize to fit the window
    bg_image = ImageTk.PhotoImage(background_image)

    # Create a canvas and set the image as the background
    gradient_canvas = tk.Canvas(root, width=screen_width, height=screen_height)
    gradient_canvas.pack(fill="both", expand=True)
    gradient_canvas.create_image(0, 0, image=bg_image, anchor="nw")  # Place the image in the canvas

except FileNotFoundError:
    messagebox.showerror("Error", "Background image not found. Please check the file path.")

# Title Label
title_label = tk.Label(root, text="PROCESS SCHEDULING SIMULATION", font=("Helvetica", 26, "bold"), fg="black", bg="#87CEEB")
title_label.place(relx=0.65, y=10, anchor='n')  # Adjusted position for better spacing

# Styles for rounded buttons with hover effect
style = ttk.Style()
style.configure("RoundedButton.TButton", relief="flat", borderwidth=1, font=("Helvetica", 10, "bold"), foreground="white", background="#4CAF50")
style.map("RoundedButton.TButton", 
          background=[("active", "#45a049"), ("!disabled", "#008CBA")],  # Blue on hover
          foreground=[("active", "#000000"), ("!disabled", "#000000")],  # White text
          font=[("active", ("Helvetica", 10, "bold")), ("!disabled", ("Helvetica", 12, "bold"))])

# Helper function for creating centered labels
def create_label(text, x, y):
    label = tk.Label(root, text=text, background="#87CEEB", font=("Helvetica", 12, "bold"), foreground="#2E8B57")
    label.place(x=x, y=y)  # Use place for positioning
    return label

# Input fields setup
create_label("Number of Processes:", 50, 30)
num_processes = tk.Entry(root)
num_processes.place(x=250, y=30)

# Set Processes Button
set_process_button = ttk.Button(root, text="Set Processes", style="RoundedButton.TButton", command=lambda: create_process_entries())
set_process_button.place(x=400, y=25)

arrival_entries = []
burst_entries = []
priority_entries = []
label_widgets = []

# Create process entry widgets with centered alignment
def create_process_entries():
    # Clear previous entries and labels
    for widget in arrival_entries + burst_entries + priority_entries + label_widgets:
        widget.destroy()

    # Reset lists for new entries
    arrival_entries.clear()
    burst_entries.clear()
    priority_entries.clear()
    label_widgets.clear()

    # Dynamically create fields based on number of processes
    num_process = int(num_processes.get())
    for i in range(num_process):
        # Arrival Time
        arrival_label = create_label(f"Process {i + 1} Arrival Time:", 50, 70 + i * 40)  # Adjusted position
        arrival_entry = tk.Entry(root, width=10)  # Set a fixed width
        arrival_entry.place(x=250, y=70 + i * 40)  # Adjusted position
        arrival_entries.append(arrival_entry)
        label_widgets.append(arrival_label)
        
        # Burst Time
        burst_label = create_label(f"Process {i + 1} Burst Time:", 350, 70 + i * 40)  # Adjusted position
        burst_entry = tk.Entry(root, width=10)  # Set a fixed width
        burst_entry.place(x=550, y=70 + i * 40)  # Adjusted position
        burst_entries.append(burst_entry)
        label_widgets.append(burst_label)
        
        # Priority (for Priority Scheduling)
        priority_label = create_label(f"Process {i + 1} Priority:", 650, 70 + i * 40)  # Adjusted position
        priority_entry = tk.Entry(root, width=10)  # Set a fixed width
        priority_entry.place(x=850, y=70 + i * 40)  # Adjusted position
        priority_entries.append(priority_entry)
        label_widgets.append(priority_label)

# Time quantum input for Round Robin
time_quantum_label = create_label("Time Quantum (for Round Robin):", 75, 500)
time_quantum_entry = tk.Entry(root, width=20)  # Set a fixed width
time_quantum_entry.place(x=350, y=500)

# Adjust button positions
button_gap = 120
ttk.Button(root, text="FCFS", style="RoundedButton.TButton", command=lambda: run_scheduling("FCFS")).place(x=50, y=550)
ttk.Button(root, text="SJF", style="RoundedButton.TButton", command=lambda: run_scheduling("SJN")).place(x=200, y=550)
ttk.Button(root, text="Priority", style="RoundedButton.TButton", command=lambda: run_scheduling("Priority")).place(x=350, y=550)
ttk.Button(root, text="Round Robin", style="RoundedButton.TButton", command=lambda: run_scheduling("Round Robin")).place(x=500, y=550)
ttk.Button(root, text="SRTF", style="RoundedButton.TButton", command=lambda: run_scheduling("SRTF")).place(x=650, y=550)

# Adding minimalist minimize and close symbols
def minimize_window():
    root.iconify()  # Minimize immediately

def close_window():
    root.quit()  # Close immediately

minimize_label = tk.Label(root, text="_", font=("Helvetica", 20), fg="white", bg="#4CAF50", cursor="hand2")
minimize_label.place(x=root.winfo_screenwidth() - 80, y=20)
minimize_label.bind("<Button-1>", lambda e: minimize_window())

close_label = tk.Label(root, text="X", font=("Helvetica", 20), fg="white", bg="#4CAF50", cursor="hand2")
close_label.place(x=root.winfo_screenwidth() - 40, y=20)
close_label.bind("<Button-1>", lambda e: close_window())

# Start the main loop
root.mainloop()

