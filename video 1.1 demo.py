# Variables
# think of it like a container

file_name = 'sale_report_2025.pdf'
file_size_mb = 2.4
is_processed = False
print(f"File: {file_name}")
print(f"Size: {file_size_mb} MB")
print(f"Processed: {is_processed}")

# Data Structure: Organizing multiple items

#Lists: Ordering collection
file_type_to_organize = ['.pdf', '.jpeg', '.xlsx', '.docx', '.png']
print(f"i need to organize {len(file_type_to_organize)} file types")

# Dictionaries: Key: Value

file_categtories = {'.pdf':'Documents',
                    '.jpg':'Images',
                    '.png': 'Images',
                    '.xlsx': 'Spreadsheets',
                    '.docx': 'Documents'}

print(f"A .pdf file goes to: {file_categtories['.pdf']}")

# Loops: Doing something repeatedly (heart of automation)

#For loop: For each files in the list, do something

file_in_folder = ['report.pdf', 'photo.jpg','budget.xlsx', 'note.docx']

for file in file_in_folder:
    #get the extension by spliting on the dot
    extension = '.' + file.split('.')[-1]
    # Look up the Category
    category = file_categtories.get(extension, 'Others')

    print(f"{file}-{category} folder")

    # Conditionals: making decisions automatically

    file_size = 150 # MB

    if file_size > 100:
        print(" Large file - compress before storing")
    elif file_size > 10:
        print("Normal file - Proceed")
    else:
        print("Small file - no action needed")

# Functions: Reusable automation blocks

def organize_file(filename):
    extension = '.'+filename.split('.')[-1]
    category = file_categtories.get(extension, 'Others')
    return category

# Test it
print(organize_file("vacation_photo.jpg"))
print(organize_file('q4_budget.xlsx'))
print(organize_file('unknown_file.xyz'))


#1: create a new python file in vs code. build a script that does the following

# create a list of 10 file names- mix up the extension.(pdf, xlsx, jpg, png, txt, docx)
# Create a dictionary mapping the extensions (file_categories)
# use a loop to categarize each file and print 
# print a summary at the end saying something like found 3 pdf, 2 images, 3 spredsheets and 1 others

#Bonus challenge: add a file size to your lists maybe mb, write a conditon that if file size is large than 20, it should flag it large

