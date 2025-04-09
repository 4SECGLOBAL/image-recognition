import os
from collections import defaultdict
import argparse

classes_names = ['Arma', 'Boleto', 'Cartao', 'Cig M', 'Dinheiro', 'Documento', 'Faca', 'Munic', 'Print']

def calculate_class_accuracies(groundtruth_folder, predictions_folder, check_fp=False, n_img=1228):
    # Ensure both folders exist
    if not os.path.exists(groundtruth_folder) and not(check_fp):
        raise FileNotFoundError(f"Groundtruth folder not found: {groundtruth_folder}")
    if not os.path.exists(predictions_folder):
        raise FileNotFoundError(f"Predictions folder not found: {predictions_folder}")
    
    # Initialize dictionaries to store counts
    class_correct = defaultdict(int)
    class_total = defaultdict(int)

    if check_fp:
        # Initialize a dictionary to count images where each class appears
        class_image_count = defaultdict(int)
        total_images = 1228

        # Iterate through prediction files
        for pred_file in os.listdir(predictions_folder):
            if not pred_file.endswith('.txt'):
                continue

            #total_images += 1
            pred_path = os.path.join(predictions_folder, pred_file)

            # Read prediction file
            with open(pred_path, 'r') as pred_f:
                pred_classes = set(line.split()[0] for line in pred_f.readlines())

            # Update image count for each class
            for cls in pred_classes:
                class_image_count[cls] += 1

        # Calculate class appearance metrics
        class_appearance_metrics = {}
        for cls in class_image_count:
            class_appearance_metrics[cls] = class_image_count[cls] / total_images

        print("False positive percentages:")
        for cls, acc in class_appearance_metrics.items():
            class_name = classes_names[int(cls)]
            print(f"Class {class_name}: {acc:.2f} | {class_image_count[cls]}/{total_images}")

    else:
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

        print("Class-by-class accuracies:")
        for cls, acc in class_accuracies.items():
            class_name = classes_names[int(cls)]
            print(f"Class {class_name}: {acc:.2f} | {class_correct[cls]}/{class_total[cls]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate class-by-class accuracies.")
    parser.add_argument("gth_folder", type=str, help="Path to the groundtruth folder")
    parser.add_argument("prd_folder", type=str, help="Path to the predictions folder")
    parser.add_argument("--check_fp", type=str, help="Verify the percentage of false positives", default=False)
    parser.add_argument("--n_img", type=int, help="Total number of images", default=1228)
    args = parser.parse_args()

    try:
        calculate_class_accuracies(args.gth_folder, args.prd_folder, args.check_fp, args.n_img)
    except Exception as e:
        print(f"Error: {e}")