import os
from tkinter import *
from tkinter import filedialog

from reader import ingest_dates
from writer import WriterConfig, writer

window = Tk()
window.title("Duty Planner")

input_path = StringVar()
output_path = StringVar()
show_individual_blocked_pct = IntVar()


def select_input_folder(label: Label):
    def f():
        folder_path = filedialog.askdirectory(title=f"Select input folder")

        if folder_path != "":
            label.configure(text=f"Selected input folder: {folder_path}")
            input_path.set(folder_path)

    return f


def select_output_folder(label: Label):
    def f():
        folder_path = filedialog.askdirectory(title=f"Select output folder")

        if folder_path:
            label.configure(text=f"Selected output folder: {folder_path}")
            output_path.set(folder_path)

    return f


def run_writer():
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

    file_name = output_file_name.get()
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


input_folder_label = Label(window, text="No input folder selected")
input_folder_label.grid(row=1, column=1, sticky="nsew")
open_input_folder = Button(window, text="Select input folder", command=select_input_folder(input_folder_label))
open_input_folder.grid(row=1, column=2, sticky="nsew")

output_folder_label = Label(window, text="No output folder selected")
output_folder_label.grid(row=2, column=1, sticky="nsew")
open_output_folder = Button(window, text="Select output folder", command=select_output_folder(output_folder_label))
open_output_folder.grid(row=2, column=2, sticky="nsew")

output_file_name_label = Label(window, text="File name")
output_file_name_label.grid(row=3, column=1, sticky="nsew")
output_file_name = Entry(window)
output_file_name.grid(row=3, column=2, sticky="nsew")

duty_year_label = Label(window, text="Duty month/year")
duty_year_label.grid(row=4, column=1, sticky="nsew")
duty_month_entry = Entry(window)
duty_month_entry.grid(row=4, column=2, sticky="nsew")
duty_year_entry = Entry(window)
duty_year_entry.grid(row=4, column=3, sticky="nsew")

public_holidays_label = Label(window, text="Public holidays")
public_holidays_label.grid(row=5, column=1, sticky="nsew")
public_holidays_entry = Entry(window)
public_holidays_entry.grid(row=5, column=2, sticky="nsew")

show_each_blocked_label = Label(window, text="Show individual blocked?")
show_each_blocked_label.grid(row=6, column=1, sticky="nsew")
show_each_blocked = Checkbutton(window, onvalue=1, offvalue=0, variable=show_individual_blocked_pct)
show_each_blocked.grid(row=6, column=2, sticky="nsew")

generate_file = Button(window, text="Generate", command=run_writer)
generate_file.grid(row=7, column=1, sticky="nsew")

window.mainloop()
