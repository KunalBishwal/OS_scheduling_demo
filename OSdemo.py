import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backend_bases import MouseEvent
import matplotlib.pyplot as plt
from PIL import Image, ImageTk  

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


# Enhanced Gantt chart with tooltips and statistics
def plot_gantt_chart(schedule, processes):
    # Dynamically set figure size based on the total runtime
    max_end_time = max([x[2] for x in schedule])
    scaling_factor = 1.5 if max_end_time > 50 else 1  # Scale down for long timelines
    fig_width = max(12, max_end_time / 10 * scaling_factor)  # Set width based on timeline
    
    fig, gnt = plt.subplots(figsize=(fig_width, 6))
    
    # Set dynamic x-axis limits
    gnt.set_xlim(0, max_end_time * scaling_factor)
    gnt.set_ylim(0, 10)  # Adjust y-axis height for bar compression
    
    gnt.set_xlabel('Time')
    gnt.set_yticks([5])
    gnt.set_yticklabels(['Execution'])
    
    waiting_times = {}
    turnaround_times = {}

    bar_height = 1.5  # Smaller bar height to prevent overlap
    
    # Adding bars to the Gantt chart with compressed vertical spacing
    for i, task in enumerate(schedule):
        process_id = task[0]
        start = task[1]
        end = task[2]
        
        # Draw process bars with adaptive height
        gnt.broken_barh([(start, end - start)], (5 - bar_height/2, bar_height), facecolors=('tab:blue'))
        gnt.text(start + (end - start) / 2, 5, f'P{process_id}', color='white', ha='center', va='center', fontsize=7)
        
        # Calculate waiting and turnaround times
        arrival_time = next(p[1] for p in processes if p[0] == process_id)
        waiting_time = start - arrival_time
        turnaround_time = end - arrival_time
        waiting_times[process_id] = waiting_time
        turnaround_times[process_id] = turnaround_time
    
    # Calculate averages
    avg_waiting_time = sum(waiting_times.values()) / len(waiting_times)
    avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times)
    
    # Display process statistics and averages
    fig.subplots_adjust(left=0.2, right=0.8, bottom=0.4)
    fig.text(0.1, 0.3, "Process Statistics:", fontweight="bold", fontsize=13)
    
    # Individual process statistics on the left side
    for i, (pid, waiting_time) in enumerate(waiting_times.items()):
        fig.text(0.1, 0.18 - i * 0.03, f'P{pid}: Waiting Time = {waiting_time}, Turnaround Time = {turnaround_times[pid]}', fontsize=9)
    
    # Average statistics on the right side
    fig.text(0.8, 0.05, f"Average Waiting Time: {avg_waiting_time:.2f}", fontweight="bold", fontsize=10, ha='right')
    fig.text(0.8, 0.02, f"Average Turnaround Time: {avg_turnaround_time:.2f}", fontweight="bold", fontsize=10, ha='right')
    
    # Adding tooltips for each process
    def on_hover(event: MouseEvent):
        if event.inaxes == gnt:
            for task in schedule:
                process_id = task[0]
                start = task[1]
                end = task[2]
                if start <= event.xdata <= end:
                    tooltip = f"P{process_id}\nStart: {start}, End: {end}"
                    gnt.set_title(tooltip)
                    fig.canvas.draw()
                    return
            gnt.set_title("Process Scheduling Gantt Chart")
            fig.canvas.draw()

    fig.canvas.mpl_connect("motion_notify_event", on_hover)
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
        
        plot_gantt_chart(schedule, processes)
    
    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI Setup
root = tk.Tk()
root.title("Process Scheduling Simulator")

# Set the window to full screen
root.attributes('-fullscreen', True)
root.bind("<F11>", lambda event: root.attributes('-fullscreen', True))  
root.bind("<Escape>", lambda event: root.attributes('-fullscreen', False))  


try:
    background_image = Image.open(r"C:\Python\OS-expo.py\operating_system.jpg")  
   
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    

    target_resolution = (screen_width, screen_height)  
    background_image = background_image.resize(target_resolution, Image.LANCZOS) 
    bg_image = ImageTk.PhotoImage(background_image)

    
    gradient_canvas = tk.Canvas(root, width=screen_width, height=screen_height)
    gradient_canvas.pack(fill="both", expand=True)
    gradient_canvas.create_image(0, 0, image=bg_image, anchor="nw") 

except FileNotFoundError:
    messagebox.showerror("Error", "Background image not found. Please check the file path.")

# Title Label
title_label = tk.Label(root, text="PROCESS SCHEDULING SIMULATION", font=("Helvetica", 26, "bold"), fg="black", bg="#87CEEB")
title_label.place(relx=0.65, y=10, anchor='n')  
style = ttk.Style()
style.configure("RoundedButton.TButton", relief="flat", borderwidth=1, font=("Helvetica", 10, "bold"), foreground="white", background="#4CAF50")
style.map("RoundedButton.TButton", 
          background=[("active", "#45a049"), ("!disabled", "#008CBA")],  
          foreground=[("active", "#000000"), ("!disabled", "#000000")],  
          font=[("active", ("Helvetica", 10, "bold")), ("!disabled", ("Helvetica", 12, "bold"))])


def create_label(text, x, y):
    label = tk.Label(root, text=text, background="#87CEEB", font=("Helvetica", 12, "bold"), foreground="#2E8B57")
    label.place(x=x, y=y) 
    return label


create_label("Number of Processes:", 50, 30)
num_processes = tk.Entry(root)
num_processes.place(x=250, y=30)


set_process_button = ttk.Button(root, text="Set Processes", style="RoundedButton.TButton", command=lambda: create_process_entries())
set_process_button.place(x=400, y=25)

arrival_entries = []
burst_entries = []
priority_entries = []
label_widgets = []


def create_process_entries():
    # Clear previous entries and labels
    for widget in arrival_entries + burst_entries + priority_entries + label_widgets:
        widget.destroy()

   
    arrival_entries.clear()
    burst_entries.clear()
    priority_entries.clear()
    label_widgets.clear()


    num_process = int(num_processes.get())
    for i in range(num_process):
 
        arrival_label = create_label(f"Process {i + 1} Arrival Time:", 50, 70 + i * 40)  
        arrival_entry = tk.Entry(root, width=10)  
        arrival_entry.place(x=250, y=70 + i * 40)  
        arrival_entries.append(arrival_entry)
        label_widgets.append(arrival_label)
        
        # Burst Time
        burst_label = create_label(f"Process {i + 1} Burst Time:", 350, 70 + i * 40)  
        burst_entry = tk.Entry(root, width=10)  
        burst_entry.place(x=550, y=70 + i * 40)  
        burst_entries.append(burst_entry)
        label_widgets.append(burst_label)
        
        # Priority (for Priority Scheduling)
        priority_label = create_label(f"Process {i + 1} Priority:", 650, 70 + i * 40)  
        priority_entry = tk.Entry(root, width=10) 
        priority_entry.place(x=850, y=70 + i * 40)  
        priority_entries.append(priority_entry)
        label_widgets.append(priority_label)

# Time quantum input for Round Robin
time_quantum_label = create_label("Time Quantum (for Round Robin):", 75, 500)
time_quantum_entry = tk.Entry(root, width=20)  
time_quantum_entry.place(x=350, y=500)

# Adjust button positions
button_gap = 120
ttk.Button(root, text="FCFS", style="RoundedButton.TButton", command=lambda: run_scheduling("FCFS")).place(x=50, y=550)
ttk.Button(root, text="SJF", style="RoundedButton.TButton", command=lambda: run_scheduling("SJN")).place(x=200, y=550)
ttk.Button(root, text="Priority", style="RoundedButton.TButton", command=lambda: run_scheduling("Priority")).place(x=350, y=550)
ttk.Button(root, text="Round Robin", style="RoundedButton.TButton", command=lambda: run_scheduling("Round Robin")).place(x=500, y=550)
ttk.Button(root, text="SRTF", style="RoundedButton.TButton", command=lambda: run_scheduling("SRTF")).place(x=650, y=550)


def minimize_window():
    root.iconify()  

def close_window():
    root.quit()  

minimize_label = tk.Label(root, text="_", font=("Helvetica", 20), fg="white", bg="#4CAF50", cursor="hand2")
minimize_label.place(x=root.winfo_screenwidth() - 80, y=20)
minimize_label.bind("<Button-1>", lambda e: minimize_window())

close_label = tk.Label(root, text="X", font=("Helvetica", 20), fg="white", bg="#4CAF50", cursor="hand2")
close_label.place(x=root.winfo_screenwidth() - 40, y=20)
close_label.bind("<Button-1>", lambda e: close_window())

# Start the main loop
root.mainloop()
