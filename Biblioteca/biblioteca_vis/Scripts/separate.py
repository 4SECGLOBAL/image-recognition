import os
import shutil
from progress.bar import Bar

def SeparaDataset(folder_path, output_folder):

    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    bar = Bar('Processing', max=len(txt_files))

    for txt_file in txt_files:
        file_path = os.path.join(folder_path, txt_file)
        bar.next()

        with open(file_path, 'r') as file:
            first_chars_set = set(line[0] for line in file.readlines())
            
            first_chars = list(first_chars_set)

        if len(first_chars) == 1:
            folder_name = first_chars[0]
            output_folder_path_lbl = os.path.join(output_folder, folder_name + "/labels")
            output_folder_path_img = os.path.join(output_folder, folder_name + "/images")
        elif len(first_chars) > 1:
            folder_name = "MultiClass"
            output_folder_path_lbl = os.path.join(output_folder, folder_name + "/labels")
            output_folder_path_img = os.path.join(output_folder, folder_name + "/images")
        else:
            folder_name = "Empty"
            output_folder_path_lbl = os.path.join(output_folder, folder_name + "/labels")
            output_folder_path_img = os.path.join(output_folder, folder_name + "/images")

        os.makedirs(output_folder_path_lbl, exist_ok=True)
        os.makedirs(output_folder_path_img, exist_ok=True)

        output_file_path_lbl = os.path.join(output_folder_path_lbl, txt_file)
        output_file_path_img = os.path.join(output_folder_path_img, (txt_file.rsplit(".",1)[0] + ".jpg"))
        shutil.copy(file_path, output_file_path_lbl)
        file_path_img = file_path.rsplit("\\", 2)[0] + "/images2/" + (txt_file.rsplit(".",1)[0] + ".jpg")
        shutil.copy(file_path_img, output_file_path_img)
    bar.finish()
