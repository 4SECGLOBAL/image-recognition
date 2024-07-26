import os 
import shutil
from sklearn.model_selection import train_test_split



dataset_path = input("Qual o path do dataset a ser dividido?")
path_imagens = os.path.join(dataset_path, "images")
path_labels = os.path.join(dataset_path, "labels")

saved_divided_path = os.path.join(dataset_path, "PREPARADO")
train_dir = os.path.join(saved_divided_path, "train")
validation_dir = os.path.join(saved_divided_path, "val")

os.makedirs(os.path.join(train_dir,"images"), exist_ok=True)
os.makedirs(os.path.join(train_dir,"labels"), exist_ok=True)

os.makedirs(os.path.join(validation_dir,"images"), exist_ok=True)
os.makedirs(os.path.join(validation_dir,"labels"), exist_ok=True)

print("comecando")

images = [os.path.join(path_imagens, x) for x in os.listdir(path_imagens)]
annotations = [os.path.join(path_labels, x) for x in os.listdir(path_labels) if x[-3:] == "txt"]
images.sort()
annotations.sort()
train_images, val_images, train_annotations, val_annotations = train_test_split(images, annotations, test_size = 0.2, random_state = 1)

def move_files_to_folder(list_of_files, destination_folder):
    for f in list_of_files:
        try:
            shutil.move(f, destination_folder)
        except:
            print(f)
            assert False

move_files_to_folder(train_images, os.path.join(train_dir,"images"))
move_files_to_folder(val_images, os.path.join(validation_dir,"images"))
move_files_to_folder(train_annotations, os.path.join(train_dir,"labels"))
move_files_to_folder(val_annotations, os.path.join(validation_dir,"labels"))