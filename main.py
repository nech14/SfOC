
from src import graphics
from src import file
import os

image_number = 13

current_directory = os.getcwd()
print("Текущая рабочая директория:", current_directory)

path = os.path.join(current_directory, "data", "ASI0", "2023", "10", "11")
new_path = os.path.join(path, "5577")

names = file.get_name_file(new_path)

save_path = os.path.join(path, "5577_img")
for name in names:

    name_path = os.path.join(new_path, name)
    data = file.open_gz(name_path)

    graphics.save_graphics(data, save_path, name[:-8])
    # graphics.print_graphics(data)
    print(name)
print('hay')
