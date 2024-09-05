import csv

input_file = "file_metadata.csv"
output_file = "file_me2data.csv"

with open(input_file, "r") as csv_input, open(
    output_file, "w", newline="", encoding="utf-8", newline="\n"
) as csv_output:
    reader = csv.reader(csv_input)
    writer = csv.writer(csv_output)

    # Write the header row
    header = next(reader)
    writer.writerow(header)

    # Iterate through the rows and update file_id
    for row in reader:
        file_id = int(row[0]) + 1
        updated_row = [file_id] + row[1:]
        writer.writerow(updated_row)

print("File updated successfully.")
