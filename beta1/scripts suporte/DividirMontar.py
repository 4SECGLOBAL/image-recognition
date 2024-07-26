import os
import shutil
from sklearn.model_selection import train_test_split

def split_dataset(dataset_path, train_dir, validation_dir, test_size=0.2, random_state=42):
    # Get the list of file names from the dataset
    file_names = os.listdir(dataset_path)

    # Split the dataset into training and validation sets
    train_files, validation_files = train_test_split(file_names, test_size=test_size, random_state=random_state)

    # Create directories for training and validation
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(validation_dir, exist_ok=True)

    # Move the files to their respective directories
    for file_name in train_files:
        source_path = os.path.join(dataset_path, file_name)
        destination_path = os.path.join(train_dir, file_name)
        shutil.copy(source_path, destination_path)

    for file_name in validation_files:
        source_path = os.path.join(dataset_path, file_name)
        destination_path = os.path.join(validation_dir, file_name)
        shutil.copy(source_path, destination_path)

if __name__ == "__main__":
    # Replace these paths with the actual paths of your dataset
    dataset_path = input("Qual o path do dataset a ser dividido?")
    saved_divided_path = input("Qual o path aonde sera salvo o dataset separado?")
    train_dir = os.path.join(saved_divided_path, "train")
    validation_dir = os.path.join(saved_divided_path, "val")

    # Proportion of instances for the validation set (0.2 means 20%)
    test_size = 0.2

    split_dataset(dataset_path, train_dir, validation_dir, test_size)

    print("Dataset separated into training and validation sets.")
