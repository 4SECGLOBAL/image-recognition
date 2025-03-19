import os
from collections import defaultdict
import argparse

classes_names = ['Arma', 'Boleto', 'Cartao', 'Cig M', 'Dinheiro', 'Documento', 'Faca', 'Munic', 'Print']

def calculate_class_accuracies(groundtruth_folder, predictions_folder):
    # Ensure both folders exist
    if not os.path.exists(groundtruth_folder):
        raise FileNotFoundError(f"Groundtruth folder not found: {groundtruth_folder}")
    if not os.path.exists(predictions_folder):
        raise FileNotFoundError(f"Predictions folder not found: {predictions_folder}")
    
    # Initialize dictionaries to store counts
    class_correct = defaultdict(int)
    class_total = defaultdict(int)

    # Iterate through groundtruth files
    for gt_file in os.listdir(groundtruth_folder):
        if not gt_file.endswith('.txt'):
            continue

        gt_path = os.path.join(groundtruth_folder, gt_file)
        pred_path = os.path.join(predictions_folder, gt_file)

        # Ensure corresponding prediction file exists
        if not os.path.exists(pred_path):
            print(f"Warning: Prediction file missing for {gt_file}")
            continue

        # Read groundtruth and prediction files
        with open(gt_path, 'r') as gt_f, open(pred_path, 'r') as pred_f:
            gt_classes = set(line.split()[0] for line in gt_f.readlines())
            pred_classes = set(line.split()[0] for line in pred_f.readlines())

        # Update counts for each class
        for cls in gt_classes:
            class_total[cls] += 1
            if cls in pred_classes:
                class_correct[cls] += 1

    # Calculate accuracies
    class_accuracies = {}
    for cls in class_total:
        class_accuracies[cls] = class_correct[cls] / class_total[cls]

    return class_accuracies

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate class-by-class accuracies.")
    parser.add_argument("gth_folder", type=str, help="Path to the groundtruth folder")
    parser.add_argument("prd_folder", type=str, help="Path to the predictions folder")
    args = parser.parse_args()

    try:
        accuracies = calculate_class_accuracies(args.gth_folder, args.prd_folder)
        print("Class-by-class accuracies:")
        for cls, acc in accuracies.items():
            class_name = classes_names[int(cls)]
            print(f"Class {class_name}: {acc:.2f}")
    except Exception as e:
        print(f"Error: {e}")