import csv

input_file = 'file_test_link.csv'
output_file = 'file_test_lunk.csv'

with open(input_file, 'r') as csv_input, open(output_file, 'w', newline='', encoding='utf-8', newline='\n') as csv_output:
    reader = csv.reader(csv_input)
    writer = csv.writer(csv_output)
    
    # Write the header row
    header = next(reader)
    writer.writerow(header)
    
    # Iterate through the rows and update first and last items
    for row in reader:
        first_item = int(row[0]) + 1
        last_item = int(row[-1]) + 1
        updated_row = [first_item] + row[1:-1] + [last_item]
        writer.writerow(updated_row)

print("File updated successfully.")

