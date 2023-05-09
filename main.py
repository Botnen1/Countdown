import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import json
import os

def color_text(text, rgb):
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

class rgb():
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    # and so on ...

# Constants
DATA_FILE = "countdowns.json"

class CountdownApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Botnen - Countdown App")
        
        self.minsize(height=300, width=600)
        self.maxsize(height=300, width=600)

        self.load_countdowns()

        self.create_widgets()
        self.update_countdown_time()

    def create_widgets(self):
        self.add_countdown_frame = ttk.Frame(self)
        self.add_countdown_frame.pack(pady=10)

        self.countdown_label = ttk.Label(self, text="")
        self.countdown_label.pack(pady=10)

        self.name_var = tk.StringVar()
        self.name_var.set("Name/Note")
        self.name_entry = ttk.Entry(self.add_countdown_frame, textvariable=self.name_var)
        self.name_entry.pack(side=tk.LEFT)
        self.name_entry.bind("<FocusIn>", self.clear_name_placeholder)
        self.name_entry.bind("<FocusOut>", self.reset_name_placeholder)


        self.date_entry = ttk.Entry(self.add_countdown_frame)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, "YYYY-MM-DD HH:MM:SS")

        
        self.add_button = tk.Button(self.add_countdown_frame, text="Add Countdown", command=self.add_countdown, 
                                    foreground="white", background="darkblue", activeforeground="black", activebackground="white")

        self.add_button.pack(side=tk.LEFT, padx=5)

        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(pady=10)

        self.listbox = tk.Listbox(self.list_frame, width=50, height=5)
        self.listbox.pack(side=tk.LEFT)

        self.scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.edit_button = tk.Button(self.list_frame, text="Edit", command=self.edit_countdown, 
                                     foreground="white", background="darkblue", activeforeground="black", activebackground="white")
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.list_frame, text="Delete", command=self.delete_countdown, 
                                       foreground="white", background="darkred", activeforeground="black", activebackground="white")
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.populate_listbox()
        
    def clear_name_placeholder(self, event):
        if self.name_var.get() == "Name/Note":
            self.name_var.set("")

    def reset_name_placeholder(self, event):
        if self.name_var.get() == "":
            self.name_var.set("Name/Note")


    def load_countdowns(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                self.countdowns = json.load(file)
        else:
            self.countdowns = []

    def save_countdowns(self):
        with open(DATA_FILE, "w") as file:
            json.dump(self.countdowns, file)
            
            print(color_text("*", rgb.RED),(color_text("update logg", rgb.YELLOW)))
            

    def populate_listbox(self):
        self.listbox.delete(0, tk.END)
        for countdown in self.countdowns:
            self.listbox.insert(tk.END, f"{countdown['name']} - {countdown['date']}")

    def add_countdown(self):
        name = self.name_entry.get()
        date_str = self.date_entry.get()
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            self.countdowns.append({"name": name, "date": date_str})
            self.save_countdowns()
            self.populate_listbox()
            print("added\n")
        except ValueError:
            print("Invalid date format. Please use 'YYYY-MM-DD HH:MM:SS'")
            

    def edit_countdown(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            countdown = self.countdowns[index]

            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, countdown["name"])

            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, countdown["date"])

            self.add_button.config(text="Update Countdown", command=lambda: self.update_countdown(index))
            print("edited\n")

    def update_countdown(self, index):
        name = self.name_entry.get()
        date_str = self.date_entry.get()
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            self.countdowns[index] = {"name": name, "date": date_str}
            self.save_countdowns()
            self.populate_listbox()
            self.add_button.config(text="Add Countdown", command=self.add_countdown)
            print("updated\n")
        except ValueError:
            print("Invalid date format. Please use 'YYYY-MM-DD HH:MM:SS'")

    def delete_countdown(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.countdowns.pop(index)
            self.save_countdowns()
            self.populate_listbox()
            print("deleted\n")
            
    def update_countdown_time(self):
        now = datetime.now()
        ongoing_countdowns = []
        expired_indices = []

        for index, countdown in enumerate(self.countdowns):
            date_obj = datetime.strptime(countdown["date"], "%Y-%m-%d %H:%M:%S")
            remaining_time = date_obj - now

            if remaining_time > timedelta(0):
                ongoing_countdowns.append((countdown["name"], remaining_time))
            else:
                expired_indices.append(index)

        if expired_indices:
            for index in sorted(expired_indices, reverse=True):
                self.countdowns.pop(index)
            self.save_countdowns()
            self.populate_listbox()

        if ongoing_countdowns:
            countdowns_text = "\n".join([f"{name}: {time}" for name, time in ongoing_countdowns])
            self.countdown_label.config(text=f"Ongoing countdowns:\n{countdowns_text}")
        else:
            self.countdown_label.config(text="No ongoing countdowns")

        self.after(1000, self.update_countdown_time)



if __name__ == "__main__":
    app = CountdownApp()
    app.mainloop()
