import os
import ntpath
import tkinter
from tkinter import *
from tkinter import filedialog

from reader import ingest_dates
from writer import WriterConfig, writer

window = Tk()
window.title("Duty Planner")
window.resizable(width=False, height=False)

input_path = StringVar()
output_path = StringVar()
output_name = StringVar()
show_individual_blocked_pct = IntVar()


def select_input_folder(path_label: Label):
    def f():
        folder_path = filedialog.askdirectory(title=f"Select input folder")

        if not folder_path:
            return
        else:
            path_label.configure(text=folder_path)
            input_path.set(folder_path)

    return f


def select_file_name():
    file_path = filedialog.asksaveasfilename(title="Save file", defaultextension=".xlsx", initialfile="Duty Planner",
                                             filetypes=[("All Files", "*.*"), ("Excel Worksheet", "*.xlsx")])

    if not file_path:
        return
    else:
        head, tail = ntpath.split(file_path)
        output_path.set(head)
        output_name.set(tail)


def run_writer(status_label: Label):
    def f():
        select_file_name()

        if not output_path.get():
            status_label.configure(text="Save file is not selected")
            return

        if not output_name.get():
            status_label.configure(text="Save file is not selected")
            return

        if not input_path.get():
            status_label.configure(text="No folder was selected to scan")
            return

        status_label.configure(text="Working...")

        dir_scan = os.scandir(input_path.get())

        # Take every file's path inside the folder
        dir_files = [entry.path for entry in dir_scan if entry.is_file()]

        # Sort into alphabetical order
        # This method will mutate the list itself
        dir_files.sort()

        duty_personnel = []

        for file_path in dir_files:
            file = open(file_path, "r")
            text = file.read()
            ingested = ingest_dates(text)
            duty_personnel.append(ingested)
            file.close()

        file_name = output_name.get()
        file_name = file_name if file_name.endswith(".xlsx") else file_name + ".xlsx"

        duty_year = int(duty_year_entry.get())
        duty_month = int(duty_month_entry.get())

        # ph = list(map(lambda x: int(x), public_holidays.get().split(",")))
        ph = [int(x) for x in public_holidays_entry.get().split(",")]

        writer_config = WriterConfig(output_path=output_path.get(), output_file_name=file_name,
                                     duty_year=duty_year,
                                     duty_month=duty_month, public_holidays=ph,
                                     show_individual_blocked_pct=bool(show_individual_blocked_pct.get()))

        writer(duty_personnel, writer_config)
        status_label.configure(text="Done")

    return f


root_frame = Frame(window)
input_folder_label = Label(root_frame, text="Select folder to scan")
input_folder_label.grid(row=0, column=0, sticky="ew")

selected_input_label = Label(root_frame, text="No input folder selected")
selected_input_label.grid(row=1, column=1, sticky="ew")

open_input_folder = Button(root_frame, text="Select input folder",
                           command=select_input_folder(selected_input_label))
open_input_folder.grid(row=0, column=1, sticky="nsew")

duty_year_label = Label(root_frame, text="Duty month/year")
duty_year_label.grid(row=2, column=0, sticky="nsew")

duty_frame = Frame(root_frame)
duty_month_entry = Entry(duty_frame)
duty_month_entry.grid(row=0, column=0, sticky="nsew")
duty_year_entry = Entry(duty_frame)
duty_year_entry.grid(row=0, column=1, sticky="nsew")
duty_frame.grid(row=2, column=1)

public_holidays_label = Label(root_frame, text="Public holidays")
public_holidays_label.grid(row=3, column=0, sticky="nsew")
public_holidays_entry = Entry(root_frame)
public_holidays_entry.grid(row=3, column=1, sticky="nsew")

show_each_blocked_label = Label(root_frame, text="Show individual blocked?")
show_each_blocked_label.grid(row=4, column=0, sticky="nsew")
show_each_blocked = Checkbutton(root_frame, onvalue=1, offvalue=0, variable=show_individual_blocked_pct)
show_each_blocked.grid(row=4, column=1, sticky="nsew")

status_label = Label(root_frame, text="Ready")
status_label.grid(row=6, columnspan=2, sticky="ew")

generate_file = Button(root_frame, text="Generate", command=run_writer(status_label))
generate_file.grid(row=5, columnspan=2, sticky="ew")

root_frame.pack(fill=tkinter.X)

window.mainloop()
