import os

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

writer(duty_personnel, writer_config)
