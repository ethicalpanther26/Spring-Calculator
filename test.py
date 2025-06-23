import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ----- DATABASE SETUP -----
conn = sqlite3.connect('spring_data.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT,
    inputs TEXT,
    result TEXT,
    timestamp TEXT
)
''')
conn.commit()

def save_to_db(operation, inputs, result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO calculations (operation, inputs, result, timestamp) VALUES (?, ?, ?, ?)",
                   (operation, inputs, result, timestamp))
    conn.commit()

# ----- HISTORY WINDOW -----
def show_history():
    history_window = tk.Toplevel(root)
    history_window.title("Calculation History")
    history_window.geometry("600x400")

    history_tree = ttk.Treeview(history_window, columns=("ID", "Operation", "Inputs", "Result", "Timestamp"), show="headings")
    history_tree.heading("ID", text="ID")
    history_tree.heading("Operation", text="Operation")
    history_tree.heading("Inputs", text="Inputs")
    history_tree.heading("Result", text="Result")
    history_tree.heading("Timestamp", text="Timestamp")

    history_tree.column("ID", width=40)
    history_tree.column("Operation", width=100)
    history_tree.column("Inputs", width=180)
    history_tree.column("Result", width=100)
    history_tree.column("Timestamp", width=140)

    history_tree.pack(fill=tk.BOTH, expand=True)

    cursor.execute("SELECT * FROM calculations ORDER BY id DESC")
    rows = cursor.fetchall()
    for row in rows:
        history_tree.insert("", tk.END, values=row)

    ttk.Button(history_window, text="Clear History", command=lambda: clear_history(history_window)).pack(pady=10)

def clear_history(win):
    if messagebox.askyesno("Clear All", "Are you sure you want to delete all history?"):
        cursor.execute("DELETE FROM calculations")
        conn.commit()
        win.destroy()
        messagebox.showinfo("Cleared", "History deleted.")

# ----- CALCULATION LOGIC -----
def calculate():
    try:
        option = option_var.get()

        if option == "Outer Diameter":
            id_val = float(entry1.get())
            wd_val = float(entry2.get())
            result = id_val + 2 * wd_val
            result_text = f"Outer Diameter = {result:.2f} mm"
            inputs = f"id={id_val}, wd={wd_val}"

        elif option == "Inner Diameter":
            od_val = float(entry1.get())
            wd_val = float(entry2.get())
            result = od_val - 2 * wd_val
            result_text = f"Inner Diameter = {result:.2f} mm"
            inputs = f"od={od_val}, wd={wd_val}"

        elif option == "Spring Rate":
            l1 = float(entry1.get())
            l2 = float(entry2.get())
            d1 = float(entry3.get())
            d2 = float(entry4.get())
            result = (l2 - l1) / (d2 - d1)
            result_text = f"Spring Rate = {result:.2f} N/m"
            inputs = f"load1={l1}, load2={l2}, def1={d1}, def2={d2}"

        elif option == "Pitch":
            etype = end_type_var.get()
            if etype == "Open End Coil":
                x = 1
            elif etype == "Close Squared End Coil":
                x = 3
            elif etype == "Closed and Grounded End Coil":
                x = 2.5
            else:
                messagebox.showerror("Error", "Please select a valid End Coil Type.")
                return
            L = float(entry1.get())
            NA = float(entry2.get())
            d = float(entry3.get())
            result = (L - (x * d)) / NA
            result_text = f"Pitch = {result:.2f} mm"
            inputs = f"EndType={etype}, L={L}, NA={NA}, d={d}"

        output_var.set(result_text)
        save_to_db(option, inputs, result_text)

    except Exception as e:
        messagebox.showerror("Error", f"Invalid input or calculation error: {e}")

# ----- GUI LAYOUT -----
def update_fields(*args):
    for widget in (entry1, entry2, entry3, entry4):
        widget.grid_remove()
        widget.delete(0, tk.END)
    end_type_menu.grid_remove()
    label1.config(text="")
    label2.config(text="")
    label3.config(text="")
    label4.config(text="")
    output_var.set("")

    if option_var.get() == "Outer Diameter":
        label1.config(text="Inner Diameter (id):")
        label2.config(text="Wire Diameter (wd):")
        entry1.grid(row=2, column=1)
        entry2.grid(row=3, column=1)
        label1.grid(row=2, column=0)
        label2.grid(row=3, column=0)

    elif option_var.get() == "Inner Diameter":
        label1.config(text="Outer Diameter (od):")
        label2.config(text="Wire Diameter (wd):")
        entry1.grid(row=2, column=1)
        entry2.grid(row=3, column=1)
        label1.grid(row=2, column=0)
        label2.grid(row=3, column=0)

    elif option_var.get() == "Spring Rate":
        label1.config(text="Load 1 (N):")
        label2.config(text="Load 2 (N):")
        label3.config(text="Deflection 1 (mm):")
        label4.config(text="Deflection 2 (mm):")
        entry1.grid(row=2, column=1)
        entry2.grid(row=3, column=1)
        entry3.grid(row=4, column=1)
        entry4.grid(row=5, column=1)
        label1.grid(row=2, column=0)
        label2.grid(row=3, column=0)
        label3.grid(row=4, column=0)
        label4.grid(row=5, column=0)

    elif option_var.get() == "Pitch":
        label1.config(text="Free Length (L):")
        label2.config(text="Number of Active Coils (NA):")
        label3.config(text="Wire Diameter (d):")
        entry1.grid(row=3, column=1)
        entry2.grid(row=4, column=1)
        entry3.grid(row=5, column=1)
        label1.grid(row=3, column=0)
        label2.grid(row=4, column=0)
        label3.grid(row=5, column=0)
        end_type_menu.grid(row=2, column=1, pady=5)

# GUI Setup
root = tk.Tk()
root.title("Spring Calculator with History")
root.geometry("520x440")
root.resizable(False, False)

ttk.Label(root, text="Spring Calculator", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

option_var = tk.StringVar()
option_menu = ttk.OptionMenu(root, option_var, "Select Option", "Outer Diameter", "Inner Diameter", "Spring Rate", "Pitch", command=update_fields)
option_menu.grid(row=1, column=1, pady=5)
ttk.Label(root, text="Select Calculation:").grid(row=1, column=0)

end_type_var = tk.StringVar()
end_type_menu = ttk.OptionMenu(root, end_type_var, "Select End Coil Type", "Open End Coil", "Close Squared End Coil", "Closed and Grounded End Coil")

label1 = ttk.Label(root, text="")
label2 = ttk.Label(root, text="")
label3 = ttk.Label(root, text="")
label4 = ttk.Label(root, text="")

entry1 = ttk.Entry(root)
entry2 = ttk.Entry(root)
entry3 = ttk.Entry(root)
entry4 = ttk.Entry(root)

output_var = tk.StringVar()
ttk.Label(root, textvariable=output_var, font=("Arial", 12), foreground="blue").grid(row=7, column=0, columnspan=2, pady=20)

ttk.Button(root, text="Calculate", command=calculate).grid(row=6, column=0, columnspan=2, pady=10)
ttk.Button(root, text="View History", command=show_history).grid(row=8, column=0, columnspan=2)

root.mainloop()

conn.close()