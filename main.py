import os
from tkinter import *
from tkinter import filedialog

from reader import ingest_dates
from writer import WriterConfig, writer

input_path = "D:\\Coding\\duty-planner-gui\\data\\apr25"
output_path = "D:\\Coding\\duty-planner-gui\\output"
output_file_name = "apr25 test b.xlsx"

duty_year = 2025
duty_month = 4
public_holidays = [18]

show_individual_blocked_pct = True

dir_scan = os.scandir(input_path)

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

writer_config = WriterConfig(output_path=output_path, output_file_name=output_file_name, duty_year=duty_year,
                             duty_month=duty_month, public_holidays=public_holidays,
                             show_individual_blocked_pct=show_individual_blocked_pct)

window = Tk()

window.title("Duty planner")
window.geometry("500x400")


def select_folder(label: Label, kind: str):
    def f():
        folder = filedialog.askdirectory(title=f"Select {kind} folder")

        if folder != "":
            label.configure(text=f"Selected {kind} folder: {folder}")

    return f


def run_writer():
    writer(duty_personnel, writer_config)


input_folder_label = Label(window, text="No input folder selected")
input_folder_label.pack()
open_input_folder = Button(window, text="Select input folder", command=select_folder(input_folder_label, "input"))
open_input_folder.pack()

output_folder_label = Label(window, text="No output folder selected")
output_folder_label.pack()
open_output_folder = Button(window, text="Select output folder", command=select_folder(output_folder_label, "output"))
open_output_folder.pack()

output_file_name_label = Label(window, text="File name (ending in .xlsx)")
output_file_name_label.pack()
output_file_name = Entry(window)
output_file_name.pack()

generate_file = Button(window, text="Generate", command=run_writer)
generate_file.pack()

window.mainloop()
