import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import threading
import time

# List of events: each event = (event_name, date_time_str, datetime_obj)
events = []

def add_event():
    name = name_entry.get().strip()
    date_str = date_entry.get().strip() # Format: YYYY-MM-DD HH:MM

    if not name or not date_str:
        messagebox.showerror("Error", "Enter event name and date/time")
        return

    try:
        # Parse: 2026-04-30 14:30
        event_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        if event_dt < datetime.datetime.now():
            messagebox.showerror("Error", "Event time must be in the future")
            return

        events.append((name, date_str, event_dt))
        refresh_table()
        name_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        messagebox.showinfo("Added", f"Reminder set for {name}")
    except ValueError:
        messagebox.showerror("Error", "Use format: YYYY-MM-DD HH:MM\nEx: 2026-04-30 14:30")

def delete_event():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Select an event to delete")
        return

    item = tree.item(selected[0])
    event_name = item['values'][0]
    event_time = item['values'][1]

    for i, event in enumerate(events):
        if event[0] == event_name and event[1] == event_time:
            events.pop(i)
            break
    refresh_table()

def refresh_table():
    tree.delete(*tree.get_children())
    # Sort by date
    sorted_events = sorted(events, key=lambda x: x[2])
    for name, date_str, _ in sorted_events:
        tree.insert("", "end", values=(name, date_str))

def check_reminders():
    """Background thread that checks for due events"""
    while True:
        now = datetime.datetime.now()
        for event in events[:]: # Copy list to avoid modification issues
            name, date_str, event_dt = event
            # Check if event time passed within last 60 seconds
            if event_dt <= now < event_dt + datetime.timedelta(minutes=1):
                messagebox.showinfo("Reminder!", f"Event Due Now:\n{name}\n{date_str}")
                events.remove(event)
                root.after(0, refresh_table) # Update GUI from thread
        time.sleep(30) # Check every 30 seconds

# GUI Setup
root = tk.Tk()
root.title("Event Reminder System")
root.geometry("500x400")

# Input Frame
input_frame = tk.Frame(root, padx=15, pady=15)
input_frame.pack(fill="x")

tk.Label(input_frame, text="Event Name:").grid(row=0, column=0, sticky="w", pady=5)
name_entry = tk.Entry(input_frame, width=40)
name_entry.grid(row=0, column=1, pady=5)

tk.Label(input_frame, text="Date Time:").grid(row=1, column=0, sticky="w", pady=5)
date_entry = tk.Entry(input_frame, width=40)
date_entry.grid(row=1, column=1, pady=5)
tk.Label(input_frame, text="Format: YYYY-MM-DD HH:MM", fg="gray").grid(row=2, column=1, sticky="w")

btn_frame = tk.Frame(input_frame)
btn_frame.grid(row=3, column=1, pady=10, sticky="w")
tk.Button(btn_frame, text="Add Reminder", command=add_event).pack(side="left", padx=5)
tk.Button(btn_frame, text="Delete Selected", command=delete_event).pack(side="left", padx=5)

# Table
tree = ttk.Treeview(root, columns=("Event", "DateTime"), show="headings")
tree.heading("Event", text="Event Name")
tree.heading("DateTime", text="Date & Time")
tree.column("Event", width=250)
tree.column("DateTime", width=200)
tree.pack(fill="both", expand=True, padx=15, pady=10)

# Start reminder checker thread
reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()

root.mainloop()